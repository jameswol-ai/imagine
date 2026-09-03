"""
Structural Eurocode 7 (EN 1997) UI Renderer Module
Path: structural/eurocode/en1997/ui.py
"""

import math
import numpy as np
import pandas as pd
import streamlit as st


def render_en1997() -> None:
    """Renders the EN 1997 Geotechnical Design & Bearing Capacity interface."""

    st.write(
        "Perform shallow foundation ultimate limit state (ULS) bearing resistance and sliding checks "
        "in accordance with EN 1997-1 (Annex D) across Eurocode Design Approaches (DA1, DA2, DA3)."
    )

    col_da, col_gam_v, col_gam_r = st.columns([1.5, 1, 1])

    with col_da:
        design_approach = st.selectbox(
            "Design Approach (EN 1997-1)",
            [
                "DA1 - Combination 1 (A1 + M1 + R1)",
                "DA1 - Combination 2 (A2 + M2 + R1)",
                "DA2 - (A1 + M1 + R2)",
                "DA3 - (A2* + M2 + R3)",
            ],
            index=1,
            help="Select Eurocode Design Approach determining partial safety factor sets for actions, soil parameters, and resistances.",
        )

    if "Combination 1" in design_approach or "DA2" in design_approach:
        gamma_phi_default, gamma_c_default, gamma_gamma_default = 1.00, 1.00, 1.00
        gamma_r_b_default = 1.40 if "DA2" in design_approach else 1.00
    else:
        gamma_phi_default, gamma_c_default, gamma_gamma_default = 1.25, 1.25, 1.00
        gamma_r_b_default = 1.00

    with col_gam_v:
        gamma_f = st.number_input(
            "Gamma F (Actions)",
            min_value=1.00,
            max_value=1.50,
            value=1.35 if "A1" in design_approach else 1.00,
            step=0.05,
            help="Partial factor on permanent/variable actions.",
        )

    with col_gam_r:
        gamma_r_b = st.number_input(
            "Gamma R,v (Bearing Resistance)",
            min_value=1.00,
            max_value=1.60,
            value=gamma_r_b_default,
            step=0.05,
            help="Partial resistance factor for bearing capacity.",
        )

    st.divider()
    col_geom_soil, col_design_results = st.columns([1, 2])

    with col_geom_soil:
        st.subheader("Geometry & Soil Parameters")
        with st.expander("Footing Geometry & Embedment", expanded=True):
            width_b = st.number_input("Footing Width B (m)", min_value=0.5, max_value=20.0, value=2.5, step=0.25)
            length_l = st.number_input("Footing Length L (m)", min_value=0.5, max_value=50.0, value=3.5, step=0.25)
            depth_d = st.number_input("Foundation Depth D (m)", min_value=0.0, max_value=10.0, value=1.2, step=0.1)

        with st.expander("Characteristic Soil Properties", expanded=True):
            phi_k = st.slider("Internal Friction Angle phi'k (deg)", min_value=10.0, max_value=45.0, value=30.0, step=1.0)
            c_k = st.number_input("Effective Cohesion c'k (kPa)", min_value=0.0, max_value=100.0, value=10.0, step=2.0)
            gamma_k = st.number_input("Soil Unit Weight gamma (kN/m³)", min_value=12.0, max_value=24.0, value=18.5, step=0.5)

        with st.expander("ULS Design Loads", expanded=True):
            v_ed = st.number_input("Vertical Design Load V_Ed (kN)", min_value=10.0, value=850.0, step=50.0)
            h_ed = st.number_input("Horizontal Design Load H_Ed (kN)", min_value=0.0, value=65.0, step=5.0)
            m_ed = st.number_input("Overturning Moment M_Ed (kNm)", min_value=0.0, value=120.0, step=10.0)

    with col_design_results:
        st.subheader("ULS Bearing Capacity & Sliding Resistance (EN 1997-1 Annex D)")
        gamma_phi = gamma_phi_default
        gamma_c = gamma_c_default
        gamma_gamma = gamma_gamma_default

        phi_d_rad = math.atan(math.tan(math.radians(phi_k)) / gamma_phi)
        phi_d_deg = math.degrees(phi_d_rad)
        c_d = c_k / gamma_c
        gamma_d = gamma_k / gamma_gamma

        e_b = m_ed / v_ed if v_ed > 0 else 0.0
        b_eff = width_b - (2 * e_b)
        l_eff = length_l
        a_eff = max(0.1, b_eff * l_eff)
        q_overburden = gamma_d * depth_d

        if phi_d_deg > 0:
            nq = math.exp(math.pi * math.tan(phi_d_rad)) * (math.tan(math.radians(45 + phi_d_deg / 2)) ** 2)
            nc = (nq - 1.0) / math.tan(phi_d_rad)
            ngamma = 2.0 * (nq - 1.0) * math.tan(phi_d_rad)
        else:
            nq = 1.0
            nc = 2.0 + math.pi
            ngamma = 0.0

        sq = 1.0 + (b_eff / l_eff) * math.sin(phi_d_rad)
        sc = (sq * nq - 1.0) / (nq - 1.0) if nq > 1.0 else 1.0 + 0.2 * (b_eff / l_eff)
        sgamma = 1.0 - 0.3 * (b_eff / l_eff)

        if phi_d_deg > 0:
            m_shape = (2 + (b_eff / l_eff)) / (1 + (b_eff / l_eff))
            denominator = v_ed + a_eff * c_d / math.tan(phi_d_rad)
            inclination_ratio = h_ed / denominator if denominator > 0 else 0.0
            iq = max(0.0, (1.0 - inclination_ratio) ** m_shape)
            ic = iq - (1.0 - iq) / (nc * math.tan(phi_d_rad)) if nc > 0 else 1.0
            igamma = max(0.0, (1.0 - h_ed / v_ed) ** (m_shape + 1)) if v_ed > 0 else 1.0
        else:
            iq, ic, igamma = 1.0, 1.0, 1.0

        q_rd = (c_d * nc * sc * ic) + (q_overburden * nq * sq * iq) + (0.5 * gamma_d * b_eff * ngamma * sgamma * igamma)
        r_d = (q_rd * a_eff) / gamma_r_b

        gamma_r_h = 1.10 if "DA2" in design_approach else 1.00
        r_h_d = (v_ed * math.tan(phi_d_rad) + a_eff * c_d) / gamma_r_h
        ur_bearing = v_ed / r_d if r_d > 0 else 99.0
        ur_sliding = h_ed / r_h_d if r_h_d > 0 else 99.0

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Effective Width B'", f"{b_eff:.2f} m", delta=f"e = {e_b:.3f} m")
        m2.metric("Bearing Res. R_d", f"{r_d:.1f} kN", delta=f"UR: {ur_bearing:.2f}")
        m3.metric("Sliding Res. R_h,d", f"{r_h_d:.1f} kN", delta=f"UR: {ur_sliding:.2f}")
        m4.metric("Design q_rd", f"{q_rd:.1f} kPa")

        if b_eff <= 0:
            st.error("Error: Load eccentricity exceeds half width (e >= B/2). Footing experiences uplift!")

        summary_df = pd.DataFrame(
            [
                {"Design Check": "Bearing Capacity ULS (V_Ed <= R_d)", "Applied Load": f"V_Ed = {v_ed:.1f} kN", "Resistance": f"R_d = {r_d:.1f} kN", "Utilization": f"{ur_bearing:.2f}", "Status": "PASS" if ur_bearing <= 1.0 else "FAIL"},
                {"Design Check": "Sliding Resistance ULS (H_Ed <= R_h,d)", "Applied Load": f"H_Ed = {h_ed:.1f} kN", "Resistance": f"R_h,d = {r_h_d:.1f} kN", "Utilization": f"{ur_sliding:.2f}", "Status": "PASS" if ur_sliding <= 1.0 else "FAIL"},
                {"Design Check": "Eccentricity Limit (e <= B/6)", "Calculated": f"e = {e_b:.3f} m", "Limit": f"B/6 = {width_b / 6:.3f} m", "Utilization": f"{e_b / (width_b / 6):.2f}", "Status": "NO UPLIFT" if e_b <= width_b / 6 else "PARTIAL UPLIFT"},
            ]
        )
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

        st.markdown("**Design Bearing Resistance (R_d) vs. Footing Width (B)**")
        widths = np.linspace(1.0, 6.0, 25)
        rd_list = []
        for w_val in widths:
            e_val = m_ed / v_ed if v_ed > 0 else 0.0
            be_val = max(0.1, w_val - (2 * e_val))
            ae_val = be_val * length_l
            sq_v = 1.0 + (be_val / length_l) * math.sin(phi_d_rad)
            sc_v = (sq_v * nq - 1.0) / (nq - 1.0) if nq > 1.0 else 1.0 + 0.2 * (be_val / length_l)
            sg_v = 1.0 - 0.3 * (be_val / length_l)
            q_rd_v = (c_d * nc * sc_v * ic) + (q_overburden * nq * sq_v * iq) + (0.5 * gamma_d * be_val * ngamma * sg_v * igamma)
            rd_list.append((q_rd_v * ae_val) / gamma_r_b)

        chart_df = pd.DataFrame({"Footing Width B (m)": widths, "Bearing Resistance R_d [kN]": rd_list}).set_index("Footing Width B (m)")
        st.line_chart(chart_df)
