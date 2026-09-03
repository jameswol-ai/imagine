"""Preliminary floor layout and space planning workspace."""

from __future__ import annotations

import math
import pandas as pd
import streamlit as st


def render_floor_planning() -> None:
    """Calculate a traceable preliminary floor planning concept."""
    st.title("Floor Layout & Planning")
    st.caption("Preliminary area, circulation, core and structural-grid planning. Final layouts require architectural, fire and structural coordination.")

    left, right = st.columns([1, 2], gap="large")
    with left:
        floor_area = st.number_input("Gross floor area (m²)", min_value=100.0, value=1250.0, step=50.0, key="fp_gross_area")
        floor_width = st.number_input("Floor width (m)", min_value=5.0, value=35.0, step=1.0, key="fp_floor_width")
        floor_depth = st.number_input("Floor depth (m)", min_value=5.0, value=25.0, step=1.0, key="fp_floor_depth")
        grid = st.slider("Column grid spacing (m)", 4.0, 12.0, 8.0, 0.5, key="fp_grid_spacing")
        circulation = st.slider("Circulation target (%)", 10, 35, 18, 1, key="fp_circulation_pct")
        core = st.number_input("Core area (m²)", min_value=20.0, value=150.0, step=10.0, key="fp_core_area")
        strategy = st.selectbox("Layout strategy", ["Central core", "Side core", "Dual cores", "Open plan"], key="fp_layout_strategy")
        generate = st.button("Generate floor concept", type="primary", use_container_width=True, key="fp_generate_btn")

    usable_after_circulation = floor_area * (1.0 - circulation / 100.0)
    net_usable = max(0.0, usable_after_circulation - core)
    bays_x = max(1, math.ceil(floor_width / grid))
    bays_y = max(1, math.ceil(floor_depth / grid))
    columns = (bays_x + 1) * (bays_y + 1)
    perimeter_ratio = 2.0 * (floor_width + floor_depth)

    with right:
        if generate:
            st.success(f"Preliminary {strategy.lower()} concept generated from the supplied geometry.")
        else:
            st.info("Set the floor geometry and generate a concept to review the calculated planning metrics.")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Gross area", f"{floor_area:,.0f} m²")
        m2.metric("Net usable", f"{net_usable:,.0f} m²")
        m3.metric("Grid", f"{bays_x} × {bays_y} bays")
        m4.metric("Indicative columns", columns)

        st.subheader("Area and planning schedule")
        schedule = pd.DataFrame([
            {"Component": "Gross floor area", "Area (m²)": floor_area, "Share": 100.0},
            {"Component": "Circulation allowance", "Area (m²)": floor_area * circulation / 100.0, "Share": float(circulation)},
            {"Component": "Core", "Area (m²)": core, "Share": 100.0 * core / floor_area},
            {"Component": "Net planning area", "Area (m²)": net_usable, "Share": 100.0 * net_usable / floor_area},
        ])
        st.dataframe(schedule.round(1), use_container_width=True, hide_index=True)

        st.subheader("Structural and circulation handoff")
        st.dataframe(pd.DataFrame([
            {"Item": "Grid spacing", "Value": f"{grid:.1f} m", "Purpose": "Initial structural coordination"},
            {"Item": "Grid bays", "Value": f"{bays_x} × {bays_y}", "Purpose": "Initial column layout"},
            {"Item": "Indicative columns", "Value": str(columns), "Purpose": "Grid count only"},
            {"Item": "Perimeter", "Value": f"{perimeter_ratio:.1f} m", "Purpose": "Envelope coordination"},
        ]), use_container_width=True, hide_index=True)
        st.warning("This is a concept-planning model. It does not generate a permit-ready architectural drawing or prove fire egress compliance.")
