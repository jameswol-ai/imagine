"""
IMAGINE Architecture
Room Programming SQLAlchemy Models
"""

from __future__ import annotations

import enum
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class RoomType(str, enum.Enum):
    OFFICE = "office"
    CONFERENCE = "conference"
    LOBBY = "lobby"
    CORRIDOR = "corridor"
    RESTROOM = "restroom"
    CAFETERIA = "cafeteria"
    STORAGE = "storage"
    PLANT = "plant"
    RETAIL = "retail"
    RESIDENTIAL = "residential"
    CLASSROOM = "classroom"
    OTHER = "other"


class AdjacencyType(str, enum.Enum):
    REQUIRED = "required"
    PREFERRED = "preferred"
    PROHIBITED = "prohibited"


class RoomProgram(Base):
    """
    Programmed room/space requirement belonging to a floor plan.

    Constraint enforcement is performed by RoomProgramService.
    """

    __tablename__ = "room_programs"

    __table_args__ = (
        UniqueConstraint(
            "floor_plan_id",
            "room_code",
            name="uq_room_program_floor_plan_code",
        ),
        Index(
            "ix_room_programs_floor_plan_id",
            "floor_plan_id",
        ),
        Index(
            "ix_room_programs_room_type",
            "room_type",
        ),
        Index(
            "ix_room_programs_active",
            "active",
        ),
        CheckConstraint(
            "area_m2 > 0",
            name="ck_room_program_area_positive",
        ),
        CheckConstraint(
            "quantity >= 1",
            name="ck_room_program_quantity_positive",
        ),
        CheckConstraint(
            "occupancy >= 0",
            name="ck_room_program_occupancy_nonnegative",
        ),
        CheckConstraint(
            "minimum_area_m2 >= 0",
            name="ck_room_program_min_area_nonnegative",
        ),
        CheckConstraint(
            "maximum_area_m2 >= 0",
            name="ck_room_program_max_area_nonnegative",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    floor_plan_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(
            "floor_plans.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    room_code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    room_type: Mapped[RoomType] = mapped_column(
        Enum(
            RoomType,
            name="room_program_type",
        ),
        nullable=False,
        default=RoomType.OTHER,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    area_m2: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    minimum_area_m2: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    maximum_area_m2: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    occupancy: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    occupancy_factor_m2_per_person: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0,
    )

    floor_level: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    adjacency_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    floor_plan = relationship(
        "FloorPlan",
        foreign_keys=[floor_plan_id],
    )