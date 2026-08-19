"""
Business logic for Architecture Compliance.

This module contains the actual compliance engine.
"""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy.orm import Session

from .models import ComplianceAssessment, ComplianceResult
from .repository import ComplianceRepository
from .schemas import (
    ComplianceAssessmentCreate,
    ComplianceCheckInput,
    ComplianceCheckResponse,
    ComplianceResultBase,
)


class ComplianceService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = ComplianceRepository(db)

    # ---------------------------------------------------------
    # CRUD
    # ---------------------------------------------------------

    def list_assessments(
        self,
        project_id: Optional[int] = None,
    ) -> list[ComplianceAssessment]:

        return self.repository.list_assessments(project_id)

    def get_assessment(
        self,
        assessment_id: int,
    ) -> Optional[ComplianceAssessment]:

        return self.repository.get_assessment(assessment_id)

    def create_assessment(
        self,
        data: ComplianceAssessmentCreate,
    ) -> ComplianceAssessment:

        assessment = ComplianceAssessment(
            project_id=data.project_id,
            zoning_id=data.zoning_id,
            site_plan_id=data.site_plan_id,
            floor_plan_id=data.floor_plan_id,
            name=data.name,
            status=data.status,
            score=data.score,
            notes=data.notes,
        )

        return self.repository.create_assessment(assessment)

    def delete_assessment(
        self,
        assessment_id: int,
    ) -> bool:

        assessment = self.get_assessment(assessment_id)

        if assessment is None:
            return False

        self.repository.delete_assessment(assessment)

        return True

    # ---------------------------------------------------------
    # Compliance calculations
    # ---------------------------------------------------------

    @staticmethod
    def calculate_site_coverage(
        site_area_m2: float,
        building_footprint_m2: float,
    ) -> float:

        if site_area_m2 <= 0:
            raise ValueError("Site area must be greater than zero.")

        return (
            building_footprint_m2
            / site_area_m2
            * 100
        )

    @staticmethod
    def calculate_far(
        site_area_m2: float,
        gross_floor_area_m2: float,
    ) -> float:

        if site_area_m2 <= 0:
            raise ValueError("Site area must be greater than zero.")

        return (
            gross_floor_area_m2
            / site_area_m2
        )

    # ---------------------------------------------------------
    # Rule evaluation
    # ---------------------------------------------------------

    @staticmethod
    def _evaluate_limit(
        *,
        rule_code: str,
        rule_name: str,
        category: str,
        actual: float,
        maximum: Optional[float],
        unit: str,
        required: bool = True,
    ) -> dict[str, Any]:

        if maximum is None:
            return {
                "rule_code": rule_code,
                "rule_name": rule_name,
                "category": category,
                "required_value": None,
                "actual_value": actual,
                "unit": unit,
                "status": "NOT_APPLICABLE",
                "required": required,
                "message": "No maximum value configured.",
            }

        passed = actual <= maximum

        return {
            "rule_code": rule_code,
            "rule_name": rule_name,
            "category": category,
            "required_value": maximum,
            "actual_value": actual,
            "unit": unit,
            "status": "PASS" if passed else "FAIL",
            "required": required,
            "message": (
                "Requirement satisfied."
                if passed
                else f"Actual value exceeds maximum of {maximum} {unit}."
            ),
        }

    @staticmethod
    def _evaluate_minimum(
        *,
        rule_code: str,
        rule_name: str,
        category: str,
        actual: float,
        minimum: Optional[float],
        unit: str,
        required: bool = True,
    ) -> dict[str, Any]:

        if minimum is None:
            return {
                "rule_code": rule_code,
                "rule_name": rule_name,
                "category": category,
                "required_value": None,
                "actual_value": actual,
                "unit": unit,
                "status": "NOT_APPLICABLE",
                "required": required,
                "message": "No minimum value configured.",
            }

        passed = actual >= minimum

        return {
            "rule_code": rule_code,
            "rule_name": rule_name,
            "category": category,
            "required_value": minimum,
            "actual_value": actual,
            "unit": unit,
            "status": "PASS" if passed else "FAIL",
            "required": required,
            "message": (
                "Requirement satisfied."
                if passed
                else f"Actual value is below minimum of {minimum} {unit}."
            ),
        }

    def evaluate(
        self,
        data: ComplianceCheckInput,
    ) -> ComplianceCheckResponse:

        coverage = self.calculate_site_coverage(
            data.site_area_m2,
            data.building_footprint_m2,
        )

        far = self.calculate_far(
            data.site_area_m2,
            data.gross_floor_area_m2,
        )

        results: list[dict[str, Any]] = []

        results.append(
            self._evaluate_limit(
                rule_code="SITE_COVERAGE",
                rule_name="Maximum Site Coverage",
                category="Zoning",
                actual=coverage,
                maximum=data.max_coverage_percent,
                unit="%",
            )
        )

        results.append(
            self._evaluate_limit(
                rule_code="FAR",
                rule_name="Floor Area Ratio",
                category="Zoning",
                actual=far,
                maximum=data.max_far,
                unit="ratio",
            )
        )

        results.append(
            self._evaluate_limit(
                rule_code="HEIGHT",
                rule_name="Maximum Building Height",
                category="Zoning",
                actual=data.building_height_m,
                maximum=data.max_height_m,
                unit="m",
            )
        )

        results.append(
            self._evaluate_minimum(
                rule_code="FRONT_SETBACK",
                rule_name="Front Setback",
                category="Site Planning",
                actual=data.front_setback_m,
                minimum=data.min_front_setback_m,
                unit="m",
            )
        )

        results.append(
            self._evaluate_minimum(
                rule_code="SIDE_SETBACK",
                rule_name="Side Setback",
                category="Site Planning",
                actual=data.side_setback_m,
                minimum=data.min_side_setback_m,
                unit="m",
            )
        )

        results.append(
            self._evaluate_minimum(
                rule_code="REAR_SETBACK",
                rule_name="Rear Setback",
                category="Site Planning",
                actual=data.rear_setback_m,
                minimum=data.min_rear_setback_m,
                unit="m",
            )
        )

        applicable = [
            result
            for result in results
            if result["status"] != "NOT_APPLICABLE"
        ]

        passed = sum(
            result["status"] == "PASS"
            for result in applicable
        )

        failed = sum(
            result["status"] == "FAIL"
            for result in applicable
        )

        warnings = sum(
            result["status"] == "WARNING"
            for result in applicable
        )

        score = (
            passed / len(applicable) * 100
            if applicable
            else 0
        )

        if failed:
            overall_status = "FAIL"
        elif warnings:
            overall_status = "WARNING"
        elif applicable:
            overall_status = "PASS"
        else:
            overall_status = "PENDING"

        typed_results = [
            ComplianceResultBase(**result)
            for result in results
        ]

        return ComplianceCheckResponse(
            status=overall_status,
            score=round(score, 2),
            passed=passed,
            warnings=warnings,
            failed=failed,
            results=typed_results,
        )

    # ---------------------------------------------------------
    # Persist an evaluation
    # ---------------------------------------------------------

    def run_and_save(
        self,
        assessment_id: int,
        data: ComplianceCheckInput,
    ) -> ComplianceCheckResponse:

        assessment = self.get_assessment(assessment_id)

        if assessment is None:
            raise ValueError(
                f"Compliance assessment {assessment_id} was not found."
            )

        result = self.evaluate(data)

        self.repository.delete_results(assessment_id)

        for item in result.results:
            self.repository.add_result(
                ComplianceResult(
                    assessment_id=assessment_id,
                    rule_code=item.rule_code,
                    rule_name=item.rule_name,
                    category=item.category,
                    required_value=item.required_value,
                    actual_value=item.actual_value,
                    unit=item.unit,
                    status=item.status,
                    required=item.required,
                    message=item.message,
                )
            )

        assessment.status = result.status
        assessment.score = result.score

        self.repository.update_assessment(assessment)

        return result