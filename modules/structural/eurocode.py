"""Eurocode load-combination workspace backed by the reusable EC0 engine."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from modules.structural.ec0 import (
    DEFAULT_PSI,
    LoadSet,
    build_uls_combinations,
    build_sls_combinations,
    governing_combination,
)


MATERIAL_FACTORS = {
    "Concrete C30/37": {"gamma_c": 1.5, "alpha_cc": 0.85, "fck": 30.0},
    "Steel S355": {"gamma_s": 1.15, "fyk": 355.0},
}


def compute_combinations(loads, material=None):
    """Compatibility wrapper returning the historical dataframe-based API."""
    load_set = LoadSet(
        permanent=float(loads.get("G", 0.0)),
        leading_variable=float(loads.get("Q_leading", 0.0)),
        accompanying_variable=float(loads.get("Q_acc", 0.0)),
        wind=float(loads.get("wind", 0.0)),
        snow=float(loads.get("snow", 0.0)),
    )
    uls_df = pd.DataFrame(build_uls_combinations(load_set, psi0=DEFAULT_PSI), columns=["Combination", "Value"])
    sls_df = pd.DataFrame(build_sls_combinations(load_set, psi0=DEFAULT_PSI), columns=["Combination", "Value"])
    gov_uls = governing_combination(build_uls_combinations(load_set, psi0=DEFAULT_PSI))
    gov_sls = governing_combination(build_sls_combinations(load_set, psi0=DEFAULT_PSI))

    mat_resistance = "Not available"
    if material in MATERIAL_FACTORS:
        data = MATERIAL_FACTORS[material]
        if "fck" in data:
            fcd = data["alpha_cc"] * data["fck"] / data["gamma_c"]
            mat_resistance = f"f_cd = {fcd:.1f} MPa"
        else:
            fyd = data["fyk"] / data["gamma_s"]
            mat_resistance = f"f_yd = {fyd:.1f} MPa"
    return uls_df, gov_uls, sls_df, gov_sls, mat_resistance


def render():
    st.subheader("Eurocode Load Combination Calculator")
    st.caption("Reusable EN 1990-style combination engine. National Annex parameters must be verified for the project jurisdiction.")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Characteristic actions**")
        G = st.number_input("Permanent action G (kN/m²)", value=5.0, step=0.5)
        Q = st.number_input("Leading variable action Q (kN/m²)", value=3.0, step=0.5)
        Q_acc = st.number_input("Accompanying variable action (kN/m²)", value=2.0, step=0.5)
        wind = st.number_input("Wind action (kN/m²)", value=0.8, step=0.1)
        snow = st.number_input("Snow action (kN/m²)", value=0.5, step=0.1)
    with c2:
        material = st.selectbox("Material", list(MATERIAL_FACTORS))
        psi0 = st.number_input("ψ₀", min_value=0.0, max_value=1.0, value=DEFAULT_PSI, step=0.05)
        st.info("The displayed defaults are screening values, not a substitute for the applicable National Annex.")

    if st.button("Calculate load combinations", type="primary"):
        load_set = LoadSet(G, Q, Q_acc, wind, snow)
        uls = build_uls_combinations(load_set, psi0=psi0)
        sls = build_sls_combinations(load_set, psi0=psi0)
        gov_uls = governing_combination(uls)
        gov_sls = governing_combination(sls)
        uls_df = pd.DataFrame(uls, columns=["Combination", "Value"])
        sls_df = pd.DataFrame(sls, columns=["Combination", "Value"])

        st.subheader("ULS")
        st.dataframe(uls_df, use_container_width=True, hide_index=True)
        st.metric("Governing ULS", gov_uls[0], f"{gov_uls[1]:.2f} kN/m²")

        st.subheader("SLS screening")
        st.dataframe(sls_df, use_container_width=True, hide_index=True)
        st.metric("Governing SLS", gov_sls[0], f"{gov_sls[1]:.2f} kN/m²")

        data = MATERIAL_FACTORS[material]
        if "fck" in data:
            resistance = data["alpha_cc"] * data["fck"] / data["gamma_c"]
            st.info(f"{material}: f_cd = {resistance:.1f} MPa")
        else:
            resistance = data["fyk"] / data["gamma_s"]
            st.info(f"{material}: f_yd = {resistance:.1f} MPa")

        combined = pd.concat([uls_df.assign(Type="ULS"), sls_df.assign(Type="SLS")])
        st.download_button("Download results as CSV", combined.to_csv(index=False), "eurocode_combinations.csv", "text/csv")


__all__ = ["compute_combinations", "render"]
