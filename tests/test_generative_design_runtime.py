"""Runtime contracts for the generative-design engine."""
from __future__ import annotations

import subprocess
import sys

from architecture.generative_design.generator import DesignCandidate, generate_candidates
from architecture.generative_design.schemas import (
    DesignConstraints,
    ProgramConstraints,
    RoomRequirement,
    SiteConstraints,
    ZoningConstraints,
)


def _constraints() -> DesignConstraints:
    return DesignConstraints(
        site=SiteConstraints(width=30, depth=40, setback_front=2, setback_rear=2),
        zoning=ZoningConstraints(max_site_coverage=0.60, max_far=2.0, max_height=15, max_storeys=3),
        program=ProgramConstraints(
            rooms=[RoomRequirement(name="Living", area=30), RoomRequirement(name="Bedroom", area=15, quantity=3)]
        ),
    )


def test_generator_returns_complete_candidate_contract() -> None:
    candidates = generate_candidates(_constraints(), count=5)
    assert len(candidates) == 5
    assert all(isinstance(item, DesignCandidate) for item in candidates)
    assert all(item.geometry["type"] == "rectangular_massing" for item in candidates)
    assert all("gross_floor_area" in item.metrics for item in candidates)
    assert all("zoning_screening" in item.evaluation for item in candidates)


def test_generator_import_is_ui_side_effect_free() -> None:
    code = (
        "import sys; import architecture.generative_design.generator; "
        "assert 'streamlit' not in sys.modules"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
