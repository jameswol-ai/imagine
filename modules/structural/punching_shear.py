"""Streamlit adapter for the preliminary punching-shear engine."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from modules.structural.punching_engine import PunchingShearInput, verify_punching_shear
from modules.utils.crud import CRUDService

STATE_KEY = "punching_shear_verifications"


def render() -> None:
    st.title("Punching Shear Verification")
    st.caption("Preliminary RC punching-shear screening around an internal rectangular column control perimeter.")
    tab_check, tab_schedule, tab_notes = st.tabs(["Verification", "Saved Records", "Scope & Notes"])

    with tab_check:
        left, right = st.columns([1, 1])
        with left:
            st.subheader("Geometry")
            c1 = st.number_input("Column width c1 (mm)", min_value=150.0, value=400.0, step=25.0)
            c2 = st.number_input("Column length c2 (mm)", min_value=150.0, value=400.0, step=25.0)
            d = st.number_input("Effective depth d (mm)", min_value=75.0, value=210.0, step=5.0)
            perimeter_factor = st.number_input("Control perimeter factor", min_value=1.0, value=4.0, step=0.5)
            st.subheader("Actions and reinforcement")
            ved = st.number_input("Applied shear V_Ed (kN)", min_value=0.0, value=650.0, step=25.0)
            as_tension = st.number_input("Tension reinforcement As (mm²)", min_value=0.0, value=1800.0, step=50.0)
            fck = st.number_input("Concrete fck (MPa)", min_value=12.0, value=30.0, step=5.0)
            gamma_c = st.number_input("Concrete gamma_c", min_value=1.0, value=1.50, step=0.05)
            mark = st.text_input("Element mark", value="SLAB-P1")
            submitted = st.button("Calculate punching check", type="primary", use_container_width=True)

        if submitted:
            try:
                result = verify_punching_shear(PunchingShearInput(column_width_mm=c1, column_length_mm=c2, effective_depth_mm=d, applied_shear_kn=ved, tension_steel_mm2=as_tension, control_perimeter_factor=perimeter_factor, fck_mpa=fck, gamma_c=gamma_c))
            except ValueError as exc:
                st.error(str(exc))
                return
            st.session_state["punching_last_result"] = result
            st.session_state["punching_last_record"] = {"mark": mark, "v_ed_kn": ved, "perimeter_mm": result.control_perimeter_mm, "stress_mpa": result.shear_stress_mpa, "resistance_mpa": result.resistance_mpa, "utilisation": result.utilisation, "status": "PASS" if result.ok else "REVIEW"}

        with right:
            result = st.session_state.get("punching_last_result")
            if result is None:
                st.info("Enter inputs and calculate a verification.")
            else:
                c1m, c2m, c3m = st.columns(3)
                c1m.metric("v_Ed", f"{result.shear_stress_mpa:.3f} MPa")
                c2m.metric("v_Rd,c", f"{result.resistance_mpa:.3f} MPa")
                c3m.metric("Utilisation", f"{result.utilisation:.2f}")
                st.dataframe(pd.DataFrame([
                    ["Control perimeter", result.control_perimeter_mm, "mm"],
                    ["Shear stress", result.shear_stress_mpa, "MPa"],
                    ["Concrete resistance", result.resistance_mpa, "MPa"],
                    ["Utilisation", result.utilisation, "ratio"],
                    ["Status", "PASS" if result.ok else "REVIEW", ""],
                ], columns=["Parameter", "Value", "Unit"]), use_container_width=True, hide_index=True)
                if result.ok:
                    st.success("Preliminary punching-shear screening passes.")
                else:
                    st.warning("Punching-shear screening requires review or a shear-reinforcement/design revision.")
                if st.button("Save punching verification", use_container_width=True):
                    items = CRUDService.get_all(STATE_KEY)
                    record = dict(st.session_state["punching_last_record"])
                    record["id"] = f"PS-{len(items) + 1:03d}"
                    CRUDService.create(STATE_KEY, record)
                    st.success("Verification saved.")

    with tab_schedule:
        items = CRUDService.get_all(STATE_KEY)
        if items:
            st.dataframe(pd.DataFrame(items), use_container_width=True, hide_index=True)
        else:
            st.info("No saved punching-shear records yet.")

    with tab_notes:
        st.markdown("This adapter delegates the calculation to `punching_engine.verify_punching_shear`. The engine is a preliminary screening primitive. It does not implement the complete EN 1992-1-1 Clause 6.4 perimeter construction, moment transfer, openings, edge/corner conditions, shear reinforcement design, maximum shear checks or National Annex provisions.")


__all__ = ["render"]
