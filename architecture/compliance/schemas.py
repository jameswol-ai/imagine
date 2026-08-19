"""
Pydantic schemas for Architecture Compliance.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ComplianceResultBase(BaseModel):
    rule_code: str = Field(min_length=1, max_length=100)
    rule_name: str = Field(min_length=1, max_length=200)
    category: str = Field(min_length=1, max_length=100)

    required_value: Optional[float] = None
    actual_value: Optional[float] = None

    unit: Optional[str] = None

    status: str = Field(
        default="PENDING",
        max_length=30,
    )

    required: bool = True

    message: Optional[str] = None


class ComplianceResultCreate(ComplianceResultBase):
    pass


class ComplianceResultRead(ComplianceResultBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    assessment_id: int


class ComplianceAssessmentBase(BaseModel):
    project_id: Optional[int] = None
    zoning_id: Optional[int] = None
    site_plan_id: Optional[int] = None
    floor_plan_id: Optional[int] = None

    name: str = Field(
        min_length=1,
        max_length=200,
    )

    status: str = Field(
        default="PENDING",
        max_length=30,
    )

    score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
    )

    notes: Optional[str] = None


class ComplianceAssessmentCreate(ComplianceAssessmentBase):
    pass


class ComplianceAssessmentUpdate(BaseModel):
    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    notes: Optional[str] = None

    status: Optional[str] = Field(
        default=None,
        max_length=30,
    )


class ComplianceAssessmentRead(ComplianceAssessmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

    rules: list[ComplianceResultRead] = Field(
        default_factory=list,
    )


class ComplianceCheckInput(BaseModel):
    """
    Input used by the compliance engine.

    Values are deliberately independent from Streamlit so the
    service can also be used through an API or background worker.
    """

    site_area_m2: float = Field(gt=0)

    building_footprint_m2: float = Field(
        ge=0,
    )

    gross_floor_area_m2: float = Field(
        ge=0,
    )

    building_height_m: float = Field(
        ge=0,
    )

    front_setback_m: float = Field(
        ge=0,
    )

    side_setback_m: float = Field(
        ge=0,
    )

    rear_setback_m: float = Field(
        ge=0,
    )

    max_height_m: Optional[float] = Field(
        default=None,
        gt=0,
    )

    max_coverage_percent: Optional[float] = Field(
        default=None,
        gt=0,
        le=100,
    )

    max_far: Optional[float] = Field(
        default=None,
        gt=0,
    )

    min_front_setback_m: Optional[float] = Field(
        default=None,
        ge=0,
    )

    min_side_setback_m: Optional[float] = Field(
        default=None,
        ge=0,
    )

    min_rear_setback_m: Optional[float] = Field(
        default=None,
        ge=0,
    )


class ComplianceCheckResponse(BaseModel):
    status: str
    score: float
    passed: int
    warnings: int
    failed: int
    results: list[ComplianceResultBase]