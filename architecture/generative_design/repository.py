"""
IMAGINE
Generative Design Repository

Async persistence layer for:

    GenerativeDesignRun
    DesignCandidateRecord

The repository is intentionally transaction-neutral.

The service layer owns the transaction boundary and is responsible
for commit/rollback.

Repository responsibilities:
    - create
    - read
    - update
    - delete
    - bulk persistence
    - candidate counting
    - ranking queries

Repository methods:
    - use AsyncSession
    - use SQLAlchemy select()
    - use UUID identifiers
    - use flush() where required

Repository methods DO NOT:
    - commit
    - rollback
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


class GenerativeDesignRepository:
    """
    Async repository for generative design persistence.

    Transaction ownership belongs to the service layer.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    # ==================================================================
    # GENERATIVE DESIGN RUNS
    # ==================================================================

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

        The UUID primary key is supplied by BaseModel.

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
        Retrieve a run together with its candidates.

        The relationship is explicitly loaded to avoid relying on
        asynchronous lazy loading.
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

        run = result.scalar_one_or_none()

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
        completed_at: datetime | None = None,
        error_message: str | None = None,
        updated_by: str | None = None,
    ) -> GenerativeDesignRun | None:
        """
        Update an existing generative design run.

        Only supplied values are modified.

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

        The model relationship provides:

            cascade="all, delete-orphan"

        and the database foreign key also provides:

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

    # ==================================================================
    # DESIGN CANDIDATES
    # ==================================================================

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

        self.session.add(
            candidate
        )

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
        Create multiple candidates in the current transaction.

        Expected candidate dictionary fields:

            name
            geometry
            metrics
            evaluation
            score
            rank
            status

        Only fields that actually exist on
        DesignCandidateRecord are persisted.
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

            self.session.add(
                record
            )

            records.append(
                record
            )

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
        Delete a single candidate.

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

    # ==================================================================
    # BULK CANDIDATE OPERATIONS
    # ==================================================================

    async def delete_candidates_for_run(
        self,
        run_id: UUID,
    ) -> int:
        """
        Delete all candidates belonging to a run.

        This is useful when regenerating a candidate population.
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

    # ==================================================================
    # CANDIDATE COUNTS
    # ==================================================================

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
        Synchronize GenerativeDesignRun.candidate_count
        with the actual number of candidate records.
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

    # ==================================================================
    # RANKING
    # ==================================================================

    async def get_best_candidate(
        self,
        run_id: UUID,
    ) -> DesignCandidateRecord | None:
        """
        Retrieve the best candidate.

        Primary ordering:
            rank ascending

        Secondary ordering:
            score descending
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
        Retrieve the top-ranked candidates.
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

    # ==================================================================
    # FLUSH
    # ==================================================================

    async def flush(self) -> None:
        """
        Flush pending changes without committing.

        The service layer remains responsible for commit/rollback.
        """

        await self.session.flush()
