"""AI Architect Copilot adapter.

The architecture decision-support engine owns deterministic calculations and
traceable recommendations. This module provides the existing AI-domain route
without duplicating that logic or requiring a session-state data table.
"""

from __future__ import annotations

import streamlit as st

from architecture.assistant.engine import ArchitectureAssistant, ArchitectureBrief


class ArchitectAIEngine:
    """Compatibility facade for the enterprise AI Architect route."""

    def __init__(self) -> None:
        self.assistant = ArchitectureAssistant()

    def run(self, inputs: dict[str, object] | None = None) -> dict[str, object]:
        payload = inputs or {}
        brief = ArchitectureBrief(
            project_type=str(payload.get("project_type", "Office")),
            site_area_m2=float(payload.get("site_area_m2", 5000.0)),
            site_width_m=float(payload.get("site_width_m", 50.0)),
            site_depth_m=float(payload.get("site_depth_m", 100.0)),
            target_occupants=int(payload.get("target_occupants", 250)),
        )
        assessment = self.assistant.assess(brief)
        return {
            "summary": self.assistant.respond("Give me the highest-priority architecture finding.", assessment),
            "buildable_footprint_m2": assessment.buildable_footprint_m2,
            "program_gross_area_m2": assessment.program_gross_area_m2,
            "screened_storeys": assessment.feasible_storeys,
            "recommendations": [item.__dict__ if hasattr(item, "__dict__") else {"category": item.category, "finding": item.finding, "action": item.action, "priority": item.priority} for item in assessment.recommendations],
        }


def render() -> None:
    """Render the AI-domain Architect Copilot using the shared assistant engine."""
    st.header("AI Architect Copilot")
    st.caption("Shared architecture decision support with traceable preliminary calculations.")

    project_type = st.selectbox("Project type", ["Office", "Residential", "Mixed-use", "Education", "Healthcare"], key="architect_ai_project_type")
    site_area = st.number_input("Site area (m²)", min_value=100.0, value=5000.0, step=100.0, key="architect_ai_site_area")
    occupants = st.number_input("Peak occupants", min_value=1, value=250, step=10, key="architect_ai_occupants")

    if st.button("Analyze architectural brief", type="primary", use_container_width=True):
        result = ArchitectAIEngine().run({"project_type": project_type, "site_area_m2": site_area, "target_occupants": occupants})
        st.session_state["architect_ai_result"] = result

    result = st.session_state.get("architect_ai_result")
    if result:
        c1, c2, c3 = st.columns(3)
        c1.metric("Buildable footprint", f"{result['buildable_footprint_m2']:,.0f} m²")
        c2.metric("Program GFA", f"{result['program_gross_area_m2']:,.0f} m²")
        c3.metric("Screened storeys", result["screened_storeys"])
        st.info(result["summary"])
        st.dataframe(result["recommendations"], use_container_width=True, hide_index=True)


__all__ = ["ArchitectAIEngine", "render"]
