"""
IMAGINE
Generative Design Constraints

Constraint normalization and validation for the generative-design
engine.

This module is intentionally independent of SQLAlchemy and database
repositories. It converts incoming project/design information into a
validated DesignConstraints object that can safely be consumed by the
generator and scoring layers.
"""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any
from uuid import UUID

from pydantic import ValidationError

from .schemas import (
    ComplianceConstraints,
    ConstraintValidationResult,
    DesignConstraints,
    ProgramConstraints,
    RoomRequirement,
    SiteConstraints,
    ZoningConstraints,
)


# =====================================================================
# CONSTANTS
# =====================================================================

MIN_SITE_DIMENSION = 1.0
MIN_ROOM_AREA = 0.1
MAX_CIRCULATION_RATIO = 1.0
MIN_CIRCULATION_RATIO = 0.0

DEFAULT_MAX_SITE_COVERAGE = 0.60
DEFAULT_MAX_FAR = 2.0
DEFAULT_MAX_HEIGHT = 15.0
DEFAULT_MAX_STOREYS = 3

DEFAULT_MIN_EGRESS_WIDTH = 1.1

SETBACK_FIELDS = (
    "setback_front",
    "setback_rear",
    "setback_left",
    "setback_right",
)


# =====================================================================
# PUBLIC API
# =====================================================================

def normalize_constraints(
    constraints: DesignConstraints | Mapping[str, Any],
) -> DesignConstraints:
    """
    Normalize incoming constraints into DesignConstraints.

    Parameters
    ----------
    constraints:
        Either an existing DesignConstraints instance or a mapping
        containing the fields required to construct one.

    Returns
    -------
    DesignConstraints
        A validated, normalized constraint object.

    Raises
    ------
    ValueError
        If the supplied structure cannot be converted into
        DesignConstraints.
    """

    if isinstance(
        constraints,
        DesignConstraints,
    ):
        # Re-validation creates a deterministic normalized copy and
        # prevents callers from accidentally mutating the object held
        # by the generation pipeline.
        return DesignConstraints.model_validate(
            constraints.model_dump(
                mode="python",
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

    normalized_input = deepcopy(
        dict(constraints)
    )

    try:
        return DesignConstraints.model_validate(
            normalized_input
        )
    except ValidationError as exc:
        raise ValueError(
            _format_pydantic_errors(exc)
        ) from exc


def validate_constraints(
    constraints: DesignConstraints | Mapping[str, Any],
) -> ConstraintValidationResult:
    """
    Normalize and validate generative-design constraints.

    Validation is deterministic. Errors and warnings are returned in
    a stable order so callers and tests can reliably compare results.

    Pydantic structural errors are returned as validation errors rather
    than raised exceptions.
    """

    try:
        normalized = normalize_constraints(
            constraints
        )
    except ValueError as exc:
        return ConstraintValidationResult(
            valid=False,
            errors=[
                str(exc),
            ],
            warnings=[],
        )

    errors: list[str] = []
    warnings: list[str] = []

    # ---------------------------------------------------------------
    # Site
    # ---------------------------------------------------------------

    _validate_site(
        normalized.site,
        errors,
        warnings,
    )

    # ---------------------------------------------------------------
    # Zoning
    # ---------------------------------------------------------------

    _validate_zoning(
        normalized.zoning,
        errors,
        warnings,
    )

    # ---------------------------------------------------------------
    # Program
    # ---------------------------------------------------------------

    _validate_program(
        normalized.program,
        normalized.site,
        errors,
        warnings,
    )

    # ---------------------------------------------------------------
    # Compliance
    # ---------------------------------------------------------------

    _validate_compliance(
        normalized.compliance,
        errors,
        warnings,
    )

    # ---------------------------------------------------------------
    # Cross-domain validation
    # ---------------------------------------------------------------

    _validate_cross_constraints(
        normalized,
        errors,
        warnings,
    )

    # ---------------------------------------------------------------
    # Deterministic ordering
    # ---------------------------------------------------------------

    errors = _sort_messages(errors)
    warnings = _sort_messages(warnings)

    return ConstraintValidationResult(
        valid=not errors,
        errors=errors,
        warnings=warnings,
    )


def normalize_and_validate_constraints(
    constraints: DesignConstraints | Mapping[str, Any],
) -> tuple[
    DesignConstraints | None,
    ConstraintValidationResult,
]:
    """
    Normalize and validate constraints in one operation.

    Returns
    -------
    tuple
        ``(normalized_constraints, validation_result)``

        If structural normalization fails, the normalized value is
        ``None``.
    """

    try:
        normalized = normalize_constraints(
            constraints
        )
    except ValueError as exc:
        result = ConstraintValidationResult(
            valid=False,
            errors=[
                str(exc),
            ],
            warnings=[],
        )

        return None, result

    result = validate_constraints(
        normalized
    )

    if not result.valid:
        return normalized, result

    return normalized, result


def constraint_summary(
    constraints: DesignConstraints | Mapping[str, Any],
) -> dict[str, Any]:
    """
    Produce a deterministic summary suitable for UI/API display.

    The summary contains normalized values only and does not contain
    database objects.
    """

    normalized = normalize_constraints(
        constraints
    )

    total_program_area = sum(
        room.area * room.quantity
        for room in normalized.program.rooms
    )

    required_room_count = sum(
        room.quantity
        for room in normalized.program.rooms
        if room.required
    )

    total_room_count = sum(
        room.quantity
        for room in normalized.program.rooms
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
            "area": (
                normalized.site.width
                * normalized.site.depth
            ),
            "north_access": normalized.site.north_access,
            "setbacks": {
                field: getattr(
                    normalized.site,
                    field,
                )
                for field in SETBACK_FIELDS
            },
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
            "room_count": total_room_count,
            "required_room_count": required_room_count,
            "total_room_area": total_program_area,
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
# SITE VALIDATION
# =====================================================================

def _validate_site(
    site: SiteConstraints,
    errors: list[str],
    warnings: list[str],
) -> None:
    """
    Validate physical site dimensions and setbacks.
    """

    if site.width < MIN_SITE_DIMENSION:
        errors.append(
            "site.width must be at least "
            f"{MIN_SITE_DIMENSION:g}."
        )

    if site.depth < MIN_SITE_DIMENSION:
        errors.append(
            "site.depth must be at least "
            f"{MIN_SITE_DIMENSION:g}."
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
            "site setbacks leave no positive "
            "buildable site width."
        )

    if buildable_depth <= 0:
        errors.append(
            "site setbacks leave no positive "
            "buildable site depth."
        )

    if (
        site.setback_left
        + site.setback_right
        >= site.width
    ):
        errors.append(
            "left and right setbacks must be smaller "
            "than total site width."
        )

    if (
        site.setback_front
        + site.setback_rear
        >= site.depth
    ):
        errors.append(
            "front and rear setbacks must be smaller "
            "than total site depth."
        )

    buildable_area = (
        buildable_width
        * buildable_depth
    )

    site_area = site.width * site.depth

    if (
        site_area > 0
        and buildable_area / site_area < 0.25
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
# ZONING VALIDATION
# =====================================================================

def _validate_zoning(
    zoning: ZoningConstraints,
    errors: list[str],
    warnings: list[str],
) -> None:
    """
    Validate zoning constraints.
    """

    if not (
        0 < zoning.max_site_coverage <= 1
    ):
        errors.append(
            "zoning.max_site_coverage must be "
            "greater than 0 and no greater than 1."
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
            "zoning.max_site_coverage exceeds 80%; "
            "site planning should verify local planning requirements."
        )

    if zoning.max_far > 5:
        warnings.append(
            "zoning.max_far exceeds 5.0; verify the applicable "
            "planning authority requirements."
        )

    if zoning.max_height > 45:
        warnings.append(
            "zoning.max_height exceeds 45 m; structural, fire, "
            "vertical circulation, and regulatory requirements "
            "should be reviewed."
        )

    if zoning.max_storeys > 12:
        warnings.append(
            "zoning.max_storeys exceeds 12; high-rise design "
            "requirements may apply."
        )


# =====================================================================
# PROGRAM VALIDATION
# =====================================================================

def _validate_program(
    program: ProgramConstraints,
    site: SiteConstraints,
    errors: list[str],
    warnings: list[str],
) -> None:
    """
    Validate room-program requirements and circulation.
    """

    if not (
        MIN_CIRCULATION_RATIO
        <= program.circulation_ratio
        <= MAX_CIRCULATION_RATIO
    ):
        errors.append(
            "program.circulation_ratio must be between "
            "0 and 1."
        )

    if (
        program.circulation_ratio > 0.40
    ):
        warnings.append(
            "program.circulation_ratio exceeds 40%; "
            "verify that the program requires this level "
            "of circulation space."
        )

    if not program.rooms:
        warnings.append(
            "program.rooms is empty; generated candidates "
            "will have no explicit room-program requirements."
        )

        return

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
                f"program.rooms[{index}].area must be at least "
                f"{MIN_ROOM_AREA:g}."
            )

        if room.quantity < 1:
            errors.append(
                f"program.rooms[{index}].quantity must be at least 1."
            )

    total_room_area = sum(
        room.area * room.quantity
        for room in program.rooms
    )

    total_required_area = sum(
        room.area * room.quantity
        for room in program.rooms
        if room.required
    )

    site_area = (
        site.width
        * site.depth
    )

    if (
        site_area > 0
        and total_required_area > site_area
    ):
        warnings.append(
            "required room area exceeds gross site area; "
            "multi-storey development will be required."
        )

    if (
        total_room_area > 0
        and total_room_area / site_area > 5
    ):
        warnings.append(
            "total room area exceeds five times the gross "
            "site area; verify that the permitted FAR can "
            "accommodate the requested program."
        )


# =====================================================================
# COMPLIANCE VALIDATION
# =====================================================================

def _validate_compliance(
    compliance: ComplianceConstraints,
    errors: list[str],
    warnings: list[str],
) -> None:
    """
    Validate high-level compliance requirements.
    """

    if compliance.minimum_egress_width <= 0:
        errors.append(
            "compliance.minimum_egress_width must be greater "
            "than 0."
        )

    if compliance.minimum_egress_width < 0.8:
        warnings.append(
            "compliance.minimum_egress_width is below 0.8 m; "
            "verify the applicable occupancy and fire-safety code."
        )

    if (
        compliance.minimum_egress_width > 3
    ):
        warnings.append(
            "compliance.minimum_egress_width exceeds 3 m; "
            "verify whether the value represents a single egress "
            "path or an aggregate requirement."
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

    if (
        not compliance.fire_separation_required
    ):
        warnings.append(
            "fire separation is disabled; the generated design "
            "must not be treated as fire-code compliant without "
            "additional verification."
        )


# =====================================================================
# CROSS-CONSTRAINT VALIDATION
# =====================================================================

def _validate_cross_constraints(
    constraints: DesignConstraints,
    errors: list[str],
    warnings: list[str],
) -> None:
    """
    Validate relationships between site, zoning, program, and
    compliance constraints.
    """

    site = constraints.site
    zoning = constraints.zoning
    program = constraints.program

    gross_site_area = (
        site.width
        * site.depth
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

    buildable_area = (
        buildable_width
        * buildable_depth
    )

    maximum_footprint = (
        gross_site_area
        * zoning.max_site_coverage
    )

    effective_footprint = min(
        buildable_area,
        maximum_footprint,
    )

    maximum_gross_floor_area = (
        gross_site_area
        * zoning.max_far
    )

    total_program_area = sum(
        room.area * room.quantity
        for room in program.rooms
    )

    if (
        total_program_area > 0
        and maximum_gross_floor_area > 0
        and total_program_area
        > maximum_gross_floor_area
    ):
        errors.append(
            "program total room area exceeds the maximum "
            "gross floor area permitted by the configured FAR."
        )

    if (
        effective_footprint <= 0
    ):
        errors.append(
            "no positive building footprint is available "
            "after applying site setbacks and coverage."
        )

    if (
        effective_footprint > 0
        and total_program_area > 0
    ):
        required_storey_equivalent = (
            total_program_area
            * (1 + program.circulation_ratio)
            / effective_footprint
        )

        if (
            required_storey_equivalent
            > zoning.max_storeys
        ):
            errors.append(
                "the requested program requires more storeys "
                "than the configured zoning.max_storeys."
            )

        elif (
            required_storey_equivalent
            > zoning.max_storeys * 0.85
        ):
            warnings.append(
                "the requested program is close to the maximum "
                "permitted storey capacity."
            )


# =====================================================================
# PYDANTIC ERROR FORMATTING
# =====================================================================

def _format_pydantic_errors(
    exc: ValidationError,
) -> str:
    """
    Convert Pydantic validation errors into a deterministic string.
    """

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

    messages = _sort_messages(
        messages
    )

    return "; ".join(
        messages
    )


# =====================================================================
# DETERMINISTIC MESSAGE ORDERING
# =====================================================================

def _sort_messages(
    messages: list[str],
) -> list[str]:
    """
    Return unique messages in deterministic lexical order.
    """

    return sorted(
        set(messages),
        key=lambda value: value.casefold(),
    )


# =====================================================================
# UUID VALIDATION HELPER
# =====================================================================

def validate_project_id(
    project_id: UUID | str | None,
) -> UUID | None:
    """
    Normalize a project identifier to UUID.

    This helper deliberately does not access the database.
    """

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
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "project_id must be a valid UUID."
        ) from exc