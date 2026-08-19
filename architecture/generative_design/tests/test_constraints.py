"""
Tests for generative design constraints.
"""

from architecture.generative_design.constraints import (
    calculate_buildable_site,
    calculate_program_area,
    calculate_required_gross_area,
    validate_constraints,
)
from architecture.generative_design.schemas import (
    DesignConstraints,
    ProgramConstraints,
    RoomRequirement,
    SiteConstraints,
    ZoningConstraints,
)


def make_constraints():
    return DesignConstraints(
        site=SiteConstraints(
            width=30,
            depth=40,
            setback_front=5,
            setback_rear=3,
            setback_left=3,
            setback_right=3,
        ),
        zoning=ZoningConstraints(
            max_site_coverage=0.60,
            max_far=2.0,
            max_storeys=3,
        ),
        program=ProgramConstraints(
            circulation_ratio=0.20,
            rooms=[
                RoomRequirement(
                    name="Bedroom",
                    area=15,
                    quantity=2,
                ),
                RoomRequirement(
                    name="Kitchen",
                    area=10,
                ),
            ],
        ),
    )


def test_buildable_site():
    constraints = make_constraints()

    result = calculate_buildable_site(
        constraints
    )

    assert result.width == 24
    assert result.depth == 32
    assert result.area == 768


def test_program_area():
    constraints = make_constraints()

    assert calculate_program_area(
        constraints
    ) == 40


def test_required_gross_area():
    constraints = make_constraints()

    assert calculate_required_gross_area(
        constraints
    ) == 48


def test_valid_constraints():
    constraints = make_constraints()

    result = validate_constraints(
        constraints
    )

    assert result.valid is True
    assert result.errors == []


def test_invalid_buildable_site():
    constraints = make_constraints()

    constraints.site.setback_left = 20
    constraints.site.setback_right = 20

    result = validate_constraints(
        constraints
    )

    assert result.valid is False
    assert any(
        "width" in error.lower()
        for error in result.errors
    )