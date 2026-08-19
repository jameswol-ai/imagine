from __future__ import annotations

import enum

from sqlalchemy import Column, Enum, Float, ForeignKey, String
from sqlalchemy.orm import relationship

from database.models.base import BaseModel


class ProjectStatus(str, enum.Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Project(BaseModel):
    __tablename__ = "projects"

    name = Column(
        String,
        index=True,
        nullable=False,
    )

    description = Column(
        String,
        nullable=True,
    )

    status = Column(
        Enum(ProjectStatus),
        default=ProjectStatus.PLANNING,
        nullable=False,
    )

    budget = Column(
        Float,
        default=0.0,
        nullable=False,
    )

    progress = Column(
        Float,
        default=0.0,
        nullable=False,
    )

    start_date = Column(
        String,
        nullable=True,
    )

    end_date = Column(
        String,
        nullable=True,
    )

    # Organization.id is Integer in the existing database model.
    client_id = Column(
        ForeignKey("organizations.id"),
        nullable=True,
    )

    client = relationship(
        "Organization",
        foreign_keys=[client_id],
    )

    approvals = relationship(
        "Approval",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    revisions = relationship(
        "Revision",
        back_populates="project",
        cascade="all, delete-orphan",
    )