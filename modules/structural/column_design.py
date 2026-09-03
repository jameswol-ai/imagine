"""Streamlit adapter for the preliminary reinforced-concrete column engine."""

from __future__ import annotations

import math
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from modules.structural.rc_column import RCColumnScreeningEngine
from modules.utils.crud import CRUDService

STATE_KEY = "rc_column_designs"


def render() -> None:
    st.title("Reinforced Concrete Column Design")
    st.caption("Preliminary EN 1992-style axial capacity and slenderness screening. Full second-order and biaxial design remains project-specific.")

    tab_design, tab_schedule, tab_notes = st.tabs(["Column Designer", "Saved Schedule", "Scope & Notes"])
    with tab_design:
        left, right = st.columns([1, 1])
        with left:
            st.subheader("Geometry")
            b = st.number_input("Width b (mm)", min_value=150.0, value=350.0, step=25.0)
            h = st.number_input("Depth h (mm)", min_value=150.0, value=350.0, step=25.0)
            l0 = st.number_input("Unbraced length L0 (m)", min_value=1.0, value=3.6, step=0.1)
            cover = st.number_input("Nominal cover (mm)", min_value=15.0, value=35.0, step=5.0)
            st.subheader("Materials and reinforcement")
            fck = st.number_input("Concrete fck (MPa)", min_value=12.0, value=30.0, step=5.0)
            fyk = st.number_input("Steel fyk (MPa)", min_value=250.0, value=500.0, step=50.0)
            gamma_c = st.number_input("Concrete gamma_c", min_value=1.0, value=1.50, step=0.05)
            gamma_s = st.number_input("Steel gamma_s", min_value=1.0, value=1.15, step=0.05)
            bar_dia = st.number_input("Longitudinal bar diameter (mm)", min_value=8.0, value=20.0, step=2.0)
            bars_y = st.number_input("Bars along depth", min_value=2, value=3, step=1)
            bars_z = st.number_input("Bars along width", min_value=2, value=3, step=1)
            st.subheader("ULS action")
            n_ed = st.number_input("N_Ed (kN)", min_value=0.0, value=1200.0, step=50.0)
            mark = st.text_input("Column mark", value="C-101")
            submitted = st.button("Calculate column screening", type="primary", use_container_width=True)

        if submitted:
            total_bars = 2 * int(bars_y) + 2 * (int(bars_z) - 2)
            steel_area = math.pi * bar_dia**2 / 4.0 * total_bars
            try:
                result = RCColumnScreeningEngine().run({"width_mm": b, "depth_mm": h, "unbraced_length_m": l0, "fck_mpa": fck, "fyk_mpa": fyk, "gamma_c": gamma_c, "gamma_s": gamma_s, "n_ed_kn": n_ed, "steel_area_mm2": steel_area})
            except ValueError as exc:
                st.error(str(exc))
                return
            st.session_state["rc_column_last_result"] = result
            st.session_state["rc_column_last_record"] = {"mark": mark, "section": f"{b:.0f} x {h:.0f} mm", "n_ed_kn": n_ed, "steel_area_mm2": steel_area, "status": result.status}

        with right:
            result = st.session_state.get("rc_column_last_result")
            if result is None:
                st.info("Enter the design inputs and calculate a screening result.")
            else:
                st.subheader("Results")
                c1, c2, c3 = st.columns(3)
                c1.metric("Axial capacity", f"{result.axial_capacity_kn:.0f} kN")
                c2.metric("Axial utilisation", f"{result.axial_utilisation:.2f}")
                c3.metric("Status", result.status)
                table = pd.DataFrame([
                    ["Concrete area", result.concrete_area_mm2, "mm²"],
                    ["Provided steel", result.steel_area_mm2, "mm²"],
                    ["Minimum steel", result.minimum_steel_area_mm2, "mm²"],
                    ["Maximum steel", result.maximum_steel_area_mm2, "mm²"],
                    ["fcd", result.concrete_design_strength_mpa, "MPa"],
                    ["fyd", result.steel_design_strength_mpa, "MPa"],
                    ["lambda_y", result.slenderness_y, "ratio"],
                    ["lambda_z", result.slenderness_z, "ratio"],
                    ["lambda_lim", result.slenderness_limit, "ratio"],
                    ["e0,y", result.minimum_eccentricity_y_mm, "mm"],
                    ["e0,z", result.minimum_eccentricity_z_mm, "mm"],
                ], columns=["Parameter", "Value", "Unit"])
                st.dataframe(table, use_container_width=True, hide_index=True)
                fig = go.Figure(go.Bar(x=["N_Ed", "N_Rd,max"], y=[st.session_state["rc_column_last_record"]["n_ed_kn"], result.axial_capacity_kn]))
                fig.update_layout(height=280, yaxis_title="Axial force (kN)", margin=dict(l=10, r=10, t=20, b=10))
                st.plotly_chart(fig, use_container_width=True)
                if result.is_slender_y or result.is_slender_z:
                    st.warning("Slenderness screening is triggered. Apply the applicable second-order procedure in the project design.")
                elif result.status == "PASS":
                    st.success("Preliminary axial and reinforcement-limit screening passes.")
                else:
                    st.warning("Preliminary screening requires review.")
                if st.button("Save column to schedule", use_container_width=True):
                    items = CRUDService.get_all(STATE_KEY)
                    record = dict(st.session_state["rc_column_last_record"])
                    record["id"] = f"COL-{len(items) + 1:03d}"
                    CRUDService.create(STATE_KEY, record)
                    st.success("Column design saved.")

    with tab_schedule:
        items = CRUDService.get_all(STATE_KEY)
        if items:
            st.dataframe(pd.DataFrame(items), use_container_width=True, hide_index=True)
        else:
            st.info("No saved column designs yet.")

    with tab_notes:
        st.markdown("This adapter now delegates calculations to `RCColumnScreeningEngine`. The engine covers axial capacity, reinforcement limits, slenderness and minimum eccentricity. It does not certify EN 1992-1-1 compliance and does not implement full second-order, biaxial interaction, creep, fire, confinement, anchorage or detailing checks. Verify the applicable National Annex and project assumptions before engineering use.")


__all__ = ["render"]
