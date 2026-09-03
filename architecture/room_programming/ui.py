"""Dynamic room schedule and spatial programming workspace."""

from __future__ import annotations

import math
import pandas as pd
import streamlit as st


def render_room_programming() -> None:
    """Build a preliminary room program from explicit occupancy assumptions."""
    st.title("Room Schedules & Spatial Programming")
    st.caption("Dynamic program synthesis from occupancy and area assumptions. Actual room standards must be confirmed with the client and adopted code.")

    left, right = st.columns([1, 2], gap="large")
    with left:
        facility = st.selectbox("Facility type", ["Office", "Education", "Residential", "Healthcare"], key="room_prog_facility_type")
        occupants = st.number_input("Peak occupants", min_value=1, value=350, step=10, key="room_prog_occupants")
        area_person = st.number_input("Net area/person (m²)", min_value=1.0, value=12.0, step=0.5, key="room_prog_density")
        efficiency = st.slider("Net-to-gross efficiency (%)", 50, 95, 80, 1, key="room_prog_efficiency")
        workstation_share = st.slider("Primary workspace share (%)", 40, 80, 60, 1, key="room_prog_workspace_share")
        generate = st.button("Generate space program", type="primary", use_container_width=True, key="room_prog_generate_btn")

    net_area = occupants * area_person
    gross_area = net_area / (efficiency / 100.0)
    shares = {
        "Primary workspace": workstation_share / 100.0,
        "Meeting & collaboration": 0.15,
        "Amenities": 0.12,
        "Support & utility": max(0.0, 1.0 - workstation_share / 100.0 - 0.15 - 0.12),
    }
    room_templates = {
        "Office": [("Open work area", 8.0, "Low"), ("Private offices", 20.0, "High"), ("Meeting rooms", 30.0, "High"), ("Focus rooms", 10.0, "Medium")],
        "Education": [("Teaching rooms", 50.0, "Medium"), ("Laboratories", 70.0, "High"), ("Staff rooms", 25.0, "Medium"), ("Library / study", 100.0, "Low")],
        "Residential": [("Apartment units", 65.0, "High"), ("Shared amenity", 80.0, "Medium"), ("Management", 20.0, "Low"), ("Storage / services", 15.0, "Low")],
        "Healthcare": [("Consultation rooms", 18.0, "High"), ("Treatment rooms", 25.0, "High"), ("Waiting", 60.0, "Medium"), ("Staff / support", 30.0, "Medium")],
    }

    rows = []
    template = room_templates[facility]
    for index, (name, unit_area, acoustic) in enumerate(template):
        zone_share = list(shares.values())[index % len(shares)]
        target_area = net_area * zone_share
        count = max(1, math.ceil(target_area / unit_area))
        rows.append({"Room / Zone": name, "Count": count, "Unit area (m²)": unit_area, "Total area (m²)": round(count * unit_area, 1), "Acoustic": acoustic})

    with right:
        if generate:
            st.success(f"Preliminary {facility.lower()} program generated from the supplied brief.")
        else:
            st.info("The schedule updates from the brief. Generate it when you are ready to record the current concept.")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Occupants", int(occupants))
        m2.metric("Net area", f"{net_area:,.0f} m²")
        m3.metric("Gross area", f"{gross_area:,.0f} m²")
        m4.metric("Efficiency", f"{efficiency}%")
        st.subheader("Room schedule")
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        st.subheader("Functional allocation")
        allocation = pd.DataFrame([{"Zone": name, "Share (%)": round(share * 100, 1), "Net area (m²)": round(net_area * share, 1)} for name, share in shares.items()])
        st.dataframe(allocation, use_container_width=True, hide_index=True)

        wc = max(2, math.ceil(occupants / 40.0))
        lavatories = max(2, math.ceil(occupants / 50.0))
        st.subheader("Early life-safety planning indicators")
        a, b, c = st.columns(3)
        a.metric("Indicative WCs", wc)
        b.metric("Indicative lavatories", lavatories)
        c.metric("Indicative stair width", f"{occupants * 0.0051:.2f} m")
        st.caption("These fixture and egress values are screening assumptions, not code determinations. Use the adopted authority standard for final sizing.")
