"""
Structural Eurocode 4 (EN 1994) UI Renderer Module
Path: structural/eurocode/en1994/ui.py
App: imagine
"""

import math
import numpy as np
import pandas as pd
import streamlit as st


def render_en1994() -> None:
    """Renders the EN 1994 Design of Composite Steel and Concrete Structures interface."""

    st.write(
        "Design simply supported composite steel-concrete beams and shear stud connection capacity "
        "at Ultimate Limit State (ULS) per EN 1994-1-1."
    )

    # --- MATERIAL & SAFETY FACTOR CONTROLS ---
    col_steel, col_conc, col_stud = st.columns(3)

    with col_steel:
        steel_grade = st.selectbox(
            "Structural Steel Grade",
            ["S235 (fy = 235 MPa)", "S275 (fy = 275 MPa)", "S355 (fy = 355 MPa)", "S460 (fy = 460 MPa)"],
            index=2,
            help="Characteristic yield strength f_yb per EN 1993-1-1.",
        )

    with col_conc:
        concrete_grade = st.selectbox(
            "Concrete Slab Class",
            [
                "C20/25 (fck = 20 MPa)",
                "C25/30 (fck = 25 MPa)",
                "C30/37 (fck = 30 MPa)",
                "C35/45 (fck = 35 MPa)",
                "C40/50 (fck = 40 MPa)",
            ],
            index=1,
            help="Characteristic cylinder compressive strength fck.",
        )

    with col_stud:
        stud_grade = st.selectbox(
            "Heading Stud Connector Class",
            ["SD1 (fu = 450 MPa)", "SD2 (fu = 500 MPa)"],
            index=0,
            help="Ultimate tensile strength f_u for headed shear studs (EN 13918).",
        )

    st.divider()

    # --- MATERIAL CONSTANTS ---
    f_yb = float(steel_grade.split("fy = ")[1].split(" MPa")[0])
    f_ck = float(concrete_grade.split("fck = ")[1].split(" MPa")[0])
    f_u = float(stud_grade.split("fu = ")[1].split(" MPa")[0])

    gamma_a = 1.00  # Partial factor for structural steel
    gamma_c = 1.50  # Partial factor for concrete
    gamma_v = 1.25  # Partial factor for shear studs

    f_yd = f_yb / gamma_a
    f_cd = (0.85 * f_ck) / gamma_c

    # Secant modulus of elasticity E_cm (EN 1992-1-1)
    e_cm = 22.0 * ((f_ck + 8.0) / 10.0) ** 0.3  # GPa

    # --- INPUT CONTROLS ---
    col_geom, col_actions = st.columns([1.1, 0.9])

    with col_geom:
        st.subheader("Composite Cross-Section Geometry")

        with st.expander("Steel Beam & Concrete Slab", expanded=True):
            span_l = st.number_input("Span Length L (m)", min_value=3.0, max_value=30.0, value=12.0, step=0.5)
            b_eff = st.number_input("Effective Slab Width b_eff (mm)", min_value=500, max_value=4000, value=2500, step=100)
            h_c = st.number_input("Concrete Slab Thickness h_c (mm)", min_value=80, max_value=300, value=130, step=10)

            st.markdown("**Steel Profile Properties (IPE / HEB Equivalent)**")
            a_a = st.number_input("Steel Cross-Section Area A_a (mm²)", min_value=1000, max_value=50000, value=7680, step=200)
            h_a = st.number_input("Steel Profile Total Depth h_a (mm)", min_value=100, max_value=1200, value=400, step=20)
            w_pl_a = st.number_input("Plastic Section Modulus W_pl,a (cm³)", min_value=100, max_value=10000, value=1307, step=50)

        with st.expander("Head Shear Stud Details", expanded=True):
            d_stud = st.selectbox("Stud Shank Diameter d (mm)", [16, 19, 22], index=1)
            h_stud = st.number_input("Overall Stud Height h_sc (mm)", min_value=50, max_value=200, value=100, step=5)
            n_studs_row = st.selectbox("Studs per Trough / Transverse Row", [1, 2], index=0)

    with col_actions:
        st.subheader("Design Internal Actions & Connector Check")

        with st.expander("Applied ULS Actions", expanded=True):
            m_ed = st.number_input("Design Bending Moment M_Ed (kNm)", min_value=0.0, value=420.0, step=10.0)
            v_ed = st.number_input("Design Vertical Shear V_Ed (kN)", min_value=0.0, value=160.0, step=10.0)

        with st.expander("Provided Connectors", expanded=True):
            n_provided_half = st.number_input(
                "Provided Shear Studs (per Half-Span)", min_value=4, max_value=200, value=30, step=2
            )

    # --- RESISTANCE CALCULATIONS ---
    # 1. Axial Force Capacities
    n_a = (a_a * f_yd) / 1000.0  # Plastic axial tensile capacity of steel (kN)
    n_cf = (b_eff * h_c * f_cd) / 1000.0  # Compressive capacity of concrete flange (kN)

    # 2. Plastic Neutral Axis (PNA) Location & Bending Resistance
    m_pl_a_rd = (w_pl_a * 1e3 * f_yd) / 1e6  # Steel beam plastic moment capacity (kNm)

    if n_cf >= n_a:
        # PNA lies within concrete slab
        x_pna = (n_a * 1000.0) / (b_eff * f_cd)  # Depth into concrete (mm)
        lever_arm_z = (h_a / 2.0) + h_c - (x_pna / 2.0)
        m_pl_rd = (n_a * lever_arm_z) / 1000.0  # kNm
        pna_location = f"Concrete Slab (x = {x_pna:.1f} mm)"
    else:
        # PNA lies in steel flange/web
        d_extra = (n_a - n_cf) * 1000.0 / (2.0 * f_yd)
        lever_arm_z = (h_a / 2.0) + (h_c / 2.0)
        m_pl_rd = m_pl_a_rd + (n_cf * lever_arm_z) / 1000.0  # kNm
        pna_location = "Steel Beam Flange/Web"

    # 3. Shear Stud Design Capacity P_Rd per stud (EN 1994-1-1 cl 6.6.3.1)
    d_sc = float(d_stud)
    a_sc = math.pi * (d_sc**2) / 4.0  # Cross-sectional area of stud (mm²)

    # Concrete crushing criteria
    alpha_stud = 0.2 * (h_stud / d_sc + 1.0) if (h_stud / d_sc) < 4.0 else 1.0
    p_rd_1 = (0.29 * alpha_stud * (d_sc**2) * math.sqrt(f_ck * e_cm * 1000.0)) / (gamma_v * 1000.0)  # kN

    # Stud shearing criteria
    p_rd_2 = (0.8 * f_u * a_sc) / (gamma_v * 1000.0)  # kN

    p_rd = min(p_rd_1, p_rd_2)  # Characteristic stud resistance (kN)

    # Required Studs for Full Shear Connection (Half-Span)
    n_f_req = math.ceil(min(n_a, n_cf) / p_rd)

    # Degree of Shear Connection
    η_conn = min(1.0, n_provided_half / n_f_req) if n_f_req > 0 else 1.0

    # Bending capacity reduction for partial interaction if applicable
    if η_conn < 1.0:
        m_rd_final = m_pl_a_rd + η_conn * (m_pl_rd - m_pl_a_rd)
    else:
        m_rd_final = m_pl_rd

    ur_flexure = m_ed / m_rd_final if m_rd_final > 0 else 0.0

    # --- DISPLAY METRICS & CALCULATIONS ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Design Bending Cap. M_Rd", f"{m_rd_final:.1f} kNm")
    m2.metric("Flexural Utilization", f"{ur_flexure:.2f}", delta="PASS" if ur_flexure <= 1.0 else "FAIL")
    m3.metric("Stud Capacity P_Rd", f"{p_rd:.1f} kN")
    m4.metric("Shear Interaction η", f"{η_conn * 100:.0f}%", delta="FULL" if η_conn >= 1.0 else "PARTIAL")

    st.subheader("ULS Verification Summary")

    summary_df = pd.DataFrame(
        [
            {
                "Design Check": "Composite Moment Resistance (M_Ed <= M_Rd)",
                "Applied / Req.": f"{m_ed:.1f} kNm",
                "Capacity / Limit": f"{m_rd_final:.1f} kNm",
                "Utilization": f"{ur_flexure:.2f}",
                "Status": "PASS" if ur_flexure <= 1.0 else "FAIL (INCREASE SECTION)",
            },
            {
                "Design Check": "Full Interaction Stud Count (per Half-Span)",
                "Applied / Req.": f"{n_provided_half} studs provided",
                "Capacity / Limit": f"{n_f_req} studs required",
                "Utilization": f"{n_f_req / n_provided_half:.2f}" if n_provided_half > 0 else "N/A",
                "Status": "FULL INTERACTION" if η_conn >= 1.0 else "PARTIAL INTERACTION",
            },
            {
                "Design Check": "Plastic Neutral Axis Location",
                "Applied / Req.": pna_location,
                "Capacity / Limit": f"Slab Depth h_c = {h_c} mm",
                "Utilization": "-",
                "Status": "VALIDATED",
            },
        ]
    )
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    # Bending Resistance Chart: M_Rd vs Degree of Shear Interaction η
    st.markdown("**Moment Resistance (M_Rd) vs. Degree of Shear Interaction (η)**")
    eta_range = np.linspace(0.0, 1.0, 20)
    m_rd_curve = [m_pl_a_rd + eta * (m_pl_rd - m_pl_a_rd) for eta in eta_range]

    chart_df = pd.DataFrame(
        {"Shear Interaction η": eta_range, "Moment Resistance M_Rd [kNm]": m_rd_curve}
    ).set_index("Shear Interaction η")

    st.line_chart(chart_df)
