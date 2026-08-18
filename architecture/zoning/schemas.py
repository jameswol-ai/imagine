from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .models import ZoningStatus, ZoningUse


class ZoningRuleBase(BaseModel):
    project_id: Optional[UUID] = None
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=150)
    description: Optional[str] = None

    allowed_use: ZoningUse
    status: ZoningStatus = ZoningStatus.ACTIVE

    max_height_m: float = Field(default=0.0, ge=0)
    site_coverage_pct: float = Field(default=0.0, ge=0, le=100)
    setback_m: float = Field(default=0.0, ge=0)
    far: float = Field(default=0.0, ge=0)


class ZoningRuleCreate(ZoningRuleBase):
    pass


class ZoningRuleUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_id: Optional[UUID] = None
    code: Optional[str] = Field(default=None, min_length=1, max_length=50)
    name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    description: Optional[str] = None

    allowed_use: Optional[ZoningUse] = None
    status: Optional[ZoningStatus] = None

    max_height_m: Optional[float] = Field(default=None, ge=0)
    site_coverage_pct: Optional[float] = Field(default=None, ge=0, le=100)
    setback_m: Optional[float] = Field(default=None, ge=0)
    far: Optional[float] = Field(default=None, ge=0)


class ZoningRuleResponse(ZoningRuleBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
