"""
IMAGINE
Generative Design Constraint Engine
"""

from __future__ import annotations

from dataclasses import dataclass

from .schemas import (
    ConstraintValidationResult,
    DesignConstraints,
)


@dataclass(frozen=True)
class NormalizedSite:
    """Buildable site dimensions."""

    width: float
    depth: float
    area: float


def calculate_buildable_site(
    constraints: DesignConstraints,
) -> NormalizedSite:
    """Calculate the usable site envelope."""

    site = constraints.site

    width = (
        site.width
        - site.setback_left
        - site.setback_right
    )

    depth = (
        site.depth
        - site.setback_front
        - site.setback_rear
    )

    return NormalizedSite(
        width=max(width, 0),
        depth=max(depth, 0),
        area=max(width, 0) * max(depth, 0),
    )


def calculate_program_area(
    constraints: DesignConstraints,
) -> float:
    """Calculate total net programmed area."""

    return sum(
        room.area * room.quantity
        for room in constraints.program.rooms
    )


def calculate_required_gross_area(
    constraints: DesignConstraints,
) -> float:
    """Convert net program area to estimated gross area."""

    net_area = calculate_program_area(
        constraints
    )

    return net_area * (
        1 + constraints.program.circulation_ratio
    )


def validate_constraints(
    constraints: DesignConstraints,
) -> ConstraintValidationResult:
    """Validate the normalized design constraints."""

    errors: list[str] = []
    warnings: list[str] = []

    buildable = calculate_buildable_site(
        constraints
    )

    if buildable.width <= 0:
        errors.append(
            "Setbacks leave no buildable site width."
        )

    if buildable.depth <= 0:
        errors.append(
            "Setbacks leave no buildable site depth."
        )

    if buildable.area <= 0:
        errors.append(
            "The resulting buildable site area is zero."
        )

    required_gross = calculate_required_gross_area(
        constraints
    )

    maximum_floor_area = (
        buildable.area
        * constraints.zoning.max_far
    )

    if required_gross > maximum_floor_area:
        errors.append(
            "The required building program exceeds "
            "the maximum permitted floor area."
        )

    maximum_footprint = (
        buildable.area
        * constraints.zoning.max_site_coverage
    )

    if required_gross > maximum_footprint:
        warnings.append(
            "The program cannot fit on one floor "
            "within the site coverage limit. "
            "Multiple storeys may be required."
        )

    if (
        constraints.zoning.max_storeys == 1
        and required_gross > maximum_footprint
    ):
        errors.append(
            "The program requires multiple storeys, "
            "but zoning allows only one."
        )

    if not constraints.program.rooms:
        errors.append(
            "At least one room requirement is required."
        )

    if (
        constraints.compliance.accessibility_required
        and constraints.compliance.minimum_egress_width <= 0
    ):
        errors.append(
            "Accessibility is required but the "
            "minimum egress width is invalid."
        )

    return ConstraintValidationResult(
        valid=not errors,
        errors=errors,
        warnings=warnings,
    )