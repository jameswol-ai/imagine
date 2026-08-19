"""
SQLAlchemy models for the IMAGINE Architecture Compliance module.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base


class ComplianceAssessment(Base):
    """
    Stores a compliance assessment for a floor/building plan.
    """

    __tablename__ = "compliance_assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    project_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        index=True,
    )

    zoning_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        index=True,
    )

    site_plan_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        index=True,
    )

    floor_plan_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="PENDING",
        index=True,
    )

    score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    rules: Mapped[list["ComplianceResult"]] = relationship(
        "ComplianceResult",
        back_populates="assessment",
        cascade="all, delete-orphan",
        order_by="ComplianceResult.id",
    )


class ComplianceResult(Base):
    """
    Individual compliance rule result.
    """

    __tablename__ = "compliance_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    assessment_id: Mapped[int] = mapped_column(
        ForeignKey(
            "compliance_assessments.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    rule_code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    rule_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    required_value: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    actual_value: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    unit: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    required: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    assessment: Mapped["ComplianceAssessment"] = relationship(
        "ComplianceAssessment",
        back_populates="rules",
    )