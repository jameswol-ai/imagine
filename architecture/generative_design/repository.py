"""
IMAGINE
Generative Design Repository
"""

from __future__ import annotations

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import (
    DesignCandidateRecord,
    GenerativeDesignRun,
)


class GenerativeDesignRepository:
    """Database access layer for generative design."""

    def __init__(self, session: Session):
        self.session = session

    def create_run(
        self,
        *,
        project_id: int | None,
        name: str,
        constraints: dict,
    ) -> GenerativeDesignRun:
        run = GenerativeDesignRun(
            project_id=project_id,
            name=name,
            status="pending",
            constraints=constraints,
        )

        self.session.add(run)
        self.session.flush()

        return run

    def get_run(
        self,
        run_id: int,
    ) -> GenerativeDesignRun | None:
        return self.session.get(
            GenerativeDesignRun,
            run_id,
        )

    def list_runs(
        self,
        project_id: int | None = None,
    ) -> Sequence[GenerativeDesignRun]:
        statement = select(GenerativeDesignRun)

        if project_id is not None:
            statement = statement.where(
                GenerativeDesignRun.project_id == project_id
            )

        statement = statement.order_by(
            GenerativeDesignRun.created_at.desc()
        )

        return self.session.scalars(statement).all()

    def update_run(
        self,
        run: GenerativeDesignRun,
        **values,
    ) -> GenerativeDesignRun:
        for key, value in values.items():
            setattr(run, key, value)

        self.session.flush()

        return run

    def add_candidate(
        self,
        *,
        run: GenerativeDesignRun,
        name: str,
        score: float,
        rank: int | None,
        geometry: dict,
        metrics: dict,
        evaluation: dict,
    ) -> DesignCandidateRecord:
        candidate = DesignCandidateRecord(
            run_id=run.id,
            name=name,
            score=score,
            rank=rank,
            geometry=geometry,
            metrics=metrics,
            evaluation=evaluation,
        )

        self.session.add(candidate)
        self.session.flush()

        return candidate

    def get_candidate(
        self,
        candidate_id: int,
    ) -> DesignCandidateRecord | None:
        return self.session.get(
            DesignCandidateRecord,
            candidate_id,
        )

    def list_candidates(
        self,
        run_id: int,
    ) -> Sequence[DesignCandidateRecord]:
        statement = (
            select(DesignCandidateRecord)
            .where(
                DesignCandidateRecord.run_id == run_id
            )
            .order_by(
                DesignCandidateRecord.rank.asc()
            )
        )

        return self.session.scalars(statement).all()

    def delete_run(
        self,
        run: GenerativeDesignRun,
    ) -> None:
        self.session.delete(run)
        self.session.flush()