"""Streamlit workspace for preliminary EN 1996 masonry wall screening."""
from __future__ import annotations
import pandas as pd
import streamlit as st
from modules.structural.ec6 import MasonryWallInput, screen_masonry_wall

def render() -> None:
    st.title("EN 1996 Masonry Wall Design")
    st.caption("Preliminary masonry wall axial resistance and slenderness screening. Verify the complete EN 1996 procedure and National Annex before use.")
    left, right = st.columns([1, 1])
    with left:
        thickness = st.number_input("Wall thickness (mm)", min_value=90.0, value=200.0, step=10.0)
        height = st.number_input("Wall height (m)", min_value=1.0, value=3.0, step=0.1)
        length = st.number_input("Wall length (m)", min_value=0.5, value=4.0, step=0.1)
        fm = st.number_input("Masonry compressive strength (MPa)", min_value=1.0, value=7.5, step=0.5)
        gamma = st.number_input("Masonry partial factor", min_value=1.0, value=2.0, step=0.1)
        axial = st.number_input("Axial demand (kN)", min_value=0.0, value=120.0, step=10.0)
        eccentricity = st.number_input("Eccentricity (mm)", min_value=0.0, value=10.0, step=5.0)
        run = st.button("Calculate masonry screening", type="primary", use_container_width=True)
    with right:
        if run:
            try:
                st.session_state["ec6_result"] = screen_masonry_wall(MasonryWallInput(thickness, height, length, fm, gamma, axial, eccentricity))
            except ValueError as exc:
                st.error(str(exc)); return
        result = st.session_state.get("ec6_result")
        if result:
            c1, c2, c3 = st.columns(3)
            c1.metric("Capacity", f"{result.capacity_kn:.0f} kN")
            c2.metric("Utilisation", f"{result.utilisation:.2f}")
            c3.metric("Status", result.status)
            st.dataframe(pd.DataFrame([
                ["Wall area", result.area_m2, "m²"],
                ["Design strength", result.design_compressive_strength_mpa, "MPa"],
                ["Slenderness", result.slenderness, "ratio"],
                ["Eccentricity ratio", result.eccentricity_ratio, "ratio"],
            ], columns=["Parameter", "Value", "Unit"]), use_container_width=True, hide_index=True)
        else:
            st.info("Enter wall inputs and calculate a screening result.")

__all__ = ["render"]
