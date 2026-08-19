"""
Structural Eurocode 6 (EN 1996) UI Renderer Module
Path: structural/eurocode/en1996/ui.py
"""

import math
import numpy as np
import pandas as pd
import streamlit as st


def render_en1996() -> None:
    """Renders the EN 1996 Design of Masonry Structures interface."""

    st.write(
        "Perform unreinforced masonry wall verification for ultimate limit state (ULS) vertical axial "
        "compression, out-of-plane flexure, and wall slenderness checks per EN 1996-1-1."
    )

    # --- MASONRY UNITS & EXECUTION CLASS BAR ---
    col_unit, col_mortar, col_exec = st.columns([1.5, 1.2, 1.3])

    with col_unit:
        unit_type = st.selectbox(
            "Masonry Unit Type & Group",
            [
                "Clay Units - Group 1",
                "Clay Units - Group 2 (Perforated)",
                "Calcium Silicate Units - Group 1",
                "Aggregate Concrete Units - Group 1",
                "Autoclaved Aerated Concrete (AAC)",
            ],
            index=0,
            help="Determines the shape constant K and exponents alpha/beta for characteristic compressive strength.",
        )

    with col_mortar:
        mortar_type = st.selectbox(
            "Mortar Class / Type",
            [
                "General Purpose - M12 (fm = 12 MPa)",
                "General Purpose - M5 (fm = 5 MPa)",
                "General Purpose - M2.5 (fm = 2.5 MPa)",
                "Thin Layer Mortar (0.5 - 3mm joint)",
                "Lightweight Mortar (fm = 5 MPa)",
            ],
            index=1,
            help="Mortar class affects bonding and composite compressive strength fk.",
        )

    with col_exec:
        exec_control = st.selectbox(
            "Execution & Manufacturing Class",
            [
                "Class 1 Execution + Category I Units (gamma_M = 1.5)",
                "Class 1 Execution + Category II Units (gamma_M = 1.8)",
                "Class 2 Execution + Category II Units (gamma_M = 2.2)",
            ],
            index=0,
            help="Selects material partial safety factor gamma_M per EN 1996-1-1 Table 2.3.",
        )

    st.divider()

    # --- MATERIAL CONSTANTS & PARTIAL SAFETY FACTOR ---
    gamma_m = float(exec_control.split("gamma_M = ")[1].replace(")", ""))

    # Mortar strength parsing
    if "Thin Layer" in mortar_type:
        f_m = 10.0  # Thin layer reference
        is_thin_bed = True
    else:
        f_m = float(mortar_type.split("fm = ")[1].split(" MPa")[0])
        is_thin_bed = False

    # Shape constants K for fk = K * fb^alpha * fm^beta (EN 1996-1-1 Table 3.3)
    if "Clay Units - Group 1" in unit_type:
        k_const, alpha, beta = (0.70, 0.85, 0.0) if is_thin_bed else (0.55, 0.70, 0.30)
    elif "Clay Units - Group 2" in unit_type:
        k_const, alpha, beta = (0.55, 0.70, 0.0) if is_thin_bed else (0.45, 0.70, 0.30)
    elif "Calcium Silicate" in unit_type:
        k_const, alpha, beta = (0.80, 0.85, 0.0) if is_thin_bed else (0.55, 0.70, 0.30)
    else:  # AAC or Aggregate
        k_const, alpha, beta = (0.80, 0.85, 0.0) if is_thin_bed else (0.55, 0.70, 0.30)

    # --- INPUT CONTROLS & CALCULATION LAYOUT ---
    col_geom_actions, col_design_results = st.columns([1, 2])

    with col_geom_actions:
        st.subheader("Geometry & Applied Actions")

        with st.expander("Unit Properties", expanded=True):
            f_b = st.number_input("Unit Normalized Compressive Strength fb (MPa)", min_value=1.5, max_value=75.0, value=15.0, step=1.0)

        with st.expander("Wall Dimensions & Support Conditions", expanded=True):
            wall_t = st.number_input("Wall Thickness t (mm)", min_value=90, max_value=500, value=215, step=5)
            wall_h = st.number_input("Clear Wall Height h (m)", min_value=1.0, max_value=10.0, value=2.8, step=0.1)
            wall_l = st.number_input("Wall Length L (m)", min_value=0.5, max_value=30.0, value=4.0, step=0.5)

            support_cond = st.selectbox(
                "Effective Height Factor (beta_h)",
                [
                    "1.00 - Restrained Top & Bottom",
                    "0.75 - Restrained Top/Bottom + Stiffened Sides",
                    "2.00 - Cantilever Wall",
                ],
                index=0,
            )

        with col_geom_actions.expander("ULS Internal Actions", expanded=True):
            n_ed = st.number_input("Design Vertical Action N_Ed (kN/m strip)", min_value=0.0, value=140.0, step=10.0)
            ecc_top = st.number_input("Top Load Eccentricity e_top (mm)", min_value=0.0, value=15.0, step=1.0)
            q_wind = st.number_input("Out-of-Plane Wind Pressure q_Ed (kPa)", min_value=0.0, max_value=5.0, value=0.50, step=0.05)

    with col_design_results:
        st.subheader("ULS Masonry Capacity & Slenderness Checks")

        # Effective Height & Slenderness Ratio
        beta_h = float(support_cond.split(" - ")[0])
        h_ef = beta_h * wall_h * 1000  # mm
        slenderness_lambda = h_ef / wall_t

        # Characteristic & Design Compressive Strength fk, fd
        f_k = k_const * (f_b**alpha) * (f_m**beta)  # MPa
        f_d = f_k / gamma_m  # MPa

        # Accidental & Initial Eccentricities (EN 1996-1-1 cl 6.1.2.2)
        e_init = h_ef / 450.0  # mm
        e_i = max(abs(ecc_top) + e_init, 0.05 * wall_t)

        # Capacity Reduction Factor Phi_i at Top/Bottom
        phi_i = 1.0 - 2.0 * (e_i / wall_t)

        # Creep Eccentricity & Middle Reduction Factor Phi_m (Simplified Method)
        e_k = 0.0  # Negligible creep for most standard masonry units
        e_mk = e_i + e_k
        slenderness_factor = (h_ef / (1400.0 * wall_t)) ** 2
        phi_m = (1.0 - 2.0 * (e_mk / wall_t)) * math.exp(-slenderness_factor)

        # Governing Capacity Reduction Factor
        phi_gov = max(0.0, min(phi_i, phi_m))

        # Vertical Axial Load Capacity NRd per meter length (kN/m)
        # NRd = Phi * t * fd * 1000mm / 1000 (to kN)
        n_rd = phi_gov * wall_t * f_d  # kN/m

        # Out-of-Plane Bending Capacity MRd (EN 1996-1-1 cl 6.3.1)
        # Flexural strength fxd1 (plane of failure parallel to bed joints)
        f_xk1 = 0.10 if "Clay" in unit_type else 0.15  # MPa characteristic
        f_xd1 = f_xk1 / gamma_m
        sigma_d = (n_ed * 1000) / (1000 * wall_t)  # Pre-compression stress (MPa)
        z_mod = (1000 * (wall_t**2)) / 6.0  # Section modulus mm³/m

        m_rd_plane = (f_xd1 + sigma_d) * z_mod / 1e6  # kNm/m
        m_ed_wind = (q_wind * (wall_h**2)) / 8.0  # Simply supported wind moment (kNm/m)

        # Utilizations
        ur_vertical = n_ed / n_rd if n_rd > 0 else 99.0
        ur_flexure = m_ed_wind / m_rd_plane if m_rd_plane > 0 else 0.0

        # Metrics Display
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Char. Strength fk", f"{f_k:.2f} MPa")
        m2.metric("Design Strength fd", f"{f_d:.2f} MPa", delta=f"gamma_M: {gamma_m}")
        m3.metric("Slenderness h_ef/t", f"{slenderness_lambda:.1f}", delta="PASS" if slenderness_lambda <= 27 else "HIGH")
        m4.metric("Capacity N_Rd", f"{n_rd:.1f} kN/m", delta=f"UR: {ur_vertical:.2f}")

        # Summary Table
        summary_df = pd.DataFrame(
            [
                {
                    "Design Check": "Wall Slenderness Limit (h_ef / t <= 27)",
                    "Calculated Value": f"lambda = {slenderness_lambda:.1f}",
                    "Limit / Capacity": "27.0",
                    "Utilization": f"{slenderness_lambda / 27.0:.2f}",
                    "Status": "PASS" if slenderness_lambda <= 27 else "EXCEEDS LIMIT",
                },
                {
                    "Design Check": "Vertical Axial Capacity ULS (N_Ed <= N_Rd)",
                    "Calculated Value": f"N_Ed = {n_ed:.1f} kN/m",
                    "Limit / Capacity": f"N_Rd = {n_rd:.1f} kN/m",
                    "Utilization": f"{ur_vertical:.2f}",
                    "Status": "PASS" if ur_vertical <= 1.0 else "FAIL",
                },
                {
                    "Design Check": "Out-of-Plane Flexure (M_Ed <= M_Rd)",
                    "Calculated Value": f"M_Ed = {m_ed_wind:.2f} kNm/m",
                    "Limit / Capacity": f"M_Rd = {m_rd_plane:.2f} kNm/m",
                    "Utilization": f"{ur_flexure:.2f}",
                    "Status": "PASS" if ur_flexure <= 1.0 else "FAIL",
                },
            ]
        )
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

        # Chart: Axial Capacity NRd vs Wall Thickness t
        st.markdown("**Design Vertical Capacity (N_Rd) vs. Wall Thickness (t)**")
        thicknesses = np.linspace(100, 400, 25)
        n_rd_list = []

        for t_val in thicknesses:
            h_e = beta_h * wall_h * 1000
            ei_val = max(abs(ecc_top) + (h_e / 450.0), 0.05 * t_val)
            phi_i_v = 1.0 - 2.0 * (ei_val / t_val)
            phi_m_v = (1.0 - 2.0 * (ei_val / t_val)) * math.exp(-((h_e / (1400.0 * t_val)) ** 2))
            phi_g = max(0.0, min(phi_i_v, phi_m_v))
            n_rd_list.append(phi_g * t_val * f_d)

        chart_df = pd.DataFrame(
            {"Wall Thickness t (mm)": thicknesses, "Vertical Capacity N_Rd [kN/m]": n_rd_list}
        ).set_index("Wall Thickness t (mm)")

        st.line_chart(chart_df)
