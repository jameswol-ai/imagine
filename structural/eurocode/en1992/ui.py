"""
Structural Eurocode 2 (EN 1992) UI Renderer Module
Path: structural/eurocode/en1992/ui.py
"""

import math
import numpy as np
import pandas as pd
import streamlit as st


def render_en1992() -> None:
    """Renders the EN 1992 Design of Concrete Structures interface."""

    st.write(
        "Perform reinforced concrete cross-section design and ultimate limit state (ULS) flexural "
        "and shear capacity checks in accordance with EN 1992-1-1."
    )

    # --- MATERIAL SELECTION BAR ---
    col_conc, col_steel, col_gamma = st.columns([1.5, 1.5, 1])

    with col_conc:
        concrete_grade = st.selectbox(
            "Concrete Class",
            [
                "C20/25 (fck = 20 MPa)",
                "C25/30 (fck = 25 MPa)",
                "C30/37 (fck = 30 MPa)",
                "C35/45 (fck = 35 MPa)",
                "C40/50 (fck = 40 MPa)",
                "C50/60 (fck = 50 MPa)",
            ],
            index=2,
        )

    with col_steel:
        steel_grade = st.selectbox(
            "Reinforcement Steel Grade",
            [
                "B500A (fyk = 500 MPa)",
                "B500B (fyk = 500 MPa)",
                "B500C (fyk = 500 MPa)",
                "B450C (fyk = 450 MPa)",
            ],
            index=1,
        )

    with col_gamma:
        acc_coefficient = st.number_input(
            "Alpha cc (acc)",
            min_value=0.80,
            max_value=1.00,
            value=0.85,
            step=0.05,
            help="Long-term coefficient for concrete strength under sustained loads.",
        )

    st.divider()

    # --- INPUT CONTROLS & CALCULATION LAYOUT ---
    col_geom_actions, col_design_results = st.columns([1, 2])

    # Material strength parsing
    fck = float(concrete_grade.split("fck = ")[1].split(" MPa")[0])
    fyk = float(steel_grade.split("fyk = ")[1].split(" MPa")[0])

    gamma_c = 1.50  # Partial factor for concrete ULS
    gamma_s = 1.15  # Partial factor for steel ULS

    fcd = (acc_coefficient * fck) / gamma_c
    fyd = fyk / gamma_s

    # Concrete tensile strength fctm approximation
    if fck <= 50:
        fctm = 0.30 * (fck ** (2 / 3))
    else:
        fctm = 2.12 * math.log(1 + (fck + 8) / 10)

    with col_geom_actions:
        st.subheader("Section Geometry & Actions")

        with st.expander("Cross-Section Dimensions", expanded=True):
            width_b = st.number_input("Width b (mm)", min_value=100, max_value=2000, value=300, step=25)
            height_h = st.number_input("Height h (mm)", min_value=150, max_value=3000, value=500, step=25)
            nom_cover = st.number_input("Nominal Concrete Cover c_nom (mm)", min_value=20, max_value=100, value=35, step=5)
            link_dia = st.selectbox("Shear Link Diameter (mm)", [8, 10, 12, 16], index=1)
            bar_dia = st.selectbox("Main Rebar Diameter (mm)", [12, 16, 20, 25, 32], index=2)

        with col_geom_actions.expander("Ultimate Internal Actions (ULS)", expanded=True):
            m_ed = st.number_input("Design Bending Moment M_Ed (kNm)", min_value=0.0, value=150.0, step=10.0)
            v_ed = st.number_input("Design Shear Force V_Ed (kN)", min_value=0.0, value=85.0, step=5.0)

    with col_design_results:
        st.subheader("Flexural & Shear Design (EN 1992-1-1)")

        # Effective depth calculation
        effective_depth_d = height_h - nom_cover - link_dia - (bar_dia / 2)

        # Flexural Factor K
        k_factor = (m_ed * 1e6) / (width_b * (effective_depth_d**2) * fck)
        k_prime = 0.168  # Assuming redistribution <= 20%

        # Required Tension Steel Calculation
        if k_factor <= k_prime:
            flexure_status = "Singly Reinforced Section"
            z_lever_arm = effective_depth_d * min(0.95, 0.5 * (1 + math.sqrt(max(0, 1 - 3.53 * k_factor))))
            as_req = (m_ed * 1e6) / (fyd * z_lever_arm)
            as_comp_req = 0.0
        else:
            flexure_status = "Doubly Reinforced Section Required"
            z_lever_arm = 0.82 * effective_depth_d
            d2 = nom_cover + link_dia + (bar_dia / 2)
            delta_m = (k_factor - k_prime) * width_b * (effective_depth_d**2) * fck
            as_comp_req = delta_m / (fyd * (effective_depth_d - d2))
            as_req = ((k_prime * width_b * (effective_depth_d**2) * fck) / (fyd * z_lever_arm)) + as_comp_req

        # Minimum & Maximum Reinforcement Limits
        as_min = max(0.26 * (fctm / fyk) * width_b * effective_depth_d, 0.0013 * width_b * effective_depth_d)
        as_max = 0.04 * width_b * height_h
        as_prov_design = max(as_req, as_min)

        # Rebar Quantity Suggestion
        single_bar_area = (math.pi * (bar_dia**2)) / 4
        bars_needed = math.ceil(as_prov_design / single_bar_area)
        as_provided = bars_needed * single_bar_area

        # Shear Design Check (EN 1992-1-1 cl 6.2.2)
        k_shear = min(2.0, 1 + math.sqrt(200 / effective_depth_d))
        rho_l = min(0.02, as_provided / (width_b * effective_depth_d))
        v_rd_c_min = 0.035 * (k_shear**1.5) * (fck**0.5) * width_b * effective_depth_d / 1000
        v_rd_c = max(
            (0.12 * k_shear * ((100 * rho_l * fck) ** (1 / 3))) * width_b * effective_depth_d / 1000,
            v_rd_c_min,
        )

        shear_reinf_req = v_ed > v_rd_c

        # Metrics display
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Effective Depth d", f"{effective_depth_d:.0f} mm")
        m2.metric("K Factor", f"{k_factor:.3f}", delta="OK" if k_factor <= k_prime else "Doubly Reinf.")
        m3.metric("Required As", f"{as_prov_design:.0f} mm²")
        m4.metric("Suggested Rebar", f"{bars_needed} T{bar_dia} ({as_provided:.0f} mm²)")

        st.markdown(f"**Section Status:** `{flexure_status}`")

        # Capacity Summary Table
        summary_df = pd.DataFrame(
            [
                {
                    "Check / Parameter": "Flexural Factor K vs K'",
                    "Calculated Value": f"K = {k_factor:.3f}",
                    "Limit / Capacity": f"K' = {k_prime:.3f}",
                    "Status": "PASS (Singly Reinforced)" if k_factor <= k_prime else "COMPRESSION STEEL REQ",
                },
                {
                    "Check / Parameter": "Tension Reinforcement Area (As)",
                    "Calculated Value": f"As,req = {as_req:.0f} mm²",
                    "Limit / Capacity": f"As,min = {as_min:.0f} mm²",
                    "Status": "PASS" if as_provided >= as_min else "BELOW MINIMUM",
                },
                {
                    "Check / Parameter": "Shear Capacity without Links (VRd,c)",
                    "Calculated Value": f"V_Ed = {v_ed:.1f} kN",
                    "Limit / Capacity": f"V_Rd,c = {v_rd_c:.1f} kN",
                    "Status": "NO SHEAR REINF. REQ" if not shear_reinf_req else "SHEAR LINKS REQUIRED",
                },
            ]
        )
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

        # Moment Resistance Curve
        st.markdown("**Moment Resistance MRd vs. Provided Tension Steel Area (As)**")
        as_range = np.linspace(as_min, as_max * 0.5, 30)
        m_rd_list = [(a * fyd * (effective_depth_d - 0.4 * ((a * fyd) / (width_b * fcd)))) / 1e6 for a in as_range]

        curve_df = pd.DataFrame(
            {"Provided As (mm²)": as_range, "Moment Resistance MRd (kNm)": m_rd_list}
        ).set_index("Provided As (mm²)")
        st.line_chart(curve_df)
