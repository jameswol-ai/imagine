"""Shared structural engineering context for the IMAGINE design pipeline.

This module is deliberately calculation-friendly: the data contracts contain no
Streamlit UI code, so structural engines can consume the same project actions,
combinations and analysis handoffs. Numerical results remain preliminary until
verified against the adopted Eurocodes, National Annex and project inputs.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


PIPELINE_STAGES = (
    "Design Basis",
    "Actions",
    "Combinations",
    "Analysis",
    "Member Design",
    "Detailing",
    "Schedules",
    "BIM / BOQ",
)


@dataclass(frozen=True, slots=True)
class ActionCase:
    """A project action case expressed in consistent scalar units."""

    name: str
    category: str
    value: float
    unit: str = "kN"
    leading: bool = False
    source: str = "Project input"

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Action name cannot be empty")
        if not self.category.strip():
            raise ValueError("Action category cannot be empty")
        if self.value < 0:
            raise ValueError("Action value cannot be negative")


@dataclass(frozen=True, slots=True)
class CombinationResult:
    """A transparent load-combination result suitable for downstream handoff."""

    name: str
    value: float
    limit_state: str
    source: str = "EN 1990-style screening"


@dataclass
class StructuralContext:
    """Shared state passed through the structural calculation pipeline."""

    project_id: str = "IMAGINE-DEMO"
    project_name: str = "Untitled Project"
    actions: list[ActionCase] = field(default_factory=list)
    combinations: list[CombinationResult] = field(default_factory=list)
    governing_uls: CombinationResult | None = None
    governing_sls: CombinationResult | None = None
    pipeline: dict[str, str] = field(
        default_factory=lambda: {stage: "Not started" for stage in PIPELINE_STAGES}
    )
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def add_action(self, action: ActionCase) -> None:
        self.actions.append(action)
        self.pipeline["Actions"] = "Configured"
        self.touch()

    def set_combinations(
        self,
        combinations: list[CombinationResult],
        governing_uls: CombinationResult | None = None,
        governing_sls: CombinationResult | None = None,
    ) -> None:
        self.combinations = list(combinations)
        self.governing_uls = governing_uls
        self.governing_sls = governing_sls
        self.pipeline["Combinations"] = "Complete" if combinations else "Not started"
        self.touch()

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_CONTEXT_KEY = "imagine_structural_context"


def get_context(session_state: Any | None = None) -> StructuralContext:
    """Return the shared context, optionally backed by Streamlit session state."""
    if session_state is None:
        import streamlit as st

        session_state = st.session_state
    if _CONTEXT_KEY not in session_state:
        session_state[_CONTEXT_KEY] = StructuralContext()
    return session_state[_CONTEXT_KEY]


def reset_context(session_state: Any | None = None) -> StructuralContext:
    """Create and return a fresh project structural context."""
    if session_state is None:
        import streamlit as st

        session_state = st.session_state
    session_state[_CONTEXT_KEY] = StructuralContext()
    return session_state[_CONTEXT_KEY]


__all__ = [
    "PIPELINE_STAGES",
    "ActionCase",
    "CombinationResult",
    "StructuralContext",
    "get_context",
    "reset_context",
]
