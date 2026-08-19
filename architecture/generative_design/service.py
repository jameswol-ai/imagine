"""
IMAGINE
Generative Design Service

Application service for constraint-driven architectural
generative design.

Responsibilities:
- normalize and validate constraints
- stop invalid generation deterministically
- invoke the generator with normalized constraints
- score generated candidates
- persist the run and candidates within one transaction
- update candidate_count
- mark successful runs completed
- mark failed runs failed
- preserve rollback semantics
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from .constraints import (
    normalize_and_validate_constraints,
)
from .generator import generate_candidates
from .repository import (
    GenerativeDesignRepository,
)
from .schemas import (
    ConstraintValidationResult,
    DesignCandidateSchema,
    DesignConstraints,
    GenerativeDesignRunCreate,
    GenerativeDesignRunResponse,
)


class GenerativeDesignValidationError(ValueError):
    """
    Raised when generative-design constraints are invalid.

    The error message is deterministic because it is produced by
    normalize_and_validate_constraints().
    """

    def __init__(
        self,
        validation: ConstraintValidationResult,
    ) -> None:
        self.validation = validation

        message = "; ".join(
            validation.errors
        )

        super().__init__(
            message
        )


class GenerativeDesignGenerationError(
    RuntimeError
):
    """
    Raised when candidate generation fails.
    """


class GenerativeDesignService:
    """
    Application service for generative architectural design.
    """

    def __init__(
        self,
        session: AsyncSession,
        repository: GenerativeDesignRepository | None = None,
        generator: Callable[
            [DesignConstraints],
            Sequence[Any],
        ]
        | None = None,
        scorer: Callable[
            [Any, DesignConstraints],
            Any,
        ]
        | None = None,
    ) -> None:
        self.session = session

        self.repository = (
            repository
            or GenerativeDesignRepository(
                session
            )
        )

        self.generator = (
            generator
            or generate_candidates
        )

        self.scorer = scorer

    # =================================================================
    # GENERATE
    # =================================================================

    async def generate(
        self,
        request: GenerativeDesignRunCreate,
    ) -> GenerativeDesignRunResponse:
        """
        Generate, score, and persist a complete design run.

        Processing order:

            1. Normalize constraints.
            2. Validate constraints.
            3. Stop immediately if invalid.
            4. Generate candidates.
            5. Score candidates.
            6. Begin one persistence transaction.
            7. Create run.
            8. Persist all candidates.
            9. Update candidate_count.
            10. Mark run completed.
            11. Commit once.

        Any persistence/generation/scoring failure rolls the database
        transaction back.

        Invalid constraints never create a database run.
        """

        # -------------------------------------------------------------
        # 1. Normalize and validate BEFORE database transaction
        # -------------------------------------------------------------

        normalized, validation = (
            normalize_and_validate_constraints(
                request.constraints
            )
        )

        if normalized is None or not validation.valid:
            raise GenerativeDesignValidationError(
                validation
            )

        # -------------------------------------------------------------
        # 2. Keep request.project_id and constraint.project_id
        #    consistent.
        # -------------------------------------------------------------

        normalized = self._normalize_project_id(
            request.project_id,
            normalized,
        )

        # -------------------------------------------------------------
        # 3. Generate candidates from normalized constraints.
        # -------------------------------------------------------------

        try:
            generated_candidates = self.generator(
                normalized
            )
        except Exception as exc:
            raise GenerativeDesignGenerationError(
                f"Generative design generation failed: {exc}"
            ) from exc

        candidates = list(
            generated_candidates
        )

        # -------------------------------------------------------------
        # 4. Respect requested candidate count.
        # -------------------------------------------------------------

        candidates = candidates[
            : request.candidate_count
        ]

        # -------------------------------------------------------------
        # 5. Score candidates before persistence.
        # -------------------------------------------------------------

        scored_candidates = []

        for candidate in candidates:

            try:
                scored = self._score_candidate(
                    candidate,
                    normalized,
                )

            except Exception as exc:
                raise GenerativeDesignGenerationError(
                    f"Generative design scoring failed: {exc}"
                ) from exc

            scored_candidates.append(
                scored
            )

        # -------------------------------------------------------------
        # 6. Single persistence transaction.
        #
        # Do not commit inside repository methods.
        # -------------------------------------------------------------

        try:
            run = await self.repository.create_run(
                project_id=normalized.project_id,
                name=request.name,
                status="generating",
                constraints=normalized.model_dump(
                    mode="json"
                ),
                candidate_count=0,
            )

            # ---------------------------------------------------------
            # 7. Persist every candidate.
            # ---------------------------------------------------------

            for index, candidate in enumerate(
                scored_candidates,
                start=1,
            ):
                candidate_data = (
                    self._candidate_to_dict(
                        candidate
                    )
                )

                if candidate_data.get(
                    "rank"
                ) is None:
                    candidate_data["rank"] = index

                await self.repository.create_candidate(
                    run_id=run.id,
                    **candidate_data,
                )

            # ---------------------------------------------------------
            # 8. Update candidate count.
            # ---------------------------------------------------------

            run = await self.repository.update_run(
                run.id,
                candidate_count=len(
                    scored_candidates
                ),
            )

            # ---------------------------------------------------------
            # 9. Mark completed.
            # ---------------------------------------------------------

            run = await self.repository.update_run(
                run.id,
                status="completed",
                completed_at=datetime.now(
                    timezone.utc
                ),
                error_message=None,
            )

            # ---------------------------------------------------------
            # 10. ONE COMMIT.
            # ---------------------------------------------------------

            await self.session.commit()

        except Exception:
            # ---------------------------------------------------------
            # Any database failure rolls back the complete operation.
            # ---------------------------------------------------------

            await self.session.rollback()

            raise

        # -------------------------------------------------------------
        # 11. Return persisted run.
        # -------------------------------------------------------------

        return await self._build_response(
            run.id
        )

    # =================================================================
    # PROJECT ID NORMALIZATION
    # =================================================================

    @staticmethod
    def _normalize_project_id(
        request_project_id: UUID | None,
        constraints: DesignConstraints,
    ) -> DesignConstraints:
        """
        Ensure project_id is represented consistently.

        If the request contains a project ID and the constraints do
        not, the request ID is copied into the normalized constraints.

        If both exist but differ, generation is rejected.
        """

        constraint_project_id = (
            constraints.project_id
        )

        if (
            request_project_id is not None
            and constraint_project_id is not None
            and request_project_id
            != constraint_project_id
        ):
            raise GenerativeDesignValidationError(
                ConstraintValidationResult(
                    valid=False,
                    errors=[
                        "project_id in request does not match "
                        "project_id in constraints."
                    ],
                    warnings=[],
                )
            )

        if (
            request_project_id is not None
            and constraint_project_id is None
        ):
            return constraints.model_copy(
                update={
                    "project_id": request_project_id
                }
            )

        return constraints

    # =================================================================
    # SCORING
    # =================================================================

    def _score_candidate(
        self,
        candidate: Any,
        constraints: DesignConstraints,
    ) -> Any:
        """
        Score one generated candidate.

        If no external scorer is supplied, the candidate is returned
        unchanged. This keeps the service compatible with the current
        generator while allowing scoring.py to be injected cleanly.
        """

        if self.scorer is None:
            return candidate

        return self.scorer(
            candidate,
            constraints,
        )

    # =================================================================
    # CANDIDATE NORMALIZATION
    # =================================================================

    @staticmethod
    def _candidate_to_dict(
        candidate: Any,
    ) -> dict[str, Any]:
        """
        Convert a generated/scored candidate into repository fields.
        """

        if isinstance(
            candidate,
            DesignCandidateSchema,
        ):
            data = candidate.model_dump(
                mode="json"
            )

        elif hasattr(
            candidate,
            "model_dump",
        ):
            data = candidate.model_dump(
                mode="json"
            )

        elif isinstance(
            candidate,
            dict,
        ):
            data = dict(candidate)

        else:
            data = {
                key: getattr(
                    candidate,
                    key,
                )
                for key in (
                    "name",
                    "status",
                    "rank",
                    "score",
                    "geometry",
                    "metrics",
                    "evaluation",
                )
                if hasattr(
                    candidate,
                    key,
                )
            }

        # -------------------------------------------------------------
        # Repository.create_candidate() should receive only fields
        # belonging to DesignCandidateRecord.
        # -------------------------------------------------------------

        allowed_fields = {
            "name",
            "status",
            "rank",
            "score",
            "geometry",
            "metrics",
            "evaluation",
        }

        return {
            key: value
            for key, value in data.items()
            if key in allowed_fields
        }

    # =================================================================
    # RESPONSE
    # =================================================================

    async def _build_response(
        self,
        run_id: UUID,
    ) -> GenerativeDesignRunResponse:
        """
        Load the completed run and construct its response schema.
        """

        run = await self.repository.get_run(
            run_id
        )

        if run is None:
            raise RuntimeError(
                "Generative design run could not be "
                "loaded after successful commit."
            )

        return GenerativeDesignRunResponse.model_validate(
            run
        )