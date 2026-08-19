"""
IMAGINE Architecture
Floor Planning Pydantic Schemas
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


FloorPlanStatus = Literal[
    "Draft",
    "Proposed",
    "Approved",
    "Archived",
]


class FloorPlanBase(BaseModel):
    project_id: UUID | None = None

    site_plan_id: UUID
    zoning_id: UUID

    name: str = Field(
        min_length=1,
        max_length=200,
    )

    plan_code: str = Field(
        min_length=1,
        max_length=100,
    )

    description: str | None = None

    status: FloorPlanStatus = "Draft"

    building_type: str = Field(
        min_length=1,
        max_length=100,
    )

    number_of_floors: int = Field(
        ge=1,
        le=200,
    )

    floor_area_m2: Decimal = Field(
        gt=0,
    )

    building_footprint_m2: Decimal = Field(
        gt=0,
    )

    gross_floor_area_m2: Decimal = Field(
        gt=0,
    )

    front_setback_m: Decimal = Field(
        ge=0,
    )

    rear_setback_m: Decimal = Field(
        ge=0,
    )

    side_setback_m: Decimal = Field(
        ge=0,
    )

    notes: str | None = None

    active: bool = True

    @field_validator("plan_code")
    @classmethod
    def normalize_plan_code(cls, value: str) -> str:
        return value.strip().upper()


class FloorPlanCreate(FloorPlanBase):
    pass


class FloorPlanUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_id: UUID | None = None

    site_plan_id: UUID | None = None
    zoning_id: UUID | None = None

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    plan_code: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    description: str | None = None

    status: FloorPlanStatus | None = None

    building_type: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    number_of_floors: int | None = Field(
        default=None,
        ge=1,
        le=200,
    )

    floor_area_m2: Decimal | None = Field(
        default=None,
        gt=0,
    )

    building_footprint_m2: Decimal | None = Field(
        default=None,
        gt=0,
    )

    gross_floor_area_m2: Decimal | None = Field(
        default=None,
        gt=0,
    )

    front_setback_m: Decimal | None = Field(
        default=None,
        ge=0,
    )

    rear_setback_m: Decimal | None = Field(
        default=None,
        ge=0,
    )

    side_setback_m: Decimal | None = Field(
        default=None,
        ge=0,
    )

    notes: str | None = None

    active: bool | None = None

    @field_validator("plan_code")
    @classmethod
    def normalize_plan_code(cls, value: str | None) -> str | None:
        if value is None:
            return None

        return value.strip().upper()


class FloorPlanRead(FloorPlanBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    created_at: datetime
    updated_at: datetime


class FloorPlanConstraintResult(BaseModel):
    floor_plan_id: UUID

    site_area_m2: Decimal

    maximum_coverage_percent: Decimal
    maximum_footprint_m2: Decimal

    proposed_footprint_m2: Decimal
    proposed_coverage_percent: Decimal

    maximum_far: Decimal
    proposed_far: Decimal

    maximum_gfa_m2: Decimal
    proposed_gfa_m2: Decimal

    required_front_setback_m: Decimal
    required_rear_setback_m: Decimal
    required_side_setback_m: Decimal

    proposed_front_setback_m: Decimal
    proposed_rear_setback_m: Decimal
    proposed_side_setback_m: Decimal

    setbacks_compliant: bool
    site_area_compliant: bool
    coverage_compliant: bool
    far_compliant: bool
    gfa_compliant: bool

    overall_compliant: bool

    violations: list[str] = []


class FloorPlanSummary(BaseModel):
    total_plans: int
    active_plans: int
    approved_plans: int

    total_site_area_m2: Decimal
    total_footprint_m2: Decimal
    total_gfa_m2: Decimal

    compliant_plans: int
    non_compliant_plans: int