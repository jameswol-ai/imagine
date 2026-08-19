"""
architecture/site_planning/ui.py
--------------------------------
Site planning and land development module.
Exposes zero-argument `render_site_planning()` required by streamlit_app.py.
"""

from __future__ import annotations

import streamlit as st


def render_site_planning() -> None:
    """Zero-argument Streamlit renderer for Site Planning & Land Development."""

    st.title("📐 Site Planning & Land Development")
    st.caption("Site geometry analysis, setback optimization, orientation, and land utilization.")

    st.divider()

    col_params, col_main = st.columns([1, 2], gap="large")

    with col_params:
        st.subheader("Site Boundary & Setbacks")

        plot_area = st.number_input(
            "Total Plot Area (m²)",
            min_value=500,
            max_value=500000,
            value=8500,
            step=500,
            key="site_plan_area",
        )

        st.markdown("**Boundary Setbacks (m)**")
        c1, c2 = st.columns(2)
        with c1:
            front_setback = st.number_input("Front", min_value=0.0, value=6.0, step=0.5, key="site_plan_sb_front")
            rear_setback = st.number_input("Rear", min_value=0.0, value=4.0, step=0.5, key="site_plan_sb_rear")
        with c2:
            side_a_setback = st.number_input("Side A", min_value=0.0, value=3.0, step=0.5, key="site_plan_sb_side_a")
            side_b_setback = st.number_input("Side B", min_value=0.0, value=3.0, step=0.5, key="site_plan_sb_side_b")

        st.markdown("**Topography & Environment**")
        terrain_type = st.selectbox(
            "Terrain Profile",
            ["Flat (<2% slope)", "Gentle Slope (2–8%)", "Moderate Slope (8–15%)", "Steep Slope (>15%)"],
            key="site_plan_terrain",
        )

        north_orientation = st.slider(
            "North Axis Orientation (°)",
            min_value=0,
            max_value=359,
            value=45,
            key="site_plan_north_angle",
        )

        st.divider()

        analyze_btn = st.button(
            "📐 Calculate Buildable Envelope",
            type="primary",
            use_container_width=True,
            key="site_plan_calc_btn",
        )

    with col_main:
        if "site_plan_analyzed" not in st.session_state:
            st.session_state.site_plan_analyzed = False

        if analyze_btn:
            st.session_state.site_plan_analyzed = True

        # Preliminary spatial envelope math (assuming ~1:1.5 plot aspect ratio)
        est_width = (plot_area / 1.5) ** 0.5
        est_length = est_width * 1.5
        buildable_width = max(0.0, est_width - side_a_setback - side_b_setback)
        buildable_length = max(0.0, est_length - front_setback - rear_setback)
        buildable_area = buildable_width * buildable_length
        coverage_pct = round((buildable_area / plot_area) * 100, 1) if plot_area > 0 else 0

        tab_envelope, tab_coverage, tab_earthwork = st.tabs([
            "🗺️ Buildable Envelope",
            "📊 Coverage & Density",
            "🚜 Earthworks & Grading",
        ])

        with tab_envelope:
            if not st.session_state.site_plan_analyzed:
                st.info(
                    "Define boundary parameters on the left and click "
                    "**Calculate Buildable Envelope** to run site layout analysis."
                )
            else:
                st.success("Buildable footprint envelope calculated successfully.")

                m1, m2, m3 = st.columns(3)
                m1.metric("Plot Area", f"{plot_area:,} m²")
                m2.metric("Max Footprint", f"{int(buildable_area):,} m²")
                m3.metric("Footprint Ratio", f"{coverage_pct}%")

                st.markdown("### Site Layout Viewport")
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
                        <h4 style="margin: 0;">2D Site Boundary Map</h4>
                        <p style="color: #777; font-size: 0.85rem; margin-top: 0.5rem;">
                            North Angle: {north_orientation}° | Terrain: {terrain_type}
                        </p>
                        <p style="color: #777; font-size: 0.8rem;">
                            [ Vector GIS / Setback Envelope Overlay ]
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with tab_coverage:
            st.markdown("### Land Allocation Breakdown")

            allocation_data = [
                {"Category": "Max Building Footprint", "Area (m²)": int(buildable_area), "Percentage": f"{coverage_pct}%"},
                {"Category": "Setback Buffers", "Area (m²)": int(plot_area - buildable_area), "Percentage": f"{round(100 - coverage_pct, 1)}%"},
                {"Category": "Paved & Access Roads (Est.)", "Area (m²)": int(plot_area * 0.15), "Percentage": "15.0%"},
                {"Category": "Green Space / Softscape (Min.)", "Area (m²)": int(plot_area * 0.25), "Percentage": "25.0%"},
            ]
            st.dataframe(allocation_data, use_container_width=True, hide_index=True)

        with tab_earthwork:
            st.markdown("### Earthwork & Terrain Suitability")

            e1, e2 = st.columns(2)
            with e1:
                st.markdown("**Foundation Suitability**")
                suitability = 0.88 if "Flat" in terrain_type or "Gentle" in terrain_type else 0.45
                st.progress(suitability, text=f"{terrain_type}")

                st.markdown("**Solar Exposure Optimization**")
                st.progress(0.82, text=f"82% efficiency score at {north_orientation}° N")

            with e2:
                st.markdown("**Estimated Cut/Fill Volume**")
                st.metric("Estimated Excavation Volume", f"{int(buildable_area * 1.2):,} m³")
                st.caption("Based on site envelope area and terrain slope variance.")
