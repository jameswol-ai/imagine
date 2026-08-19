"""
Structural Eurocode 2 (EN 1992) UI Renderer Module
Path: structural/eurocode/en1992/ui.py
App: imagine
"""

import math
import numpy as np
import pandas as pd
import streamlit as st


def render_en1992() -> None:
    """Renders the EN 1992 Design of Concrete Structures interface."""

    st.write(
        "Perform reinforced concrete rectangular section design for ultimate limit state (ULS) flexure, "
        "shear capacity, and minimum reinforcement checks per EN 1992-1-1."
    )

    # --- MATERIAL & SAFETY FACTOR CONTROLS ---
    col_conc, col_steel, col_gamma = st.columns([1.5, 1.2, 1.3])

    with col_conc:
        concrete_grade = st.selectbox(
            "Concrete Strength Class",
            [
                "C20/25 (fck = 20 MPa)",
                "C25/30 (fck = 25 MPa)",
                "C30/37 (fck = 30 MPa)",
                "C35/45 (fck = 35 MPa)",
                "C40/50 (fck = 40 MPa)",
                "C50/60 (fck = 50 MPa)",
            ],
            index=2,
            help="Characteristic cylinder/cube compressive strength fck/fck,cube in MPa.",
        )

    with col_steel:
        steel_grade = st.selectbox(
            "Reinforcing Steel Grade",
            [
                "B500A (fyk = 500 MPa)",
                "B500B (fyk = 500 MPa)",
                "B500C (fyk = 500 MPa)",
                "B450C (fyk = 450 MPa)",
            ],
            index=1,
            help="High-yield characteristic steel yield strength fyk.",
        )

    with col_gamma:
        national_annex = st.selectbox(
            "Partial Safety Factors (γc / γs)",
            [
                "Recommended (γc = 1.50, γs = 1.15)",
                "UK National Annex (γc = 1.50, γs = 1.15)",
                "Accidental Combination (γc = 1.20, γs = 1.00)",
            ],
            index=0,
            help="Partial factors for concrete (γc) and steel (γs) at ULS.",
        )

    st.divider()

    # --- MATERIAL CONSTANTS & DESIGN STRENGTHS ---
    f_ck = float(concrete_grade.split("fck = ")[1].split(" MPa")[0])
    f_yk = float(steel_grade.split("fyk = ")[1].split(" MPa")[0])

    if "Accidental" in national_annex:
        gamma_c, gamma_s = 1.20, 1.00
    else:
        gamma_c, gamma_s = 1.50, 1.15

    alpha_cc = 0.85  # Coefficient for long-term compressive strength effects
    f_cd = (alpha_cc * f_ck) / gamma_c  # MPa
    f_yd = f_yk / gamma_s  # MPa

    # Mean tensile strength fctm (EN 1992-1-1 Table 3.1)
    if f_ck <= 50:
        f_ctm = 0.30 * (f_ck ** (2.0 / 3.0))
    else:
        f_ctm = 2.12 * math.log(1.0 + (f_ck + 8.0) / 10.0)

    # --- INPUT CONTROLS & CALCULATIONS LAYOUT ---
    col_geom_actions, col_design_results = st.columns([1, 2])

    with col_geom_actions:
        st.subheader("Geometry & Internal Actions")

        with st.expander("Section Dimensions & Cover", expanded=True):
            width_b = st.number_input("Section Width b (mm)", min_value=100, max_value=2000, value=300, step=25)
            height_h = st.number_input("Section Height h (mm)", min_value=150, max_value=3000, value=500, step=25)
            cover_c = st.number_input("Nominal Concrete Cover c_nom (mm)", min_value=20, max_value=100, value=35, step=5)
            bar_dia = st.selectbox("Assumed Tension Bar Diameter ϕ (mm)", [12, 16, 20, 25, 32], index=2)
            link_dia = st.selectbox("Assumed Shear Link Diameter ϕ_sw (mm)", [8, 10, 12], index=1)

        with st.expander("ULS Internal Actions", expanded=True):
            m_ed = st.number_input("Design Bending Moment M_Ed (kNm)", min_value=0.0, value=175.0, step=5.0)
            v_ed = st.number_input("Design Shear Force V_Ed (kN)", min_value=0.0, value=95.0, step=5.0)

        with st.expander("Provided Reinforcement (Optional Check)", expanded=True):
            n_bars = st.number_input("Number of Tension Bars", min_value=2, max_value=12, value=4, step=1)
            a_s_provided = n_bars * (math.pi * (bar_dia ** 2) / 4.0)
            st.caption(f"Provided Steel Area As,prov = **{a_s_provided:.0f} mm²**")

    with col_design_results:
        st.subheader("ULS Flexure & Shear Verification")

        # Effective Depth d calculation
        d_eff = height_h - cover_c - link_dia - (bar_dia / 2.0)  # mm

        # Flexural Design (Singly Reinforced Section)
        # K = M_Ed / (b * d^2 * fck)
        k_val = (m_ed * 1e6) / (width_b * (d_eff ** 2) * f_ck)
        k_prime = 0.168  # Standard limit for 15% redistribution / unredistributed

        if k_val <= k_prime:
            compression_steel_req = False
            z_arm = d_eff * min(0.95, 0.5 * (1.0 + math.sqrt(max(0.0, 1.0 - 3.53 * k_val))))
            a_s_req = (m_ed * 1e6) / (f_yd * z_arm)
        else:
            compression_steel_req = True
            # Doubly reinforced section basic estimation
            z_arm = 0.82 * d_eff
            a_s_req = (m_ed * 1e6) / (f_yd * z_arm)

        # Minimum Reinforcement As,min (EN 1992-1-1 cl 9.2.1.1)
        a_s_min = max(0.26 * (f_ctm / f_yk) * width_b * d_eff, 0.0013 * width_b * d_eff)
        a_s_max = 0.04 * width_b * height_h  # 4% gross section limit

        # Shear Capacity without shear reinforcement VRd,c (EN 1992-1-1 cl 6.2.2)
        k_shear = min(2.0, 1.0 + math.sqrt(200.0 / d_eff))
        rho_l = min(0.02, a_s_provided / (width_b * d_eff))
        c_rdc = 0.18 / gamma_c

        v_min = 0.035 * (k_shear ** 1.5) * (f_ck ** 0.5)
        v_rdc_mpa = max((c_rdc * k_shear * ((100.0 * rho_l * f_ck) ** (1.0 / 3.0))), v_min)
        v_rdc_kn = (v_rdc_mpa * width_b * d_eff) / 1000.0  # kN

        # Maximum Shear Capacity VRd,max (Crushing of Concrete Struts, theta = 45 deg)
        nu_1 = 0.6 * (1.0 - f_ck / 250.0)
        v_rd_max_kn = (0.5 * width_b * d_eff * nu_1 * f_cd) / 1000.0  # kN

        # Utilizations
        ur_flexure = a_s_req / a_s_provided if a_s_provided > 0 else 0.0
        ur_shear = v_ed / v_rdc_kn if v_rdc_kn > 0 else 0.0

        # Metrics Display
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Effective Depth d", f"{d_eff:.0f} mm")
        m2.metric("Req. Steel As,req", f"{a_s_req:.0f} mm²", delta=f"Min: {a_s_min:.0f} mm²")
        m3.metric("Flexure UR", f"{ur_flexure:.2f}", delta="PASS" if ur_flexure <= 1.0 else "REINFORCE")
        m4.metric("Shear Capacity VRd,c", f"{v_rdc_kn:.1f} kN", delta="PASS" if v_ed <= v_rdc_kn else "LINKS REQ")

        if compression_steel_req:
            st.warning("⚠️ K > K' (0.168): Section requires compression reinforcement or larger dimensions.")

        # Summary Table
        summary_df = pd.DataFrame(
            [
                {
                    "Design Check": "Flexural Reinforcement (As,req <= As,prov)",
                    "Calculated / Applied": f"{a_s_req:.1f} mm²",
                    "Capacity / Limit": f"{a_s_provided:.1f} mm²",
                    "Utilization": f"{ur_flexure:.2f}",
                    "Status": "PASS" if ur_flexure <= 1.0 else "FAIL (ADD STEEL)",
                },
                {
                    "Design Check": "Minimum Tension Reinforcement (As,prov >= As,min)",
                    "Calculated / Applied": f"{a_s_provided:.1f} mm²",
                    "Capacity / Limit": f"{a_s_min:.1f} mm²",
                    "Utilization": f"{a_s_min / a_s_provided:.2f}" if a_s_provided > 0 else "N/A",
                    "Status": "PASS" if a_s_provided >= a_s_min else "FAIL",
                },
                {
                    "Design Check": "Unreinforced Shear Resistance (V_Ed <= V_Rd,c)",
                    "Calculated / Applied": f"{v_ed:.1f} kN",
                    "Capacity / Limit": f"{v_rdc_kn:.1f} kN",
                    "Utilization": f"{ur_shear:.2f}",
                    "Status": "PASS (NO LINKS)" if ur_shear <= 1.0 else "SHEAR LINKS REQ",
                },
                {
                    "Design Check": "Concrete Strut Crushing Limit (V_Ed <= V_Rd,max)",
                    "Calculated / Applied": f"{v_ed:.1f} kN",
                    "Capacity / Limit": f"{v_rd_max_kn:.1f} kN",
                    "Utilization": f"{v_ed / v_rd_max_kn:.2f}",
                    "Status": "PASS" if v_ed <= v_rd_max_kn else "SECTION TOO SMALL",
                },
            ]
        )
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

        # Chart: Moment Resistance MRd vs. Tension Steel Area As
        st.markdown("**Design Moment Resistance (M_Rd) vs. Tension Steel Area (As)**")
        as_range = np.linspace(a_s_min, max(a_s_provided * 1.5, 2500.0), 30)
        m_rd_list = []

        for as_val in as_range:
            # Concrete compression zone depth x = (As * fyd) / (0.8 * b * fcd)
            x_depth = (as_val * f_yd) / (0.8 * width_b * f_cd)
            x_limit = 0.45 * d_eff  # Ductility limit
            x_used = min(x_depth, x_limit)
            z_val = d_eff - 0.4 * x_used
            m_rd_list.append((as_val * f_yd * z_val) / 1e6)  # kNm

        chart_df = pd.DataFrame(
            {"Tension Steel As (mm²)": as_range, "Moment Capacity M_Rd [kNm]": m_rd_list}
        ).set_index("Tension Steel As (mm²)")

        st.line_chart(chart_df)
