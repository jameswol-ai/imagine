"""
IMAGINE Architecture
Floor Planning Seed Data
"""

from decimal import Decimal

from sqlalchemy import select

from .models import FloorPlan


SEED_FLOOR_PLANS = [
    {
        "name": "Green Tower Concept",
        "plan_code": "FP-GT-001",
        "status": "Proposed",
        "building_type": "Office",
        "number_of_floors": 8,
        "floor_area_m2": Decimal("2500"),
        "building_footprint_m2": Decimal("2100"),
        "gross_floor_area_m2": Decimal("20000"),
        "front_setback_m": Decimal("6"),
        "rear_setback_m": Decimal("5"),
        "side_setback_m": Decimal("4"),
        "notes": (
            "Initial commercial office floor planning concept."
        ),
        "active": True,
    },
    {
        "name": "Harbor Bridge Administration Block",
        "plan_code": "FP-HB-001",
        "status": "Draft",
        "building_type": "Office",
        "number_of_floors": 4,
        "floor_area_m2": Decimal("1200"),
        "building_footprint_m2": Decimal("1000"),
        "gross_floor_area_m2": Decimal("4800"),
        "front_setback_m": Decimal("8"),
        "rear_setback_m": Decimal("6"),
        "side_setback_m": Decimal("5"),
        "notes": (
            "Administration and operations building."
        ),
        "active": True,
    },
]


async def seed_floor_plans(
    session,
    *,
    site_plan_id,
    zoning_id,
    project_id=None,
) -> int:
    """
    Insert floor-plan seed records only when the table is empty.

    Site and zoning IDs are supplied by the application seeder so
    this module never invents foreign-key identifiers.
    """

    existing = await session.scalar(
        select(FloorPlan.id).limit(1)
    )

    if existing:
        return 0

    inserted = 0

    for data in SEED_FLOOR_PLANS:

        record = FloorPlan(
            **data,
            site_plan_id=site_plan_id,
            zoning_id=zoning_id,
            project_id=project_id,
        )

        session.add(record)

        inserted += 1

    await session.flush()

    return inserted