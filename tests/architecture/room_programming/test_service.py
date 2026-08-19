from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest

from architecture.room_programming.models import RoomProgram
from architecture.room_programming.service import (
    RoomProgramService,
)


def make_floor_plan(
    floor_area=1000,
):
    return SimpleNamespace(
        id=uuid4(),
        floor_area_m2=Decimal(
            str(floor_area)
        ),
    )


def make_room(
    area=20,
    minimum=0,
    maximum=0,
    occupancy=0,
    factor=0,
    quantity=1,
    code="OFF-101",
):
    return RoomProgram(
        id=uuid4(),
        floor_plan_id=uuid4(),
        room_code=code,
        name="Test Room",
        area_m2=Decimal(str(area)),
        minimum_area_m2=Decimal(str(minimum)),
        maximum_area_m2=Decimal(str(maximum)),
        occupancy=occupancy,
        occupancy_factor_m2_per_person=Decimal(
            str(factor)
        ),
        quantity=quantity,
        active=True,
    )


def test_required_area_uses_minimum_area():
    room = make_room(
        area=30,
        minimum=25,
        occupancy=2,
        factor=5,
    )

    required = RoomProgramService._required_area(
        room
    )

    assert required == Decimal("25")


def test_required_area_uses_occupancy_requirement():
    room = make_room(
        area=60,
        minimum=20,
        occupancy=10,
        factor=6,
    )

    required = RoomProgramService._required_area(
        room
    )

    assert required == Decimal("60")


def test_room_with_valid_area_and_occupancy_is_compliant():
    floor_plan = make_floor_plan(1000)

    room = make_room(
        area=50,
        minimum=30,
        maximum=80,
        occupancy=5,
        factor=8,
    )

    result = RoomProgramService._constraint_result(
        floor_plan,
        room,
    )

    assert result.area_compliant is True
    assert result.occupancy_compliant is True
    assert result.overall_compliant is True
    assert result.violations == []


def test_room_below_minimum_is_not_compliant():
    floor_plan = make_floor_plan(1000)

    room = make_room(
        area=20,
        minimum=30,
    )

    result = RoomProgramService._constraint_result(
        floor_plan,
        room,
    )

    assert result.area_compliant is False
    assert result.overall_compliant is False
    assert result.violations


def test_room_exceeding_maximum_is_not_compliant():
    floor_plan = make_floor_plan(1000)

    room = make_room(
        area=100,
        minimum=20,
        maximum=80,
    )

    result = RoomProgramService._constraint_result(
        floor_plan,
        room,
    )

    assert result.area_compliant is False
    assert result.overall_compliant is False


def test_occupancy_constraint_is_enforced():
    floor_plan = make_floor_plan(1000)

    room = make_room(
        area=20,
        minimum=10,
        occupancy=10,
        factor=5,
    )

    result = RoomProgramService._constraint_result(
        floor_plan,
        room,
    )

    assert result.occupancy_compliant is False
    assert result.overall_compliant is False


def test_total_program_area_cannot_exceed_floor_area():
    floor_plan = make_floor_plan(100)

    room_a = make_room(
        area=60,
        code="ROOM-A",
    )

    room_b = make_room(
        area=60,
        code="ROOM-B",
    )

    violations = RoomProgramService._validate_program(
        floor_plan,
        [
            room_a,
            room_b,
        ],
    )

    assert any(
        "exceeds floor area" in message
        for message in violations
    )


def test_duplicate_room_codes_are_rejected():
    floor_plan = make_floor_plan(1000)

    room_a = make_room(
        area=20,
        code="ROOM-01",
    )

    room_b = make_room(
        area=20,
        code="ROOM-01",
    )

    violations = RoomProgramService._validate_program(
        floor_plan,
        [
            room_a,
            room_b,
        ],
    )

    assert any(
        "Duplicate room code" in message
        for message in violations
    )