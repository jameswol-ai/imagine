"""
IMAGINE
Generative Design Service

Application service for constraint-driven architectural
generative design.

The service owns the application transaction boundary.

Constraint validation happens before generation and before
any database write.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from .constraints import (
    normalize_and_validate_constraints,
)
from .generator import (
    DesignCandidate,
    generate_candidates,
)
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
    Raised when candidate generation or scoring fails.
    """


class GenerativeDesignService:
    """
    Application service for generative architectural design.

    Generation and scoring occur before database persistence.

    Once persistence begins, this service owns the single transaction
    and performs exactly one commit on success.
    """

    def __init__(
        self,
        session: AsyncSession,
        repository: GenerativeDesignRepository | None = None,
        scorer: Callable[
            [DesignCandidate, DesignConstraints],
            DesignCandidate,
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

        self.scorer = scorer

    # =================================================================
    # GENERATE
    # =================================================================

    async def generate(
        self,
        request: GenerativeDesignRunCreate,
    ) -> GenerativeDesignRunResponse:
        """
        Generate and persist a complete generative-design run.

        Processing order:

        1. Normalize constraints.
        2. Validate constraints.
        3. Stop immediately if invalid.
        4. Resolve project UUID consistency.
        5. Generate candidates using the actual generator contract.
        6. Score candidates if a scorer has been supplied.
        7. Persist the run.
        8. Persist all candidates.
        9. Update candidate_count.
        10. Mark the run completed.
        11. Commit exactly once.

        Any persistence failure causes a rollback.

        Generation/scoring failures occur before persistence, so no
        database rollback is required for those failures.
        """

        # -------------------------------------------------------------
        # 1. Normalize and validate constraints.
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
        # 2. Resolve project ID.
        # -------------------------------------------------------------

        normalized = self._normalize_project_id(
            request.project_id,
            normalized,
        )

        # -------------------------------------------------------------
        # 3. Generate candidates.
        #
        # IMPORTANT:
        # generator.py expects:
        #
        # generate_candidates(
        #     constraints,
        #     count,
        # )
        #
        # It returns list[DesignCandidate].
        # -------------------------------------------------------------

        try:
            candidates = generate_candidates(
                normalized,
                count=request.candidate_count,
            )
        except Exception as exc:
            raise GenerativeDesignGenerationError(
                f"Generative design generation failed: {exc}"
            ) from exc

        # -------------------------------------------------------------
        # 4. Score candidates.
        #
        # generator.py currently initializes score=0.0 and rank=None.
        # The optional scorer can enrich those fields.
        # -------------------------------------------------------------

        try:
            candidates = self._score_candidates(
                candidates,
                normalized,
            )
        except Exception as exc:
            raise GenerativeDesignGenerationError(
                f"Generative design scoring failed: {exc}"
            ) from exc

        # -------------------------------------------------------------
        # 5. Persistence transaction.
        #
        # Repository methods remain transaction-neutral.
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
            # 6. Persist every candidate.
            # ---------------------------------------------------------

            for index, candidate in enumerate(
                candidates,
                start=1,
            ):
                candidate_data = (
                    self._candidate_to_dict(
                        candidate
                    )
                )

                # The generator deliberately leaves rank unset.
                # The service establishes deterministic initial ranking.
                if candidate_data.get(
                    "rank"
                ) is None:
                    candidate_data["rank"] = index

                await self.repository.create_candidate(
                    run_id=run.id,
                    **candidate_data,
                )

            # ---------------------------------------------------------
            # 7. Update candidate count.
            # ---------------------------------------------------------

            run = await self.repository.update_run(
                run.id,
                candidate_count=len(
                    candidates
                ),
            )

            # ---------------------------------------------------------
            # 8. Mark run completed.
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
            # 9. SINGLE COMMIT.
            # ---------------------------------------------------------

            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise

        # -------------------------------------------------------------
        # 10. Reload committed run.
        # -------------------------------------------------------------

        return await self._build_response(
            run.id
        )

    # =================================================================
    # PROJECT ID
    # =================================================================

    @staticmethod
    def _normalize_project_id(
        request_project_id: UUID | None,
        constraints: DesignConstraints,
    ) -> DesignConstraints:
        """
        Ensure the request and normalized constraints contain the same
        project UUID.
        """

        constraint_project_id = (
            constraints.project_id
        )

        # Both supplied and different.
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

        # Request supplies the project ID but the nested constraints
        # do not. Copy it into the normalized constraints.
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

    def _score_candidates(
        self,
        candidates: list[DesignCandidate],
        constraints: DesignConstraints,
    ) -> list[DesignCandidate]:
        """
        Score generated candidates.

        The current generator does not perform scoring, so the scorer
        is optional.

        If no scorer is supplied, generated candidates pass through
        unchanged.
        """

        if self.scorer is None:
            return candidates

        scored: list[DesignCandidate] = []

        for candidate in candidates:
            result = self.scorer(
                candidate,
                constraints,
            )

            scored.append(
                result
            )

        return scored

    # =================================================================
    # CANDIDATE SERIALIZATION
    # =================================================================

    @staticmethod
    def _candidate_to_dict(
        candidate: DesignCandidate,
    ) -> dict[str, Any]:
        """
        Convert the actual generator DesignCandidate dataclass into
        fields accepted by DesignCandidateRecord.
        """

        return {
            "name": candidate.name,
            "status": candidate.status,
            "rank": candidate.rank,
            "score": candidate.score,
            "geometry": candidate.geometry,
            "metrics": candidate.metrics,
            "evaluation": candidate.evaluation,
        }

    # =================================================================
    # RESPONSE
    # =================================================================

    async def _build_response(
        self,
        run_id: UUID,
    ) -> GenerativeDesignRunResponse:
        """
        Reload a persisted run and convert it to the response schema.
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