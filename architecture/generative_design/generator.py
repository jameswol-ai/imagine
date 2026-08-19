"""
IMAGINE
Generative Design Candidate Generator
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import ceil
from typing import Any

from .constraints import (
    calculate_buildable_site,
    calculate_required_gross_area,
)
from .schemas import DesignConstraints


@dataclass
class DesignCandidate:
    """In-memory generated design candidate."""

    name: str

    geometry: dict[str, Any]

    metrics: dict[str, Any]

    evaluation: dict[str, Any] = field(
        default_factory=dict
    )

    score: float = 0.0

    rank: int | None = None

    status: str = "generated"


def _generate_layout(
    constraints: DesignConstraints,
    storeys: int,
) -> DesignCandidate:

    buildable = calculate_buildable_site(
        constraints
    )

    gross_area = calculate_required_gross_area(
        constraints
    )

    footprint = gross_area / storeys

    max_footprint = (
        buildable.area
        * constraints.zoning.max_site_coverage
    )

    footprint = min(
        footprint,
        max_footprint,
    )

    aspect_ratio = (
        buildable.width / buildable.depth
        if buildable.depth
        else 1.0
    )

    width = min(
        buildable.width,
        (footprint * aspect_ratio) ** 0.5,
    )

    depth = (
        footprint / width
        if width
        else 0.0
    )

    height_per_storey = (
        constraints.zoning.max_height
        / constraints.zoning.max_storeys
    )

    total_height = (
        height_per_storey * storeys
    )

    room_count = sum(
        room.quantity
        for room in constraints.program.rooms
    )

    return DesignCandidate(
        name="Generated Option",
        geometry={
            "type": "rectangular_massing",
            "footprint": {
                "width": round(width, 3),
                "depth": round(depth, 3),
            },
            "storeys": storeys,
            "height": round(
                total_height,
                3,
            ),
            "orientation": (
                "north_access"
                if constraints.site.north_access
                else "neutral"
            ),
        },
        metrics={
            "site_area": round(
                buildable.area,
                3,
            ),
            "footprint_area": round(
                footprint,
                3,
            ),
            "gross_floor_area": round(
                footprint * storeys,
                3,
            ),
            "site_coverage": round(
                footprint / buildable.area,
                4,
            ),
            "room_count": room_count,
            "storeys": storeys,
        },
    )


def generate_candidates(
    constraints: DesignConstraints,
    count: int = 5,
) -> list[DesignCandidate]:
    """Generate deterministic design candidates."""

    if count < 1:
        raise ValueError(
            "Candidate count must be at least 1."
        )

    buildable = calculate_buildable_site(
        constraints
    )

    required_area = calculate_required_gross_area(
        constraints
    )

    maximum_footprint = (
        buildable.area
        * constraints.zoning.max_site_coverage
    )

    if maximum_footprint <= 0:
        raise ValueError(
            "No positive building footprint is available."
        )

    minimum_storeys = max(
        1,
        ceil(
            required_area
            / maximum_footprint
        ),
    )

    maximum_storeys = (
        constraints.zoning.max_storeys
    )

    candidates: list[DesignCandidate] = []

    for index in range(count):

        storeys = min(
            minimum_storeys + index,
            maximum_storeys,
        )

        candidate = _generate_layout(
            constraints,
            storeys,
        )

        candidate.name = (
            f"Generated Option {index + 1}"
        )

        candidates.append(candidate)

    return candidates


__all__ = [
    "DesignCandidate",
    "generate_candidates",
]