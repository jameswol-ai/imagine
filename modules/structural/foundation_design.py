"""Streamlit adapter for the preliminary RC pad footing engine."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from modules.structural.ec7 import Soil
from modules.structural.rc_foundation import PadFootingInput, RCPadFootingDesignEngine
from modules.utils.crud import CRUDService

STATE_KEY = "pad_footing_designs"


def render() -> None:
    st.title("Reinforced Concrete Pad Footing Design")
    st.caption("Preliminary EN 1997/EN 1992-style bearing, eccentricity, flexure and one-way shear screening.")
    tab_design, tab_schedule, tab_notes = st.tabs(["Footing Designer", "Saved Schedule", "Scope & Notes"])

    with tab_design:
        left, right = st.columns([1, 1])
        with left:
            st.subheader("Geometry")
            width = st.number_input("Footing width B (m)", min_value=0.8, value=2.2, step=0.1)
            length = st.number_input("Footing length L (m)", min_value=0.8, value=2.2, step=0.1)
            depth = st.number_input("Footing thickness H (m)", min_value=0.3, value=0.60, step=0.05)
            col_w = st.number_input("Column width (m)", min_value=0.15, value=0.40, step=0.05)
            col_l = st.number_input("Column length (m)", min_value=0.15, value=0.40, step=0.05)
            cover = st.number_input("Nominal cover (mm)", min_value=25.0, value=50.0, step=5.0)
            st.subheader("Soil")
            allowable = st.number_input("Allowable bearing capacity (kPa)", min_value=50.0, value=200.0, step=10.0)
            soil_gamma = st.number_input("Soil unit weight (kN/m³)", min_value=10.0, value=18.0, step=0.5)
            cohesion = st.number_input("Cohesion c' (kPa)", min_value=0.0, value=10.0, step=1.0)
            phi = st.number_input("Friction angle phi' (degrees)", min_value=0.0, max_value=89.0, value=30.0, step=1.0)
            st.subheader("Materials and loads")
            fck = st.number_input("Concrete fck (MPa)", min_value=12.0, value=30.0, step=5.0)
            fyk = st.number_input("Steel fyk (MPa)", min_value=250.0, value=500.0, step=50.0)
            gamma_c = st.number_input("Concrete gamma_c", min_value=1.0, value=1.50, step=0.05)
            gamma_s = st.number_input("Steel gamma_s", min_value=1.0, value=1.15, step=0.05)
            permanent = st.number_input("Permanent axial load (kN)", min_value=0.0, value=700.0, step=25.0)
            imposed = st.number_input("Imposed axial load (kN)", min_value=0.0, value=250.0, step=25.0)
            mx = st.number_input("Moment Mx (kNm)", value=65.0, step=5.0)
            my = st.number_input("Moment My (kNm)", value=30.0, step=5.0)
            bar_dia = st.number_input("Footing bar diameter (mm)", min_value=8.0, value=16.0, step=2.0)
            spacing = st.number_input("Bar spacing (mm)", min_value=75.0, value=200.0, step=25.0)
            psi0 = st.number_input("psi0", min_value=0.0, max_value=1.0, value=0.70, step=0.05)
            mark = st.text_input("Footing mark", value="F-101")
            submitted = st.button("Calculate footing screening", type="primary", use_container_width=True)

        if submitted:
            try:
                soil = Soil(soil_gamma, cohesion, phi, allowable)
                result = RCPadFootingDesignEngine.run(PadFootingInput(width_m=width, length_m=length, depth_m=depth, column_width_m=col_w, column_length_m=col_l, cover_mm=cover, permanent_load_kn=permanent, imposed_load_kn=imposed, moment_x_kn_m=mx, moment_y_kn_m=my, soil=soil, fck_mpa=fck, fyk_mpa=fyk, bar_dia_mm=bar_dia, spacing_mm=spacing, gamma_c=gamma_c, gamma_s=gamma_s, psi0=psi0))
            except ValueError as exc:
                st.error(str(exc))
                return
            st.session_state["pad_last_result"] = result
            st.session_state["pad_last_record"] = {"mark": mark, "width_m": width, "length_m": length, "uls_axial_kn": result.uls_axial_kn, "q_max_kpa": result.q_max_kpa, "bearing_utilisation": result.bearing_utilisation, "status": "PASS" if result.overall_ok else "REVIEW"}

        with right:
            result = st.session_state.get("pad_last_result")
            if result is None:
                st.info("Enter inputs and calculate a screening result.")
            else:
                st.subheader("Results")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("ULS axial", f"{result.uls_axial_kn:.0f} kN")
                c2.metric("qmax", f"{result.q_max_kpa:.1f} kPa")
                c3.metric("Bearing utilisation", f"{result.bearing_utilisation:.2f}")
                c4.metric("Status", "PASS" if result.overall_ok else "REVIEW")
                table = pd.DataFrame([
                    ["Eccentricity x", result.eccentricity_x_m, "m"],
                    ["Eccentricity y", result.eccentricity_y_m, "m"],
                    ["qmax", result.q_max_kpa, "kPa"],
                    ["qmin", result.q_min_kpa, "kPa"],
                    ["Allowable bearing", result.allowable_bearing_kpa, "kPa"],
                    ["Design moment x", result.design_moment_x_kn_m, "kNm"],
                    ["Design moment y", result.design_moment_y_kn_m, "kNm"],
                    ["Effective depth", result.effective_depth_mm, "mm"],
                    ["Required As x", result.as_required_x_mm2_m, "mm²/m"],
                    ["Required As y", result.as_required_y_mm2_m, "mm²/m"],
                    ["Provided As", result.as_provided_mm2_m, "mm²/m"],
                    ["Shear stress", result.one_way_shear_stress_mpa, "MPa"],
                    ["Shear resistance", result.vrdc_mpa, "MPa"],
                ], columns=["Parameter", "Value", "Unit"])
                st.dataframe(table, use_container_width=True, hide_index=True)
                fig = go.Figure(go.Bar(x=["qmin", "qmax", "qallow"], y=[result.q_min_kpa, result.q_max_kpa, result.allowable_bearing_kpa]))
                fig.update_layout(height=280, yaxis_title="Pressure (kPa)", margin=dict(l=10, r=10, t=20, b=10))
                st.plotly_chart(fig, use_container_width=True)
                checks = {"Bearing": result.bearing_ok, "Flexure": result.flexure_ok, "One-way shear": result.shear_ok}
                st.dataframe(pd.DataFrame([{"Check": k, "Status": "PASS" if v else "REVIEW"} for k, v in checks.items()]), use_container_width=True, hide_index=True)
                if st.button("Save footing to schedule", use_container_width=True):
                    items = CRUDService.get_all(STATE_KEY)
                    record = dict(st.session_state["pad_last_record"])
                    record["id"] = f"F-{len(items) + 1:03d}"
                    CRUDService.create(STATE_KEY, record)
                    st.success("Footing design saved.")

    with tab_schedule:
        items = CRUDService.get_all(STATE_KEY)
        if items:
            st.dataframe(pd.DataFrame(items), use_container_width=True, hide_index=True)
        else:
            st.info("No saved footing designs yet.")

    with tab_notes:
        st.markdown("The calculation engine is a preliminary screening implementation. Bearing resistance is simplified and the structural shear/flexure model is not a complete foundation design. Settlement, sliding, groundwater, soil layering, effective dimensions, load eccentricity combinations, punching shear, detailing, National Annex values and project geotechnical requirements must be verified by the engineer of record.")


__all__ = ["render"]
