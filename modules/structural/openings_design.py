"""Preliminary structural opening and lintel screening workspace."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def calculate_opening(width_m: float, height_m: float, wall_thickness_mm: float, tributary_width_m: float, masonry_dead_kn_m2: float, imposed_kn_m2: float, lintel_depth_mm: float) -> dict[str, float]:
    opening_area = width_m * height_m
    tributary_area = width_m * tributary_width_m
    service_load = tributary_area * (masonry_dead_kn_m2 + imposed_kn_m2)
    lintel_span = width_m + 0.30
    line_load = service_load / max(lintel_span, 0.1)
    moment = line_load * lintel_span**2 / 8
    shear = line_load * lintel_span / 2
    return {"opening_area_m2": opening_area, "lintel_span_m": lintel_span, "tributary_area_m2": tributary_area, "service_load_kn": service_load, "line_load_kn_m": line_load, "moment_knm": moment, "shear_kn": shear, "wall_thickness_mm": wall_thickness_mm, "lintel_depth_mm": lintel_depth_mm}


def render() -> None:
    st.subheader("Openings Design")
    st.caption("Preliminary structural coordination for wall openings, lintels and load paths.")
    c1, c2, c3 = st.columns(3)
    with c1:
        width = st.number_input("Opening width (m)", min_value=0.3, value=1.2, step=0.1)
        height = st.number_input("Opening height (m)", min_value=0.3, value=2.1, step=0.1)
    with c2:
        wall = st.number_input("Wall thickness (mm)", min_value=75.0, value=200.0, step=25.0)
        tributary = st.number_input("Tributary wall height (m)", min_value=0.5, value=2.5, step=0.1)
    with c3:
        masonry = st.number_input("Wall load allowance (kN/m²)", min_value=0.0, value=8.0, step=0.5)
        imposed = st.number_input("Additional imposed load (kN/m²)", min_value=0.0, value=0.0, step=0.5)
        lintel = st.number_input("Indicative lintel depth (mm)", min_value=100.0, value=200.0, step=10.0)
    if st.button("Assess opening", type="primary"):
        st.session_state["opening_design_result"] = calculate_opening(width, height, wall, tributary, masonry, imposed, lintel)
    result = st.session_state.get("opening_design_result")
    if not result:
        return
    a, b, c, d = st.columns(4)
    a.metric("Opening", f'{width:.2f} × {height:.2f} m')
    b.metric("Lintel span", f'{result["lintel_span_m"]:.2f} m')
    c.metric("Service load", f'{result["service_load_kn"]:.1f} kN')
    d.metric("Moment", f'{result["moment_knm"]:.2f} kNm')
    tabs = st.tabs(["Opening", "Lintel actions", "Coordination"])
    with tabs[0]:
        fig = go.Figure()
        fig.add_shape(type="rect", x0=0, y0=0, x1=result["wall_thickness_mm"]/1000, y1=height)
        fig.add_shape(type="rect", x0=0, y0=0, x1=result["wall_thickness_mm"]/1000, y1=0.15, fillcolor="rgba(100,100,100,.25)")
        fig.update_layout(height=350, title="Conceptual wall/opening elevation", xaxis_title="Wall depth (m)", yaxis_title="Height (m)", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with tabs[1]:
        st.dataframe(pd.DataFrame([{"Parameter": "Service load", "Value": result["service_load_kn"], "Unit": "kN"}, {"Parameter": "Line load", "Value": result["line_load_kn_m"], "Unit": "kN/m"}, {"Parameter": "Idealised moment", "Value": result["moment_knm"], "Unit": "kNm"}, {"Parameter": "Idealised shear", "Value": result["shear_kn"], "Unit": "kN"}]), use_container_width=True, hide_index=True)
    with tabs[2]:
        st.dataframe(pd.DataFrame({"Coordination item": ["Opening dimensions", "Wall material and thickness", "Lintel bearing", "Loads from floors/roof above", "Services penetrations", "Fire/acoustic requirements", "Construction sequence"], "Status": ["Review"] * 7}), use_container_width=True, hide_index=True)
    st.warning("Opening loads are simplified screening assumptions. Check masonry/RC/steel lintel resistance, bearings, concentrated loads, stability, fire and service penetrations using the applicable material standard and project information.")


__all__ = ["calculate_opening", "render"]
