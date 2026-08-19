"""
Tests for candidate generation.
"""

from architecture.generative_design.generator import (
    generate_candidates,
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
        ),
        zoning=ZoningConstraints(
            max_site_coverage=0.60,
            max_far=2.0,
            max_storeys=3,
        ),
        program=ProgramConstraints(
            rooms=[
                RoomRequirement(
                    name="Living",
                    area=30,
                ),
                RoomRequirement(
                    name="Bedroom",
                    area=15,
                    quantity=3,
                ),
            ]
        ),
    )


def test_generate_requested_number_of_candidates():
    constraints = make_constraints()

    candidates = generate_candidates(
        constraints,
        count=5,
    )

    assert len(candidates) == 5


def test_candidate_has_geometry():
    constraints = make_constraints()

    candidates = generate_candidates(
        constraints,
        count=1,
    )

    candidate = candidates[0]

    assert candidate.geometry
    assert candidate.geometry["type"] == (
        "rectangular_massing"
    )


def test_candidate_has_metrics():
    constraints = make_constraints()

    candidate = generate_candidates(
        constraints,
        count=1,
    )[0]

    assert "site_area" in candidate.metrics
    assert "footprint_area" in candidate.metrics
    assert "gross_floor_area" in candidate.metrics