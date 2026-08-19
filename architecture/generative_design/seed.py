"""
IMAGINE
Generative Design Seed Data
"""

from __future__ import annotations

from .schemas import (
    ComplianceConstraints,
    DesignConstraints,
    ProgramConstraints,
    RoomRequirement,
    SiteConstraints,
    ZoningConstraints,
)


def demo_constraints() -> DesignConstraints:
    """Return a realistic demonstration project."""

    return DesignConstraints(
        project_id=None,

        site=SiteConstraints(
            width=30,
            depth=40,
            north_access=True,
            setback_front=5,
            setback_rear=3,
            setback_left=3,
            setback_right=3,
        ),

        zoning=ZoningConstraints(
            max_site_coverage=0.60,
            max_far=2.0,
            max_height=15,
            max_storeys=3,
        ),

        program=ProgramConstraints(
            circulation_ratio=0.18,
            rooms=[
                RoomRequirement(
                    name="Living Room",
                    area=30,
                ),
                RoomRequirement(
                    name="Kitchen",
                    area=18,
                ),
                RoomRequirement(
                    name="Bedroom",
                    area=16,
                    quantity=3,
                ),
                RoomRequirement(
                    name="Bathroom",
                    area=6,
                    quantity=3,
                ),
                RoomRequirement(
                    name="Office",
                    area=12,
                ),
            ],
        ),

        compliance=ComplianceConstraints(
            minimum_egress_width=1.2,
            accessibility_required=True,
            fire_separation_required=True,
        ),

        metadata={
            "source": "IMAGINE demo seed",
            "building_type": "residential",
        },
    )


def seed_payload() -> dict:
    """Return a serializable seed payload."""

    constraints = demo_constraints()

    return {
        "name": "Demo Generative Design Run",
        "project_id": constraints.project_id,
        "constraints": constraints.model_dump(),
        "candidate_count": 5,
    }