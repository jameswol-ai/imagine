"""Preliminary site planning and land-development workspace."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def _brief_value(name: str, default):
    brief = st.session_state.get("architecture_brief")
    return getattr(brief, name, default) if brief is not None else default


def render_site_planning() -> None:
    """Render a traceable site-envelope study using explicit site dimensions."""
    st.title("Site Planning & Land Development")
    st.caption("Preliminary site envelope, setbacks, orientation and land-allocation study. Survey, cadastral and authority data are required for real site design.")

    width_default = float(_brief_value("site_width_m", 50.0))
    depth_default = float(_brief_value("site_depth_m", 100.0))
    area_default = float(_brief_value("site_area_m2", width_default * depth_default))

    left, right = st.columns([1, 2], gap="large")
    with left:
        plot_area = st.number_input("Plot area (m²)", min_value=100.0, value=area_default, step=100.0, key="site_plan_area")
        site_width = st.number_input("Site width (m)", min_value=5.0, value=width_default, step=1.0, key="site_plan_width")
        site_depth = st.number_input("Site depth (m)", min_value=5.0, value=depth_default, step=1.0, key="site_plan_depth")
        front = st.number_input("Front setback (m)", min_value=0.0, value=float(_brief_value("front_setback_m", 6.0)), step=0.5, key="site_plan_sb_front")
        rear = st.number_input("Rear setback (m)", min_value=0.0, value=float(_brief_value("rear_setback_m", 4.0)), step=0.5, key="site_plan_sb_rear")
        side_a = st.number_input("Side A setback (m)", min_value=0.0, value=float(_brief_value("side_setback_m", 3.0)), step=0.5, key="site_plan_sb_side_a")
        side_b = st.number_input("Side B setback (m)", min_value=0.0, value=float(_brief_value("side_setback_m", 3.0)), step=0.5, key="site_plan_sb_side_b")
        north = st.slider("North axis orientation (°)", 0.0, 359.0, float(_brief_value("north_angle_deg", 0.0)), 1.0, key="site_plan_north_angle")
        terrain = st.selectbox("Terrain profile", ["Flat (<2% slope)", "Gentle slope (2–8%)", "Moderate slope (8–15%)", "Steep slope (>15%)"], key="site_plan_terrain")
        analyze = st.button("Calculate buildable envelope", type="primary", use_container_width=True, key="site_plan_calc_btn")

    if site_width * site_depth <= 0 or plot_area <= 0:
        st.error("Site dimensions and area must be positive.")
        return
    if front + rear >= site_depth:
        st.error("Front and rear setbacks leave no buildable depth. Reduce setbacks or increase site depth.")
        return
    if side_a + side_b >= site_width:
        st.error("Side setbacks leave no buildable width. Reduce setbacks or increase site width.")
        return

    footprint = (site_width - side_a - side_b) * (site_depth - front - rear)
    stated_rectangle_area = site_width * site_depth
    area_factor = plot_area / stated_rectangle_area
    adjusted_footprint = footprint * area_factor if area_factor > 0 else 0.0
    coverage = 100.0 * adjusted_footprint / plot_area
    setback_area = max(0.0, plot_area - adjusted_footprint)

    if analyze:
        st.session_state["site_plan_result"] = {
            "plot_area_m2": plot_area,
            "site_width_m": site_width,
            "site_depth_m": site_depth,
            "buildable_width_m": site_width - side_a - side_b,
            "buildable_depth_m": site_depth - front - rear,
            "buildable_area_m2": adjusted_footprint,
            "coverage_pct": coverage,
            "north_angle_deg": north,
        }

    with right:
        if analyze:
            st.success("Buildable envelope calculated from the supplied dimensions and setbacks.")
        else:
            st.info("Review the envelope below. Click Calculate buildable envelope to store the current result for the architecture workflow.")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Plot Area", f"{plot_area:,.0f} m²")
        m2.metric("Buildable Footprint", f"{adjusted_footprint:,.0f} m²")
        m3.metric("Coverage", f"{coverage:.1f}%")
        m4.metric("Open / Setback Area", f"{setback_area:,.0f} m²")

        tab_map, tab_allocation, tab_terrain = st.tabs(["Envelope Plan", "Land Allocation", "Terrain & Orientation"])
        with tab_map:
            fig = go.Figure()
            fig.add_shape(type="rect", x0=0, y0=0, x1=site_width, y1=site_depth, line_width=2)
            fig.add_shape(type="rect", x0=side_a, y0=front, x1=site_width - side_b, y1=site_depth - rear, line_width=2)
            fig.add_annotation(x=site_width / 2, y=site_depth / 2, text="BUILDABLE ENVELOPE", showarrow=False)
            fig.add_annotation(x=site_width / 2, y=site_depth + max(site_depth * 0.04, 2), text=f"NORTH {north:.0f}°", showarrow=False)
            fig.update_xaxes(title="Width (m)", range=[-site_width * 0.05, site_width * 1.05], scaleanchor="y", scaleratio=1)
            fig.update_yaxes(title="Depth (m)", range=[-site_depth * 0.05, site_depth * 1.1])
            fig.update_layout(height=480, margin=dict(l=20, r=20, t=35, b=20), title="Dimension-based site envelope")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(pd.DataFrame([
                {"Parameter": "Buildable width", "Value": f"{site_width - side_a - side_b:.2f} m"},
                {"Parameter": "Buildable depth", "Value": f"{site_depth - front - rear:.2f} m"},
                {"Parameter": "Buildable area", "Value": f"{adjusted_footprint:,.2f} m²"},
            ]), use_container_width=True, hide_index=True)

        with tab_allocation:
            allocation = pd.DataFrame([
                {"Category": "Buildable footprint", "Area (m²)": adjusted_footprint, "Share (%)": coverage},
                {"Category": "Setback / open area", "Area (m²)": setback_area, "Share (%)": 100.0 - coverage},
            ])
            st.dataframe(allocation.round(2), use_container_width=True, hide_index=True)
            st.caption("Roads, parking, landscape and drainage should be allocated from an actual site plan. They are not deducted from the envelope automatically.")

        with tab_terrain:
            suitability = {"Flat (<2% slope)": "High", "Gentle slope (2–8%)": "Moderate", "Moderate slope (8–15%)": "Requires grading study", "Steep slope (>15%)": "Specialist geotechnical/grading study"}[terrain]
            st.metric("Terrain screening", suitability)
            st.metric("North orientation", f"{north:.0f}°")
            st.warning("Earthwork quantities are not estimated from footprint alone. Reliable cut/fill requires surveyed levels, proposed grades and a terrain surface model.")

    st.warning("This is a preliminary geometric envelope. It is not a cadastral boundary, GIS survey, planning approval or permit-ready site plan.")
