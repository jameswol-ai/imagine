"""
Seed data for Architecture Compliance.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from .models import ComplianceAssessment
from .repository import ComplianceRepository


def seed_compliance(db: Session) -> None:
    """
    Insert initial compliance assessment data if none exists.
    """

    repository = ComplianceRepository(db)

    existing = repository.list_assessments()

    if existing:
        return

    assessment = ComplianceAssessment(
        name="Green Tower - Preliminary Compliance",
        project_id=None,
        zoning_id=None,
        site_plan_id=None,
        floor_plan_id=None,
        status="PENDING",
        score=0,
        notes=(
            "Initial architecture compliance assessment "
            "for the Green Tower concept."
        ),
    )

    repository.create_assessment(assessment)