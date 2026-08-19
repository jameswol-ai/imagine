"""
IMAGINE
Generative Design Service
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from .constraints import validate_constraints
from .generator import generate_candidates
from .repository import GenerativeDesignRepository
from .scoring import score_and_rank
from .schemas import (
    DesignConstraints,
    GenerativeDesignRunCreate,
)


class GenerativeDesignService:
    """
    Application service for generative design.

    Coordinates:

        validation
        generation
        scoring
        ranking
        persistence
    """

    def __init__(self, session: Session):
        self.repository = GenerativeDesignRepository(
            session
        )

        self.session = session

    def create_run(
        self,
        request: GenerativeDesignRunCreate,
    ):
        constraints = request.constraints

        validation = validate_constraints(
            constraints
        )

        if not validation.valid:
            raise ValueError(
                "; ".join(validation.errors)
            )

        run = self.repository.create_run(
            project_id=request.project_id,
            name=request.name,
            constraints=constraints.model_dump(),
        )

        try:
            run.status = "generating"

            candidates = generate_candidates(
                constraints,
                request.candidate_count,
            )

            ranked = score_and_rank(
                candidates,
                constraints,
            )

            for candidate in ranked:
                self.repository.add_candidate(
                    run=run,
                    name=candidate.name,
                    score=candidate.score,
                    rank=candidate.rank,
                    geometry=candidate.geometry,
                    metrics=candidate.metrics,
                    evaluation=candidate.evaluation,
                )

            run.candidate_count = len(
                ranked
            )

            run.status = "completed"
            run.completed_at = datetime.utcnow()

            self.session.commit()
            self.session.refresh(run)

            return run

        except Exception as exc:
            self.session.rollback()

            run = self.repository.get_run(
                run.id
            )

            if run is not None:
                run.status = "failed"
                run.error_message = str(exc)

                self.session.commit()

            raise

    def get_run(
        self,
        run_id: int,
    ):
        return self.repository.get_run(
            run_id
        )

    def list_runs(
        self,
        project_id: int | None = None,
    ):
        return self.repository.list_runs(
            project_id
        )

    def get_candidates(
        self,
        run_id: int,
    ):
        return self.repository.list_candidates(
            run_id
        )

    def delete_run(
        self,
        run_id: int,
    ) -> bool:
        run = self.repository.get_run(
            run_id
        )

        if run is None:
            return False

        self.repository.delete_run(
            run
        )

        self.session.commit()

        return True