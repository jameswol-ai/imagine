"""
IMAGINE
Generative Design Repository

Async persistence layer for generative design runs and candidates.

Responsibilities:
    - Create, retrieve, update, and delete generative design runs.
    - Create, retrieve, update, and delete generated candidates.
    - Persist data using SQLAlchemy AsyncSession.
    - Keep database transaction handling inside the repository.
"""

from __future__ import annotations

from typing import Any, Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from architecture.generative_design.models import (
    DesignCandidateRecord,
    GenerativeDesignRun,
)


class GenerativeDesignRepository:
    """
    Async repository for generative design persistence.

    The repository deliberately does not contain generation,
    scoring, compliance, or architectural decision logic.
    It is responsible only for database persistence.
    """

    def __init__(self, session: AsyncSession) -> None:
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
        Create and persist a generative design run.

        The transaction is committed only after the object has
        been flushed successfully.
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

        try:
            await self.session.flush()
            await self.session.commit()

            # Refresh so server-generated fields such as created_at
            # are available to the caller.
            await self.session.refresh(run)

            return run

        except SQLAlchemyError:
            await self.session.rollback()
            raise

    async def get_run(
        self,
        run_id: UUID,
    ) -> GenerativeDesignRun | None:
        """
        Retrieve a single generative design run by UUID.
        """

        statement = select(GenerativeDesignRun).where(
            GenerativeDesignRun.id == run_id
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_run_with_candidates(
        self,
        run_id: UUID,
    ) -> GenerativeDesignRun | None:
        """
        Retrieve a run and its candidates.

        Uses select-in loading explicitly so the async repository
        does not accidentally trigger synchronous lazy loading.
        """

        from sqlalchemy.orm import selectinload

        statement = (
            select(GenerativeDesignRun)
            .options(
                selectinload(
                    GenerativeDesignRun.candidates
                )
            )
            .where(
                GenerativeDesignRun.id == run_id
            )
        )

        result = await self.session.execute(statement)

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

        Optional filtering:
            project_id
            status

        Results are ordered newest first.
        """

        statement = select(GenerativeDesignRun)

        if project_id is not None:
            statement = statement.where(
                GenerativeDesignRun.project_id == project_id
            )

        if status is not None:
            statement = statement.where(
                GenerativeDesignRun.status == status
            )

        statement = (
            statement
            .order_by(
                GenerativeDesignRun.created_at.desc()
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(statement)

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

        Only explicitly supplied values are changed.
        """

        run = await self.get_run(run_id)

        if run is None:
            return None

        if name is not None:
            run.name = name

        if status is not None:
            run.status = status

        if constraints is not None:
            run.constraints = constraints

        if candidate_count is not None:
            run.candidate_count = candidate_count

        if completed_at is not None:
            run.completed_at = completed_at

        if error_message is not None:
            run.error_message = error_message

        if updated_by is not None:
            run.updated_by = updated_by

        try:
            await self.session.flush()
            await self.session.commit()
            await self.session.refresh(run)

            return run

        except SQLAlchemyError:
            await self.session.rollback()
            raise

    async def delete_run(
        self,
        run_id: UUID,
    ) -> bool:
        """
        Delete a generative design run.

        The database FK and SQLAlchemy relationship cascade
        remove associated candidate records.
        """

        run = await self.get_run(run_id)

        if run is None:
            return False

        try:
            await self.session.delete(run)
            await self.session.flush()
            await self.session.commit()

            return True

        except SQLAlchemyError:
            await self.session.rollback()
            raise

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
        Create and persist a generated design candidate.
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

        self.session.add(candidate)

        try:
            await self.session.flush()
            await self.session.commit()
            await self.session.refresh(candidate)

            return candidate

        except SQLAlchemyError:
            await self.session.rollback()
            raise

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
            DesignCandidateRecord.id == candidate_id
        )

        result = await self.session.execute(statement)

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

        Candidates are ordered by rank when available,
        followed by descending score.
        """

        statement = select(DesignCandidateRecord)

        if run_id is not None:
            statement = statement.where(
                DesignCandidateRecord.run_id == run_id
            )

        if status is not None:
            statement = statement.where(
                DesignCandidateRecord.status == status
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

        result = await self.session.execute(statement)

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
        Update a generated candidate.

        Only explicitly supplied non-None values are changed.
        """

        candidate = await self.get_candidate(candidate_id)

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

        try:
            await self.session.flush()
            await self.session.commit()
            await self.session.refresh(candidate)

            return candidate

        except SQLAlchemyError:
            await self.session.rollback()
            raise

    async def delete_candidate(
        self,
        candidate_id: UUID,
    ) -> bool:
        """
        Delete a generated design candidate.
        """

        candidate = await self.get_candidate(candidate_id)

        if candidate is None:
            return False

        try:
            await self.session.delete(candidate)
            await self.session.flush()
            await self.session.commit()

            return True

        except SQLAlchemyError:
            await self.session.rollback()
            raise

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
        Persist multiple generated candidates as one transaction.

        This is the preferred method when the generator produces
        an entire population of design options.
        """

        records: list[DesignCandidateRecord] = []

        for candidate_data in candidates:
            record = DesignCandidateRecord(
                run_id=run_id,
                name=candidate_data["name"],
                geometry=candidate_data.get("geometry", {}),
                metrics=candidate_data.get("metrics", {}),
                evaluation=candidate_data.get("evaluation", {}),
                score=candidate_data.get("score", 0.0),
                rank=candidate_data.get("rank"),
                status=candidate_data.get(
                    "status",
                    "generated",
                ),
                created_by=created_by,
            )

            self.session.add(record)
            records.append(record)

        try:
            await self.session.flush()
            await self.session.commit()

            for record in records:
                await self.session.refresh(record)

            return records

        except SQLAlchemyError:
            await self.session.rollback()
            raise

    async def delete_candidates_for_run(
        self,
        run_id: UUID,
    ) -> int:
        """
        Delete all candidates belonging to a run.

        This is useful when regenerating a run's population.
        """

        statement = select(
            DesignCandidateRecord
        ).where(
            DesignCandidateRecord.run_id == run_id
        )

        result = await self.session.execute(statement)

        candidates = result.scalars().all()

        if not candidates:
            return 0

        try:
            for candidate in candidates:
                await self.session.delete(candidate)

            await self.session.flush()
            await self.session.commit()

            return len(candidates)

        except SQLAlchemyError:
            await self.session.rollback()
            raise

    # =====================================================================
    # RUN / CANDIDATE UTILITIES
    # =====================================================================

    async def count_candidates(
        self,
        run_id: UUID,
    ) -> int:
        """
        Return the number of candidates belonging to a run.
        """

        from sqlalchemy import func

        statement = select(
            func.count(DesignCandidateRecord.id)
        ).where(
            DesignCandidateRecord.run_id == run_id
        )

        result = await self.session.execute(statement)

        return int(result.scalar_one())

    async def update_run_candidate_count(
        self,
        run_id: UUID,
    ) -> GenerativeDesignRun | None:
        """
        Synchronize a run's candidate_count with the database.
        """

        run = await self.get_run(run_id)

        if run is None:
            return None

        count = await self.count_candidates(run_id)

        run.candidate_count = count

        try:
            await self.session.flush()
            await self.session.commit()
            await self.session.refresh(run)

            return run

        except SQLAlchemyError:
            await self.session.rollback()
            raise
