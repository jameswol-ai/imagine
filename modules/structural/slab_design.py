"""Streamlit adapter for the preliminary reinforced-concrete slab engine."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from modules.structural.rc_slab import RCSLabDesignEngine, SlabDesignInput
from modules.utils.crud import CRUDService

STATE_KEY = "rc_slab_designs"


def render() -> None:
    st.title("Reinforced Concrete Slab Design")
    st.caption("Preliminary EN 1992-style one-way/two-way slab screening with shared action combinations and EC2 primitives.")
    tab_design, tab_schedule, tab_notes = st.tabs(["Slab Designer", "Saved Schedule", "Scope & Notes"])

    with tab_design:
        left, right = st.columns([1, 1])
        with left:
            st.subheader("Geometry and support")
            slab_type = st.selectbox("Slab type", ["One-Way Slab", "Two-Way Rectangular Slab"])
            lx = st.number_input("Short span Lx (m)", min_value=1.0, value=4.0, step=0.25)
            ly_default = 5.5 if slab_type == "Two-Way Rectangular Slab" else 8.0
            ly = st.number_input("Long span Ly (m)", min_value=1.0, value=ly_default, step=0.25)
            thickness = st.number_input("Thickness h (mm)", min_value=80.0, value=175.0, step=5.0)
            cover = st.number_input("Nominal cover (mm)", min_value=15.0, value=25.0, step=5.0)
            support = st.selectbox("Support condition", ["Simply Supported", "One End Continuous", "Both Ends Continuous", "Cantilever"])
            st.subheader("Loads and materials")
            permanent = st.number_input("Additional permanent load (kN/m²)", min_value=0.0, value=4.0, step=0.5)
            imposed = st.number_input("Imposed load (kN/m²)", min_value=0.0, value=3.0, step=0.5)
            fck = st.number_input("Concrete fck (MPa)", min_value=12.0, value=30.0, step=5.0)
            fyk = st.number_input("Steel fyk (MPa)", min_value=250.0, value=500.0, step=50.0)
            gamma_c = st.number_input("Concrete gamma_c", min_value=1.0, value=1.50, step=0.05)
            gamma_s = st.number_input("Steel gamma_s", min_value=1.0, value=1.15, step=0.05)
            psi0 = st.number_input("psi0", min_value=0.0, max_value=1.0, value=0.70, step=0.05)
            st.subheader("Reinforcement")
            dia_x = st.number_input("X bar diameter (mm)", min_value=8.0, value=10.0, step=2.0)
            spacing_x = st.number_input("X spacing (mm)", min_value=75.0, value=200.0, step=25.0)
            dia_y = st.number_input("Y bar diameter (mm)", min_value=8.0, value=10.0, step=2.0)
            spacing_y = st.number_input("Y spacing (mm)", min_value=75.0, value=200.0, step=25.0)
            mark = st.text_input("Slab mark", value="S-101")
            submitted = st.button("Calculate slab screening", type="primary", use_container_width=True)

        if submitted:
            try:
                result = RCSLabDesignEngine.run(SlabDesignInput(lx_m=lx, ly_m=ly, thickness_mm=thickness, cover_mm=cover, slab_type=slab_type, support_condition=support, permanent_load_kn_m2=permanent, imposed_load_kn_m2=imposed, fck_mpa=fck, fyk_mpa=fyk, gamma_c=gamma_c, gamma_s=gamma_s, psi0=psi0, bar_dia_x_mm=dia_x, spacing_x_mm=spacing_x, bar_dia_y_mm=dia_y, spacing_y_mm=spacing_y))
            except ValueError as exc:
                st.error(str(exc))
                return
            st.session_state["rc_slab_last_result"] = result
            st.session_state["rc_slab_last_record"] = {"mark": mark, "lx_m": lx, "ly_m": ly, "thickness_mm": thickness, "uls_load_kn_m2": result.uls_load_kn_m2, "as_x_mm2_m": result.as_provided_x_mm2_m, "as_y_mm2_m": result.as_provided_y_mm2_m, "status": "PASS" if result.overall_ok else "REVIEW"}

        with right:
            result = st.session_state.get("rc_slab_last_result")
            if result is None:
                st.info("Enter inputs and calculate a screening result.")
            else:
                st.subheader("Results")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("ULS load", f"{result.uls_load_kn_m2:.1f} kN/m²")
                c2.metric("Mx", f"{result.moment_x_kn_m:.1f} kNm/m")
                c3.metric("My", f"{result.moment_y_kn_m:.1f} kNm/m")
                c4.metric("Status", "PASS" if result.overall_ok else "REVIEW")
                table = pd.DataFrame([
                    ["Aspect ratio", result.aspect_ratio, "ratio"],
                    ["Self-weight", result.self_weight_kn_m2, "kN/m²"],
                    ["ULS load", result.uls_load_kn_m2, "kN/m²"],
                    ["SLS load", result.sls_load_kn_m2, "kN/m²"],
                    ["Effective depth x", result.effective_depth_x_mm, "mm"],
                    ["Effective depth y", result.effective_depth_y_mm, "mm"],
                    ["Required As x", result.as_required_x_mm2_m, "mm²/m"],
                    ["Provided As x", result.as_provided_x_mm2_m, "mm²/m"],
                    ["Required As y", result.as_required_y_mm2_m, "mm²/m"],
                    ["Provided As y", result.as_provided_y_mm2_m, "mm²/m"],
                    ["Shear stress", result.shear_stress_mpa, "MPa"],
                    ["Shear resistance", result.vrdc_mpa, "MPa"],
                    ["Actual L/d", result.actual_ld, "ratio"],
                    ["Allowable L/d", result.allowable_ld, "ratio"],
                    ["ULS combination", result.governing_uls_name, ""],
                    ["SLS combination", result.governing_sls_name, ""],
                ], columns=["Parameter", "Value", "Unit"])
                st.dataframe(table, use_container_width=True, hide_index=True)
                fig = go.Figure(go.Bar(x=["As x required", "As x provided", "As y required", "As y provided"], y=[result.as_required_x_mm2_m, result.as_provided_x_mm2_m, result.as_required_y_mm2_m, result.as_provided_y_mm2_m]))
                fig.update_layout(height=280, yaxis_title="Reinforcement (mm²/m)", margin=dict(l=10, r=10, t=20, b=10))
                st.plotly_chart(fig, use_container_width=True)
                checks = {"Flexure X": result.flexure_x_ok, "Flexure Y": result.flexure_y_ok, "Shear": result.shear_ok, "Deflection": result.deflection_ok}
                st.write("Check status")
                st.dataframe(pd.DataFrame([{"Check": k, "Status": "PASS" if v else "REVIEW"} for k, v in checks.items()]), use_container_width=True, hide_index=True)
                if st.button("Save slab to schedule", use_container_width=True):
                    items = CRUDService.get_all(STATE_KEY)
                    record = dict(st.session_state["rc_slab_last_record"])
                    record["id"] = f"SLAB-{len(items) + 1:03d}"
                    CRUDService.create(STATE_KEY, record)
                    st.success("Slab design saved.")

    with tab_schedule:
        items = CRUDService.get_all(STATE_KEY)
        if items:
            st.dataframe(pd.DataFrame(items), use_container_width=True, hide_index=True)
        else:
            st.info("No saved slab designs yet.")

    with tab_notes:
        st.markdown("The calculation engine is intentionally transparent and deterministic. The two-way coefficients, shear model and span/depth screening are simplified preliminary checks. They do not replace project-specific EN 1992 design, punching shear, crack control, detailing, National Annex values or professional verification.")


__all__ = ["render"]
