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
        else 0
    )

    height_per_storey = (
        constraints.zoning.max_height
        / constraints.zoning.max_storeys
    )

    total_height = (
        height_per_storey
        * storeys
    )

    room_count = sum(
        room.quantity
        for room in constraints.program.rooms
    )

    geometry = {
        "type": "rectangular_massing",
        "footprint": {
            "width": round(
                width,
                3,
            ),
            "depth": round(
                depth,
                3,
            ),
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
    }

    metrics = {
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
    }

    return DesignCandidate(
        name=f"Generated Option {storeys} Storey",
        geometry=geometry,
        metrics=metrics,
    )


def generate_candidates(
    constraints: DesignConstraints,
    count: int = 5,
) -> list[DesignCandidate]:
    """
    Generate a deterministic collection of candidates.

    Candidates vary primarily by storey configuration.
    """

    if count < 1:
        raise ValueError(
            "Candidate count must be at least 1."
        )

    buildable = calculate_buildable_site(
        constraints
    )

    minimum_required_area = (
        calculate_required_gross_area(
            constraints
        )
    )

    maximum_footprint = (
        buildable.area
        * constraints.zoning.max_site_coverage
    )

    if maximum_footprint <= 0:
        raise ValueError(
            "Maximum building footprint must be greater than zero."
        )

    minimum_storeys = max(
        1,
        ceil(
            minimum_required_area
            / maximum_footprint
        ),
    )

    maximum_storeys = (
        constraints.zoning.max_storeys
    )

    if minimum_storeys > maximum_storeys:
        raise ValueError(
            "Required program cannot be accommodated within "
            "the configured maximum number of storeys."
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

        candidate.rank = (
            index + 1
        )

        candidates.append(
            candidate
        )

    return candidates