"""
Structural Eurocode 3 (EN 1993) UI Renderer Module
Path: structural/eurocode/en1993/ui.py
"""

import math
import numpy as np
import pandas as pd
import streamlit as st


def render_en1993() -> None:
    """Renders the EN 1993 Design of Steel Structures interface."""

    st.write(
        "Perform steel cross-section classification, section resistance checks (axial, bending, shear), "
        "and member buckling stability checks in accordance with EN 1993-1-1."
    )

    # --- MATERIAL & SAFETY FACTORS BAR ---
    col_steel, col_g0, col_g1 = st.columns([1.5, 1, 1])

    with col_steel:
        steel_grade = st.selectbox(
            "Steel Grade",
            [
                "S235 (fy = 235 MPa)",
                "S275 (fy = 275 MPa)",
                "S355 (fy = 355 MPa)",
                "S460 (fy = 460 MPa)",
            ],
            index=2,
        )

    with col_g0:
        gamma_m0 = st.number_input(
            "Gamma M0 (Cross-Section)",
            min_value=0.90,
            max_value=1.20,
            value=1.00,
            step=0.05,
            help="Partial factor for resistance of cross-sections whatever the class.",
        )

    with col_g1:
        gamma_m1 = st.number_input(
            "Gamma M1 (Stability)",
            min_value=0.90,
            max_value=1.20,
            value=1.00,
            step=0.05,
            help="Partial factor for resistance of members to instability assessed by member checks.",
        )

    st.divider()

    # Material strength parsing
    fy = float(steel_grade.split("fy = ")[1].split(" MPa")[0])
    epsilon = math.sqrt(235.0 / fy)

    # --- INPUT CONTROLS & CALCULATION LAYOUT ---
    col_geom_actions, col_design_results = st.columns([1, 2])

    with col_geom_actions:
        st.subheader("Section Geometry & Actions")

        with st.expander("Rolled I-Section Dimensions (mm)", expanded=True):
            h = st.number_input("Overall Height h (mm)", min_value=80, max_value=1200, value=300, step=10)
            b = st.number_input("Flange Width b (mm)", min_value=50, max_value=500, value=150, step=10)
            tf = st.number_input("Flange Thickness tf (mm)", min_value=3, max_value=60, value=10, step=1)
            tw = st.number_input("Web Thickness tw (mm)", min_value=3, max_value=40, value=6, step=1)
            r = st.number_input("Root Radius r (mm)", min_value=0, max_value=40, value=15, step=1)

        with st.expander("Member Stability Parameters", expanded=True):
            l_cr = st.number_input("Buckling Length L_cr (m)", min_value=0.5, max_value=25.0, value=4.5, step=0.5)
            buckling_curve = st.selectbox(
                "Major Axis Buckling Curve",
                ["a0 (alpha = 0.13)", "a (alpha = 0.21)", "b (alpha = 0.34)", "c (alpha = 0.49)", "d (alpha = 0.76)"],
                index=2,
            )

        with st.expander("Ultimate Internal Actions (ULS)", expanded=True):
            n_ed = st.number_input("Axial Force N_Ed (kN, Comp)", min_value=0.0, value=220.0, step=10.0)
            m_ed = st.number_input("Bending Moment M_y,Ed (kNm)", min_value=0.0, value=75.0, step=5.0)
            v_ed = st.number_input("Shear Force V_z,Ed (kN)", min_value=0.0, value=40.0, step=5.0)

    with col_design_results:
        st.subheader("Section Classification & Member Resistance")

        # Geometric Calculations
        d_web = h - 2 * tf - 2 * r
        c_flange = (b - tw - 2 * r) / 2
        area_mm2 = 2 * b * tf + d_web * tw + (4 - math.pi) * (r**2)

        # Approximated Second Moment of Area & Section Moduli (Major Axis y-y)
        i_y = (tw * (d_web**3) / 12) + 2 * ((b * (tf**3) / 12) + (b * tf * ((h - tf) / 2) ** 2))
        wel_y = i_y / (h / 2)
        wpl_y = (tw * (d_web**2) / 4) + (2 * b * tf * ((h - tf) / 2))
        iy_radius = math.sqrt(i_y / area_mm2)

        # Cross-Section Classification (EN 1993-1-1 Table 5.2)
        c_tf_ratio = c_flange / tf if tf > 0 else 0
        c_tw_ratio = d_web / tw if tw > 0 else 0

        # Flange class (Outstand flange in compression)
        if c_tf_ratio <= 9 * epsilon:
            class_flange = 1
        elif c_tf_ratio <= 10 * epsilon:
            class_flange = 2
        elif c_tf_ratio <= 14 * epsilon:
            class_flange = 3
        else:
            class_flange = 4

        # Web class (Internal compression/bending part)
        if c_tw_ratio <= 33 * epsilon:
            class_web = 1
        elif c_tw_ratio <= 38 * epsilon:
            class_web = 2
        elif c_tw_ratio <= 42 * epsilon:
            class_web = 3
        else:
            class_web = 4

        section_class = max(class_flange, class_web)

        # Cross-Section Resistance
        # 1. Axial Compression Resistance Nc,Rd (cl 6.2.4)
        n_c_rd = (area_mm2 * fy / gamma_m0) / 1000  # kN

        # 2. Bending Resistance My,c,Rd (cl 6.2.5)
        w_eff = wpl_y if section_class in [1, 2] else wel_y
        m_c_rd = (w_eff * fy / gamma_m0) / 1e6  # kNm

        # 3. Shear Resistance Vz,c,Rd (cl 6.2.6)
        av_z = max(area_mm2 - 2 * b * tf + (tw + 2 * r) * tf, h * tw)
        v_c_rd = (av_z * (fy / math.sqrt(3)) / gamma_m0) / 1000  # kN

        # Member Flexural Buckling Resistance Nb,Rd (cl 6.3.1)
        alpha_map = {"a0": 0.13, "a": 0.21, "b": 0.34, "c": 0.49, "d": 0.76}
        curve_code = buckling_curve.split(" ")[0]
        alpha = alpha_map[curve_code]

        lambda_y = (l_cr * 1000) / iy_radius
        lambda_1 = 93.9 * epsilon
        slenderness_bar = lambda_y / lambda_1

        phi = 0.5 * (1 + alpha * (slenderness_bar - 0.2) + slenderness_bar**2)
        chi = min(1.0, 1.0 / (phi + math.sqrt(max(0, phi**2 - slenderness_bar**2))))
        n_b_rd = (chi * area_mm2 * fy / gamma_m1) / 1000  # kN

        # Metrics display
        ur_n = n_ed / n_b_rd if n_b_rd > 0 else 0.0
        ur_m = m_ed / m_c_rd if m_c_rd > 0 else 0.0
        ur_v = v_ed / v_c_rd if v_c_rd > 0 else 0.0

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Section Class", f"Class {section_class}")
        m2.metric("Axial Nb,Rd", f"{n_b_rd:.1f} kN", delta=f"UR: {ur_n:.2f}")
        m3.metric("Bending My,c,Rd", f"{m_c_rd:.1f} kNm", delta=f"UR: {ur_m:.2f}")
        m4.metric("Shear Vz,c,Rd", f"{v_c_rd:.1f} kN", delta=f"UR: {ur_v:.2f}")

        # Summary Table
        summary_df = pd.DataFrame(
            [
                {
                    "Design Check": "Section Compression Resistance (Nc,Rd)",
                    "Applied (Ed)": f"{n_ed:.1f} kN",
                    "Capacity (Rd)": f"{n_c_rd:.1f} kN",
                    "Utilization": f"{n_ed / n_c_rd:.2f}",
                    "Status": "PASS" if n_ed <= n_c_rd else "FAIL",
                },
                {
                    "Design Check": "Major Axis Bending Resistance (My,c,Rd)",
                    "Applied (Ed)": f"{m_ed:.1f} kNm",
                    "Capacity (Rd)": f"{m_c_rd:.1f} kNm",
                    "Utilization": f"{ur_m:.2f}",
                    "Status": "PASS" if ur_m <= 1.0 else "FAIL",
                },
                {
                    "Design Check": "Shear Resistance (Vz,c,Rd)",
                    "Applied (Ed)": f"{v_ed:.1f} kN",
                    "Capacity (Rd)": f"{v_c_rd:.1f} kN",
                    "Utilization": f"{ur_v:.2f}",
                    "Status": "PASS" if ur_v <= 1.0 else "FAIL",
                },
                {
                    "Design Check": "Flexural Buckling Resistance (Nb,Rd)",
                    "Applied (Ed)": f"{n_ed:.1f} kN",
                    "Capacity (Rd)": f"{n_b_rd:.1f} kN",
                    "Utilization": f"{ur_n:.2f}",
                    "Status": "PASS" if ur_n <= 1.0 else "FAIL",
                },
            ]
        )
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

        # Buckling Capacity Curve vs Length
        st.markdown("**Member Compression Capacity (Nb,Rd) vs. Effective Length (L_cr)**")
        lengths = np.linspace(1.0, 12.0, 30)
        nb_list = []

        for l_val in lengths:
            lam = (l_val * 1000) / iy_radius
            s_bar = lam / lambda_1
            p_val = 0.5 * (1 + alpha * (s_bar - 0.2) + s_bar**2)
            c_val = min(1.0, 1.0 / (p_val + math.sqrt(max(0, p_val**2 - s_bar**2))))
            nb_list.append((c_val * area_mm2 * fy / gamma_m1) / 1000)

        chart_df = pd.DataFrame(
            {"Effective Length L_cr (m)": lengths, "Buckling Resistance Nb,Rd [kN]": nb_list}
        ).set_index("Effective Length L_cr (m)")
        st.line_chart(chart_df)
