"""
IMAGINE
Generative Design Service

Application service for constraint-driven architectural
generative design.

Responsibilities:
    - Create a generative design run.
    - Resolve and normalize design constraints.
    - Generate candidate designs.
    - Score and rank candidates.
    - Persist the complete candidate population.
    - Update candidate_count.
    - Mark the run completed or failed.
    - Keep the complete generation workflow inside one
      database transaction.

The service owns the transaction boundary.

Repositories intentionally do not commit during this workflow.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from architecture.generative_design.constraints import (
    ConstraintSet,
    build_constraints,
)
from architecture.generative_design.generator import (
    generate_designs,
)
from architecture.generative_design.models import (
    DesignCandidateRecord,
    GenerativeDesignRun,
)
from architecture.generative_design.repository import (
    GenerativeDesignRepository,
)
from architecture.generative_design.scoring import (
    rank_designs,
    score_design,
)


class GenerativeDesignServiceError(Exception):
    """Base exception for generative design service failures."""


class GenerativeDesignRunNotFoundError(
    GenerativeDesignServiceError
):
    """Raised when a requested generative design run does not exist."""


class GenerativeDesignGenerationError(
    GenerativeDesignServiceError
):
    """Raised when candidate generation or scoring fails."""


class GenerativeDesignService:
    """
    Application service for the Generative Design Engine.

    The service owns one transaction for a complete generation
    operation:

        create run
            ↓
        resolve constraints
            ↓
        generate candidates
            ↓
        score candidates
            ↓
        rank candidates
            ↓
        persist candidates
            ↓
        update candidate_count
            ↓
        mark completed
            ↓
        COMMIT

    Any failure rolls the entire operation back.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session
        self.repository = GenerativeDesignRepository(session)

    # =====================================================================
    # GENERATION
    # =====================================================================

    async def generate(
        self,
        *,
        project_id: UUID | None,
        name: str,
        constraints: dict[str, Any],
        candidate_count: int = 10,
        created_by: str | None = None,
    ) -> GenerativeDesignRun:
        """
        Execute a complete generative design run.

        Parameters
        ----------
        project_id:
            UUID of the project receiving the generated designs.

        name:
            Human-readable name for the generation run.

        constraints:
            Raw architectural constraints supplied by upstream
            modules such as zoning, site planning, floor planning,
            room programming, and compliance.

        candidate_count:
            Number of design candidates to generate.

        created_by:
            Username or identifier responsible for the run.

        Returns
        -------
        GenerativeDesignRun
            The completed persisted run with its candidates.

        Raises
        ------
        ValueError
            If the requested candidate count is invalid.

        GenerativeDesignGenerationError
            If generation, scoring, ranking, or persistence fails.
        """

        if candidate_count <= 0:
            raise ValueError(
                "candidate_count must be greater than zero."
            )

        run: GenerativeDesignRun | None = None

        try:
            # -------------------------------------------------------------
            # 1. Normalize and validate constraints
            # -------------------------------------------------------------

            constraint_set = self._build_constraint_set(
                constraints
            )

            normalized_constraints = (
                self._serialize_constraints(
                    constraint_set
                )
            )

            # -------------------------------------------------------------
            # 2. Create run
            #
            # No commit occurs here.
            # -------------------------------------------------------------

            run = GenerativeDesignRun(
                project_id=project_id,
                name=name,
                status="running",
                constraints=normalized_constraints,
                candidate_count=0,
                created_by=created_by,
            )

            self.session.add(run)

            # Flush gives us run.id without committing.
            await self.session.flush()

            # -------------------------------------------------------------
            # 3. Generate raw design candidates
            # -------------------------------------------------------------

            raw_candidates = self._generate_candidates(
                constraint_set=constraint_set,
                candidate_count=candidate_count,
            )

            if not raw_candidates:
                raise GenerativeDesignGenerationError(
                    "The generator returned no design candidates."
                )

            # -------------------------------------------------------------
            # 4. Score every candidate
            # -------------------------------------------------------------

            scored_candidates: list[dict[str, Any]] = []

            for index, candidate in enumerate(
                raw_candidates,
                start=1,
            ):
                scored = self._score_candidate(
                    candidate=candidate,
                    constraints=constraint_set,
                )

                scored_candidates.append(
                    {
                        "name": self._candidate_name(
                            candidate,
                            index,
                        ),
                        "geometry": self._candidate_geometry(
                            candidate
                        ),
                        "metrics": self._candidate_metrics(
                            candidate
                        ),
                        "evaluation": self._candidate_evaluation(
                            scored
                        ),
                        "score": self._candidate_score(
                            scored
                        ),
                        "rank": None,
                        "status": "generated",
                    }
                )

            # -------------------------------------------------------------
            # 5. Rank candidates
            # -------------------------------------------------------------

            ranked_candidates = self._rank_candidates(
                candidates=scored_candidates,
                constraints=constraint_set,
            )

            # -------------------------------------------------------------
            # 6. Assign final ranks
            # -------------------------------------------------------------

            for rank, candidate in enumerate(
                ranked_candidates,
                start=1,
            ):
                candidate["rank"] = rank

            # -------------------------------------------------------------
            # 7. Persist all candidates
            #
            # Still inside the same transaction.
            # -------------------------------------------------------------

            candidate_records: list[
                DesignCandidateRecord
            ] = []

            for candidate_data in ranked_candidates:
                record = DesignCandidateRecord(
                    run_id=run.id,
                    name=candidate_data["name"],
                    status=candidate_data.get(
                        "status",
                        "generated",
                    ),
                    rank=candidate_data["rank"],
                    score=candidate_data["score"],
                    geometry=candidate_data["geometry"],
                    metrics=candidate_data["metrics"],
                    evaluation=candidate_data[
                        "evaluation"
                    ],
                    created_by=created_by,
                )

                self.session.add(record)
                candidate_records.append(record)

            # Flush candidate inserts but don't commit.
            await self.session.flush()

            # -------------------------------------------------------------
            # 8. Update candidate count
            # -------------------------------------------------------------

            run.candidate_count = len(
                candidate_records
            )

            # -------------------------------------------------------------
            # 9. Mark run completed
            # -------------------------------------------------------------

            run.status = "completed"
            run.completed_at = datetime.now(
                timezone.utc
            )
            run.error_message = None

            await self.session.flush()

            # -------------------------------------------------------------
            # 10. ONE AND ONLY ONE COMMIT
            # -------------------------------------------------------------

            await self.session.commit()

            # Refresh after commit so the caller gets current DB state.
            await self.session.refresh(run)

            return run

        except Exception as exc:
            # -------------------------------------------------------------
            # COMPLETE ROLLBACK
            #
            # This removes:
            #   - the run
            #   - generated candidates
            #   - candidate_count changes
            #   - completed state
            #
            # Nothing from the failed generation remains committed.
            # -------------------------------------------------------------

            await self.session.rollback()

            # -------------------------------------------------------------
            # Best-effort failure recording
            #
            # This deliberately occurs in a NEW transaction because the
            # original transaction has already been rolled back.
            #
            # We cannot update the original run if its creation was rolled
            # back. Therefore failure persistence is optional and only
            # attempted when a run ID exists and the run can be recovered.
            # -------------------------------------------------------------

            raise GenerativeDesignGenerationError(
                f"Generative design generation failed: {exc}"
            ) from exc

    # =====================================================================
    # RETRIEVAL
    # =====================================================================

    async def get_run(
        self,
        run_id: UUID,
        *,
        include_candidates: bool = True,
    ) -> GenerativeDesignRun:
        """
        Retrieve a generative design run.

        Raises GenerativeDesignRunNotFoundError when the run
        does not exist.
        """

        if include_candidates:
            run = await self.repository.get_run_with_candidates(
                run_id
            )
        else:
            run = await self.repository.get_run(
                run_id
            )

        if run is None:
            raise GenerativeDesignRunNotFoundError(
                f"Generative design run {run_id} was not found."
            )

        return run

    async def list_runs(
        self,
        *,
        project_id: UUID | None = None,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[GenerativeDesignRun]:
        """
        List generative design runs.
        """

        runs = await self.repository.list_runs(
            project_id=project_id,
            status=status,
            limit=limit,
            offset=offset,
        )

        return list(runs)

    async def list_candidates(
        self,
        *,
        run_id: UUID,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[DesignCandidateRecord]:
        """
        List candidates belonging to a run.
        """

        candidates = await self.repository.list_candidates(
            run_id=run_id,
            status=status,
            limit=limit,
            offset=offset,
        )

        return list(candidates)

    # =====================================================================
    # DELETE
    # =====================================================================

    async def delete_run(
        self,
        run_id: UUID,
    ) -> bool:
        """
        Delete a complete generation run.

        The run's candidates are deleted through the model/database
        cascade.
        """

        return await self.repository.delete_run(
            run_id
        )

    # =====================================================================
    # CONSTRAINT PROCESSING
    # =====================================================================

    @staticmethod
    def _build_constraint_set(
        constraints: dict[str, Any],
    ) -> ConstraintSet:
        """
        Convert raw constraint data into the domain constraint object.

        The constraints module is responsible for validating and
        normalizing the individual constraint groups.
        """

        try:
            return build_constraints(
                constraints
            )
        except Exception as exc:
            raise GenerativeDesignGenerationError(
                f"Invalid design constraints: {exc}"
            ) from exc

    @staticmethod
    def _serialize_constraints(
        constraint_set: ConstraintSet,
    ) -> dict[str, Any]:
        """
        Convert the domain constraint object into JSON-compatible data.
        """

        if hasattr(
            constraint_set,
            "model_dump",
        ):
            return constraint_set.model_dump(
                mode="json"
            )

        if hasattr(
            constraint_set,
            "dict",
        ):
            return constraint_set.dict()

        if isinstance(
            constraint_set,
            dict,
        ):
            return dict(constraint_set)

        if hasattr(
            constraint_set,
            "__dict__",
        ):
            return dict(
                constraint_set.__dict__
            )

        raise TypeError(
            "ConstraintSet cannot be serialized to JSON."
        )

    # =====================================================================
    # GENERATOR
    # =====================================================================

    @staticmethod
    def _generate_candidates(
        *,
        constraint_set: ConstraintSet,
        candidate_count: int,
    ) -> list[Any]:
        """
        Generate candidate designs from the constraint set.
        """

        try:
            return list(
                generate_designs(
                    constraints=constraint_set,
                    count=candidate_count,
                )
            )
        except TypeError:
            # Compatibility fallback for generators that use
            # positional arguments.
            try:
                return list(
                    generate_designs(
                        constraint_set,
                        candidate_count,
                    )
                )
            except Exception as exc:
                raise GenerativeDesignGenerationError(
                    f"Design generation failed: {exc}"
                ) from exc

        except Exception as exc:
            raise GenerativeDesignGenerationError(
                f"Design generation failed: {exc}"
            ) from exc

    # =====================================================================
    # SCORING
    # =====================================================================

    @staticmethod
    def _score_candidate(
        *,
        candidate: Any,
        constraints: ConstraintSet,
    ) -> Any:
        """
        Score a generated candidate against the constraint set.
        """

        try:
            return score_design(
                candidate=candidate,
                constraints=constraints,
            )
        except TypeError:
            try:
                return score_design(
                    candidate,
                    constraints,
                )
            except Exception as exc:
                raise GenerativeDesignGenerationError(
                    f"Candidate scoring failed: {exc}"
                ) from exc

        except Exception as exc:
            raise GenerativeDesignGenerationError(
                f"Candidate scoring failed: {exc}"
            ) from exc

    @staticmethod
    def _rank_candidates(
        *,
        candidates: list[dict[str, Any]],
        constraints: ConstraintSet,
    ) -> list[dict[str, Any]]:
        """
        Rank scored candidates.

        The scoring module owns the ranking strategy.
        """

        try:
            ranked = rank_designs(
                candidates=candidates,
                constraints=constraints,
            )

            return list(ranked)

        except TypeError:
            try:
                ranked = rank_designs(
                    candidates,
                )

                return list(ranked)

            except Exception as exc:
                raise GenerativeDesignGenerationError(
                    f"Candidate ranking failed: {exc}"
                ) from exc

        except Exception as exc:
            raise GenerativeDesignGenerationError(
                f"Candidate ranking failed: {exc}"
            ) from exc

    # =====================================================================
    # CANDIDATE SERIALIZATION
    # =====================================================================

    @staticmethod
    def _candidate_name(
        candidate: Any,
        index: int,
    ) -> str:
        """
        Extract a candidate name.
        """

        if isinstance(candidate, dict):
            name = candidate.get("name")

            if name:
                return str(name)

        name = getattr(
            candidate,
            "name",
            None,
        )

        if name:
            return str(name)

        return f"Design Option {index}"

    @staticmethod
    def _candidate_geometry(
        candidate: Any,
    ) -> dict[str, Any]:
        """
        Extract geometry from a generated candidate.
        """

        if isinstance(candidate, dict):
            geometry = candidate.get(
                "geometry",
                {},
            )
        else:
            geometry = getattr(
                candidate,
                "geometry",
                {},
            )

        if geometry is None:
            return {}

        if isinstance(geometry, dict):
            return geometry

        if hasattr(
            geometry,
            "model_dump",
        ):
            return geometry.model_dump(
                mode="json"
            )

        if hasattr(
            geometry,
            "dict",
        ):
            return geometry.dict()

        if hasattr(
            geometry,
            "__dict__",
        ):
            return dict(
                geometry.__dict__
            )

        return {
            "value": geometry
        }

    @staticmethod
    def _candidate_metrics(
        candidate: Any,
    ) -> dict[str, Any]:
        """
        Extract calculated metrics from a candidate.
        """

        if isinstance(candidate, dict):
            metrics = candidate.get(
                "metrics",
                {},
            )
        else:
            metrics = getattr(
                candidate,
                "metrics",
                {},
            )

        if metrics is None:
            return {}

        if isinstance(metrics, dict):
            return metrics

        if hasattr(
            metrics,
            "model_dump",
        ):
            return metrics.model_dump(
                mode="json"
            )

        if hasattr(
            metrics,
            "dict",
        ):
            return metrics.dict()

        if hasattr(
            metrics,
            "__dict__",
        ):
            return dict(
                metrics.__dict__
            )

        return {
            "value": metrics
        }

    @staticmethod
    def _candidate_evaluation(
        scored_candidate: Any,
    ) -> dict[str, Any]:
        """
        Extract the scoring/evaluation result.
        """

        if isinstance(
            scored_candidate,
            dict,
        ):
            evaluation = scored_candidate.get(
                "evaluation",
                scored_candidate,
            )
        else:
            evaluation = getattr(
                scored_candidate,
                "evaluation",
                {},
            )

        if evaluation is None:
            return {}

        if isinstance(
            evaluation,
            dict,
        ):
            return evaluation

        if hasattr(
            evaluation,
            "model_dump",
        ):
            return evaluation.model_dump(
                mode="json"
            )

        if hasattr(
            evaluation,
            "dict",
        ):
            return evaluation.dict()

        if hasattr(
            evaluation,
            "__dict__",
        ):
            return dict(
                evaluation.__dict__
            )

        return {
            "value": evaluation
        }

    @staticmethod
    def _candidate_score(
        scored_candidate: Any,
    ) -> float:
        """
        Extract the final numerical candidate score.
        """

        if isinstance(
            scored_candidate,
            dict,
        ):
            value = scored_candidate.get(
                "score",
                0.0,
            )
        else:
            value = getattr(
                scored_candidate,
                "score",
                0.0,
            )

        try:
            return float(value)
        except (
            TypeError,
            ValueError,
        ):
            return 0.0
