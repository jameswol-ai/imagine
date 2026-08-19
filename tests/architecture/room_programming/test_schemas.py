from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from architecture.room_programming.schemas import (
    RoomProgramCreate,
)


def test_room_code_is_normalized():
    payload = RoomProgramCreate(
        floor_plan_id=uuid4(),
        room_code=" off-101 ",
        name="Office 101",
        area_m2=20,
    )

    assert payload.room_code == "OFF-101"


def test_negative_area_is_rejected():
    with pytest.raises(ValidationError):
        RoomProgramCreate(
            floor_plan_id=uuid4(),
            room_code="OFF-101",
            name="Office 101",
            area_m2=-1,
        )


def test_maximum_area_cannot_be_less_than_minimum():
    with pytest.raises(ValidationError):
        RoomProgramCreate(
            floor_plan_id=uuid4(),
            room_code="OFF-101",
            name="Office 101",
            area_m2=20,
            minimum_area_m2=30,
            maximum_area_m2=25,
        )


def test_area_below_minimum_is_rejected():
    with pytest.raises(ValidationError):
        RoomProgramCreate(
            floor_plan_id=uuid4(),
            room_code="OFF-101",
            name="Office 101",
            area_m2=10,
            minimum_area_m2=20,
        )


def test_area_above_maximum_is_rejected():
    with pytest.raises(ValidationError):
        RoomProgramCreate(
            floor_plan_id=uuid4(),
            room_code="OFF-101",
            name="Office 101",
            area_m2=50,
            maximum_area_m2=40,
        )


def test_valid_room_program():
    payload = RoomProgramCreate(
        floor_plan_id=uuid4(),
        room_code="CONF-101",
        name="Conference Room",
        area_m2=40,
        minimum_area_m2=30,
        maximum_area_m2=80,
        occupancy=12,
        occupancy_factor_m2_per_person=Decimal("2.5"),
    )

    assert payload.area_m2 == Decimal("40")
    assert payload.occupancy == 12