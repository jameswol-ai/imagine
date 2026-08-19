"""
Structural Eurocode 8 (EN 1998) UI Renderer Module
Path: structural/eurocode/en1998/ui.py
"""

import math
import numpy as np
import pandas as pd
import streamlit as st


def render_en1998() -> None:
    """Renders the EN 1998 Seismic Design & Elastic/Design Spectrum interface."""

    st.write(
        "Generate Eurocode 8 seismic response spectra (elastic $S_e$ and design $S_d$) "
        "and perform base shear calculations ($F_b$) according to EN 1998-1."
    )

    # --- SEISMIC HAZARD & IMPORTANCE CLASS BAR ---
    col_ag, col_imp, col_spec = st.columns([1.5, 1.5, 1])

    with col_ag:
        agR = st.number_input(
            "Reference Peak Ground Acc. agR (g)",
            min_value=0.01,
            max_value=1.00,
            value=0.25,
            step=0.05,
            help="Reference peak ground acceleration on Type A ground.",
        )

    with col_imp:
        importance_class = st.selectbox(
            "Importance Class (gamma_I)",
            [
                "Class I - Minor / Temporary (gamma_I = 0.8)",
                "Class II - Ordinary Buildings (gamma_I = 1.0)",
                "Class III - High Occupancy / Schools (gamma_I = 1.2)",
                "Class IV - Critical / Hospitals (gamma_I = 1.4)",
            ],
            index=1,
        )

    with col_spec:
        spectrum_type = st.radio(
            "Spectrum Type",
            ["Type 1 (Ms > 5.5)", "Type 2 (Ms <= 5.5)"],
            index=0,
            help="Type 1 recommended for high/moderate seismicity zones (Ms > 5.5).",
        )

    st.divider()

    # Parse importance factor gamma_I
    gamma_i = float(importance_class.split("gamma_I = ")[1].replace(")", ""))
    ag = agR * gamma_i  # Design ground acceleration in g

    # --- INPUT CONTROLS & CALCULATION LAYOUT ---
    col_inputs, col_results = st.columns([1, 2])

    with col_inputs:
        st.subheader("Site & Structure Parameters")

        with st.expander("Ground / Soil Classification", expanded=True):
            ground_type = st.selectbox(
                "Ground Type",
                [
                    "A - Rock / Hard Soil (vs > 800 m/s)",
                    "B - Very Dense Sand / Stiff Clay",
                    "C - Dense Sand / Medium Clay",
                    "D - Loose Soil / Soft Clay",
                    "E - Surface Alluvial Layer",
                ],
                index=1,
            )

        with st.expander("Structural Behavior & Period", expanded=True):
            q_factor = st.number_input(
                "Behavior Factor q",
                min_value=1.0,
                max_value=6.0,
                value=3.0,
                step=0.1,
                help="Accounts for ductility and energy dissipation capacity.",
            )
            t1_period = st.number_input(
                "Fundamental Period T1 (s)",
                min_value=0.05,
                max_value=4.0,
                value=0.50,
                step=0.05,
            )
            total_mass = st.number_input(
                "Total Seismic Mass m (tonnes)",
                min_value=1.0,
                value=850.0,
                step=50.0,
            )
            num_storeys = st.number_input(
                "Number of Storeys",
                min_value=1,
                max_value=100,
                value=5,
                step=1,
            )

        with st.expander("Damping & Lower Bound Factors", expanded=True):
            damping_ratio = st.number_input("Viscous Damping Ratio xi (%)", min_value=1.0, max_value=20.0, value=5.0, step=0.5)
            beta_factor = st.number_input("Lower Bound Factor beta", min_value=0.10, max_value=0.30, value=0.20, step=0.02)

    with col_results:
        st.subheader("Seismic Response & Base Shear Analysis")

        # EN 1998-1 Table 3.2 & 3.3 Spectral Parameters Lookup
        g_code = ground_type.split(" - ")[0]
        is_type_1 = "Type 1" in spectrum_type

        if is_type_1:
            params = {
                "A": (1.00, 0.15, 0.40, 2.00),
                "B": (1.35, 0.15, 0.50, 2.00),
                "C": (1.50, 0.20, 0.60, 2.00),
                "D": (1.80, 0.20, 0.80, 2.00),
                "E": (1.40, 0.15, 0.50, 2.00),
            }
        else:
            params = {
                "A": (1.00, 0.05, 0.25, 1.20),
                "B": (1.40, 0.05, 0.25, 1.20),
                "C": (1.50, 0.10, 0.25, 1.20),
                "D": (1.80, 0.10, 0.30, 1.20),
                "E": (1.60, 0.05, 0.25, 1.20),
            }

        s_soil, tb, tc, td = params[g_code]

        # Damping correction factor eta
        eta = math.sqrt(10.0 / (5.0 + damping_ratio))

        # Design Spectrum Calculation Function Sd(T)
        def get_sd(t_val: float) -> float:
            if 0 <= t_val <= tb:
                return ag * s_soil * (2 / 3 + (t_val / tb) * (2.5 / q_factor - 2 / 3))
            elif tb <= t_val <= tc:
                return ag * s_soil * (2.5 / q_factor)
            elif tc <= t_val <= td:
                val = ag * s_soil * (2.5 / q_factor) * (tc / t_val)
                return max(val, beta_factor * ag)
            else:
                val = ag * s_soil * (2.5 / q_factor) * ((tc * td) / (t_val**2))
                return max(val, beta_factor * ag)

        # Elastic Spectrum Calculation Function Se(T)
        def get_se(t_val: float) -> float:
            if 0 <= t_val <= tb:
                return ag * s_soil * (1 + (t_val / tb) * (eta * 2.5 - 1))
            elif tb <= t_val <= tc:
                return ag * s_soil * eta * 2.5
            elif tc <= t_val <= td:
                return ag * s_soil * eta * 2.5 * (tc / t_val)
            else:
                return ag * s_soil * eta * 2.5 * ((tc * td) / (t_val**2))

        # Spectral acceleration at fundamental period T1
        sd_t1 = get_sd(t1_period)
        se_t1 = get_se(t1_period)

        # Total Base Shear Force Fb = Sd(T1) * m * lambda
        lambda_corr = 0.85 if (t1_period <= 2 * tc and num_storeys > 2) else 1.0
        g_acc = 9.81  # m/s²
        seismic_weight = total_mass * g_acc  # kN
        base_shear_fb = sd_t1 * seismic_weight * lambda_corr  # kN

        # Metrics Display
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Design Acc. ag", f"{ag:.3f} g")
        m2.metric("Soil Factor S", f"{s_soil:.2f}")
        m3.metric("Sd(T1) [g]", f"{sd_t1:.3f} g")
        m4.metric("Base Shear Fb", f"{base_shear_fb:.1f} kN", delta=f"{base_shear_fb / seismic_weight * 100:.1f}% W")

        # Summary DataFrame
        summary_df = pd.DataFrame(
            [
                {
                    "Parameter / Check": "Design Ground Acceleration (ag)",
                    "Value": f"{ag:.3f} g ({ag * g_acc:.2f} m/s²)",
                    "Reference": "ag = agR * gamma_I",
                    "Status": "COMPUTED",
                },
                {
                    "Parameter / Check": "Corner Periods (TB, TC, TD)",
                    "Value": f"TB={tb:.2f}s, TC={tc:.2f}s, TD={td:.2f}s",
                    "Reference": f"Ground Type {g_code} ({spectrum_type.split()[0]})",
                    "Status": "OK",
                },
                {
                    "Parameter / Check": "Design Spectral Ordinate Sd(T1)",
                    "Value": f"{sd_t1:.4f} g",
                    "Reference": "EN 1998-1 cl 3.2.2.5",
                    "Status": "OK",
                },
                {
                    "Parameter / Check": "Seismic Base Shear Force (Fb)",
                    "Value": f"{base_shear_fb:.2f} kN",
                    "Reference": "Fb = Sd(T1) * m * g * lambda",
                    "Status": f"lambda = {lambda_corr}",
                },
            ]
        )
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

        # Plot Response Spectra Curve
        st.markdown("**Elastic (Se) and Design (Sd) Horizontal Response Spectra**")
        periods = np.linspace(0.01, 3.5, 100)
        se_vals = [get_se(t) for t in periods]
        sd_vals = [get_sd(t) for t in periods]

        chart_df = pd.DataFrame(
            {
                "Period T (s)": periods,
                "Elastic Spectrum Se(T) [g]": se_vals,
                "Design Spectrum Sd(T) [g]": sd_vals,
            }
        ).set_index("Period T (s)")

        st.line_chart(chart_df)
