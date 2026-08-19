"""
Tests for IMAGINE Room Programming Adjacencies.
"""

import pytest

from architecture.room_programming.models import (
    RoomProgram,
)
from architecture.room_programming.schemas import (
    RoomAdjacencyCreate,
)
from architecture.room_programming.service import (
    RoomProgrammingService,
)


def create_rooms(db):
    room_a = RoomProgram(
        floor_plan_id=1,
        room_name="Lobby",
        room_type="Lobby",
        required_area_m2=80,
        occupancy=40,
    )

    room_b = RoomProgram(
        floor_plan_id=1,
        room_name="Reception",
        room_type="Reception",
        required_area_m2=25,
        occupancy=4,
    )

    db.add_all(
        [
            room_a,
            room_b,
        ]
    )

    db.commit()

    db.refresh(room_a)
    db.refresh(room_b)

    return room_a, room_b


def test_create_adjacency(db_session):
    room_a, room_b = create_rooms(
        db_session
    )

    service = RoomProgrammingService(
        db_session
    )

    adjacency = service.create_adjacency(
        RoomAdjacencyCreate(
            room_program_id=room_a.id,
            target_room_program_id=room_b.id,
            adjacency_type="Adjacent",
            distance_m=0,
            required=True,
            notes="Reception serves lobby.",
        )
    )

    assert adjacency.id is not None
    assert (
        adjacency.room_program_id
        == room_a.id
    )
    assert (
        adjacency.target_room_program_id
        == room_b.id
    )


def test_self_adjacency_is_rejected(
    db_session,
):
    room_a, _ = create_rooms(
        db_session
    )

    service = RoomProgrammingService(
        db_session
    )

    with pytest.raises(ValueError):
        service.create_adjacency(
            RoomAdjacencyCreate(
                room_program_id=room_a.id,
                target_room_program_id=room_a.id,
                adjacency_type="Adjacent",
                required=True,
            )
        )


def test_missing_source_room_is_rejected(
    db_session,
):
    _, room_b = create_rooms(
        db_session
    )

    service = RoomProgrammingService(
        db_session
    )

    with pytest.raises(ValueError):
        service.create_adjacency(
            RoomAdjacencyCreate(
                room_program_id=99999,
                target_room_program_id=room_b.id,
                adjacency_type="Near",
                required=True,
            )
        )


def test_missing_target_room_is_rejected(
    db_session,
):
    room_a, _ = create_rooms(
        db_session
    )

    service = RoomProgrammingService(
        db_session
    )

    with pytest.raises(ValueError):
        service.create_adjacency(
            RoomAdjacencyCreate(
                room_program_id=room_a.id,
                target_room_program_id=99999,
                adjacency_type="Near",
                required=True,
            )
        )


def test_duplicate_adjacency_is_rejected(
    db_session,
):
    room_a, room_b = create_rooms(
        db_session
    )

    service = RoomProgrammingService(
        db_session
    )

    payload = RoomAdjacencyCreate(
        room_program_id=room_a.id,
        target_room_program_id=room_b.id,
        adjacency_type="Adjacent",
        required=True,
    )

    service.create_adjacency(payload)

    with pytest.raises(ValueError):
        service.create_adjacency(payload)


def test_list_adjacencies_for_room(
    db_session,
):
    room_a, room_b = create_rooms(
        db_session
    )

    service = RoomProgrammingService(
        db_session
    )

    service.create_adjacency(
        RoomAdjacencyCreate(
            room_program_id=room_a.id,
            target_room_program_id=room_b.id,
            adjacency_type="Adjacent",
            required=True,
        )
    )

    results = service.list_adjacencies(
        room_program_id=room_a.id
    )

    assert len(results) == 1
    assert (
        results[0].target_room_program_id
        == room_b.id
    )


def test_delete_adjacency(db_session):
    room_a, room_b = create_rooms(
        db_session
    )

    service = RoomProgrammingService(
        db_session
    )

    adjacency = service.create_adjacency(
        RoomAdjacencyCreate(
            room_program_id=room_a.id,
            target_room_program_id=room_b.id,
            adjacency_type="Near",
            distance_m=10,
            required=False,
        )
    )

    adjacency_id = adjacency.id

    service.delete_adjacency(
        adjacency_id
    )

    assert (
        service.get_adjacency(adjacency_id)
        is None
    )