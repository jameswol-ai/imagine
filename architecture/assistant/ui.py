"""Streamlit interface for the IMAGINE Architecture Assistant."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from .engine import ArchitectureAssistant, ArchitectureBrief, ArchitectureAssessment


def _build_brief() -> ArchitectureBrief:
    with st.sidebar:
        st.markdown("### Assistant Brief")
        project_type = st.selectbox("Project type", ["Office", "Residential", "Mixed-use", "Education", "Healthcare", "Hospitality"], key="arch_ai_project_type")
        site_area = st.number_input("Site area (m²)", min_value=100.0, value=5000.0, step=100.0, key="arch_ai_site_area")
        c1, c2 = st.columns(2)
        with c1:
            site_width = st.number_input("Site width (m)", min_value=5.0, value=50.0, step=1.0, key="arch_ai_site_width")
            front = st.number_input("Front setback (m)", min_value=0.0, value=6.0, step=0.5, key="arch_ai_front")
            side = st.number_input("Side setback (m)", min_value=0.0, value=3.0, step=0.5, key="arch_ai_side")
        with c2:
            site_depth = st.number_input("Site depth (m)", min_value=5.0, value=100.0, step=1.0, key="arch_ai_site_depth")
            rear = st.number_input("Rear setback (m)", min_value=0.0, value=4.0, step=0.5, key="arch_ai_rear")
            max_storeys = st.number_input("Maximum storeys", min_value=1, value=10, step=1, key="arch_ai_storeys")
        c3, c4 = st.columns(2)
        with c3:
            far = st.number_input("Maximum FAR", min_value=0.1, value=4.5, step=0.1, key="arch_ai_far")
            occupants = st.number_input("Peak occupants", min_value=1, value=250, step=10, key="arch_ai_occupants")
        with c4:
            height = st.number_input("Maximum height (m)", min_value=3.5, value=45.0, step=1.0, key="arch_ai_height")
            density = st.number_input("Area/person (m²)", min_value=1.0, value=12.0, step=0.5, key="arch_ai_density")
        circulation = st.slider("Circulation allowance (%)", 5.0, 40.0, 18.0, 1.0, key="arch_ai_circulation")
        north = st.slider("North axis rotation (°)", 0.0, 359.0, 0.0, 1.0, key="arch_ai_north")

    return ArchitectureBrief(
        project_type=project_type,
        site_area_m2=site_area,
        site_width_m=site_width,
        site_depth_m=site_depth,
        front_setback_m=front,
        rear_setback_m=rear,
        side_setback_m=side,
        max_far=far,
        max_height_m=height,
        target_occupants=int(occupants),
        area_per_person_m2=density,
        circulation_pct=circulation,
        max_storeys=int(max_storeys),
        north_angle_deg=north,
    )


def _assessment_table(assessment: ArchitectureAssessment) -> pd.DataFrame:
    return pd.DataFrame([
        {"Metric": "Buildable width", "Value": f"{assessment.buildable_width_m:.1f} m"},
        {"Metric": "Buildable depth", "Value": f"{assessment.buildable_depth_m:.1f} m"},
        {"Metric": "Buildable footprint", "Value": f"{assessment.buildable_footprint_m2:,.0f} m²"},
        {"Metric": "Screening GFA capacity", "Value": f"{assessment.max_gfa_by_far_m2:,.0f} m²"},
        {"Metric": "Program gross area", "Value": f"{assessment.program_gross_area_m2:,.0f} m²"},
        {"Metric": "Screened storeys", "Value": str(assessment.feasible_storeys)},
        {"Metric": "Indicative parking", "Value": str(assessment.estimated_parking_spaces)},
    ])


def render_architecture_assistant() -> None:
    """Render the cross-module architecture decision-support workspace."""
    st.title("IMAGINE Architecture Assistant")
    st.caption("A traceable design copilot for site, program, zoning, floor planning, compliance and structural handoff.")

    assistant = ArchitectureAssistant()
    brief = _build_brief()
    assessment = assistant.assess(brief)
    st.session_state["architecture_assessment"] = assessment

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Buildable Footprint", f"{assessment.buildable_footprint_m2:,.0f} m²")
    k2.metric("Program GFA", f"{assessment.program_gross_area_m2:,.0f} m²")
    k3.metric("Screened Storeys", assessment.feasible_storeys)
    k4.metric("Indicative Parking", assessment.estimated_parking_spaces)

    tabs = st.tabs(["Assessment", "Recommendations", "Design Assistant", "Workflow Handoff"])
    with tabs[0]:
        st.subheader("Project feasibility snapshot")
        left, right = st.columns([1, 1.2])
        with left:
            st.dataframe(_assessment_table(assessment), use_container_width=True, hide_index=True)
        with right:
            chart = pd.DataFrame({"Capacity": [assessment.max_gfa_by_far_m2, assessment.program_gross_area_m2]})
            chart["Metric"] = ["Zoning capacity", "Program demand"]
            fig = px.bar(chart, x="Metric", y="Capacity", title="GFA demand vs screening capacity", height=330)
            st.plotly_chart(fig, use_container_width=True)
        st.caption("All values are preliminary planning calculations. The rectangular envelope assumes the supplied site dimensions and uniform setbacks.")

    with tabs[1]:
        st.subheader("Assistant findings")
        rows = [
            {"Priority": item.priority, "Category": item.category, "Finding": item.finding, "Recommended action": item.action}
            for item in assessment.recommendations
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with tabs[2]:
        st.subheader("Ask the architecture assistant")
        if "architecture_chat" not in st.session_state:
            st.session_state.architecture_chat = [
                {"role": "assistant", "content": "I have assessed the current brief. Ask me about the site, program, zoning, floor planning, compliance, generative options or structural handoff."}
            ]
        for message in st.session_state.architecture_chat:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        prompt = st.chat_input("Ask about this design brief...")
        if prompt:
            st.session_state.architecture_chat.append({"role": "user", "content": prompt})
            response = assistant.respond(prompt, assessment)
            st.session_state.architecture_chat.append({"role": "assistant", "content": response})
            st.rerun()

    with tabs[3]:
        st.subheader("Controlled handoff to the next disciplines")
        handoff = pd.DataFrame([
            {"Discipline": "Site Planning", "Inputs": "Site dimensions, setbacks, north orientation", "Next action": "Develop actual boundary and access geometry"},
            {"Discipline": "Space Programming", "Inputs": f"{brief.target_occupants:,} occupants, {assessment.program_gross_area_m2:,.0f} m² gross", "Next action": "Replace assumptions with an approved room schedule"},
            {"Discipline": "Compliance", "Inputs": "Occupancy, height, egress and adopted code", "Next action": "Run authority-specific code checks"},
            {"Discipline": "Structural", "Inputs": "Storeys, grid concept, geometry and loads", "Next action": "Run preliminary beam/column/slab/foundation screening"},
            {"Discipline": "Generative Design", "Inputs": "Envelope, program and objectives", "Next action": "Generate and compare constrained options"},
        ])
        st.dataframe(handoff, use_container_width=True, hide_index=True)
        st.warning("The assistant coordinates preliminary decisions. It does not certify zoning, code compliance, structural safety or planning approval.")
