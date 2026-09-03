"""
IMAGINE Architecture
Floor Planning SQLAlchemy Models
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import Base


class FloorPlan(Base):
    """Proposed building floor-plan configuration."""

    __tablename__ = "floor_plans"

    __table_args__ = (
        Index("ix_floor_plans_project_id", "project_id"),
        Index("ix_floor_plans_site_plan_id", "site_plan_id"),
        Index("ix_floor_plans_zoning_id", "zoning_id"),
        Index("ix_floor_plans_status", "status"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    project_id: Mapped[UUID | None] = mapped_column(ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    site_plan_id: Mapped[UUID] = mapped_column(ForeignKey("site_plans.id", ondelete="RESTRICT"), nullable=False)
    zoning_id: Mapped[UUID] = mapped_column(ForeignKey("zoning_rules.id", ondelete="RESTRICT"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    plan_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft")
    gross_floor_area_m2: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    net_floor_area_m2: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    storeys: Mapped[int | None] = mapped_column(Integer, nullable=True)
    circulation_pct: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
