"""Architectural design handbook for the IMAGINE standards workspace."""
from __future__ import annotations

import pandas as pd
import streamlit as st

HANDBOOK_SECTIONS = {
    "Design Basis": ["Project brief", "Site and climate", "Occupancy and user profile", "Applicable planning/building regulations", "Accessibility strategy"],
    "Site Planning": ["Plot boundaries", "Setbacks", "Access and circulation", "Parking and servicing", "Orientation", "Landscape/open space", "Levels and drainage"],
    "Space Planning": ["Room schedule", "Net-to-gross efficiency", "Adjacencies", "Circulation", "Vertical circulation", "Service/core planning", "Furniture and equipment allowances"],
    "Building Envelope": ["Daylight and openings", "Solar control", "Thermal envelope", "Moisture control", "Acoustics", "Fire compartmentation", "Maintenance access"],
    "Life Safety": ["Occupant load", "Means of escape", "Travel distance", "Exit capacity", "Stairs", "Fire access", "Emergency strategy"],
    "Accessibility": ["Accessible routes", "Entrances", "Doors", "Lifts", "Sanitary facilities", "Ramps", "Wayfinding"],
    "Coordination": ["Structural grid", "MEP zones", "Ceiling/service zones", "Plant rooms", "BIM coordinates", "Drawing standards", "Specification coordination"],
    "Design Development": ["Concept options", "Developed plans", "Elevations and sections", "Schedules", "Material selection", "Performance review", "Authority submission"],
}


def render_architectural_handbook() -> None:
    st.title("Architectural Design Handbook")
    st.caption("Project-neutral architectural planning and design-development reference. Use the adopted local regulations and project brief for final decisions.")

    section_names = list(HANDBOOK_SECTIONS)
    selected = st.selectbox("Handbook section", section_names, key="architectural_handbook_section")
    topics = HANDBOOK_SECTIONS[selected]
    st.dataframe(pd.DataFrame({"Topic": topics}), use_container_width=True, hide_index=True)

    st.subheader("Design checklist")
    checklist = pd.DataFrame({"Item": topics, "Status": ["Not reviewed"] * len(topics), "Notes": [""] * len(topics)})
    edited = st.data_editor(checklist, use_container_width=True, hide_index=True, key="architectural_handbook_checklist", column_config={"Status": st.column_config.SelectboxColumn("Status", options=["Not reviewed", "In progress", "Reviewed", "Requires specialist input"]), "Notes": st.column_config.TextColumn("Notes")})
    reviewed = int((edited["Status"] == "Reviewed").sum())
    st.metric("Reviewed topics", f"{reviewed}/{len(edited)}")
    st.info("This handbook is a design management aid. It does not reproduce proprietary standards and does not replace statutory requirements, authority guidance or professional review.")


__all__ = ["HANDBOOK_SECTIONS", "render_architectural_handbook"]
