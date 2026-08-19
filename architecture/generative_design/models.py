"""
IMAGINE
Generative Design Database Models

Persistence models for constraint-driven architectural
generative design runs and their generated candidates.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship

from database.models.base import BaseModel


class GenerativeDesignRun(BaseModel):
    """
    Represents one generative-design execution.

    A run belongs to a project and contains the normalized
    design constraints used to generate candidate options.
    """

    __tablename__ = "generative_design_runs"

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "projects.id",
            ondelete="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    name = Column(
        String(255),
        nullable=False,
    )

    status = Column(
        String(50),
        nullable=False,
        default="pending",
        index=True,
    )

    constraints = Column(
        MutableDict.as_mutable(JSON),
        nullable=False,
        default=dict,
    )

    candidate_count = Column(
        Integer,
        nullable=False,
        default=0,
    )

    completed_at = Column(
        # DateTime is intentionally imported below to keep
        # the model declaration easy to scan.
        __import__("sqlalchemy").DateTime,
        nullable=True,
    )

    error_message = Column(
        __import__("sqlalchemy").Text,
        nullable=True,
    )

    candidates = relationship(
        "DesignCandidateRecord",
        back_populates="run",
        cascade="all, delete-orphan",
        order_by="DesignCandidateRecord.rank",
    )


class DesignCandidateRecord(BaseModel):
    """
    Represents one generated architectural design candidate.

    Candidate geometry, calculated metrics, and evaluation
    results are stored as JSON so the schema can evolve as
    the generative engine becomes more sophisticated.
    """

    __tablename__ = "generative_design_candidates"

    run_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "generative_design_runs.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    name = Column(
        String(255),
        nullable=False,
    )

    status = Column(
        String(50),
        nullable=False,
        default="generated",
    )

    rank = Column(
        Integer,
        nullable=True,
        index=True,
    )

    score = Column(
        Float,
        nullable=False,
        default=0.0,
    )

    geometry = Column(
        MutableDict.as_mutable(JSON),
        nullable=False,
        default=dict,
    )

    metrics = Column(
        MutableDict.as_mutable(JSON),
        nullable=False,
        default=dict,
    )

    evaluation = Column(
        MutableDict.as_mutable(JSON),
        nullable=False,
        default=dict,
    )

    run = relationship(
        "GenerativeDesignRun",
        back_populates="candidates",
    )
