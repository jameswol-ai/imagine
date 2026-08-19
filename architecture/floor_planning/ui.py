"""
architecture/floor_planning/ui.py
---------------------------------
Floor layout and space planning module.
Exposes zero-argument `render_floor_planning()` required by streamlit_app.py.
"""

from __future__ import annotations

import streamlit as st


def render_floor_planning() -> None:
    """Zero-argument Streamlit renderer for Floor Layout & Planning."""

    st.title("🏢 Floor Layout & Planning")
    st.caption("Automated floor layout generation, circulation pathways, core placement, and structural grid alignment.")

    st.divider()

    col_params, col_main = st.columns([1, 2], gap="large")

    with col_params:
        st.subheader("Layout Controls")

        selected_level = st.selectbox(
            "Floor Level",
            [
                "Ground Floor (L1)",
                "Typical Floor (L2–L10)",
                "Executive / Mechanical (L11)",
                "Penthouse Level (L12)",
            ],
            key="fp_selected_level",
        )

        layout_strategy = st.selectbox(
            "Layout Typology",
            [
                "Central Core & Perimeter",
                "Double-Loaded Corridor",
                "Open-Plan Flexible Office",
                "Courtyard / Atrium Enclosed",
            ],
            key="fp_layout_strategy",
        )

        st.markdown("**Structural & Space Parameters**")
        grid_spacing = st.slider(
            "Column Grid Spacing (m)",
            min_value=6.0,
            max_value=12.0,
            value=8.4,
            step=0.6,
            key="fp_grid_spacing",
        )

        circulation_pct = st.slider(
            "Circulation Target (%)",
            min_value=10,
            max_value=30,
            value=18,
            key="fp_circulation_pct",
        )

        core_position = st.radio(
            "Core Location",
            ["Center", "Side/Offset", "Dual End Cores"],
            key="fp_core_pos",
            horizontal=True,
        )

        st.divider()

        generate_plan_btn = st.button(
            "📐 Generate Floor Layout",
            type="primary",
            use_container_width=True,
            key="fp_generate_btn",
        )

    with col_main:
        if "fp_generated" not in st.session_state:
            st.session_state.fp_generated = False

        if generate_plan_btn:
            st.session_state.fp_generated = True

        tab_layout, tab_adjacency, tab_grid = st.tabs([
            "📐 Layout Plan",
            "🔄 Adjacency & Flow",
            "🧱 Structural Grid",
        ])

        with tab_layout:
            if not st.session_state.fp_generated:
                st.info(
                    "Configure floor level and spatial parameters on the left and click "
                    "**Generate Floor Layout** to run the layout synthesis."
                )
            else:
                st.success(f"Layout synthesized for **{selected_level}** using **{layout_strategy}** pattern.")

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Gross Area", "1,250 m²")
                m2.metric("Usable Area", "1,025 m²")
                m3.metric("Circulation", f"{circulation_pct}%")
                m4.metric("Grid Module", f"{grid_spacing} × {grid_spacing} m")

                st.markdown("### Floor Plan Viewport")
                st.markdown(
                    f"""
                    <div style="
                        background-color: rgba(128, 128, 128, 0.08);
                        border: 1px dashed rgba(128, 128, 128, 0.3);
                        border-radius: 12px;
                        padding: 3.5rem 1.5rem;
                        text-align: center;
                        margin-bottom: 1.5rem;
                    ">
                        <h4 style="margin: 0;">2D Floor Layout Canvas</h4>
                        <p style="color: #777; font-size: 0.85rem; margin-top: 0.5rem;">
                            Level: {selected_level} | Strategy: {layout_strategy} | Core: {core_position}
                        </p>
                        <p style="color: #777; font-size: 0.8rem;">
                            [ Interactive SVG / Canvas Floor Plan Visualizer ]
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with tab_adjacency:
            st.markdown("### Functional Adjacency Matrix")

            adjacency_data = [
                {"Zone A": "Central Core (Egress/MEP)", "Zone B": "Primary Corridor", "Adjacency Demand": "High (Direct)", "Status": "Optimal"},
                {"Zone A": "Primary Workstations", "Zone B": "Glazed Exterior Facade", "Adjacency Demand": "High (Daylight)", "Status": "Optimal"},
                {"Zone A": "Conference Rooms", "Zone B": "Workstation Area", "Adjacency Demand": "Medium (Acoustic)", "Status": "Compliant"},
                {"Zone A": "Restrooms / Amenities", "Zone B": "Central Core", "Adjacency Demand": "High (Wet Core)", "Status": "Optimal"},
            ]
            st.dataframe(adjacency_data, use_container_width=True, hide_index=True)

        with tab_grid:
            st.markdown("### Structural Column Grid Layout")

            g1, g2 = st.columns(2)
            with g1:
                st.metric("Total Bays (X-Axis)", f"{int(35 / grid_spacing) + 1}")
                st.metric("Total Bays (Y-Axis)", f"{int(25 / grid_spacing) + 1}")
            with g2:
                st.metric("Total Column Count", f"{int((35 / grid_spacing) + 1) * int((25 / grid_spacing) + 1)}")
                st.metric("Cantilever Clearance", "1.2 m")
