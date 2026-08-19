"""
IMAGINE
Generative Design Repository

Async persistence layer for generative design runs and candidates.

Transaction policy
------------------
The repository does NOT commit or rollback transactions.

The service layer owns the transaction boundary:

    BEGIN
      |
      +-- repository operations
      |
    COMMIT

or:

    BEGIN
      |
      +-- repository operations
      |
    ROLLBACK

Repository responsibilities:
    - Create generative design runs.
    - Retrieve generative design runs.
    - Update generative design runs.
    - Delete generative design runs.
    - Create generated candidates.
    - Retrieve generated candidates.
    - Update generated candidates.
    - Delete generated candidates.
    - Bulk candidate persistence.
    - Candidate counting.

All database operations are asynchronous.
"""

from __future__ import annotations

from typing import Any, Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from architecture.generative_design.models import (
    DesignCandidateRecord,
    GenerativeDesignRun,
)


class GenerativeDesignRepository:
    """
    Async repository for generative design persistence.

    Important:
        This class intentionally does not call commit() or rollback().

    Transaction ownership belongs to GenerativeDesignService.
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

        The record is added and flushed so that database-generated
        values are available to the caller.

        No commit is performed.
        """

        run = GenerativeDesignRun(
            project_id=project_id,
            name=name,
            constraints=constraints,
            status=status,
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

        statement = select(
            GenerativeDesignRun
        ).where(
            GenerativeDesignRun.id == run_id
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
        Retrieve a run together with its generated candidates.

        selectinload() is explicitly used because implicit lazy loading
        is unsafe in asynchronous SQLAlchemy code.
        """

        statement = (
            select(
                GenerativeDesignRun
            )
            .options(
                selectinload(
                    GenerativeDesignRun.candidates
                )
            )
            .where(
                GenerativeDesignRun.id == run_id
            )
        )

        result = await self.session.execute(
            statement
        )

        return result.scalar_one_or_none()

    async def list_runs(
        self,
        *,
        project_id: UUID | None = None,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[GenerativeDesignRun]:
        """
        Return generative design runs.

        Optional filters:
            project_id
            status
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
        constraints: dict[str, Any] | None = None,
        candidate_count: int | None = None,
        completed_at: Any | None = None,
        error_message: str | None = None,
        updated_by: str | None = None,
    ) -> GenerativeDesignRun | None:
        """
        Update a generative design run.

        Only supplied values are changed.

        No commit is performed.
        """

        run = await self.get_run(
            run_id
        )

        if run is None:
            return None

        if name is not None:
            run.name = name

        if status is not None:
            run.status = status

        if constraints is not None:
            run.constraints = constraints

        if candidate_count is not None:
            if candidate_count < 0:
                raise ValueError(
                    "candidate_count cannot be negative."
                )

            run.candidate_count = candidate_count

        if completed_at is not None:
            run.completed_at = completed_at

        if error_message is not None:
            run.error_message = error_message

        if updated_by is not None:
            run.updated_by = updated_by

        await self.session.flush()

        return run

    async def delete_run(
        self,
        run_id: UUID,
    ) -> bool:
        """
        Delete a generative design run.

        Candidate deletion is handled by the configured
        SQLAlchemy/database cascade.

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
        Create a generated design candidate.

        No commit is performed.
        """

        candidate = DesignCandidateRecord(
            run_id=run_id,
            name=name,
            geometry=geometry,
            metrics=metrics,
            evaluation=evaluation,
            score=score,
            rank=rank,
            status=status,
            created_by=created_by,
        )

        self.session.add(
            candidate
        )

        await self.session.flush()

        return candidate

    async def get_candidate(
        self,
        candidate_id: UUID,
    ) -> DesignCandidateRecord | None:
        """
        Retrieve a candidate by UUID.
        """

        statement = select(
            DesignCandidateRecord
        ).where(
            DesignCandidateRecord.id
            == candidate_id
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

        Candidates are ordered by:
            1. rank ascending
            2. score descending
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
        rank: int | None = None,
        score: float | None = None,
        geometry: dict[str, Any] | None = None,
        metrics: dict[str, Any] | None = None,
        evaluation: dict[str, Any] | None = None,
        updated_by: str | None = None,
    ) -> DesignCandidateRecord | None:
        """
        Update a generated design candidate.

        No commit is performed.
        """

        candidate = await self.get_candidate(
            candidate_id
        )

        if candidate is None:
            return None

        if name is not None:
            candidate.name = name

        if status is not None:
            candidate.status = status

        if rank is not None:
            if rank < 1:
                raise ValueError(
                    "rank must be greater than zero."
                )

            candidate.rank = rank

        if score is not None:
            candidate.score = score

        if geometry is not None:
            candidate.geometry = geometry

        if metrics is not None:
            candidate.metrics = metrics

        if evaluation is not None:
            candidate.evaluation = evaluation

        if updated_by is not None:
            candidate.updated_by = updated_by

        await self.session.flush()

        return candidate

    async def delete_candidate(
        self,
        candidate_id: UUID,
    ) -> bool:
        """
        Delete a single generated candidate.

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

    async def create_candidates(
        self,
        *,
        run_id: UUID,
        candidates: list[dict[str, Any]],
        created_by: str | None = None,
    ) -> list[DesignCandidateRecord]:
        """
        Persist a complete candidate population.

        All candidates are added to the current transaction and
        flushed together.

        The caller controls commit/rollback.
        """

        if not candidates:
            return []

        records: list[
            DesignCandidateRecord
        ] = []

        for candidate_data in candidates:
            record = DesignCandidateRecord(
                run_id=run_id,
                name=str(
                    candidate_data["name"]
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
                score=float(
                    candidate_data.get(
                        "score",
                        0.0,
                    )
                ),
                rank=candidate_data.get(
                    "rank"
                ),
                status=candidate_data.get(
                    "status",
                    "generated",
                ),
                created_by=created_by,
            )

            self.session.add(
                record
            )

            records.append(
                record
            )

        await self.session.flush()

        return records

    async def delete_candidates_for_run(
        self,
        run_id: UUID,
    ) -> int:
        """
        Delete every candidate belonging to a run.

        No commit is performed.
        """

        statement = select(
            DesignCandidateRecord
        ).where(
            DesignCandidateRecord.run_id
            == run_id
        )

        result = await self.session.execute(
            statement
        )

        candidates = result.scalars().all()

        if not candidates:
            return 0

        for candidate in candidates:
            await self.session.delete(
                candidate
            )

        await self.session.flush()

        return len(candidates)

    # =====================================================================
    # COUNTS
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
        Synchronize candidate_count with the actual candidate count.

        No commit is performed.
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
    # BEST / RANKED CANDIDATES
    # =====================================================================

    async def get_best_candidate(
        self,
        run_id: UUID,
    ) -> DesignCandidateRecord | None:
        """
        Return the highest-ranked candidate for a run.

        Rank takes precedence over score.
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
        Return the top-ranked candidates for a run.
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
    # TRANSACTION SAFETY
    # =====================================================================

    async def flush(self) -> None:
        """
        Explicitly flush the current transaction.

        This is provided for service-layer orchestration.

        It does NOT commit.
        """

        await self.session.flush()
