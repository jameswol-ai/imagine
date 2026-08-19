from __future__ import annotations
from decimal import Decimal
from uuid import UUID
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator
Status = Literal["Draft", "Proposed", "Approved", "Archived"]

class SitePlanBase(BaseModel):
    project_id: UUID | None = None
    name: str = Field(min_length=1, max_length=200)
    site_code: str = Field(min_length=1, max_length=100)
    description: str | None = None
    status: Status = "Draft"
    site_area_m2: Decimal = Field(gt=0)
    building_footprint_m2: Decimal = Field(ge=0)
    road_area_m2: Decimal = Field(ge=0)
    parking_area_m2: Decimal = Field(ge=0)
    landscape_area_m2: Decimal = Field(ge=0)
    north_orientation_deg: Decimal = Field(ge=0, lt=360)
    slope_percent: Decimal = Field(ge=0, le=100)
    soil_type: str | None = Field(default=None, max_length=80)
    drainage_strategy: str | None = Field(default=None, max_length=200)
    access_strategy: str | None = Field(default=None, max_length=200)
    active: bool = True
    @field_validator("site_code")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        return value.strip().upper()

class SitePlanCreate(SitePlanBase): pass
class SitePlanUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    project_id: UUID | None = None
    name: str | None = Field(default=None, min_length=1, max_length=200)
    site_code: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    status: Status | None = None
    site_area_m2: Decimal | None = Field(default=None, gt=0)
    building_footprint_m2: Decimal | None = Field(default=None, ge=0)
    road_area_m2: Decimal | None = Field(default=None, ge=0)
    parking_area_m2: Decimal | None = Field(default=None, ge=0)
    landscape_area_m2: Decimal | None = Field(default=None, ge=0)
    north_orientation_deg: Decimal | None = Field(default=None, ge=0, lt=360)
    slope_percent: Decimal | None = Field(default=None, ge=0, le=100)
    soil_type: str | None = None
    drainage_strategy: str | None = None
    access_strategy: str | None = None
    active: bool | None = None

class SitePlanRead(SitePlanBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime
    updated_at: datetime

class SitePlanSummary(BaseModel):
    total_plans: int
    active_plans: int
    approved_plans: int
    total_site_area_m2: Decimal
    total_landscaped_area_m2: Decimal
