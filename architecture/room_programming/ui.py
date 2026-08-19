"""
architecture/room_programming/ui.py
-----------------------------------
Room schedules, spatial allocation, and occupancy programming module.
Exposes zero-argument `render_room_programming()` required by streamlit_app.py.
"""

from __future__ import annotations

import streamlit as st


def render_room_programming() -> None:
    """Zero-argument Streamlit renderer for Room Schedules & Spatial Programming."""

    st.title("🚪 Room Schedules & Spatial Programming")
    st.caption("Spatial requirements, occupancy loads, room adjacency requirements, and area allocations.")

    st.divider()

    col_params, col_main = st.columns([1, 2], gap="large")

    with col_params:
        st.subheader("Program Inputs")

        program_type = st.selectbox(
            "Facility Type",
            [
                "Corporate Office Building",
                "Higher Education Facility",
                "Residential Apartment Complex",
                "Healthcare Outpatient Clinic",
            ],
            key="room_prog_facility_type",
        )

        st.markdown("**Occupancy & Density**")
        target_occupants = st.number_input(
            "Target Peak Occupancy (Persons)",
            min_value=10,
            max_value=10000,
            value=350,
            step=25,
            key="room_prog_occupants",
        )

        area_per_person = st.number_input(
            "Target Area Density (m² / Person)",
            min_value=5.0,
            max_value=50.0,
            value=12.0,
            step=1.0,
            key="room_prog_density",
        )

        st.markdown("**Efficiency & Loss Factors**")
        net_gross_ratio = st.slider(
            "Net-to-Gross Factor (Multiplier)",
            min_value=1.1,
            max_value=1.5,
            value=1.25,
            step=0.05,
            key="room_prog_ng_ratio",
        )

        st.divider()

        generate_schedule_btn = st.button(
            "📋 Generate Space Program",
            type="primary",
            use_container_width=True,
            key="room_prog_generate_btn",
        )

    with col_main:
        if "room_prog_generated" not in st.session_state:
            st.session_state.room_prog_generated = False

        if generate_schedule_btn:
            st.session_state.room_prog_generated = True

        net_area = target_occupants * area_per_person
        gross_area = net_area * net_gross_ratio

        tab_schedule, tab_allocation, tab_occupancy = st.tabs([
            "📋 Room Schedule",
            "📊 Area Allocation",
            "👥 Egress & Amenities",
        ])

        with tab_schedule:
            if not st.session_state.room_prog_generated:
                st.info(
                    "Configure occupancy targets and density factors on the left and click "
                    "**Generate Space Program** to build the detailed room schedule."
                )
            else:
                st.success(f"Space schedule synthesized for **{program_type}**.")

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Peak Occupants", f"{target_occupants}")
                m2.metric("Target Net Area", f"{int(net_area):,} m²")
                m3.metric("Est. Gross Area", f"{int(gross_area):,} m²")
                m4.metric("Efficiency", f"{round((1 / net_gross_ratio) * 100, 1)}%")

                st.markdown("### Detailed Room Inventory")

                room_data = [
                    {"Room Category": "Primary Workstations / Open Office", "Count": 24, "Unit Area (m²)": 120, "Total Net (m²)": 2880, "Acoustic Req.": "Low"},
                    {"Room Category": "Executive Private Offices", "Count": 12, "Unit Area (m²)": 20, "Total Net (m²)": 240, "Acoustic Req.": "High"},
                    {"Room Category": "Large Conference Rooms", "Count": 4, "Unit Area (m²)": 45, "Total Net (m²)": 180, "Acoustic Req.": "High"},
                    {"Room Category": "Focus / Huddle Rooms", "Count": 8, "Unit Area (m²)": 12, "Total Net (m²)": 96, "Acoustic Req.": "Medium"},
                    {"Room Category": "Cafeteria & Wellness Lounge", "Count": 2, "Unit Area (m²)": 200, "Total Net (m²)": 400, "Acoustic Req.": "Low"},
                    {"Room Category": "IT Data Closet & Storage", "Count": 3, "Unit Area (m²)": 25, "Total Net (m²)": 75, "Acoustic Req.": "N/A"},
                ]
                st.dataframe(room_data, use_container_width=True, hide_index=True)

        with tab_allocation:
            st.markdown("### Functional Zone Distribution")

            zones = [
                {"Zone": "Primary Workspace", "Share": "65%", "Net Area (m²)": int(net_area * 0.65)},
                {"Zone": "Meeting & Collaboration", "Share": "15%", "Net Area (m²)": int(net_area * 0.15)},
                {"Zone": "Communal & Amenities", "Share": "12%", "Net Area (m²)": int(net_area * 0.12)},
                {"Zone": "Support & Utility", "Share": "8%", "Net Area (m²)": int(net_area * 0.08)},
            ]
            st.dataframe(zones, use_container_width=True, hide_index=True)

        with tab_occupancy:
            st.markdown("### Code Occupancy & Sanitary Requirements")

            st.markdown("**Plumbing Fixture Requirements (IBC Estimate)**")
            f1, f2, f3 = st.columns(3)
            f1.metric("Water Closets (Male/Female)", f"{max(2, int(target_occupants / 40))}")
            f2.metric("Lavatories / Basins", f"{max(2, int(target_occupants / 50))}")
            f3.metric("Drinking Fountains", f"{max(1, int(target_occupants / 100))}")

            st.markdown("**Egress & Exit Widths**")
            st.caption("Based on 0.2 inches (5.1 mm) per occupant for stairways.")
            st.metric("Minimum Combined Egress Stair Width", f"{round(target_occupants * 0.0051, 2)} m")
