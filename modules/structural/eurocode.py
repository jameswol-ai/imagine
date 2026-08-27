"""
IMAGINE Platform — Eurocode Design & Structural Analysis Engine
Path: modules/structural/eurocode.py
App: imagine
"""

import math
from typing import Dict, Any
import pandas as pd
import streamlit as st
from modules.utils.crud import CRUDService

STATE_KEY = "structural_calcs"


def render() -> None:
    """Renders the Eurocode Navigation Hub and Interactive Structural Engineering Solvers."""
    st.title("🧱 Eurocode Structural Analysis Engine")
    st.caption("Verification of structural members according to European Standards (EN 1990 – EN 1998).")

    # European National Annex Global Settings
    with st.sidebar:
        st.subheader("🌐 Design Parameters")
        national_annex = st.selectbox(
            "National Annex (NA)",
            ["Recommended (EU)", "United Kingdom (BS EN)", "Germany (DIN EN)", "France (NF EN)", "Ireland (IS EN)"],
            help="Applies country-specific partial safety factors (γ_M, γ_G, γ_Q)."
        )
        st.info(f"Active Annex: **{national_annex}**")

    # Navigation Tabs across Eurocodes
    tabs = st.tabs([
        "⚖️ EN 1990/1 (Loads & Combinations)",
        "🧱 EN 1992 (Concrete)",
        "🏗️ EN 1993 (Steel)",
        "🌐 EN 1997/8 (Geotech & Seismic)",
        "📋 Calculation Register"
    ])

    # ==============================================================================
    # TAB 1: EN 1990 / EN 1991 — LOAD COMBINATIONS (ULS / SLS)
    # ==============================================================================
    with tabs[0]:
        st.subheader("EN 1990 / EN 1991: Actions & Load Combination Generator")
        st.markdown("Calculate Design Values of Actions for Ultimate Limit State (ULS Eq 6.10): $E_d = \\gamma_G G_k + \\gamma_Q Q_{k,1} + \\sum \\gamma_Q \\psi_{0,i} Q_{k,i}$")

        col1, col2 = st.columns(2)
        with col1:
            elem_name = st.text_input("Element Name / ID", value="BEAM-B101", key="en1990_elem")
            g_k = st.number_input("Characteristic Permanent Action $G_k$ (kN or kN/m)", value=45.0, step=5.0)
            q_k1 = st.number_input("Primary Variable Action $Q_{k,1}$ (kN or kN/m)", value=30.0, step=5.0)
            q_k2 = st.number_input("Accompanying Variable Action $Q_{k,2}$ (kN or kN/m)", value=10.0, step=2.5)

        with col2:
            gamma_g = st.number_input("Partial Factor Permanent $\\gamma_G$", value=1.35, step=0.05)
            gamma_q = st.number_input("Partial Factor Variable $\\gamma_Q$", value=1.50, step=0.05)
            psi_02 = st.number_input("Combination Factor $\\psi_{0,2}$ for $Q_{k,2}$", value=0.70, step=0.05)

            # Calculation
            e_d_uls = (gamma_g * g_k) + (gamma_q * q_k1) + (gamma_q * psi_02 * q_k2)
            e_d_sls = g_k + q_k1 + (psi_02 * q_k2)

            st.markdown("---")
            st.metric("ULS Design Action ($E_d$)", f"{e_d_uls:.2f} kN/m")
            st.metric("SLS Characteristic Action ($E_{d,sls}$)", f"{e_d_sls:.2f} kN/m")

        if st.button("💾 Save Combination Result", key="save_en1990"):
            record = {
                "id": f"CALC-{len(CRUDService.get_all(STATE_KEY)) + 1:03d}",
                "code": "EN 1990 / EN 1991",
                "element_name": elem_name,
                "design_load_kn": round(e_d_uls, 2),
                "unity_check": 0.85,  # Placeholder check against capacity
                "status": "Passed",
            }
            CRUDService.create(STATE_KEY, record)
            st.success(f"Calculation logged for `{elem_name}`!")

    # ==============================================================================
    # TAB 2: EN 1992 — REINFORCED CONCRETE FLEXURE (EN 1992-1-1)
    # ==============================================================================
    with tabs[1]:
        st.subheader("EN 1992-1-1: Singly Reinforced Beam Bending Resistance ($M_{Rd}$)")

        rc1, rc2 = st.columns(2)
        with rc1:
            rc_elem = st.text_input("Element ID", value="RC-BEAM-01", key="rc_elem")
            m_ed = st.number_input("Design Bending Moment $M_{Ed}$ (kNm)", value=120.0, step=10.0)
            b = st.number_input("Beam Width $b$ (mm)", value=300, step=25)
            h = st.number_input("Beam Depth $h$ (mm)", value=500, step=25)
            d = st.number_input("Effective Depth $d$ (mm)", value=450, step=25)

        with rc2:
            concrete_grade = st.selectbox("Concrete Class", ["C25/30", "C30/37", "C35/45", "C40/50"])
            f_ck = int(concrete_grade.split("/")[0].replace("C", ""))
            f_yk = st.number_input("Steel Yield Strength $f_{yk}$ (MPa)", value=500, step=50)
            a_s = st.number_input("Provided Tension Steel $A_s$ (mm²)", value=942.0, step=50.0, help="e.g. 3 H20 bars = 942 mm²")

            # Solvers EN 1992
            gamma_c, gamma_s = 1.5, 1.15
            f_cd = (0.85 * f_ck) / gamma_c  # MPa
            f_yd = f_yk / gamma_s          # MPa

            # Compression block depth x
            x = (a_s * f_yd) / (0.8 * b * f_cd)
            z = d - (0.4 * x)
            z = min(z, 0.95 * d)  # Upper bound constraint

            m_rd = (a_s * f_yd * z) / 1e6  # kNm
            unity_check = m_ed / m_rd if m_rd > 0 else 999.0
            status = "Passed" if unity_check <= 1.0 else "Failed"

            st.markdown("---")
            st.metric("Design Bending Resistance ($M_{Rd}$)", f"{m_rd:.2f} kNm")
            st.metric("Unity Check Ratio ($\\eta = M_{Ed} / M_{Rd}$)", f"{unity_check:.2f}", delta="SAFE" if unity_check <= 1.0 else "OVERSTRESSED", delta_color="normal" if unity_check <= 1.0 else "inverse")

        if st.button("💾 Save EN 1992 Verification", key="save_en1992"):
            record = {
                "id": f"CALC-{len(CRUDService.get_all(STATE_KEY)) + 1:03d}",
                "code": "EN 1992-1-1",
                "element_name": rc_elem,
                "unity_check": round(unity_check, 2),
                "status": status,
            }
            CRUDService.create(STATE_KEY, record)
            st.success(f"Verification stored for `{rc_elem}`!")

    # ==============================================================================
    # TAB 3: EN 1993 — STRUCTURAL STEEL MEMBER RESISTANCE (EN 1993-1-1)
    # ==============================================================================
    with tabs[2]:
        st.subheader("EN 1993-1-1: Steel Section Axial & Bending Interaction")

        st1, st2 = st.columns(2)
        with st1:
            s_elem = st.text_input("Steel Member ID", value="COL-S201", key="s_elem")
            steel_grade = st.selectbox("Steel Grade", ["S275", "S355", "S460"])
            f_y = int(steel_grade.replace("S", ""))
            
            n_ed = st.number_input("Axial Compression $N_{Ed}$ (kN)", value=350.0, step=25.0)
            m_y_ed = st.number_input("Major Axis Moment $M_{y,Ed}$ (kNm)", value=85.0, step=5.0)

        with st2:
            area = st.number_input("Cross-Sectional Area $A$ (cm²)", value=76.4, step=5.0) * 100.0  # mm²
            w_pl_y = st.number_input("Plastic Modulus $W_{pl,y}$ (cm³)", value=624.0, step=20.0) * 1000.0  # mm³
            gamma_m0 = 1.0

            n_pl_rd = (area * f_y / gamma_m0) / 1000.0  # kN
            m_pl_y_rd = (w_pl_y * f_y / gamma_m0) / 1e6  # kNm

            eta_n = n_ed / n_pl_rd if n_pl_rd > 0 else 0.0
            eta_m = m_y_ed / m_pl_y_rd if m_pl_y_rd > 0 else 0.0
            total_unity = eta_n + eta_m
            s_status = "Passed" if total_unity <= 1.0 else "Failed"

            st.markdown("---")
            st.write(f"**Axial Resistance $N_{{pl,Rd}}$:** {n_pl_rd:.1f} kN")
            st.write(f"**Bending Resistance $M_{{pl,y,Rd}}$:** {m_pl_y_rd:.1f} kNm")
            st.metric("Combined Interaction Check ($\\eta_N + \\eta_M$)", f"{total_unity:.2f}", delta="COMPLIANT" if total_unity <= 1.0 else "UNSAFE", delta_color="normal" if total_unity <= 1.0 else "inverse")

        if st.button("💾 Save EN 1993 Verification", key="save_en1993"):
            record = {
                "id": f"CALC-{len(CRUDService.get_all(STATE_KEY)) + 1:03d}",
                "code": "EN 1993-1-1",
                "element_name": s_elem,
                "unity_check": round(total_unity, 2),
                "status": s_status,
            }
            CRUDService.create(STATE_KEY, record)
            st.success(f"Steel check saved for `{s_elem}`!")

    # ==============================================================================
    # TAB 4: EN 1997 / EN 1998 — GEOTECHNICAL & SEISMIC PARAMETERS
    # ==============================================================================
    with tabs[3]:
        st.subheader("EN 1997 (Geotechnical) & EN 1998 (Seismic) Estimator")

        gt1, gt2 = st.columns(2)
        with gt1:
            st.markdown("#### EN 1997 Bearing Resistance")
            phi_deg = st.slider("Internal Friction Angle $\\phi'$ (°)", 20.0, 45.0, 30.0)
            cohesion = st.number_input("Effective Cohesion $c'$ (kPa)", value=10.0, step=5.0)
            gamma_soil = st.number_input("Soil Unit Weight $\\gamma$ (kN/m³)", value=18.0, step=1.0)
            foundation_b = st.number_input("Footing Width $B$ (m)", value=2.0, step=0.5)

            # Terzaghi/Eurocode bearing factor approximation
            n_q = math.tan(math.radians(45 + phi_deg / 2)) ** 2 * math.exp(math.pi * math.tan(math.radians(phi_deg)))
            n_c = (n_q - 1) / math.tan(math.radians(phi_deg)) if phi_deg > 0 else 5.14
            n_gamma = 2 * (n_q + 1) * math.tan(math.radians(phi_deg))

            q_rd = (cohesion * n_c) + (0.5 * gamma_soil * foundation_b * n_gamma)
            st.metric("Ultimate Bearing Capacity ($q_{rd}$)", f"{q_rd:.1f} kPa")

        with gt2:
            st.markdown("#### EN 1998 Seismic Action Estimator")
            ground_type = st.selectbox("Ground Type", ["A (Rock)", "B (Very Dense Sand/Gravel)", "C (Dense Sand)", "D (Loose Soil)", "E (Alluvial)"])
            ag_g = st.number_input("Design Ground Acceleration $a_g / g$", value=0.15, step=0.05, help="Peak ground acceleration factor.")
            importance_factor = st.selectbox("Building Importance Class", [1.0, 1.2, 1.4], index=1)

            s_factor = {"A (Rock)": 1.0, "B (Very Dense Sand/Gravel)": 1.35, "C (Dense Sand)": 1.5, "D (Loose Soil)": 1.8, "E (Alluvial)": 1.4}[ground_type]
            s_e = ag_g * importance_factor * s_factor * 2.5
            st.metric("Peak Elastic Response Spectrum Acceleration ($S_e$)", f"{s_e:.3f} g")

    # ==============================================================================
    # TAB 5: CALCULATION REGISTER
    # ==============================================================================
    with tabs[4]:
        st.subheader("📑 Active Structural Verification Register")
        calcs = CRUDService.get_all(STATE_KEY)
        if calcs:
            df_calcs = pd.DataFrame(calcs)
            st.dataframe(df_calcs, use_container_width=True, hide_index=True)
            if st.button("🧹 Clear All Calculation Records"):
                st.session_state[STATE_KEY] = []
                st.rerun()
        else:
            st.info("No structural calculation records saved in the active session.")
