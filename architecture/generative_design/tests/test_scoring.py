"""
Tests for design scoring and ranking.
"""

from architecture.generative_design.generator import (
    DesignCandidate,
)
from architecture.generative_design.schemas import (
    DesignConstraints,
    ProgramConstraints,
    RoomRequirement,
    SiteConstraints,
    ZoningConstraints,
)
from architecture.generative_design.scoring import (
    score_and_rank,
    score_candidate,
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
            ]
        ),
    )


def make_candidate(
    name: str,
    gross_area: float,
):
    return DesignCandidate(
        name=name,
        geometry={},
        metrics={
            "gross_floor_area": gross_area,
            "footprint_area": gross_area,
            "site_coverage": 0.40,
            "storeys": 1,
        },
    )


def test_score_is_bounded():
    constraints = make_constraints()

    candidate = make_candidate(
        "Option",
        35,
    )

    score = score_candidate(
        candidate,
        constraints,
    )

    assert 0 <= score.total <= 100
    assert 0 <= score.compliance <= 100


def test_candidates_are_ranked():
    constraints = make_constraints()

    candidates = [
        make_candidate("A", 20),
        make_candidate("B", 30),
        make_candidate("C", 40),
    ]

    ranked = score_and_rank(
        candidates,
        constraints,
    )

    assert len(ranked) == 3

    assert ranked[0].rank == 1
    assert ranked[1].rank == 2
    assert ranked[2].rank == 3

    assert (
        ranked[0].score
        >= ranked[1].score
    )