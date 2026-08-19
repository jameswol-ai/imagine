"""
Repository layer for Architecture Compliance.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .models import ComplianceAssessment, ComplianceResult


class ComplianceRepository:
    """
    Database access layer.

    Business rules should not live here.
    """

    def __init__(self, db: Session):
        self.db = db

    def list_assessments(
        self,
        project_id: Optional[int] = None,
    ) -> list[ComplianceAssessment]:

        stmt = (
            select(ComplianceAssessment)
            .options(selectinload(ComplianceAssessment.rules))
            .order_by(ComplianceAssessment.id.desc())
        )

        if project_id is not None:
            stmt = stmt.where(
                ComplianceAssessment.project_id == project_id
            )

        return list(self.db.scalars(stmt).all())

    def get_assessment(
        self,
        assessment_id: int,
    ) -> Optional[ComplianceAssessment]:

        stmt = (
            select(ComplianceAssessment)
            .options(selectinload(ComplianceAssessment.rules))
            .where(ComplianceAssessment.id == assessment_id)
        )

        return self.db.scalars(stmt).first()

    def create_assessment(
        self,
        assessment: ComplianceAssessment,
    ) -> ComplianceAssessment:

        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)

        return assessment

    def update_assessment(
        self,
        assessment: ComplianceAssessment,
    ) -> ComplianceAssessment:

        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)

        return assessment

    def delete_assessment(
        self,
        assessment: ComplianceAssessment,
    ) -> None:

        self.db.delete(assessment)
        self.db.commit()

    def add_result(
        self,
        result: ComplianceResult,
    ) -> ComplianceResult:

        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)

        return result

    def delete_results(
        self,
        assessment_id: int,
    ) -> None:

        results = self.db.scalars(
            select(ComplianceResult).where(
                ComplianceResult.assessment_id == assessment_id
            )
        ).all()

        for result in results:
            self.db.delete(result)

        self.db.commit()