"""
IMAGINE
Generative Design Schemas
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SiteConstraints(BaseModel):
    """Physical site constraints."""

    width: float = Field(gt=0)
    depth: float = Field(gt=0)

    north_access: bool = True

    setback_front: float = Field(default=0.0, ge=0)
    setback_rear: float = Field(default=0.0, ge=0)
    setback_left: float = Field(default=0.0, ge=0)
    setback_right: float = Field(default=0, ge=0)


class ZoningConstraints(BaseModel):
    """Planning and zoning constraints."""

    max_site_coverage: float = Field(
        default=0.60,
        gt=0,
        le=1,
    )

    max_far: float = Field(
        default=2.0,
        gt=0,
    )

    max_height: float = Field(
        default=15.0,
        gt=0,
    )

    max_storeys: int = Field(
        default=3,
        ge=1,
    )


class RoomRequirement(BaseModel):
    """Individual room/program requirement."""

    name: str = Field(
        min_length=1,
    )

    area: float = Field(
        gt=0,
    )

    quantity: int = Field(
        default=1,
        ge=1,
    )

    required: bool = True


class ProgramConstraints(BaseModel):
    """Functional building-program constraints."""

    rooms: list[RoomRequirement] = Field(
        default_factory=list,
    )

    circulation_ratio: float = Field(
        default=0.15,
        ge=0,
        le=1,
    )


class ComplianceConstraints(BaseModel):
    """High-level compliance constraints."""

    minimum_egress_width: float = Field(
        default=1.1,
        gt=0,
    )

    accessibility_required: bool = True

    fire_separation_required: bool = True


class DesignConstraints(BaseModel):
    """Complete normalized generative-design input."""

    project_id: UUID | None = None

    site: SiteConstraints

    zoning: ZoningConstraints

    program: ProgramConstraints

    compliance: ComplianceConstraints = Field(
        default_factory=ComplianceConstraints,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


class ConstraintValidationResult(BaseModel):
    """Result of constraint validation."""

    valid: bool

    errors: list[str] = Field(
        default_factory=list,
    )

    warnings: list[str] = Field(
        default_factory=list,
    )


class DesignCandidateSchema(BaseModel):
    """Generated candidate representation."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID | None = None

    name: str

    status: str = "generated"

    rank: int | None = None

    score: float = 0.0

    geometry: dict[str, Any] = Field(
        default_factory=dict,
    )

    metrics: dict[str, Any] = Field(
        default_factory=dict,
    )

    evaluation: dict[str, Any] = Field(
        default_factory=dict,
    )


class GenerativeDesignRunCreate(BaseModel):
    """Create a new generative-design run."""

    project_id: UUID | None = None

    name: str = Field(
        default="Generative Design Run",
        min_length=1,
        max_length=255,
    )

    constraints: DesignConstraints

    candidate_count: int = Field(
        default=5,
        ge=1,
        le=100,
    )


class GenerativeDesignRunResponse(BaseModel):
    """API response for a design run."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    project_id: UUID | None

    name: str

    status: str

    constraints: dict[str, Any]

    candidate_count: int

    created_at: datetime

    completed_at: datetime | None = None

    error_message: str | None = None

    candidates: list[DesignCandidateSchema] = Field(
        default_factory=list,
    )


__all__ = [
    "SiteConstraints",
    "ZoningConstraints",
    "RoomRequirement",
    "ProgramConstraints",
    "ComplianceConstraints",
    "DesignConstraints",
    "ConstraintValidationResult",
    "DesignCandidateSchema",
    "GenerativeDesignRunCreate",
    "GenerativeDesignRunResponse",
]