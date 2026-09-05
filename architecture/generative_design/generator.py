"""Pure deterministic generator for architectural massing candidates.

This module is intentionally UI-free. It is imported by the generative-design
service and therefore must never call Streamlit page configuration or render UI.
The generated geometry is preliminary design-assistance output and must be
validated against the adopted planning, structural, fire, accessibility and
other project requirements before use.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .schemas import DesignConstraints


@dataclass
class DesignCandidate:
    """Generated design option shared by generation, scoring and persistence."""

    name: str
    geometry: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    status: str = "generated"
    rank: int | None = None
    score: float = 0.0
    evaluation: dict[str, Any] = field(default_factory=dict)


def _program_area(constraints: DesignConstraints) -> float:
    return sum(
        room.area * room.quantity
        for room in constraints.program.rooms
        if room.required
    ) * (1.0 + constraints.program.circulation_ratio)


def _buildable_dimensions(constraints: DesignConstraints) -> tuple[float, float]:
    site = constraints.site
    width = site.width - site.setback_left - site.setback_right
    depth = site.depth - site.setback_front - site.setback_rear
    if width <= 0 or depth <= 0:
        raise ValueError("Site setbacks leave no buildable footprint.")
    return width, depth


def _candidate_scale(index: int, count: int) -> float:
    if count <= 1:
        return 0.82
    low, high = 0.55, 0.95
    return low + (high - low) * (index / (count - 1))


def generate_candidates(
    constraints: DesignConstraints,
    count: int = 5,
) -> list[DesignCandidate]:
    """Generate deterministic rectangular massing options from validated inputs."""
    if count < 1:
        raise ValueError("count must be at least 1")

    build_w, build_d = _buildable_dimensions(constraints)
    site_area = constraints.site.width * constraints.site.depth
    max_footprint = site_area * constraints.zoning.max_site_coverage
    max_gfa = site_area * constraints.zoning.max_far
    program_gfa = _program_area(constraints)

    candidates: list[DesignCandidate] = []
    for index in range(count):
        scale = _candidate_scale(index, count)
        footprint = min(build_w * build_d * scale, max_footprint)
        footprint = max(1.0, footprint)

        required_storeys = max(1, int((program_gfa + footprint - 1e-9) // footprint))
        if program_gfa > footprint:
            required_storeys = int((program_gfa / footprint) + 0.999999)
        storeys = min(constraints.zoning.max_storeys, required_storeys)
        if max_gfa > 0:
            storeys = min(storeys, max(1, int(max_gfa / footprint)))
        storeys = max(1, storeys)

        gross_floor_area = footprint * storeys
        coverage = footprint / site_area
        far = gross_floor_area / site_area
        height = gross_floor_area / footprint * min(
            constraints.zoning.max_height / max(constraints.zoning.max_storeys, 1),
            constraints.zoning.max_height,
        )

        aspect = max(build_w, build_d) / max(min(build_w, build_d), 1e-9)
        regularity = max(0.0, min(1.0, 1.0 - abs(aspect - 1.5) / 3.0))
        target_fit = max(0.0, min(1.0, 1.0 - abs(gross_floor_area - max(program_gfa, 1.0)) / max(program_gfa, 1.0)))
        compliance = 1.0
        if coverage > constraints.zoning.max_site_coverage + 1e-9:
            compliance = 0.0
        if far > constraints.zoning.max_far + 1e-9:
            compliance = 0.0
        if height > constraints.zoning.max_height + 1e-9:
            compliance = 0.0

        candidate = DesignCandidate(
            name=f"Massing Option {index + 1:02d}",
            geometry={
                "type": "rectangular_massing",
                "footprint_width_m": round(build_w * scale, 3),
                "footprint_depth_m": round(build_d * scale, 3),
                "storeys": storeys,
                "orientation": "north_access" if constraints.site.north_access else "site_defined",
            },
            metrics={
                "site_area": round(site_area, 3),
                "footprint_area": round(footprint, 3),
                "gross_floor_area": round(gross_floor_area, 3),
                "site_coverage": round(coverage, 4),
                "far": round(far, 4),
                "storeys": storeys,
                "height_m": round(height, 3),
                "program_gross_area": round(program_gfa, 3),
                "program_fit": round(target_fit, 4),
                "structural_regularity": round(regularity, 4),
            },
            evaluation={
                "preliminary": True,
                "program_compliance": target_fit >= 0.95,
                "zoning_screening": compliance > 0,
            },
        )
        candidates.append(candidate)

    return candidates


__all__ = ["DesignCandidate", "generate_candidates"]
