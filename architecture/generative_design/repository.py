"""
IMAGINE
Generative Design Repository

Async persistence layer for:

    GenerativeDesignRun
    DesignCandidateRecord

Transaction policy
------------------
This repository is transaction-neutral.

It may:
    - add records
    - update records
    - delete records
    - execute SELECT statements
    - flush pending changes

It must NOT:
    - commit
    - rollback

The service layer owns the transaction boundary.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from architecture.generative_design.models import (
    DesignCandidateRecord,
    GenerativeDesignRun,
)


# =========================================================================
# SENTINEL
# =========================================================================

_UNSET = object()


class GenerativeDesignRepository:
    """
    Async repository for generative design persistence.

    A sentinel is used for update operations so that:

        field omitted
            -> do not modify field

        field=None
            -> explicitly clear nullable field

        field=value
            -> replace field with value
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    # =====================================================================
    # GENERATIVE DESIGN RUNS
    # =====================================================================

    async def create_run(
        self,
        *,
        project_id: UUID | None,
        name: str,
        constraints: dict[str, Any],
        status: str = "pending",
        candidate_count: int = 0,
        created_by: str | None = None,
    ) -> GenerativeDesignRun:
        """
        Create a generative design run.

        No commit is performed.
        """

        if candidate_count < 0:
            raise ValueError(
                "candidate_count cannot be negative."
            )

        run = GenerativeDesignRun(
            project_id=project_id,
            name=name,
            status=status,
            constraints=constraints,
            candidate_count=candidate_count,
            created_by=created_by,
        )

        self.session.add(run)

        await self.session.flush()

        return run

    async def get_run(
        self,
        run_id: UUID,
    ) -> GenerativeDesignRun | None:
        """
        Retrieve a generative design run by UUID.
        """

        statement = (
            select(GenerativeDesignRun)
            .where(
                GenerativeDesignRun.id == run_id
            )
        )

        result = await self.session.execute(
            statement
        )

        return result.scalar_one_or_none()

    async def get_run_with_candidates(
        self,
        run_id: UUID,
    ) -> GenerativeDesignRun | None:
        """
        Retrieve a run and its candidates.

        The `candidates` relationship is explicitly refreshed so
        asynchronous code does not depend on implicit lazy loading.
        """

        run = await self.get_run(run_id)

        if run is None:
            return None

        await self.session.refresh(
            run,
            attribute_names=["candidates"],
        )

        return run

    async def list_runs(
        self,
        *,
        project_id: UUID | None = None,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[GenerativeDesignRun]:
        """
        List generative design runs.
        """

        if limit < 1:
            raise ValueError(
                "limit must be greater than zero."
            )

        if offset < 0:
            raise ValueError(
                "offset cannot be negative."
            )

        statement = select(
            GenerativeDesignRun
        )

        if project_id is not None:
            statement = statement.where(
                GenerativeDesignRun.project_id
                == project_id
            )

        if status is not None:
            statement = statement.where(
                GenerativeDesignRun.status
                == status
            )

        statement = (
            statement
            .order_by(
                GenerativeDesignRun.created_at.desc()
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(
            statement
        )

        return result.scalars().all()

    async def update_run(
        self,
        run_id: UUID,
        *,
        name: str | None = None,
        status: str | None = None,
        constraints: Any = _UNSET,
        candidate_count: int | None = None,
        completed_at: Any = _UNSET,
        error_message: Any = _UNSET,
        updated_by: Any = _UNSET,
    ) -> GenerativeDesignRun | None:
        """
        Update a generative design run.

        Sentinel semantics
        ------------------
        For nullable fields:

            omitted:
                leave unchanged

            None:
                explicitly clear the value

            value:
                replace the value

        Examples
        --------

        Clear completed_at:

            await repository.update_run(
                run_id,
                completed_at=None,
            )

        Clear error_message:

            await repository.update_run(
                run_id,
                error_message=None,
            )

        Replace constraints:

            await repository.update_run(
                run_id,
                constraints={
                    "site_area": 1200,
                    "max_height": 18,
                },
            )

        Clear the JSONB constraints document:

            await repository.update_run(
                run_id,
                constraints=None,
            )

        No commit is performed.
        """

        run = await self.get_run(
            run_id
        )

        if run is None:
            return None

        # -------------------------------------------------------------
        # Non-null / conventional fields
        # -------------------------------------------------------------

        if name is not None:
            run.name = name

        if status is not None:
            run.status = status

        if candidate_count is not None:
            if candidate_count < 0:
                raise ValueError(
                    "candidate_count cannot be negative."
                )

            run.candidate_count = candidate_count

        # -------------------------------------------------------------
        # JSONB constraints
        #
        # `constraints=None` intentionally clears the column.
        # -------------------------------------------------------------

        if constraints is not _UNSET:
            run.constraints = constraints

        # -------------------------------------------------------------
        # Nullable completion timestamp
        #
        # None explicitly clears completed_at.
        # -------------------------------------------------------------

        if completed_at is not _UNSET:
            run.completed_at = completed_at

        # -------------------------------------------------------------
        # Nullable error message
        #
        # None explicitly clears error_message.
        # -------------------------------------------------------------

        if error_message is not _UNSET:
            run.error_message = error_message

        # -------------------------------------------------------------
        # BaseModel audit field
        # -------------------------------------------------------------

        if updated_by is not _UNSET:
            run.updated_by = updated_by

        await self.session.flush()

        return run

    async def delete_run(
        self,
        run_id: UUID,
    ) -> bool:
        """
        Delete a generative design run.

        The model relationship provides:

            cascade="all, delete-orphan"

        The database FK also provides:

            ON DELETE CASCADE

        No commit is performed.
        """

        run = await self.get_run(
            run_id
        )

        if run is None:
            return False

        await self.session.delete(
            run
        )

        await self.session.flush()

        return True

    # =====================================================================
    # DESIGN CANDIDATES
    # =====================================================================

    async def create_candidate(
        self,
        *,
        run_id: UUID,
        name: str,
        geometry: dict[str, Any],
        metrics: dict[str, Any],
        evaluation: dict[str, Any],
        score: float = 0.0,
        rank: int | None = None,
        status: str = "generated",
        created_by: str | None = None,
    ) -> DesignCandidateRecord:
        """
        Create one generated design candidate.

        No commit is performed.
        """

        candidate = DesignCandidateRecord(
            run_id=run_id,
            name=name,
            status=status,
            rank=rank,
            score=score,
            geometry=geometry,
            metrics=metrics,
            evaluation=evaluation,
            created_by=created_by,
        )

        self.session.add(candidate)

        await self.session.flush()

        return candidate

    async def create_candidates(
        self,
        *,
        run_id: UUID,
        candidates: Sequence[
            dict[str, Any]
        ],
        created_by: str | None = None,
    ) -> list[DesignCandidateRecord]:
        """
        Persist multiple generated candidates.

        No commit is performed.
        """

        if not candidates:
            return []

        records: list[
            DesignCandidateRecord
        ] = []

        for candidate_data in candidates:
            record = DesignCandidateRecord(
                run_id=run_id,
                name=candidate_data["name"],
                status=candidate_data.get(
                    "status",
                    "generated",
                ),
                rank=candidate_data.get(
                    "rank"
                ),
                score=float(
                    candidate_data.get(
                        "score",
                        0.0,
                    )
                ),
                geometry=candidate_data.get(
                    "geometry",
                    {},
                ),
                metrics=candidate_data.get(
                    "metrics",
                    {},
                ),
                evaluation=candidate_data.get(
                    "evaluation",
                    {},
                ),
                created_by=created_by,
            )

            self.session.add(record)

            records.append(record)

        await self.session.flush()

        return records

    async def get_candidate(
        self,
        candidate_id: UUID,
    ) -> DesignCandidateRecord | None:
        """
        Retrieve a candidate by UUID.
        """

        statement = (
            select(
                DesignCandidateRecord
            )
            .where(
                DesignCandidateRecord.id
                == candidate_id
            )
        )

        result = await self.session.execute(
            statement
        )

        return result.scalar_one_or_none()

    async def list_candidates(
        self,
        *,
        run_id: UUID | None = None,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[DesignCandidateRecord]:
        """
        List generated candidates.
        """

        if limit < 1:
            raise ValueError(
                "limit must be greater than zero."
            )

        if offset < 0:
            raise ValueError(
                "offset cannot be negative."
            )

        statement = select(
            DesignCandidateRecord
        )

        if run_id is not None:
            statement = statement.where(
                DesignCandidateRecord.run_id
                == run_id
            )

        if status is not None:
            statement = statement.where(
                DesignCandidateRecord.status
                == status
            )

        statement = (
            statement
            .order_by(
                DesignCandidateRecord.rank.asc().nullslast(),
                DesignCandidateRecord.score.desc(),
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(
            statement
        )

        return result.scalars().all()

    async def update_candidate(
        self,
        candidate_id: UUID,
        *,
        name: str | None = None,
        status: str | None = None,
        rank: Any = _UNSET,
        score: float | None = None,
        geometry: Any = _UNSET,
        metrics: Any = _UNSET,
        evaluation: Any = _UNSET,
        updated_by: Any = _UNSET,
    ) -> DesignCandidateRecord | None:
        """
        Update a generated design candidate.

        Sentinel semantics
        ------------------
        For nullable or clearable fields:

            omitted:
                leave unchanged

            None:
                explicitly clear the value

            value:
                replace the value

        Examples
        --------

        Clear rank:

            await repository.update_candidate(
                candidate_id,
                rank=None,
            )

        Replace rank:

            await repository.update_candidate(
                candidate_id,
                rank=1,
            )

        Clear JSONB geometry:

            await repository.update_candidate(
                candidate_id,
                geometry=None,
            )

        Replace geometry:

            await repository.update_candidate(
                candidate_id,
                geometry={
                    "footprint": [...],
                },
            )

        No commit is performed.
        """

        candidate = await self.get_candidate(
            candidate_id
        )

        if candidate is None:
            return None

        # -------------------------------------------------------------
        # Standard fields
        # -------------------------------------------------------------

        if name is not None:
            candidate.name = name

        if status is not None:
            candidate.status = status

        if score is not None:
            candidate.score = score

        # -------------------------------------------------------------
        # Nullable rank
        #
        # rank=None explicitly clears the rank.
        # -------------------------------------------------------------

        if rank is not _UNSET:
            candidate.rank = rank

        # -------------------------------------------------------------
        # JSONB fields
        #
        # None explicitly clears the JSONB column.
        # -------------------------------------------------------------

        if geometry is not _UNSET:
            candidate.geometry = geometry

        if metrics is not _UNSET:
            candidate.metrics = metrics

        if evaluation is not _UNSET:
            candidate.evaluation = evaluation

        # -------------------------------------------------------------
        # BaseModel audit field
        # -------------------------------------------------------------

        if updated_by is not _UNSET:
            candidate.updated_by = updated_by

        await self.session.flush()

        return candidate

    async def delete_candidate(
        self,
        candidate_id: UUID,
    ) -> bool:
        """
        Delete one candidate.

        No commit is performed.
        """

        candidate = await self.get_candidate(
            candidate_id
        )

        if candidate is None:
            return False

        await self.session.delete(
            candidate
        )

        await self.session.flush()

        return True

    # =====================================================================
    # BULK CANDIDATE OPERATIONS
    # =====================================================================

    async def delete_candidates_for_run(
        self,
        run_id: UUID,
    ) -> int:
        """
        Delete all candidates belonging to a run.

        No commit is performed.
        """

        statement = (
            select(
                DesignCandidateRecord
            )
            .where(
                DesignCandidateRecord.run_id
                == run_id
            )
        )

        result = await self.session.execute(
            statement
        )

        candidates = result.scalars().all()

        for candidate in candidates:
            await self.session.delete(
                candidate
            )

        if candidates:
            await self.session.flush()

        return len(candidates)

    # =====================================================================
    # CANDIDATE COUNTS
    # =====================================================================

    async def count_candidates(
        self,
        run_id: UUID,
    ) -> int:
        """
        Count candidates belonging to a run.
        """

        statement = select(
            func.count(
                DesignCandidateRecord.id
            )
        ).where(
            DesignCandidateRecord.run_id
            == run_id
        )

        result = await self.session.execute(
            statement
        )

        return int(
            result.scalar_one()
        )

    async def update_run_candidate_count(
        self,
        run_id: UUID,
    ) -> GenerativeDesignRun | None:
        """
        Synchronize candidate_count with the actual
        number of persisted candidates.
        """

        run = await self.get_run(
            run_id
        )

        if run is None:
            return None

        count = await self.count_candidates(
            run_id
        )

        run.candidate_count = count

        await self.session.flush()

        return run

    # =====================================================================
    # RANKING
    # =====================================================================

    async def get_best_candidate(
        self,
        run_id: UUID,
    ) -> DesignCandidateRecord | None:
        """
        Return the best-ranked candidate.

        Ranking:
            1. lowest non-null rank
            2. highest score
        """

        statement = (
            select(
                DesignCandidateRecord
            )
            .where(
                DesignCandidateRecord.run_id
                == run_id
            )
            .order_by(
                DesignCandidateRecord.rank.asc().nullslast(),
                DesignCandidateRecord.score.desc(),
            )
            .limit(1)
        )

        result = await self.session.execute(
            statement
        )

        return result.scalar_one_or_none()

    async def get_top_candidates(
        self,
        run_id: UUID,
        *,
        limit: int = 10,
    ) -> Sequence[DesignCandidateRecord]:
        """
        Return the top-ranked candidates.
        """

        if limit < 1:
            raise ValueError(
                "limit must be greater than zero."
            )

        statement = (
            select(
                DesignCandidateRecord
            )
            .where(
                DesignCandidateRecord.run_id
                == run_id
            )
            .order_by(
                DesignCandidateRecord.rank.asc().nullslast(),
                DesignCandidateRecord.score.desc(),
            )
            .limit(limit)
        )

        result = await self.session.execute(
            statement
        )

        return result.scalars().all()

    # =====================================================================
    # TRANSACTION SUPPORT
    # =====================================================================

    async def flush(self) -> None:
        """
        Flush pending changes.

        This does NOT commit the transaction.
        """

        await self.session.flush()
