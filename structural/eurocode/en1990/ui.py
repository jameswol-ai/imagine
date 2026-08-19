"""
Structural Eurocode 0 (EN 1990) UI Renderer Module
Path: structural/eurocode/en1990/ui.py
App: imagine
"""

import pandas as pd
import streamlit as st


def render_en1990() -> None:
    """Renders the EN 1990 Basis of Structural Design and Load Combinations interface."""

    st.write(
        "Calculate ULS and SLS partial safety factor load combinations (Expressions 6.10, 6.10a, 6.10b) "
        "and combination factors (ψ) per EN 1990."
    )

    # --- CATEGORY & PSI FACTOR TABLE (EN 1990 Table A1.1) ---
    psi_table = {
        "Category A: Domestic, residential": {"psi_0": 0.7, "psi_1": 0.5, "psi_2": 0.3},
        "Category B: Office areas": {"psi_0": 0.7, "psi_1": 0.5, "psi_2": 0.3},
        "Category C: Congregation areas": {"psi_0": 0.7, "psi_1": 0.7, "psi_2": 0.6},
        "Category D: Shopping areas": {"psi_0": 0.7, "psi_1": 0.7, "psi_2": 0.6},
        "Category E: Storage areas": {"psi_0": 1.0, "psi_1": 0.9, "psi_2": 0.8},
        "Category F: Traffic area (vehicle weight <= 30kN)": {"psi_0": 0.7, "psi_1": 0.7, "psi_2": 0.6},
        "Category G: Traffic area (30kN < vehicle weight <= 160kN)": {"psi_0": 0.7, "psi_1": 0.5, "psi_2": 0.3},
        "Category H: Roofs": {"psi_0": 0.7, "psi_1": 0.0, "psi_2": 0.0},
        "Snow loads on buildings (altitude <= 1000m)": {"psi_0": 0.5, "psi_1": 0.2, "psi_2": 0.0},
        "Wind loads on buildings": {"psi_0": 0.6, "psi_1": 0.2, "psi_2": 0.0},
    }

    # --- INPUT CONTROLS ---
    col_cc, col_design_exp = st.columns(2)

    with col_cc:
        consequence_class = st.selectbox(
            "Consequences Class (CC) / Reliability Class (RC)",
            [
                "CC1 / RC1 (Low consequences for loss of human life)",
                "CC2 / RC2 (Medium consequences for loss of human life - Standard)",
                "CC3 / RC3 (High consequences for loss of human life)",
            ],
            index=1,
            help="Determines K_FI factor applied to actions.",
        )

    with col_design_exp:
        combination_rule = st.selectbox(
            "ULS Combination Approach (STR/GEO)",
            [
                "Expression 6.10 (Standard Combination)",
                "Expression 6.10a / 6.10b (Less conservative for permanent loads)",
            ],
            index=0,
            help="EN 1990 cl. 6.4.3.2 - Set by National Annex selection.",
        )

    # K_FI Factor determination
    if "CC1" in consequence_class:
        k_fi = 0.9
    elif "CC3" in consequence_class:
        k_fi = 1.1
    else:
        k_fi = 1.0

    st.divider()

    col_inputs, col_results = st.columns([1, 1.2])

    with col_inputs:
        st.subheader("Characteristic Actions")

        g_k = st.number_input("Permanent Load G_k (kN or kN/m²)", min_value=0.0, value=100.0, step=10.0)

        st.markdown("**Leading Variable Action (Q_k,1)**")
        q_cat1 = st.selectbox("Leading Variable Category", list(psi_table.keys()), index=0)
        q_k1 = st.number_input("Leading Variable Load Q_k,1 (kN or kN/m²)", min_value=0.0, value=50.0, step=5.0)

        st.markdown("**Accompanying Variable Action (Q_k,2)**")
        q_cat2 = st.selectbox("Accompanying Category", list(psi_table.keys()), index=9)
        q_k2 = st.number_input("Accompanying Variable Load Q_k,2 (kN or kN/m²)", min_value=0.0, value=20.0, step=5.0)

    # Calculate Factors & Combinations
    psi_1 = psi_table[q_cat1]
    psi_2 = psi_table[q_cat2]

    gamma_g_unfav = 1.35 * k_fi
    gamma_q_unfav = 1.50 * k_fi
    xi = 0.85

    # ULS Exp 6.10
    e_d_610 = (gamma_g_unfav * g_k) + (gamma_q_unfav * q_k1) + (gamma_q_unfav * psi_2["psi_0"] * q_k2)

    # ULS Exp 6.10a
    e_d_610a = (gamma_g_unfav * g_k) + (gamma_q_unfav * psi_1["psi_0"] * q_k1) + (gamma_q_unfav * psi_2["psi_0"] * q_k2)

    # ULS Exp 6.10b
    e_d_610b = (xi * gamma_g_unfav * g_k) + (gamma_q_unfav * q_k1) + (gamma_q_unfav * psi_2["psi_0"] * q_k2)

    # SLS Combinations
    sls_characteristic = g_k + q_k1 + (psi_2["psi_0"] * q_k2)
    sls_frequent = g_k + (psi_1["psi_1"] * q_k1) + (psi_2["psi_2"] * q_k2)
    sls_quasi_permanent = g_k + (psi_1["psi_2"] * q_k1) + (psi_2["psi_2"] * q_k2)

    with col_results:
        st.subheader("Design Combinations (E_d)")

        m1, m2 = st.columns(2)
        m1.metric("Reliability Factor K_FI", f"{k_fi:.2f}")

        if "Expression 6.10 (" in combination_rule:
            m2.metric("Governing ULS Load E_d", f"{e_d_610:.2f} kN")
        else:
            gov_uls = max(e_d_610a, e_d_610b)
            m2.metric("Governing ULS Load E_d", f"{gov_uls:.2f} kN")

        st.markdown("**ULS Combinations Table**")
        uls_df = pd.DataFrame(
            [
                {
                    "Expression": "Exp 6.10 (Standard)",
                    "Formula": "γG·Gk + γQ,1·Qk,1 + γQ,2·ψ0,2·Qk,2",
                    "Design Action E_d": f"{e_d_610:.2f}",
                },
                {
                    "Expression": "Exp 6.10a",
                    "Formula": "γG·Gk + γQ,1·ψ0,1·Qk,1 + γQ,2·ψ0,2·Qk,2",
                    "Design Action E_d": f"{e_d_610a:.2f}",
                },
                {
                    "Expression": "Exp 6.10b",
                    "Formula": "ξ·γG·Gk + γQ,1·Qk,1 + γQ,2·ψ0,2·Qk,2",
                    "Design Action E_d": f"{e_d_610b:.2f}",
                },
            ]
        )
        st.dataframe(uls_df, use_container_width=True, hide_index=True)

        st.markdown("**SLS Serviceability Combinations**")
        sls_df = pd.DataFrame(
            [
                {
                    "Limit State": "Characteristic (Irreversible)",
                    "Combination": "Gk + Qk,1 + ψ0,2·Qk,2",
                    "E_d": f"{sls_characteristic:.2f}",
                },
                {
                    "Limit State": "Frequent (Reversible)",
                    "Combination": "Gk + ψ1,1·Qk,1 + ψ2,2·Qk,2",
                    "E_d": f"{sls_frequent:.2f}",
                },
                {
                    "Limit State": "Quasi-Permanent (Long term)",
                    "Combination": "Gk + ψ2,1·Qk,1 + ψ2,2·Qk,2",
                    "E_d": f"{sls_quasi_permanent:.2f}",
                },
            ]
        )
        st.dataframe(sls_df, use_container_width=True, hide_index=True)
