"""
Structural Eurocode 0 (EN 1990) UI Renderer Module
Path: structural/eurocode_0/ui.py
"""

import pandas as pd
import streamlit as st


def render_eurocode_0() -> None:
    """Renders the EN 1990 Basis of Structural Design & Load Combination interface."""

    st.write(
        "Define structural reliability classes, design working life, and generate "
        "Ultimate (ULS) and Serviceability (SLS) limit state load combinations per EN 1990."
    )

    # --- GENERAL STRUCTURAL ASSUMPTIONS BAR ---
    col_cc, col_dwl, col_eq = st.columns([1, 1, 1.5])

    with col_cc:
        cc_class = st.selectbox(
            "Consequence Class",
            ["CC1 (Low)", "CC2 (Medium / Standard)", "CC3 (High)"],
            index=1,
            help="Determines the $K_{FI}$ factor applied to unfavorable actions.",
        )

    with col_dwl:
        dwl_category = st.selectbox(
            "Design Working Life",
            ["10 Years (Temporary)", "25 Years (Replaceable)", "50 Years (Building)", "100 Years (Monumental)"],
            index=2,
        )

    with col_eq:
        combination_rule = st.selectbox(
            "ULS Combination Expression",
            [
                "Eq. 6.10: γG·Gk + γQ,1·Qk,1 + Σ(γQ,i·ψ0,i·Qk,i)",
                "Eq. 6.10a/b: Max of (6.10a, 6.10b) [Economy / Modified]",
            ],
            index=0,
        )

    st.divider()

    # --- MAIN CONTROLS & LOAD COMBINATIONS ---
    left_actions_col, right_results_col = st.columns([1, 2])

    # K_FI factor lookup
    k_fi = 0.9 if "CC1" in cc_class else (1.1 if "CC3" in cc_class else 1.0)

    with left_actions_col:
        st.subheader("Characteristic Actions")

        with st.expander("Permanent Actions (Gk)", expanded=True):
            g_k1 = st.number_input("Self-Weight & Dead Load Gk,1 (kN/m²)", min_value=0.0, value=5.0, step=0.5)
            g_k2 = st.number_input("Superimposed Dead Load Gk,2 (kN/m²)", min_value=0.0, value=2.0, step=0.5)

        with st.expander("Variable Actions (Qk)", expanded=True):
            q_k1_category = st.selectbox(
                "Leading Variable Action Category",
                ["Category A: Domestic / Residential", "Category B: Office Areas", "Category E: Storage", "Wind Load", "Snow Load"],
                index=1,
            )
            q_k1 = st.number_input("Leading Action Qk,1 (kN/m²)", min_value=0.0, value=3.0, step=0.5)

            st.markdown("---")

            q_k2_category = st.selectbox(
                "Accompanying Action Category",
                ["None", "Wind Load", "Snow Load", "Category A: Domestic"],
                index=1,
            )
            q_k2 = st.number_input("Accompanying Action Qk,2 (kN/m²)", min_value=0.0, value=1.5, step=0.5)

        # Eurocode partial safety factors
        gamma_G = 1.35 * k_fi
        gamma_Q = 1.50 * k_fi

        # Psi factors lookup dictionary (Table A1.1)
        psi_map = {
            "Category A: Domestic / Residential": {"psi0": 0.7, "psi1": 0.5, "psi2": 0.3},
            "Category B: Office Areas": {"psi0": 0.7, "psi1": 0.5, "psi2": 0.3},
            "Category E: Storage": {"psi0": 1.0, "psi1": 0.9, "psi2": 0.8},
            "Wind Load": {"psi0": 0.6, "psi1": 0.2, "psi2": 0.0},
            "Snow Load": {"psi0": 0.5, "psi1": 0.2, "psi2": 0.0},
            "None": {"psi0": 0.0, "psi1": 0.0, "psi2": 0.0},
        }

        psi_q1 = psi_map.get(q_k1_category, {"psi0": 0.7})["psi0"]
        psi_q2 = psi_map.get(q_k2_category, {"psi0": 0.6})["psi0"]

    with right_results_col:
        st.subheader("EN 1990 Combination Calculations")

        total_Gk = g_k1 + g_k2

        # ULS Design Value Computation (Eq. 6.10)
        uls_design_load = (gamma_G * total_Gk) + (gamma_Q * q_k1) + (gamma_Q * psi_q2 * q_k2)

        # SLS Characteristic & Quasi-Permanent
        sls_characteristic = total_Gk + q_k1 + (psi_q2 * q_k2)
        sls_quasi_permanent = total_Gk + (psi_map[q_k1_category]["psi2"] * q_k1) + (psi_map[q_k2_category]["psi2"] * q_k2)

        # Key Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("K_FI Factor", f"{k_fi:.2f}")
        m2.metric("ULS Design Load (Ed)", f"{uls_design_load:.2f} kN/m²")
        m3.metric("SLS Characteristic", f"{sls_characteristic:.2f} kN/m²")
        m4.metric("SLS Quasi-Permanent", f"{sls_quasi_permanent:.2f} kN/m²")

        st.markdown("**Design Combinations Breakdown (Table)**")

        comb_df = pd.DataFrame(
            [
                {
                    "Limit State": "ULS (STR/GEO) - Eq. 6.10",
                    "Formula Expression": f"{gamma_G:.2f}·Gk + {gamma_Q:.2f}·Qk,1 + {gamma_Q:.2f}·({psi_q2:.2f})·Qk,2",
                    "Design Load (kN/m²)": round(uls_design_load, 2),
                    "Governing Status": "Critical ULS",
                },
                {
                    "Limit State": "SLS - Characteristic",
                    "Formula Expression": "1.0·Gk + 1.0·Qk,1 + ψ0,2·Qk,2",
                    "Design Load (kN/m²)": round(sls_characteristic, 2),
                    "Governing Status": "Deflection / Cracking",
                },
                {
                    "Limit State": "SLS - Frequent",
                    "Formula Expression": f"1.0·Gk + {psi_map[q_k1_category]['psi1']}·Qk,1 + {psi_map[q_k2_category]['psi2']}·Qk,2",
                    "Design Load (kN/m²)": round(
                        total_Gk + (psi_map[q_k1_category]["psi1"] * q_k1) + (psi_map[q_k2_category]["psi2"] * q_k2),
                        2,
                    ),
                    "Governing Status": "Reversible Effects",
                },
                {
                    "Limit State": "SLS - Quasi-Permanent",
                    "Formula Expression": f"1.0·Gk + {psi_map[q_k1_category]['psi2']}·Qk,1 + {psi_map[q_k2_category]['psi2']}·Qk,2",
                    "Design Load (kN/m²)": round(sls_quasi_permanent, 2),
                    "Governing Status": "Long-Term Creep",
                },
            ]
        )

        st.dataframe(comb_df, use_container_width=True, hide_index=True)

        st.markdown("**Load Distribution Composition**")
        chart_data = pd.DataFrame(
            {
                "Load Type": ["Permanent (Gk)", "Leading Variable (Qk,1)", "Accompanying (Qk,2)"],
                "Factored Design Load (kN/m²)": [
                    gamma_G * total_Gk,
                    gamma_Q * q_k1,
                    gamma_Q * psi_q2 * q_k2,
                ],
            }
        ).set_index("Load Type")

        st.bar_chart(chart_data)
