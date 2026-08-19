"""
Structural Eurocode 5 (EN 1995) UI Renderer Module
Path: structural/eurocode/en1995/ui.py
"""

import math
import numpy as np
import pandas as pd
import streamlit as st


def render_en1995() -> None:
    """Renders the EN 1995 Design of Timber Structures interface."""

    st.write(
        "Perform timber cross-section verification for ultimate limit state (ULS) flexure, shear, "
        "and serviceability limit state (SLS) instantaneous and final creep deflections per EN 1995-1-1."
    )

    # --- TIMBER MATERIAL & ENVIRONMENTAL CLASS BAR ---
    col_mat, col_sc, col_ldc = st.columns([1.5, 1, 1.2])

    with col_mat:
        timber_grade = st.selectbox(
            "Timber Grade / Family",
            [
                "Solid Timber - C18 (fm,k = 18 MPa)",
                "Solid Timber - C24 (fm,k = 24 MPa)",
                "Solid Timber - C30 (fm,k = 30 MPa)",
                "Glulam - GL24h (fm,k = 24 MPa)",
                "Glulam - GL28h (fm,k = 28 MPa)",
                "Glulam - GL32h (fm,k = 32 MPa)",
            ],
            index=1,
            help="Select timber strength class. Glulam benefits from lower material partial safety factors.",
        )

    with col_sc:
        service_class = st.selectbox(
            "Service Class",
            ["Service Class 1 (RH < 65%)", "Service Class 2 (RH < 85%)", "Service Class 3 (Exposed / RH > 85%)"],
            index=0,
            help="Affects moisture content and long-term creep deformation (kdef).",
        )

    with col_ldc:
        load_duration = st.selectbox(
            "Load Duration Class",
            [
                "Permanent (> 10 yrs)",
                "Long-term (6 months - 10 yrs)",
                "Medium-term (1 week - 6 months)",
                "Short-term (< 1 week)",
                "Instantaneous",
            ],
            index=2,
            help="Determines modification factor kmod for strength adaptation.",
        )

    st.divider()

    # --- MATERIAL PROPERTIES & MODIFICATION FACTORS ---
    is_glulam = "Glulam" in timber_grade
    gamma_m = 1.25 if is_glulam else 1.30  # Partial factor for timber material

    # Characteristic Strength Lookup
    prop_map = {
        "C18": {"fmk": 18.0, "fvk": 3.4, "fc0k": 18.0, "e0mean": 9.0},
        "C24": {"fmk": 24.0, "fvk": 4.0, "fc0k": 21.0, "e0mean": 11.0},
        "C30": {"fmk": 30.0, "fvk": 4.0, "fc0k": 24.0, "e0mean": 12.0},
        "GL24h": {"fmk": 24.0, "fvk": 3.5, "fc0k": 24.0, "e0mean": 11.5},
        "GL28h": {"fmk": 28.0, "fvk": 3.5, "fc0k": 28.0, "e0mean": 12.6},
        "GL32h": {"fmk": 32.0, "fvk": 3.5, "fc0k": 32.0, "e0mean": 14.2},
    }

    grade_key = timber_grade.split(" - ")[1].split(" ")[0]
    mat_props = prop_map[grade_key]

    # kmod Factor Matrix (EN 1995-1-1 Table 3.1)
    kmod_table = {
        "Service Class 1": [0.60, 0.70, 0.80, 0.90, 1.10],
        "Service Class 2": [0.60, 0.70, 0.80, 0.90, 1.10],
        "Service Class 3": [0.50, 0.55, 0.65, 0.70, 0.90],
    }
    sc_key = service_class.split(" (")[0]
    ldc_idx = [
        "Permanent (> 10 yrs)",
        "Long-term (6 months - 10 yrs)",
        "Medium-term (1 week - 6 months)",
        "Short-term (< 1 week)",
        "Instantaneous",
    ].index(load_duration)

    k_mod = kmod_table[sc_key][ldc_idx]

    # Deformation Factor kdef (EN 1995-1-1 Table 3.2)
    kdef_map = {
        "Service Class 1": 0.60,
        "Service Class 2": 0.80,
        "Service Class 3": 2.00,
    }
    k_def = kdef_map[sc_key]

    # --- INPUT CONTROLS & CALCULATION LAYOUT ---
    col_geom_actions, col_design_results = st.columns([1, 2])

    with col_geom_actions:
        st.subheader("Geometry & Applied Actions")

        with st.expander("Member Dimensions & Span", expanded=True):
            width_b = st.number_input("Width b (mm)", min_value=38, max_value=600, value=120, step=10)
            height_h = st.number_input("Height h (mm)", min_value=70, max_value=2000, value=240, step=10)
            span_l = st.number_input("Span Length L (m)", min_value=1.0, max_value=25.0, value=4.5, step=0.5)

        with st.expander("ULS Internal Actions", expanded=True):
            m_ed = st.number_input("Design Moment M_y,Ed (kNm)", min_value=0.0, value=18.5, step=1.0)
            v_ed = st.number_input("Design Shear V_z,Ed (kN)", min_value=0.0, value=12.0, step=1.0)

        with st.expander("SLS Load Intensity (Unfactored)", expanded=True):
            g_qk_inst = st.number_input("Characteristic Permanent Load g_k (kN/m)", min_value=0.0, value=2.0, step=0.5)
            q_k_var = st.number_input("Characteristic Variable Load q_k (kN/m)", min_value=0.0, value=1.5, step=0.5)
            psi_2 = st.slider("Quasi-Permanent Factor psi_2", min_value=0.0, max_value=1.0, value=0.3, step=0.1)

    with col_design_results:
        st.subheader("ULS Verification & SLS Deflection Checks")

        # Geometric Calculations
        area_mm2 = width_b * height_h
        wy_mm3 = (width_b * (height_h**2)) / 6.0
        iy_mm4 = (width_b * (height_h**3)) / 12.0

        # Depth Modification Factor kh (EN 1995-1-1 cl 3.2)
        if not is_glulam and height_h < 150:
            k_h = min(1.3, (150.0 / height_h) ** 0.2)
        elif is_glulam and height_h < 600:
            k_h = min(1.1, (600.0 / height_h) ** 0.1)
        else:
            k_h = 1.0

        # System Factor ksys (Assumed single member = 1.0)
        k_sys = 1.0

        # Design Strengths
        fm_d = (k_mod * k_sys * k_h * mat_props["fmk"]) / gamma_m
        fv_d = (k_mod * mat_props["fvk"]) / gamma_m

        # Applied Stresses
        sigma_m_yd = (m_ed * 1e6) / wy_mm3  # MPa
        k_cr = 0.67  # Crack factor for shear (EN 1995-1-1 cl 6.1.7)
        b_eff = width_b * k_cr
        tau_vd = (1.5 * (v_ed * 1000)) / (b_eff * height_h)  # MPa

        # SLS Deflections (Simply Supported Beam Under Uniform Load)
        e_mean_mpa = mat_props["e0mean"] * 1000  # N/mm²

        # Instantaneous Deflection w_inst
        q_inst_total = g_qk_inst + q_k_var  # kN/m
        w_inst = (5.0 * q_inst_total * ((span_l * 1000) ** 4)) / (384.0 * e_mean_mpa * iy_mm4)  # mm

        # Creep / Final Deflection w_fin
        w_g_inst = (5.0 * g_qk_inst * ((span_l * 1000) ** 4)) / (384.0 * e_mean_mpa * iy_mm4)
        w_q_inst = (5.0 * q_k_var * ((span_l * 1000) ** 4)) / (384.0 * e_mean_mpa * iy_mm4)
        w_fin = w_g_inst * (1.0 + k_def) + w_q_inst * (1.0 + psi_2 * k_def)

        # Deflection Limits (EN 1995-1-1 Table 7.2)
        w_inst_lim = (span_l * 1000) / 300.0
        w_fin_lim = (span_l * 1000) / 200.0

        # Utilizations
        ur_flexure = sigma_m_yd / fm_d if fm_d > 0 else 0.0
        ur_shear = tau_vd / fv_d if fv_d > 0 else 0.0
        ur_w_inst = w_inst / w_inst_lim
        ur_w_fin = w_fin / w_fin_lim

        # Metrics Display
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Design fm,d", f"{fm_d:.2f} MPa", delta=f"kmod: {k_mod:.2f}")
        m2.metric("Flexure UR", f"{ur_flexure:.2f}", delta="PASS" if ur_flexure <= 1.0 else "FAIL")
        m3.metric("Shear UR", f"{ur_shear:.2f}", delta="PASS" if ur_shear <= 1.0 else "FAIL")
        m4.metric("Final Defl. w_fin", f"{w_fin:.1f} mm", delta=f"Lim: {w_fin_lim:.1f} mm")

        # Summary Table
        summary_df = pd.DataFrame(
            [
                {
                    "Design Check": "Bending Stress (sigma_m,y,d <= fm,d)",
                    "Applied / Calculated": f"{sigma_m_yd:.2f} MPa",
                    "Capacity / Limit": f"{fm_d:.2f} MPa",
                    "Utilization": f"{ur_flexure:.2f}",
                    "Status": "PASS" if ur_flexure <= 1.0 else "FAIL",
                },
                {
                    "Design Check": "Shear Stress (tau_v,d <= fv,d)",
                    "Applied / Calculated": f"{tau_vd:.2f} MPa",
                    "Capacity / Limit": f"{fv_d:.2f} MPa",
                    "Utilization": f"{ur_shear:.2f}",
                    "Status": "PASS" if ur_shear <= 1.0 else "FAIL",
                },
                {
                    "Design Check": "Instantaneous Deflection (w_inst <= L/300)",
                    "Applied / Calculated": f"{w_inst:.2f} mm",
                    "Capacity / Limit": f"{w_inst_lim:.2f} mm",
                    "Utilization": f"{ur_w_inst:.2f}",
                    "Status": "PASS" if ur_w_inst <= 1.0 else "FAIL",
                },
                {
                    "Design Check": "Final Creep Deflection (w_fin <= L/200)",
                    "Applied / Calculated": f"{w_fin:.2f} mm",
                    "Capacity / Limit": f"{w_fin_lim:.2f} mm",
                    "Utilization": f"{ur_w_fin:.2f}",
                    "Status": "PASS" if ur_w_fin <= 1.0 else "FAIL",
                },
            ]
        )
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

        # Chart: Moment Resistance vs Beam Height h
        st.markdown("**Design Moment Resistance (M_y,Rd) vs. Beam Height (h)**")
        heights = np.linspace(100.0, 800.0, 30)
        m_rd_list = []

        for h_val in heights:
            wy_val = (width_b * (h_val**2)) / 6.0
            if not is_glulam and h_val < 150:
                kh_v = min(1.3, (150.0 / h_val) ** 0.2)
            elif is_glulam and h_val < 600:
                kh_v = min(1.1, (600.0 / h_val) ** 0.1)
            else:
                kh_v = 1.0

            fmd_v = (k_mod * k_sys * kh_v * mat_props["fmk"]) / gamma_m
            m_rd_list.append((wy_val * fmd_v) / 1e6)  # kNm

        chart_df = pd.DataFrame(
            {"Beam Height h (mm)": heights, "Moment Resistance M_y,Rd [kNm]": m_rd_list}
        ).set_index("Beam Height h (mm)")

        st.line_chart(chart_df)
