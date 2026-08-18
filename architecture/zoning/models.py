from __future__ import annotations

import enum

from sqlalchemy import CheckConstraint, Column, Enum, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database.models.base import BaseModel


class ZoningStatus(str, enum.Enum):
    ACTIVE = "active"
    DRAFT = "draft"
    ARCHIVED = "archived"


class ZoningUse(str, enum.Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    MIXED_USE = "mixed_use"
    INDUSTRIAL = "industrial"
    INSTITUTIONAL = "institutional"
    AGRICULTURAL = "agricultural"
    SPECIAL = "special"


class ZoningRule(BaseModel):
    __tablename__ = "zoning_rules"

    __table_args__ = (
        UniqueConstraint("project_id", "code", name="uq_zoning_rules_project_code"),
        CheckConstraint(
            "max_height_m >= 0",
            name="ck_zoning_max_height_nonnegative",
        ),
        CheckConstraint(
            "site_coverage_pct >= 0 AND site_coverage_pct <= 100",
            name="ck_zoning_coverage_range",
        ),
        CheckConstraint(
            "setback_m >= 0",
            name="ck_zoning_setback_nonnegative",
        ),
        CheckConstraint(
            "far >= 0",
            name="ck_zoning_far_nonnegative",
        ),
    )

    # NULL project_id means this is a reusable zoning template.
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    code = Column(String(50), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    description = Column(String, nullable=True)

    allowed_use = Column(
        Enum(ZoningUse, name="zoning_use"),
        nullable=False,
    )

    status = Column(
        Enum(ZoningStatus, name="zoning_status"),
        nullable=False,
        default=ZoningStatus.ACTIVE,
        index=True,
    )

    max_height_m = Column(Float, nullable=False, default=0.0)
    site_coverage_pct = Column(Float, nullable=False, default=0.0)
    setback_m = Column(Float, nullable=False, default=0.0)
    far = Column(Float, nullable=False, default=0.0)

    project = relationship("Project", foreign_keys=[project_id])
