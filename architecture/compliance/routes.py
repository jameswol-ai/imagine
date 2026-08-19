"""
FastAPI routes for Architecture Compliance.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db

from .schemas import (
    ComplianceAssessmentCreate,
    ComplianceAssessmentRead,
    ComplianceCheckInput,
    ComplianceCheckResponse,
)
from .service import ComplianceService


router = APIRouter(
    prefix="/api/architecture/compliance",
    tags=["Architecture Compliance"],
)


@router.get(
    "",
    response_model=list[ComplianceAssessmentRead],
)
def list_assessments(
    project_id: int | None = None,
    db: Session = Depends(get_db),
):
    service = ComplianceService(db)

    return service.list_assessments(project_id)


@router.get(
    "/{assessment_id}",
    response_model=ComplianceAssessmentRead,
)
def get_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
):
    service = ComplianceService(db)

    assessment = service.get_assessment(assessment_id)

    if assessment is None:
        raise HTTPException(
            status_code=404,
            detail="Compliance assessment not found.",
        )

    return assessment


@router.post(
    "",
    response_model=ComplianceAssessmentRead,
)
def create_assessment(
    data: ComplianceAssessmentCreate,
    db: Session = Depends(get_db),
):
    service = ComplianceService(db)

    return service.create_assessment(data)


@router.delete(
    "/{assessment_id}",
)
def delete_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
):
    service = ComplianceService(db)

    deleted = service.delete_assessment(assessment_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Compliance assessment not found.",
        )

    return {
        "success": True,
        "message": "Compliance assessment deleted.",
    }


@router.post(
    "/{assessment_id}/check",
    response_model=ComplianceCheckResponse,
)
def run_compliance_check(
    assessment_id: int,
    data: ComplianceCheckInput,
    db: Session = Depends(get_db),
):
    service = ComplianceService(db)

    try:
        return service.run_and_save(
            assessment_id,
            data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc