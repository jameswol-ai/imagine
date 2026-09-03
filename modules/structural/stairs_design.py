"""Preliminary structural stair design workspace for IMAGINE."""
from __future__ import annotations

import math
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def calculate_stairs(rise_mm: float, going_mm: float, width_m: float, storey_height_m: float, tread_thickness_mm: float, dead_load_kn_m2: float, imposed_load_kn_m2: float) -> dict[str, float]:
    steps = max(1, round(storey_height_m * 1000 / rise_mm))
    actual_rise = storey_height_m * 1000 / steps
    pitch = math.degrees(math.atan2(actual_rise, going_mm))
    flight_run_m = max(0.0, (steps - 1) * going_mm / 1000)
    slope_length_m = math.hypot(flight_run_m, storey_height_m)
    design_load = dead_load_kn_m2 + imposed_load_kn_m2
    line_load = design_load * width_m
    moment = line_load * slope_length_m**2 / 8
    shear = line_load * slope_length_m / 2
    return {"steps": float(steps), "rise_mm": actual_rise, "going_mm": going_mm, "pitch_deg": pitch, "flight_run_m": flight_run_m, "slope_length_m": slope_length_m, "design_load_kn_m2": design_load, "line_load_kn_m": line_load, "moment_knm": moment, "shear_kn": shear, "tread_thickness_mm": tread_thickness_mm}


def render() -> None:
    st.subheader("Stairs Design")
    st.caption("Preliminary stair geometry and load-path screening. Structural stair slabs, landings, supports and reinforcement require project-specific verification.")
    c1, c2, c3 = st.columns(3)
    with c1:
        storey = st.number_input("Storey height (m)", min_value=1.5, value=3.2, step=0.1)
        rise = st.number_input("Target riser (mm)", min_value=100.0, value=175.0, step=5.0)
        going = st.number_input("Going (mm)", min_value=200.0, value=280.0, step=5.0)
    with c2:
        width = st.number_input("Stair width (m)", min_value=0.8, value=1.2, step=0.1)
        thickness = st.number_input("Indicative waist thickness (mm)", min_value=100.0, value=180.0, step=10.0)
        imposed = st.number_input("Imposed load (kN/m²)", min_value=0.0, value=3.0, step=0.1)
    with c3:
        dead = st.number_input("Dead load allowance (kN/m²)", min_value=0.0, value=4.0, step=0.1)
        landing = st.number_input("Landing length (m)", min_value=0.5, value=1.5, step=0.1)
        st.info("Check local accessibility, fire and egress requirements separately.")
    if st.button("Calculate stair scheme", type="primary"):
        result = calculate_stairs(rise, going, width, storey, thickness, dead, imposed)
        result["landing_length_m"] = landing
        st.session_state["stairs_design_result"] = result
    result = st.session_state.get("stairs_design_result")
    if not result:
        return
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Risers", int(result["steps"]))
    m2.metric("Actual riser", f'{result["rise_mm"]:.0f} mm')
    m3.metric("Pitch", f'{result["pitch_deg"]:.1f}°')
    m4.metric("Slope length", f'{result["slope_length_m"]:.2f} m')
    tabs = st.tabs(["Geometry", "Actions", "Schedule"])
    with tabs[0]:
        x = [0.0]
        y = [0.0]
        for i in range(int(result["steps"])):
            x += [x[-1] + result["going_mm"] / 1000, x[-1]]
            y += [y[-1], y[-1] + result["rise_mm"] / 1000]
        fig = go.Figure(go.Scatter(x=x, y=y, mode="lines", line_width=3))
        fig.update_layout(height=360, xaxis_title="Run (m)", yaxis_title="Rise (m)", margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(pd.DataFrame([{k.replace("_", " ").title(): v for k, v in result.items()}]), use_container_width=True, hide_index=True)
    with tabs[1]:
        st.dataframe(pd.DataFrame([{"Action": "Serviceability / characteristic", "Load": result["design_load_kn_m2"]}, {"Action": "Indicative line load", "Load": result["line_load_kn_m"]}, {"Action": "Idealised max moment", "Load": result["moment_knm"]}, {"Action": "Idealised support shear", "Load": result["shear_kn"]}]), use_container_width=True, hide_index=True)
        st.caption("The idealised moment and shear use a simply supported slope-length model. They are not a complete stair or landing analysis.")
    with tabs[2]:
        st.dataframe(pd.DataFrame([{"Item": "Flight", "Quantity": 1, "Length": f'{result["slope_length_m"]:.2f} m'}, {"Item": "Risers", "Quantity": int(result["steps"]), "Length": f'{result["rise_mm"]:.0f} mm each'}, {"Item": "Treads", "Quantity": max(0, int(result["steps"])-1), "Length": f'{result["going_mm"]:.0f} mm each'}, {"Item": "Waist", "Quantity": 1, "Length": f'{result["tread_thickness_mm"]:.0f} mm indicative'}]), use_container_width=True, hide_index=True)
    st.warning("Preliminary only. Verify geometry, headroom, fire/egress, accessibility, vibration, support conditions, reinforcement, landings and applicable National Annex/project requirements before design use.")


__all__ = ["calculate_stairs", "render"]
