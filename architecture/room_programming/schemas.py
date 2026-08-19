"""
IMAGINE Architecture
Room Programming Pydantic Schemas
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


RoomType = Literal[
    "office",
    "conference",
    "lobby",
    "corridor",
    "restroom",
    "cafeteria",
    "storage",
    "plant",
    "retail",
    "residential",
    "classroom",
    "other",
]


AdjacencyType = Literal[
    "required",
    "preferred",
    "prohibited",
]


class RoomAdjacency(BaseModel):
    """
    Defines a relationship between this room and another room.

    Example:
        Office 101 requires adjacency to Corridor.
    """

    target_room_code: str = Field(
        min_length=1,
        max_length=100,
    )

    adjacency_type: AdjacencyType = "preferred"

    @field_validator("target_room_code")
    @classmethod
    def normalize_target_code(cls, value: str) -> str:
        return value.strip().upper()


class RoomProgramBase(BaseModel):
    floor_plan_id: UUID

    room_code: str = Field(
        min_length=1,
        max_length=100,
    )

    name: str = Field(
        min_length=1,
        max_length=200,
    )

    room_type: RoomType = "other"

    description: str | None = None

    quantity: int = Field(
        default=1,
        ge=1,
    )

    area_m2: Decimal = Field(
        gt=0,
    )

    minimum_area_m2: Decimal = Field(
        default=Decimal("0"),
        ge=0,
    )

    maximum_area_m2: Decimal = Field(
        default=Decimal("0"),
        ge=0,
    )

    occupancy: int = Field(
        default=0,
        ge=0,
    )

    occupancy_factor_m2_per_person: Decimal = Field(
        default=Decimal("0"),
        ge=0,
    )

    floor_level: str | None = Field(
        default=None,
        max_length=100,
    )

    adjacency_notes: str | None = None

    active: bool = True

    @field_validator("room_code")
    @classmethod
    def normalize_room_code(cls, value: str) -> str:
        return value.strip().upper()

    @model_validator(mode="after")
    def validate_area_range(self):
        if (
            self.maximum_area_m2 > 0
            and self.maximum_area_m2 < self.minimum_area_m2
        ):
            raise ValueError(
                "maximum_area_m2 cannot be less than minimum_area_m2."
            )

        if self.minimum_area_m2 > 0:
            if self.area_m2 < self.minimum_area_m2:
                raise ValueError(
                    "area_m2 is below minimum_area_m2."
                )

        if self.maximum_area_m2 > 0:
            if self.area_m2 > self.maximum_area_m2:
                raise ValueError(
                    "area_m2 exceeds maximum_area_m2."
                )

        return self


class RoomProgramCreate(RoomProgramBase):
    adjacency: list[RoomAdjacency] = Field(
        default_factory=list,
    )


class RoomProgramUpdate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    floor_plan_id: UUID | None = None

    room_code: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    room_type: RoomType | None = None

    description: str | None = None

    quantity: int | None = Field(
        default=None,
        ge=1,
    )

    area_m2: Decimal | None = Field(
        default=None,
        gt=0,
    )

    minimum_area_m2: Decimal | None = Field(
        default=None,
        ge=0,
    )

    maximum_area_m2: Decimal | None = Field(
        default=None,
        ge=0,
    )

    occupancy: int | None = Field(
        default=None,
        ge=0,
    )

    occupancy_factor_m2_per_person: Decimal | None = Field(
        default=None,
        ge=0,
    )

    floor_level: str | None = Field(
        default=None,
        max_length=100,
    )

    adjacency_notes: str | None = None

    active: bool | None = None

    adjacency: list[RoomAdjacency] | None = None

    @field_validator("room_code")
    @classmethod
    def normalize_room_code(cls, value: str | None) -> str | None:
        if value is None:
            return None

        return value.strip().upper()

    @model_validator(mode="after")
    def validate_area_range(self):
        if (
            self.minimum_area_m2 is not None
            and self.maximum_area_m2 is not None
            and self.maximum_area_m2 > 0
            and self.maximum_area_m2 < self.minimum_area_m2
        ):
            raise ValueError(
                "maximum_area_m2 cannot be less than minimum_area_m2."
            )

        if (
            self.area_m2 is not None
            and self.minimum_area_m2 is not None
            and self.minimum_area_m2 > 0
            and self.area_m2 < self.minimum_area_m2
        ):
            raise ValueError(
                "area_m2 is below minimum_area_m2."
            )

        if (
            self.area_m2 is not None
            and self.maximum_area_m2 is not None
            and self.maximum_area_m2 > 0
            and self.area_m2 > self.maximum_area_m2
        ):
            raise ValueError(
                "area_m2 exceeds maximum_area_m2."
            )

        return self


class RoomProgramRead(RoomProgramBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    created_at: datetime
    updated_at: datetime


class RoomProgramConstraintResult(BaseModel):
    room_program_id: UUID

    room_code: str

    area_m2: Decimal

    minimum_area_m2: Decimal
    maximum_area_m2: Decimal

    occupancy: int

    occupancy_factor_m2_per_person: Decimal

    calculated_required_area_m2: Decimal

    area_compliant: bool
    occupancy_compliant: bool

    adjacency_compliant: bool
    overall_compliant: bool

    violations: list[str] = Field(
        default_factory=list,
    )


class RoomProgramSummary(BaseModel):
    floor_plan_id: UUID

    room_count: int

    total_quantity: int

    total_programmed_area_m2: Decimal

    floor_area_m2: Decimal

    remaining_floor_area_m2: Decimal

    total_occupancy: int

    compliant_rooms: int

    non_compliant_rooms: int

    overall_compliant: bool