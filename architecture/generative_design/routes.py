"""
IMAGINE
Generative Design API Routes
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.connection import get_db

from .schemas import (
    DesignCandidateSchema,
    GenerativeDesignRunCreate,
    GenerativeDesignRunResponse,
)
from .service import GenerativeDesignService


router = APIRouter(
    prefix="/api/generative-design",
    tags=["Generative Design"],
)


@router.post(
    "/runs",
    response_model=GenerativeDesignRunResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_run(
    request: GenerativeDesignRunCreate,
    db: Session = Depends(get_db),
):
    service = GenerativeDesignService(db)

    try:
        return service.create_run(
            request
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.get(
    "/runs/{run_id}",
    response_model=GenerativeDesignRunResponse,
)
def get_run(
    run_id: int,
    db: Session = Depends(get_db),
):
    service = GenerativeDesignService(db)

    run = service.get_run(
        run_id
    )

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Generative design run not found.",
        )

    return run


@router.get(
    "/runs/{run_id}/candidates",
    response_model=list[DesignCandidateSchema],
)
def get_candidates(
    run_id: int,
    db: Session = Depends(get_db),
):
    service = GenerativeDesignService(db)

    run = service.get_run(
        run_id
    )

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Generative design run not found.",
        )

    return service.get_candidates(
        run_id
    )


@router.get(
    "/runs",
    response_model=list[GenerativeDesignRunResponse],
)
def list_runs(
    project_id: int | None = None,
    db: Session = Depends(get_db),
):
    service = GenerativeDesignService(db)

    return service.list_runs(
        project_id
    )


@router.delete(
    "/runs/{run_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_run(
    run_id: int,
    db: Session = Depends(get_db),
):
    service = GenerativeDesignService(db)

    deleted = service.delete_run(
        run_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Generative design run not found.",
        )

    return None