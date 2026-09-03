"""Preliminary floor layout and space planning workspace."""

from __future__ import annotations

import math
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def render_floor_planning() -> None:
    """Calculate and store a traceable preliminary floor planning concept."""
    st.title("Floor Layout & Planning")
    st.caption("Preliminary area, circulation, core and structural-grid planning. Final layouts require architectural, fire and structural coordination.")

    assessment = st.session_state.get("architecture_assessment")
    program = st.session_state.get("room_program_result")
    default_area = float(program["gross_area_m2"]) if program else float(assessment.program_gross_area_m2) if assessment else 1250.0
    default_width = float(assessment.buildable_width_m) if assessment else 35.0
    default_depth = float(assessment.buildable_depth_m) if assessment else 25.0

    left, right = st.columns([1, 2], gap="large")
    with left:
        floor_area = st.number_input("Gross floor area (m²)", min_value=100.0, value=max(100.0, default_area), step=50.0, key="fp_gross_area")
        floor_width = st.number_input("Floor width (m)", min_value=5.0, value=max(5.0, default_width), step=1.0, key="fp_floor_width")
        floor_depth = st.number_input("Floor depth (m)", min_value=5.0, value=max(5.0, default_depth), step=1.0, key="fp_floor_depth")
        grid = st.slider("Column grid spacing (m)", 4.0, 12.0, 8.0, 0.5, key="fp_grid_spacing")
        circulation = st.slider("Circulation target (%)", 10, 35, 18, 1, key="fp_circulation_pct")
        core = st.number_input("Core area (m²)", min_value=20.0, value=150.0, step=10.0, key="fp_core_area")
        strategy = st.selectbox("Layout strategy", ["Central core", "Side core", "Dual cores", "Open plan"], key="fp_layout_strategy")
        generate = st.button("Generate floor concept", type="primary", use_container_width=True, key="fp_generate_btn")

    if core >= floor_area:
        st.error("Core area must be smaller than the gross floor area.")
        return

    usable_after_circulation = floor_area * (1.0 - circulation / 100.0)
    net_usable = max(0.0, usable_after_circulation - core)
    bays_x = max(1, math.ceil(floor_width / grid))
    bays_y = max(1, math.ceil(floor_depth / grid))
    columns = (bays_x + 1) * (bays_y + 1)
    perimeter = 2.0 * (floor_width + floor_depth)
    actual_rectangle = floor_width * floor_depth
    area_fit = floor_area / actual_rectangle

    result = {
        "gross_area_m2": floor_area,
        "net_usable_m2": net_usable,
        "grid_m": grid,
        "bays_x": bays_x,
        "bays_y": bays_y,
        "columns": columns,
        "perimeter_m": perimeter,
        "area_fit_ratio": area_fit,
        "strategy": strategy,
    }
    if generate:
        st.session_state["floor_planning_result"] = result

    with right:
        st.success(f"Preliminary {strategy.lower()} concept generated.") if generate else st.info("The floor concept responds to the current architecture program and envelope. Generate to store the structural-planning handoff.")
        if area_fit > 1.0:
            st.warning("The requested gross floor area exceeds the supplied floor rectangle. Increase the floor dimensions or reduce the target area.")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Gross area", f"{floor_area:,.0f} m²")
        m2.metric("Net usable", f"{net_usable:,.0f} m²")
        m3.metric("Grid", f"{bays_x} × {bays_y} bays")
        m4.metric("Indicative columns", columns)

        st.subheader("Floor geometry")
        fig = go.Figure()
        fig.add_shape(type="rect", x0=0, y0=0, x1=floor_width, y1=floor_depth, line_width=2)
        if strategy == "Central core":
            x0, x1 = floor_width * .4, floor_width * .6
            y0, y1 = floor_depth * .3, floor_depth * .7
        elif strategy == "Side core":
            x0, x1 = 0, floor_width * .2
            y0, y1 = floor_depth * .25, floor_depth * .75
        elif strategy == "Dual cores":
            x0, x1 = floor_width * .1, floor_width * .25
            y0, y1 = floor_depth * .3, floor_depth * .7
        else:
            x0, x1 = floor_width * .45, floor_width * .55
            y0, y1 = floor_depth * .45, floor_depth * .55
        fig.add_shape(type="rect", x0=x0, y0=y0, x1=x1, y1=y1, line_width=2)
        for x in [i * grid for i in range(1, bays_x) if i * grid < floor_width]:
            fig.add_vline(x=x, line_dash="dot")
        for y in [i * grid for i in range(1, bays_y) if i * grid < floor_depth]:
            fig.add_hline(y=y, line_dash="dot")
        fig.update_xaxes(title="Width (m)", scaleanchor="y", scaleratio=1)
        fig.update_yaxes(title="Depth (m)")
        fig.update_layout(height=430, title=f"Conceptual {strategy.lower()} floor geometry", margin=dict(l=20, r=20, t=45, b=20))
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Area and structural handoff")
        st.dataframe(pd.DataFrame([
            {"Component": "Gross floor area", "Area (m²)": floor_area, "Share (%)": 100.0},
            {"Component": "Circulation allowance", "Area (m²)": floor_area * circulation / 100.0, "Share (%)": float(circulation)},
            {"Component": "Core", "Area (m²)": core, "Share (%)": 100.0 * core / floor_area},
            {"Component": "Net planning area", "Area (m²)": net_usable, "Share (%)": 100.0 * net_usable / floor_area},
        ]).round(1), use_container_width=True, hide_index=True)
        st.dataframe(pd.DataFrame([
            {"Item": "Grid spacing", "Value": f"{grid:.1f} m", "Purpose": "Initial structural coordination"},
            {"Item": "Grid bays", "Value": f"{bays_x} × {bays_y}", "Purpose": "Initial column layout"},
            {"Item": "Indicative columns", "Value": str(columns), "Purpose": "Grid count only"},
            {"Item": "Perimeter", "Value": f"{perimeter:.1f} m", "Purpose": "Envelope coordination"},
        ]), use_container_width=True, hide_index=True)
        st.warning("This is a concept-planning model. It does not generate permit-ready drawings or prove fire, accessibility or structural compliance.")
