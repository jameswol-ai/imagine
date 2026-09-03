"""Streamlit workspace for preliminary EN 1994 composite design."""
from __future__ import annotations
import pandas as pd
import streamlit as st
from modules.structural.ec4 import CompositeBeamInput, design_composite_beam

def render() -> None:
    st.title("EN 1994 Composite Steel-Concrete Design")
    st.caption("Preliminary composite resistance screening. Verify construction stage, shear connectors, buckling, vibration, fire and the project National Annex.")
    left, right = st.columns([1, 1])
    with left:
        steel_area = st.number_input("Steel area (mm²)", min_value=100.0, value=6500.0, step=250.0)
        steel_fy = st.number_input("Steel fy (MPa)", min_value=200.0, value=355.0, step=5.0)
        concrete_area = st.number_input("Concrete compression area (mm²)", min_value=1000.0, value=180000.0, step=5000.0)
        concrete_fck = st.number_input("Concrete fck (MPa)", min_value=12.0, value=30.0, step=5.0)
        effective_width = st.number_input("Effective slab width (mm)", min_value=100.0, value=2500.0, step=100.0)
        steel_arm = st.number_input("Steel lever-arm coordinate (mm)", value=0.0, step=10.0)
        concrete_arm = st.number_input("Concrete lever-arm coordinate (mm)", value=180.0, step=10.0)
        axial = st.number_input("Axial demand (kN)", min_value=0.0, value=0.0, step=25.0)
        moment = st.number_input("Moment demand (kNm)", min_value=0.0, value=180.0, step=10.0)
        run = st.button("Calculate composite screening", type="primary", use_container_width=True)
    with right:
        if run:
            try:
                result = design_composite_beam(CompositeBeamInput(steel_area, steel_fy, concrete_area, concrete_fck, effective_width, steel_arm, concrete_arm, axial_demand_kn=axial, moment_demand_kn_m=moment))
            except ValueError as exc:
                st.error(str(exc)); return
            st.session_state["ec4_result"] = result
        result = st.session_state.get("ec4_result")
        if result:
            c1, c2, c3 = st.columns(3)
            c1.metric("Moment capacity", f"{result.simplified_moment_capacity_kn_m:.1f} kNm")
            c2.metric("Interaction", f"{result.interaction_utilisation:.2f}")
            c3.metric("Status", result.status)
            st.dataframe(pd.DataFrame([
                ["Steel capacity", result.steel_tension_capacity_kn, "kN"],
                ["Concrete capacity", result.concrete_compression_capacity_kn, "kN"],
                ["Composite compression", result.composite_compression_capacity_kn, "kN"],
                ["Axial utilisation", result.axial_utilisation, "ratio"],
                ["Moment utilisation", result.moment_utilisation, "ratio"],
            ], columns=["Check", "Value", "Unit"]), use_container_width=True, hide_index=True)
        else:
            st.info("Enter composite member inputs and calculate a screening result.")

__all__ = ["render"]
