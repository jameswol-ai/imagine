"""Deterministic architecture standards comparison engine.

Values in this module are reference design benchmarks, not a substitute for the
adopted jurisdictional code, project brief, authority approval, or professional
review. Standards change and many requirements depend on occupancy, building
height, evacuation strategy and other project-specific conditions.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Requirement:
    category: str
    item: str
    value: float | None
    unit: str
    basis: str
    notes: str = ""


@dataclass(frozen=True, slots=True)
class StandardProfile:
    name: str
    jurisdiction: str
    description: str
    requirements: tuple[Requirement, ...]


STANDARD_PROFILES: tuple[StandardProfile, ...] = (
    StandardProfile(
        name="Universal Accessibility Reference",
        jurisdiction="International reference",
        description="Accessibility benchmarks derived from widely used accessible-route principles; verify the adopted local accessibility standard.",
        requirements=(
            Requirement("Circulation", "Accessible route clear width", 915, "mm", "2010 ADA 403.5.1", "36 in minimum in typical accessible-route conditions."),
            Requirement("Circulation", "Accessible route turning width", 1220, "mm", "2010 ADA 403.5.2", "48 in clear at the cited 180-degree turn condition."),
            Requirement("Doors", "Typical accessible clear opening", 815, "mm", "2010 ADA 404.2.3", "32 in minimum clear opening; door configuration matters."),
        ),
    ),
    StandardProfile(
        name="UK Building Regulations Reference",
        jurisdiction="England",
        description="Reference points from Approved Documents. Final values depend on building type, occupancy and applicable edition/amendments.",
        requirements=(
            Requirement("Stairs", "Common/firefighting stair width", 1100, "mm", "Approved Document B", "1100 mm is cited for firefighting stairs and specified common-stair cases."),
            Requirement("Stairs", "Small escape stair reference", 800, "mm", "Approved Document B Table 3.1", "A lower value is listed for certain stairs serving up to 50 people; accessibility may require more."),
            Requirement("Stairs", "Public-building central handrail trigger", 2000, "mm", "Approved Document B", "Stairs over 2000 mm wide should have a central handrail."),
        ),
    ),
    StandardProfile(
        name="IMAGINE Planning Benchmark",
        jurisdiction="Project-neutral",
        description="Configurable early-stage planning benchmarks used only for concept generation when an adopted code has not yet been selected.",
        requirements=(
            Requirement("Rooms", "Minimum planning room area", 9, "m²", "IMAGINE benchmark", "Concept-stage benchmark; set project-specific room schedules before design development."),
            Requirement("Circulation", "Primary corridor width", 1500, "mm", "IMAGINE benchmark", "Planning benchmark intended to provide comfortable two-way circulation."),
            Requirement("Stairs", "Concept stair clear width", 1200, "mm", "IMAGINE benchmark", "Concept benchmark only; egress capacity and local requirements govern."),
            Requirement("Doors", "Concept internal door clear width", 900, "mm", "IMAGINE benchmark", "Concept benchmark; accessibility and occupancy requirements govern."),
            Requirement("Ceiling", "Concept habitable room height", 2700, "mm", "IMAGINE benchmark", "Not a code minimum."),
        ),
    ),
)


def get_standard_profile(name: str) -> StandardProfile:
    """Return a named profile."""
    for profile in STANDARD_PROFILES:
        if profile.name == name:
            return profile
    raise KeyError(f"Unknown standards profile: {name}")


def compare_standard_requirements(
    category: str,
    item: str,
    profiles: tuple[StandardProfile, ...] = STANDARD_PROFILES,
) -> list[dict[str, object]]:
    """Return matching requirements from multiple standards for comparison."""
    rows: list[dict[str, object]] = []
    for profile in profiles:
        for req in profile.requirements:
            if req.category == category and req.item == item:
                rows.append({
                    "Standard": profile.name,
                    "Jurisdiction": profile.jurisdiction,
                    "Requirement": req.item,
                    "Value": req.value,
                    "Unit": req.unit,
                    "Basis": req.basis,
                    "Notes": req.notes,
                })
    return rows


__all__ = ["Requirement", "StandardProfile", "STANDARD_PROFILES", "get_standard_profile", "compare_standard_requirements"]
