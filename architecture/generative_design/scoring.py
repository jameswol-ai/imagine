"""
IMAGINE
Generative Design Scoring Engine
"""

from __future__ import annotations

from dataclasses import dataclass

from .constraints import (
    calculate_buildable_site,
    calculate_required_gross_area,
)
from .generator import DesignCandidate
from .schemas import DesignConstraints


@dataclass(frozen=True)
class DesignScore:
    """Calculated candidate score."""

    total: float

    efficiency: float

    compliance: float

    site_fit: float

    compactness: float


def _clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 100.0,
) -> float:
    return max(
        minimum,
        min(maximum, value),
    )


def score_candidate(
    candidate: DesignCandidate,
    constraints: DesignConstraints,
) -> DesignScore:
    """Calculate a normalized design score."""

    buildable = calculate_buildable_site(
        constraints
    )

    required_area = calculate_required_gross_area(
        constraints
    )

    gross_area = candidate.metrics.get(
        "gross_floor_area",
        0,
    )

    coverage = candidate.metrics.get(
        "site_coverage",
        0,
    )

    efficiency = (
        min(
            gross_area / required_area,
            1.0,
        )
        * 100
        if required_area
        else 0
    )

    compliance = 100.0

    if coverage > constraints.zoning.max_site_coverage:
        compliance -= 40

    storeys = candidate.metrics.get(
        "storeys",
        1,
    )

    if storeys > constraints.zoning.max_storeys:
        compliance -= 40

    site_fit = (
        100.0
        if candidate.metrics.get(
            "footprint_area",
            0,
        )
        <= (
            buildable.area
            * constraints.zoning.max_site_coverage
        )
        else 0.0
    )

    compactness = (
        100.0
        - abs(
            0.5 - coverage
        )
        * 100
    )

    total = (
        efficiency * 0.35
        + compliance * 0.35
        + site_fit * 0.20
        + compactness * 0.10
    )

    return DesignScore(
        total=round(
            _clamp(total),
            3,
        ),
        efficiency=round(
            _clamp(efficiency),
            3,
        ),
        compliance=round(
            _clamp(compliance),
            3,
        ),
        site_fit=round(
            _clamp(site_fit),
            3,
        ),
        compactness=round(
            _clamp(compactness),
            3,
        ),
    )


def score_and_rank(
    candidates: list[DesignCandidate],
    constraints: DesignConstraints,
) -> list[DesignCandidate]:
    """Score and rank candidates."""

    scored: list[tuple[DesignCandidate, DesignScore]] = []

    for candidate in candidates:
        score = score_candidate(
            candidate,
            constraints,
        )

        candidate.score = score.total

        candidate.evaluation = {
            "total": score.total,
            "efficiency": score.efficiency,
            "compliance": score.compliance,
            "site_fit": score.site_fit,
            "compactness": score.compactness,
        }

        scored.append(
            (candidate, score)
        )

    scored.sort(
        key=lambda item: item[1].total,
        reverse=True,
    )

    ranked = []

    for rank, (candidate, _) in enumerate(
        scored,
        start=1,
    ):
        candidate.rank = rank
        ranked.append(candidate)

    return ranked