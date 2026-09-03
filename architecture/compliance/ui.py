"""Preliminary building-code and design compliance screening workspace."""

from __future__ import annotations

import pandas as pd
import streamlit as st


def render_compliance() -> None:
    """Evaluate explicit life-safety and accessibility screening inputs."""
    st.title("Building Code & Design Compliance")
    st.caption("Explicit screening checks for egress, accessibility and fire strategy. This is not a legal code certification.")

    assessment = st.session_state.get("architecture_assessment")
    program = st.session_state.get("room_program_result")
    default_floors = int(assessment.feasible_storeys) if assessment else 6
    default_occupants = int(program["occupants"]) if program else int(getattr(assessment, "brief", None).target_occupants) if assessment and getattr(assessment, "brief", None) else 350

    left, right = st.columns([1, 2], gap="large")
    with left:
        code = st.selectbox("Code framework", ["IBC", "Eurocode / EN", "UK Building Regulations", "National Building Code"], key="comp_code_standard")
        occupancy = st.selectbox("Occupancy", ["Business / Office", "Assembly", "Residential", "Mercantile", "Healthcare"], key="comp_occupancy_group")
        floors = st.number_input("Storeys", min_value=1, value=max(1, default_floors), step=1, key="comp_storeys")
        occupants = st.number_input("Peak occupants", min_value=1, value=max(1, default_occupants), step=10, key="comp_occupants")
        sprinklers = st.toggle("Automatic sprinklers provided", value=True, key="comp_sprinklers")
        travel = st.number_input("Maximum travel distance (m)", min_value=1.0, value=45.0, step=1.0, key="comp_travel_dist")
        exits = st.number_input("Available exits / exit stairs", min_value=1, value=2, step=1, key="comp_exits")
        accessible_route = st.number_input("Accessible route width (m)", min_value=0.5, value=1.2, step=0.05, key="comp_access_width")
        ramp_slope = st.number_input("Ramp slope (%)", min_value=0.0, value=8.0, step=0.5, key="comp_ramp_slope")
        audit = st.button("Run compliance screening", type="primary", use_container_width=True, key="comp_run_audit_btn")

    travel_limit = 75.0 if sprinklers else 60.0
    required_exits = 2 if occupants > 50 else 1
    checks = [
        {"Check": "Travel distance", "Proposed": f"{travel:.1f} m", "Screening limit": f"{travel_limit:.1f} m", "Status": "PASS" if travel <= travel_limit else "REVIEW"},
        {"Check": "Exit count", "Proposed": str(int(exits)), "Screening minimum": str(required_exits), "Status": "PASS" if exits >= required_exits else "REVIEW"},
        {"Check": "Accessible route width", "Proposed": f"{accessible_route:.2f} m", "Screening minimum": "1.20 m", "Status": "PASS" if accessible_route >= 1.2 else "REVIEW"},
        {"Check": "Ramp slope", "Proposed": f"{ramp_slope:.1f}%", "Screening maximum": "8.3%", "Status": "PASS" if ramp_slope <= 8.3 else "REVIEW"},
        {"Check": "High-rise review trigger", "Proposed": f"{int(floors)} storeys", "Screening trigger": "> 4 storeys", "Status": "REVIEW" if floors > 4 else "PASS"},
    ]
    result = {"code": code, "occupancy": occupancy, "storeys": int(floors), "occupants": int(occupants), "sprinklers": sprinklers, "checks": checks}
    if audit:
        st.session_state["compliance_result"] = result

    with right:
        if audit:
            passed = sum(row["Status"] == "PASS" for row in checks)
            st.success(f"{code} screening complete: {passed}/{len(checks)} checks pass.") if passed == len(checks) else st.warning(f"{code} screening complete: {passed}/{len(checks)} checks pass. Review the flagged items.")
        else:
            st.info("Inputs are pre-populated from the architecture workflow where available. Run the screening to store the current assessment.")
        st.dataframe(pd.DataFrame(checks), use_container_width=True, hide_index=True)

        st.subheader("Architecture handoff")
        if assessment:
            st.dataframe(pd.DataFrame([
                {"Source": "Architecture Assistant", "Metric": "Screened storeys", "Value": assessment.feasible_storeys},
                {"Source": "Architecture Assistant", "Metric": "Program GFA", "Value": f"{assessment.program_gross_area_m2:,.0f} m²"},
                {"Source": "Room Programming", "Metric": "Program occupants", "Value": default_occupants},
            ]), use_container_width=True, hide_index=True)
        else:
            st.info("Run Architecture Assistant first to populate upstream design assumptions.")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Occupancy", int(occupants))
        c2.metric("Required exits", required_exits)
        c3.metric("Travel limit", f"{travel_limit:.0f} m")
        c4.metric("Sprinklers", "Yes" if sprinklers else "No")
        st.subheader("Accessibility inputs")
        st.dataframe(pd.DataFrame([
            {"Requirement": "Accessible route", "Proposed": f"{accessible_route:.2f} m", "Status": "PASS" if accessible_route >= 1.2 else "REVIEW"},
            {"Requirement": "Ramp slope", "Proposed": f"{ramp_slope:.1f}%", "Status": "PASS" if ramp_slope <= 8.3 else "REVIEW"},
        ]), use_container_width=True, hide_index=True)
        st.warning("Code limits shown here are screening assumptions. Verify the adopted edition, local amendments, occupancy-specific provisions and authority requirements before treating any result as compliant.")
