"""Interactive EN 1990-style load combination workspace.

Screening tool only. Project National Annex and combination factors must be verified.
"""
from __future__ import annotations
import pandas as pd
import streamlit as st
from modules.structural.ec0 import LoadSet, build_sls_combinations, build_uls_combinations


def render() -> None:
    st.title("Load Combinations")
    st.caption("Transparent EN 1990-style ULS and SLS combination generator for preliminary structural design.")
    c1, c2 = st.columns(2)
    with c1:
        g = st.number_input("Permanent action G (kN)", min_value=0.0, value=100.0, step=5.0)
        q = st.number_input("Leading variable action Q (kN)", min_value=0.0, value=50.0, step=5.0)
        qa = st.number_input("Accompanying variable action (kN)", min_value=0.0, value=0.0, step=5.0)
    with c2:
        wind = st.number_input("Wind W (kN)", min_value=0.0, value=0.0, step=5.0)
        snow = st.number_input("Snow S (kN)", min_value=0.0, value=0.0, step=5.0)
        psi0 = st.number_input("psi0", min_value=0.0, max_value=1.0, value=0.70, step=0.05)
    actions = LoadSet(g, q, qa, wind, snow)
    uls = build_uls_combinations(actions, psi0=psi0)
    sls = build_sls_combinations(actions, psi0=psi0)
    st.subheader("ULS")
    st.dataframe(pd.DataFrame(uls, columns=["Combination", "Action"]), use_container_width=True, hide_index=True)
    st.subheader("SLS")
    st.dataframe(pd.DataFrame(sls, columns=["Combination", "Action"]), use_container_width=True, hide_index=True)
    st.info("Screening defaults are not a substitute for the adopted EN 1990 National Annex or project-specific load combinations.")


__all__ = ["render"]
