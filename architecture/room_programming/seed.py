"""
IMAGINE Architecture
Room Programming Seed Data
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from architecture.floor_planning.models import FloorPlan

from .models import RoomProgram, RoomType


DEFAULT_ROOMS = [
    {
        "room_code": "OFF-101",
        "name": "Office 101",
        "room_type": RoomType.OFFICE,
        "description": "Standard office workspace.",
        "quantity": 10,
        "area_m2": 20,
        "minimum_area_m2": 15,
        "maximum_area_m2": 35,
        "occupancy": 2,
        "occupancy_factor_m2_per_person": 8,
        "floor_level": "Level 1",
        "adjacency_notes": "Prefer corridor access.",
    },
    {
        "room_code": "CONF-101",
        "name": "Conference Room",
        "room_type": RoomType.CONFERENCE,
        "description": "Primary meeting and conference room.",
        "quantity": 2,
        "area_m2": 40,
        "minimum_area_m2": 30,
        "maximum_area_m2": 80,
        "occupancy": 12,
        "occupancy_factor_m2_per_person": 2.5,
        "floor_level": "Level 1",
        "adjacency_notes": "Adjacent to lobby.",
    },
    {
        "room_code": "LOB-101",
        "name": "Main Lobby",
        "room_type": RoomType.LOBBY,
        "description": "Main public entrance and reception area.",
        "quantity": 1,
        "area_m2": 60,
        "minimum_area_m2": 40,
        "maximum_area_m2": 120,
        "occupancy": 20,
        "occupancy_factor_m2_per_person": 2,
        "floor_level": "Level 1",
        "adjacency_notes": "Adjacent to reception and conference rooms.",
    },
    {
        "room_code": "RR-101",
        "name": "Restroom",
        "room_type": RoomType.RESTROOM,
        "description": "General-purpose restroom.",
        "quantity": 4,
        "area_m2": 10,
        "minimum_area_m2": 6,
        "maximum_area_m2": 20,
        "occupancy": 2,
        "occupancy_factor_m2_per_person": 3,
        "floor_level": "Level 1",
        "adjacency_notes": "Accessible from common circulation.",
    },
]


async def seed_room_programming(
    db: AsyncSession,
) -> int:

    floor_plan = await db.scalar(
        select(FloorPlan)
        .where(FloorPlan.active.is_(True))
        .order_by(FloorPlan.created_at)
    )

    if floor_plan is None:
        return 0

    created = 0

    for data in DEFAULT_ROOMS:

        existing = await db.scalar(
            select(RoomProgram).where(
                RoomProgram.floor_plan_id == floor_plan.id,
                RoomProgram.room_code == data["room_code"],
            )
        )

        if existing:
            continue

        room = RoomProgram(
            floor_plan_id=floor_plan.id,
            **data,
        )

        db.add(room)
        created += 1

    await db.flush()

    return created