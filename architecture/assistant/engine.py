"""Deterministic architecture decision-support engine.

This module deliberately has no Streamlit or LLM dependency. It turns a project
brief into traceable preliminary planning recommendations that can be consumed
by the Streamlit assistant and later by an LLM/RAG layer.

All code, zoning, accessibility and planning outputs are screening guidance.
Project-specific regulations and the applicable authority requirements must be
verified by the responsible architect/engineer before use for permitting or
construction.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import re
from typing import Iterable


@dataclass(frozen=True, slots=True)
class ArchitectureBrief:
    project_type: str = "Office"
    site_area_m2: float = 5000.0
    site_width_m: float = 50.0
    site_depth_m: float = 100.0
    front_setback_m: float = 6.0
    rear_setback_m: float = 4.0
    side_setback_m: float = 3.0
    max_far: float = 4.5
    max_height_m: float = 45.0
    target_occupants: int = 250
    area_per_person_m2: float = 12.0
    circulation_pct: float = 18.0
    max_storeys: int = 10
    north_angle_deg: float = 0.0

    def __post_init__(self) -> None:
        numeric_nonnegative = (
            "site_area_m2",
            "site_width_m",
            "site_depth_m",
            "front_setback_m",
            "rear_setback_m",
            "side_setback_m",
            "max_far",
            "max_height_m",
            "target_occupants",
            "area_per_person_m2",
            "circulation_pct",
            "max_storeys",
        )
        for field_name in numeric_nonnegative:
            if getattr(self, field_name) < 0:
                raise ValueError(f"{field_name} must be non-negative")
        if self.site_area_m2 <= 0 or self.site_width_m <= 0 or self.site_depth_m <= 0:
            raise ValueError("Site dimensions and area must be positive")
        if self.target_occupants <= 0:
            raise ValueError("target_occupants must be positive")
        if not 0 <= self.circulation_pct < 100:
            raise ValueError("circulation_pct must be between 0 and 100")
        if self.max_storeys < 1:
            raise ValueError("max_storeys must be at least 1")


@dataclass(frozen=True, slots=True)
class ArchitectureRecommendation:
    category: str
    finding: str
    action: str
    priority: str = "Medium"


@dataclass(frozen=True, slots=True)
class ArchitectureAssessment:
    brief: ArchitectureBrief
    buildable_width_m: float
    buildable_depth_m: float
    buildable_footprint_m2: float
    max_gfa_by_far_m2: float
    program_net_area_m2: float
    program_gross_area_m2: float
    feasible_storeys: int
    estimated_parking_spaces: int
    recommendations: tuple[ArchitectureRecommendation, ...]

    @property
    def coverage_pct(self) -> float:
        return 100.0 * self.buildable_footprint_m2 / self.brief.site_area_m2

    @property
    def far_used(self) -> float:
        return self.program_gross_area_m2 / self.brief.site_area_m2

    @property
    def height_used_m(self) -> float:
        return self.feasible_storeys * 3.5


class ArchitectureAssistant:
    """Traceable planning assistant that coordinates the architecture workflow."""

    KEYWORDS = {
        "site": ("site", "plot", "setback", "envelope", "land"),
        "program": ("program", "room", "space", "area", "occupancy"),
        "zoning": ("zoning", "far", "fsr", "height", "coverage", "parking"),
        "floor": ("floor", "layout", "core", "corridor", "grid"),
        "compliance": ("code", "compliance", "egress", "access", "fire", "ada"),
        "structural": ("beam", "column", "slab", "foundation", "structural", "load"),
        "generative": ("generate", "option", "concept", "variant", "optimize"),
    }

    def assess(self, brief: ArchitectureBrief) -> ArchitectureAssessment:
        width = max(0.0, brief.site_width_m - 2.0 * brief.side_setback_m)
        depth = max(0.0, brief.site_depth_m - brief.front_setback_m - brief.rear_setback_m)
        footprint = min(brief.site_area_m2, width * depth)
        max_gfa_far = brief.site_area_m2 * brief.max_far
        net_area = brief.target_occupants * brief.area_per_person_m2
        gross_area = net_area / max(0.01, 1.0 - brief.circulation_pct / 100.0)
        gfa_cap = min(max_gfa_far, footprint * brief.max_storeys)
        required_storeys = max(1, math.ceil(gross_area / max(1.0, footprint)))
        feasible_storeys = min(brief.max_storeys, int(brief.max_height_m // 3.5))
        parking = max(0, math.ceil(gross_area / 100.0 * 1.5))

        recommendations: list[ArchitectureRecommendation] = []
        if footprint <= 0:
            recommendations.append(ArchitectureRecommendation("Site", "Setbacks leave no buildable footprint.", "Revisit plot dimensions or setbacks before developing a layout.", "Critical"))
        if gross_area > gfa_cap:
            recommendations.append(ArchitectureRecommendation("Zoning", f"Indicative program needs {gross_area:,.0f} m² but the screening GFA capacity is {gfa_cap:,.0f} m².", "Reduce program, increase allowable FAR, or test a different site strategy.", "High"))
        if required_storeys > feasible_storeys:
            recommendations.append(ArchitectureRecommendation("Massing", f"The program needs about {required_storeys} storeys, above the screened limit of {feasible_storeys}.", "Reduce gross area, increase permitted height, or increase buildable footprint.", "High"))
        if brief.circulation_pct < 15:
            recommendations.append(ArchitectureRecommendation("Planning", "The circulation allowance is unusually tight for an early office/residential planning study.", "Validate corridors, stairs, lifts, lobbies and fire egress before freezing the program.", "Medium"))
        if brief.target_occupants >= 500:
            recommendations.append(ArchitectureRecommendation("Life Safety", f"Peak occupancy is {brief.target_occupants:,} persons.", "Run a dedicated egress and fire strategy using the adopted building code and authority requirements.", "High"))
        if brief.north_angle_deg % 360 not in (0, 180):
            recommendations.append(ArchitectureRecommendation("Environment", f"North axis is rotated {brief.north_angle_deg:.0f}° from the reference axis.", "Test solar exposure, glare, shading and façade orientation before selecting a preferred massing option.", "Medium"))
        if not recommendations:
            recommendations.append(ArchitectureRecommendation("Workflow", "The brief is internally consistent at screening level.", "Proceed to site planning, space programming, compliance review and structural concept design.", "Low"))

        return ArchitectureAssessment(
            brief=brief,
            buildable_width_m=width,
            buildable_depth_m=depth,
            buildable_footprint_m2=footprint,
            max_gfa_by_far_m2=max_gfa_far,
            program_net_area_m2=net_area,
            program_gross_area_m2=gross_area,
            feasible_storeys=max(1, feasible_storeys),
            estimated_parking_spaces=parking,
            recommendations=tuple(recommendations),
        )

    def respond(self, message: str, assessment: ArchitectureAssessment | None = None) -> str:
        """Return a concise, deterministic response to an architecture question."""
        text = message.strip()
        if not text:
            return "Describe the project, site, program, zoning or design problem you want me to assess."
        lower = text.casefold()
        intents = self._detect_intents(lower)

        if assessment is None:
            return "I can help with site planning, zoning, space programming, floor planning, compliance and generative design. Run an assessment first, then ask a specific question."

        if "site" in intents:
            return (f"Screening site envelope: {assessment.buildable_width_m:.1f} m × "
                    f"{assessment.buildable_depth_m:.1f} m, or {assessment.buildable_footprint_m2:,.0f} m². "
                    "This is a rectangular-envelope estimate, not a cadastral or GIS boundary solution.")
        if "program" in intents:
            return (f"The current program indicates {assessment.program_net_area_m2:,.0f} m² net and "
                    f"{assessment.program_gross_area_m2:,.0f} m² gross at the supplied circulation allowance. "
                    "The room schedule should be developed from actual room types and authority requirements.")
        if "zoning" in intents:
            return (f"Screening zoning capacity is {assessment.max_gfa_by_far_m2:,.0f} m² GFA at FAR "
                    f"{assessment.brief.max_far:.2f}. The current program uses about {assessment.far_used:.2f} FAR "
                    f"and {assessment.coverage_pct:.1f}% of the site as footprint.")
        if "compliance" in intents:
            return "Compliance is a verification workflow, not a fixed percentage score. Confirm the adopted code, occupancy, fire strategy, accessibility standard, egress limits and local amendments before treating a design as compliant."
        if "structural" in intents:
            return "The architecture workflow should hand a controlled design brief to Structural: geometry, grids, storeys, loads, material system and soil assumptions. Structural modules in IMAGINE provide preliminary screening, not a certified design."
        if "generative" in intents:
            return "Use the generative workflow after the brief is constrained. Compare options on footprint, GFA, circulation, daylight, adjacency, code constraints and structural regularity rather than selecting a visually attractive option alone."
        if "floor" in intents:
            return f"A preliminary floor strategy can target about {assessment.program_gross_area_m2 / assessment.feasible_storeys:,.0f} m² gross per storey across {assessment.feasible_storeys} screened storeys. Core, egress and structural-grid sizing still require project-specific design."

        top = assessment.recommendations[0]
        return f"My highest-priority finding is {top.finding} Next action: {top.action}"

    def _detect_intents(self, message: str) -> set[str]:
        return {intent for intent, words in self.KEYWORDS.items() if any(re.search(rf"\b{re.escape(word)}\b", message) for word in words)}


__all__ = ["ArchitectureBrief", "ArchitectureRecommendation", "ArchitectureAssessment", "ArchitectureAssistant"]
