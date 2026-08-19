from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4
from sqlalchemy import Boolean, DateTime, Numeric, String, Text, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from database.models.base import Base

class SitePlan(Base):
    __tablename__ = "site_plans"
    __table_args__ = (Index("ix_site_plans_project_id", "project_id"), Index("ix_site_plans_status", "status"))
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    project_id: Mapped[UUID | None] = mapped_column(ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    site_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="Draft", nullable=False)
    site_area_m2: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    building_footprint_m2: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    road_area_m2: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    parking_area_m2: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    landscape_area_m2: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    north_orientation_deg: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=0, nullable=False)
    slope_percent: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=0, nullable=False)
    soil_type: Mapped[str | None] = mapped_column(String(80))
    drainage_strategy: Mapped[str | None] = mapped_column(String(200))
    access_strategy: Mapped[str | None] = mapped_column(String(200))
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
