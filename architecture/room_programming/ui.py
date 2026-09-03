"""Dynamic room schedule and spatial programming workspace."""

from __future__ import annotations

import math
import pandas as pd
import plotly.express as px
import streamlit as st


def _brief_value(name: str, default):
    brief = st.session_state.get("architecture_brief")
    return getattr(brief, name, default) if brief is not None else default


def render_room_programming() -> None:
    """Build and store a preliminary room program from explicit assumptions."""
    st.title("Room Schedules & Spatial Programming")
    st.caption("Dynamic program synthesis from occupancy and area assumptions. Actual room standards must be confirmed with the client and adopted code.")

    assessment = st.session_state.get("architecture_assessment")
    default_occupants = int(_brief_value("target_occupants", 350))
    default_density = float(_brief_value("area_per_person_m2", 12.0))
    default_gross = float(assessment.program_gross_area_m2) if assessment else default_occupants * default_density / 0.80

    left, right = st.columns([1, 2], gap="large")
    with left:
        facility = st.selectbox("Facility type", ["Office", "Education", "Residential", "Healthcare", "Mixed-use"], key="room_prog_facility_type")
        occupants = st.number_input("Peak occupants", min_value=1, value=default_occupants, step=10, key="room_prog_occupants")
        area_person = st.number_input("Net area/person (m²)", min_value=1.0, value=default_density, step=0.5, key="room_prog_density")
        efficiency = st.slider("Net-to-gross efficiency (%)", 50, 95, 80, 1, key="room_prog_efficiency")
        workspace_share = st.slider("Primary workspace share (%)", 40, 80, 60, 1, key="room_prog_workspace_share")
        if assessment:
            st.caption(f"Architecture Assistant program GFA: {assessment.program_gross_area_m2:,.0f} m²")
        generate = st.button("Generate space program", type="primary", use_container_width=True, key="room_prog_generate_btn")

    net_area = float(occupants) * area_person
    gross_area = net_area / (efficiency / 100.0)
    shares = {
        "Primary workspace": workspace_share / 100.0,
        "Meeting & collaboration": 0.15,
        "Amenities": 0.12,
        "Support & utility": max(0.0, 1.0 - workspace_share / 100.0 - 0.15 - 0.12),
    }
    templates = {
        "Office": [("Open work area", 8.0, "Low"), ("Private offices", 20.0, "High"), ("Meeting rooms", 30.0, "High"), ("Focus rooms", 10.0, "Medium")],
        "Education": [("Teaching rooms", 50.0, "Medium"), ("Laboratories", 70.0, "High"), ("Staff rooms", 25.0, "Medium"), ("Library / study", 100.0, "Low")],
        "Residential": [("Apartment units", 65.0, "High"), ("Shared amenity", 80.0, "Medium"), ("Management", 20.0, "Low"), ("Storage / services", 15.0, "Low")],
        "Healthcare": [("Consultation rooms", 18.0, "High"), ("Treatment rooms", 25.0, "High"), ("Waiting", 60.0, "Medium"), ("Staff / support", 30.0, "Medium")],
        "Mixed-use": [("Primary use area", 50.0, "Medium"), ("Commercial / shared", 30.0, "High"), ("Amenities", 40.0, "Medium"), ("Support / services", 20.0, "Low")],
    }
    rows = []
    for index, (name, unit_area, acoustic) in enumerate(templates[facility]):
        target = net_area * list(shares.values())[index]
        count = max(1, math.ceil(target / unit_area))
        rows.append({"Room / Zone": name, "Count": count, "Unit area (m²)": unit_area, "Total area (m²)": round(count * unit_area, 1), "Acoustic": acoustic})
    schedule = pd.DataFrame(rows)

    if generate:
        st.session_state["room_program_result"] = {
            "facility": facility,
            "occupants": int(occupants),
            "net_area_m2": net_area,
            "gross_area_m2": gross_area,
            "schedule": schedule.to_dict("records"),
        }

    with right:
        st.success(f"Preliminary {facility.lower()} program generated from the current brief.") if generate else st.info("The schedule responds to the current architecture brief. Generate to store the concept for downstream planning.")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Occupants", int(occupants))
        m2.metric("Net area", f"{net_area:,.0f} m²")
        m3.metric("Gross area", f"{gross_area:,.0f} m²")
        m4.metric("Efficiency", f"{efficiency}%")
        st.subheader("Room schedule")
        st.dataframe(schedule, use_container_width=True, hide_index=True)

        st.subheader("Functional allocation")
        allocation = pd.DataFrame([{"Zone": n, "Share (%)": round(s * 100, 1), "Net area (m²)": round(net_area * s, 1)} for n, s in shares.items()])
        st.dataframe(allocation, use_container_width=True, hide_index=True)
        fig = px.pie(allocation, names="Zone", values="Net area (m²)", hole=0.45, title="Preliminary net-area allocation", height=330)
        st.plotly_chart(fig, use_container_width=True)

        wc = max(2, math.ceil(occupants / 40.0))
        lavatories = max(2, math.ceil(occupants / 50.0))
        st.subheader("Early life-safety planning indicators")
        a, b, c = st.columns(3)
        a.metric("Indicative WCs", wc)
        b.metric("Indicative lavatories", lavatories)
        c.metric("Indicative stair width", f"{occupants * 0.0051:.2f} m")
        st.warning("Fixture counts and stair width are screening assumptions. Use the adopted authority standard and occupancy-specific provisions for final design.")
