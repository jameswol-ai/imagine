"""
IMAGINE
Generative Design Constraints

Constraint normalization, deterministic validation, and
geometric calculations used by the generative-design engine.
"""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from pydantic import ValidationError

from .schemas import (
    ComplianceConstraints,
    ConstraintValidationResult,
    DesignConstraints,
    ProgramConstraints,
    SiteConstraints,
    ZoningConstraints,
)


# =====================================================================
# CONSTANTS
# =====================================================================

MIN_SITE_DIMENSION = 1.0
MIN_ROOM_AREA = 0.1

SETBACK_FIELDS = (
    "setback_front",
    "setback_rear",
    "setback_left",
    "setback_right",
)


# =====================================================================
# GEOMETRY VALUE OBJECT
# =====================================================================

@dataclass(frozen=True)
class BuildableSite:
    """Calculated rectangular buildable site."""

    width: float
    depth: float
    area: float


# =====================================================================
# NORMALIZATION
# =====================================================================

def normalize_constraints(
    constraints: DesignConstraints | Mapping[str, Any],
) -> DesignConstraints:
    """
    Normalize incoming data into DesignConstraints.

    No database access occurs here.
    """

    if isinstance(
        constraints,
        DesignConstraints,
    ):
        return DesignConstraints.model_validate(
            constraints.model_dump(
                mode="python"
            )
        )

    if not isinstance(
        constraints,
        Mapping,
    ):
        raise ValueError(
            "Constraints must be a DesignConstraints instance "
            "or a mapping."
        )

    payload = deepcopy(
        dict(constraints)
    )

    try:
        return DesignConstraints.model_validate(
            payload
        )
    except ValidationError as exc:
        raise ValueError(
            _format_validation_errors(exc)
        ) from exc


# =====================================================================
# NORMALIZE + VALIDATE
# =====================================================================

def normalize_and_validate_constraints(
    constraints: DesignConstraints | Mapping[str, Any],
) -> tuple[
    DesignConstraints | None,
    ConstraintValidationResult,
]:
    """
    Normalize and validate constraints.

    Returns:

        (normalized_constraints, validation_result)

    Structural validation failures return ``None`` for the normalized
    constraints.
    """

    try:
        normalized = normalize_constraints(
            constraints
        )
    except ValueError as exc:
        return (
            None,
            ConstraintValidationResult(
                valid=False,
                errors=[
                    str(exc)
                ],
                warnings=[],
            ),
        )

    result = validate_constraints(
        normalized
    )

    return normalized, result


# =====================================================================
# VALIDATION
# =====================================================================

def validate_constraints(
    constraints: DesignConstraints | Mapping[str, Any],
) -> ConstraintValidationResult:
    """Validate normalized generative-design constraints."""

    try:
        normalized = normalize_constraints(
            constraints
        )
    except ValueError as exc:
        return ConstraintValidationResult(
            valid=False,
            errors=[
                str(exc)
            ],
            warnings=[],
        )

    errors: list[str] = []
    warnings: list[str] = []

    _validate_site(
        normalized.site,
        errors,
        warnings,
    )

    _validate_zoning(
        normalized.zoning,
        errors,
        warnings,
    )

    _validate_program(
        normalized.program,
        errors,
        warnings,
    )

    _validate_compliance(
        normalized.compliance,
        errors,
        warnings,
    )

    _validate_cross_constraints(
        normalized,
        errors,
        warnings,
    )

    return ConstraintValidationResult(
        valid=not errors,
        errors=_sort_messages(errors),
        warnings=_sort_messages(warnings),
    )


# =====================================================================
# SITE
# =====================================================================

def _validate_site(
    site: SiteConstraints,
    errors: list[str],
    warnings: list[str],
) -> None:

    if site.width < MIN_SITE_DIMENSION:
        errors.append(
            "site.width must be at least 1."
        )

    if site.depth < MIN_SITE_DIMENSION:
        errors.append(
            "site.depth must be at least 1."
        )

    for field in SETBACK_FIELDS:

        value = getattr(
            site,
            field,
        )

        if value < 0:
            errors.append(
                f"site.{field} cannot be negative."
            )

    buildable_width = (
        site.width
        - site.setback_left
        - site.setback_right
    )

    buildable_depth = (
        site.depth
        - site.setback_front
        - site.setback_rear
    )

    if buildable_width <= 0:
        errors.append(
            "site setbacks leave no positive buildable width."
        )

    if buildable_depth <= 0:
        errors.append(
            "site setbacks leave no positive buildable depth."
        )

    if (
        buildable_width > 0
        and buildable_depth > 0
    ):
        gross_area = (
            site.width * site.depth
        )

        buildable_area = (
            buildable_width * buildable_depth
        )

        if (
            gross_area > 0
            and buildable_area / gross_area < 0.25
        ):
            warnings.append(
                "site setbacks leave less than 25% of the "
                "gross site area available for development."
            )

    if not site.north_access:
        warnings.append(
            "north_access is disabled; site orientation "
            "constraints should be considered during generation."
        )


# =====================================================================
# ZONING
# =====================================================================

def _validate_zoning(
    zoning: ZoningConstraints,
    errors: list[str],
    warnings: list[str],
) -> None:

    if not (
        0 < zoning.max_site_coverage <= 1
    ):
        errors.append(
            "zoning.max_site_coverage must be greater than 0 "
            "and no greater than 1."
        )

    if zoning.max_far <= 0:
        errors.append(
            "zoning.max_far must be greater than 0."
        )

    if zoning.max_height <= 0:
        errors.append(
            "zoning.max_height must be greater than 0."
        )

    if zoning.max_storeys < 1:
        errors.append(
            "zoning.max_storeys must be at least 1."
        )

    if zoning.max_site_coverage > 0.80:
        warnings.append(
            "zoning.max_site_coverage exceeds 80%; verify "
            "local planning requirements."
        )

    if zoning.max_far > 5:
        warnings.append(
            "zoning.max_far exceeds 5.0; verify the applicable "
            "planning requirements."
        )

    if zoning.max_height > 45:
        warnings.append(
            "zoning.max_height exceeds 45 m; additional "
            "structural and regulatory requirements may apply."
        )

    if zoning.max_storeys > 12:
        warnings.append(
            "zoning.max_storeys exceeds 12; high-rise design "
            "requirements may apply."
        )


# =====================================================================
# PROGRAM
# =====================================================================

def _validate_program(
    program: ProgramConstraints,
    errors: list[str],
    warnings: list[str],
) -> None:

    if not (
        0 <= program.circulation_ratio <= 1
    ):
        errors.append(
            "program.circulation_ratio must be between 0 and 1."
        )

    if program.circulation_ratio > 0.40:
        warnings.append(
            "program.circulation_ratio exceeds 40%; verify "
            "the required circulation allowance."
        )

    seen_names: set[str] = set()

    for index, room in enumerate(
        program.rooms,
        start=1,
    ):

        normalized_name = (
            room.name.strip().lower()
        )

        if not normalized_name:
            errors.append(
                f"program.rooms[{index}].name cannot be empty."
            )

        if normalized_name in seen_names:
            warnings.append(
                f"program.rooms[{index}].name duplicates "
                "another room requirement."
            )

        seen_names.add(
            normalized_name
        )

        if room.area < MIN_ROOM_AREA:
            errors.append(
                f"program.rooms[{index}].area must be at least 0.1."
            )

        if room.quantity < 1:
            errors.append(
                f"program.rooms[{index}].quantity must be at least 1."
            )

    if not program.rooms:
        warnings.append(
            "program.rooms is empty; generated candidates "
            "will have no explicit room-program requirements."
        )


# =====================================================================
# COMPLIANCE
# =====================================================================

def _validate_compliance(
    compliance: ComplianceConstraints,
    errors: list[str],
    warnings: list[str],
) -> None:

    if compliance.minimum_egress_width <= 0:
        errors.append(
            "compliance.minimum_egress_width must be greater than 0."
        )

    if compliance.minimum_egress_width < 0.8:
        warnings.append(
            "compliance.minimum_egress_width is below 0.8 m; "
            "verify the applicable fire-safety requirements."
        )

    if (
        compliance.accessibility_required
        and compliance.minimum_egress_width < 1.1
    ):
        warnings.append(
            "accessibility is required while minimum egress width "
            "is below 1.1 m; verify the applicable accessibility "
            "standard."
        )

    if not compliance.fire_separation_required:
        warnings.append(
            "fire separation is disabled; the generated design "
            "must not be treated as fire-code compliant."
        )


# =====================================================================
# CROSS CONSTRAINTS
# =====================================================================

def _validate_cross_constraints(
    constraints: DesignConstraints,
    errors: list[str],
    warnings: list[str],
) -> None:

    buildable = calculate_buildable_site(
        constraints
    )

    required_area = calculate_required_gross_area(
        constraints
    )

    site_area = (
        constraints.site.width
        * constraints.site.depth
    )

    maximum_gross_area = (
        site_area
        * constraints.zoning.max_far
    )

    if (
        required_area > maximum_gross_area
    ):
        errors.append(
            "program total gross area exceeds the maximum "
            "gross floor area permitted by the configured FAR."
        )

    maximum_footprint = (
        buildable.area
        * constraints.zoning.max_site_coverage
    )

    if maximum_footprint <= 0:
        errors.append(
            "no positive building footprint is available."
        )

    if maximum_footprint > 0:
        required_storeys = (
            required_area
            / maximum_footprint
        )

        if (
            required_storeys
            > constraints.zoning.max_storeys
        ):
            errors.append(
                "the requested program requires more storeys "
                "than zoning.max_storeys permits."
            )

        elif (
            required_storeys
            > constraints.zoning.max_storeys * 0.85
        ):
            warnings.append(
                "the requested program is close to the maximum "
                "permitted storey capacity."
            )


# =====================================================================
# CALCULATIONS USED BY GENERATOR
# =====================================================================

def calculate_buildable_site(
    constraints: DesignConstraints,
) -> BuildableSite:
    """
    Calculate the rectangular site remaining after setbacks.
    """

    width = (
        constraints.site.width
        - constraints.site.setback_left
        - constraints.site.setback_right
    )

    depth = (
        constraints.site.depth
        - constraints.site.setback_front
        - constraints.site.setback_rear
    )

    if width <= 0:
        raise ValueError(
            "Site setbacks leave no positive buildable width."
        )

    if depth <= 0:
        raise ValueError(
            "Site setbacks leave no positive buildable depth."
        )

    return BuildableSite(
        width=width,
        depth=depth,
        area=width * depth,
    )


def calculate_required_gross_area(
    constraints: DesignConstraints,
) -> float:
    """
    Calculate required gross floor area.

    Room areas are multiplied by quantity and then increased by
    the configured circulation ratio.
    """

    room_area = sum(
        room.area * room.quantity
        for room in constraints.program.rooms
    )

    return room_area * (
        1.0
        + constraints.program.circulation_ratio
    )


# =====================================================================
# SUMMARY
# =====================================================================

def constraint_summary(
    constraints: DesignConstraints | Mapping[str, Any],
) -> dict[str, Any]:

    normalized = normalize_constraints(
        constraints
    )

    buildable = calculate_buildable_site(
        normalized
    )

    required_area = calculate_required_gross_area(
        normalized
    )

    return {
        "project_id": (
            str(normalized.project_id)
            if normalized.project_id is not None
            else None
        ),
        "site": {
            "width": normalized.site.width,
            "depth": normalized.site.depth,
            "gross_area": (
                normalized.site.width
                * normalized.site.depth
            ),
            "buildable_width": buildable.width,
            "buildable_depth": buildable.depth,
            "buildable_area": buildable.area,
        },
        "zoning": {
            "max_site_coverage": (
                normalized.zoning.max_site_coverage
            ),
            "max_far": normalized.zoning.max_far,
            "max_height": normalized.zoning.max_height,
            "max_storeys": normalized.zoning.max_storeys,
        },
        "program": {
            "room_types": len(
                normalized.program.rooms
            ),
            "room_count": sum(
                room.quantity
                for room in normalized.program.rooms
            ),
            "room_area": sum(
                room.area * room.quantity
                for room in normalized.program.rooms
            ),
            "required_gross_area": required_area,
            "circulation_ratio": (
                normalized.program.circulation_ratio
            ),
        },
        "compliance": {
            "minimum_egress_width": (
                normalized.compliance.minimum_egress_width
            ),
            "accessibility_required": (
                normalized.compliance.accessibility_required
            ),
            "fire_separation_required": (
                normalized.compliance.fire_separation_required
            ),
        },
    }


# =====================================================================
# UUID
# =====================================================================

def validate_project_id(
    project_id: UUID | str | None,
) -> UUID | None:

    if project_id is None:
        return None

    if isinstance(
        project_id,
        UUID,
    ):
        return project_id

    try:
        return UUID(
            str(project_id)
        )
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise ValueError(
            "project_id must be a valid UUID."
        ) from exc


# =====================================================================
# ERROR FORMATTING
# =====================================================================

def _format_validation_errors(
    exc: ValidationError,
) -> str:

    messages: list[str] = []

    for error in exc.errors():

        location = ".".join(
            str(part)
            for part in error.get(
                "loc",
                (),
            )
        )

        message = str(
            error.get(
                "msg",
                "Invalid value.",
            )
        )

        if location:
            messages.append(
                f"{location}: {message}"
            )
        else:
            messages.append(
                message
            )

    return "; ".join(
        _sort_messages(
            messages
        )
    )


def _sort_messages(
    messages: list[str],
) -> list[str]:

    return sorted(
        set(messages),
        key=str.casefold,
    )