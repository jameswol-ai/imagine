"""
Structural Eurocode 1 (EN 1991) UI Renderer Module
Path: structural/eurocode/en1991/ui.py
"""

import numpy as np
import pandas as pd
import streamlit as st


def render_en1991() -> None:
    """Renders the EN 1991 Wind and Snow Load Estimations interface."""

    st.write(
        "Calculate basic wind velocity pressures, terrain roughness effects (EN 1991-1-4), "
        "and ground/roof snow load distributions (EN 1991-1-3)."
    )

    # --- REGIONAL & SITE ASSUMPTIONS BAR ---
    col_region, col_alt, col_orog = st.columns([1.5, 1, 1])

    with col_region:
        national_annex = st.selectbox(
            "National Annex / Region",
            ["Standard EN 1991 Core", "UK National Annex", "German National Annex", "French National Annex"],
            index=0,
        )

    with col_alt:
        altitude = st.number_input("Site Altitude (m above sea level)", min_value=0, max_value=3000, value=250, step=50)

    with col_orog:
        orography = st.selectbox(
            "Orography Factor (co)",
            ["Flat Terrain (co = 1.0)", "Isolated Hill / Crest (co = 1.15)", "Cliffs / Escarpment (co = 1.30)"],
            index=0,
        )

    st.divider()

    # --- ACTIONS TABS ---
    tab_wind, tab_snow = st.tabs(["Wind Actions (EN 1991-1-4)", "Snow Loads (EN 1991-1-3)"])

    # =========================================================================
    # TAB 1: WIND ACTIONS (EN 1991-1-4)
    # =========================================================================
    with tab_wind:
        col_w_input, col_w_results = st.columns([1, 2])

        with col_w_input:
            st.subheader("Wind Parameters")

            vb0 = st.number_input("Basic Wind Velocity vb,0 (m/s)", min_value=10.0, max_value=60.0, value=26.0, step=1.0)

            terrain_cat = st.selectbox(
                "Terrain Category",
                [
                    "0 - Sea or coastal area",
                    "I - Lakes / flat area with negligible vegetation",
                    "II - Area with low vegetation (farmland)",
                    "III - Area with regular cover of vegetation or buildings",
                    "IV - Urban areas (at least 15% built up > 15m)",
                ],
                index=2,
            )

            bldg_height = st.slider("Building Reference Height z (m)", min_value=2.0, max_value=120.0, value=18.0, step=1.0)
            c_dir = st.slider("Directional Factor (c_dir)", min_value=0.8, max_value=1.0, value=1.0, step=0.05)
            c_season = st.slider("Season Factor (c_season)", min_value=0.8, max_value=1.0, value=1.0, step=0.05)

        with col_w_results:
            st.subheader("Velocity Pressure & Terrain Profile")

            # Simplified EN 1991-1-4 terrain roughness calculation lookup
            cat_code = terrain_cat.split(" - ")[0]
            z0_map = {"0": 0.003, "I": 0.01, "II": 0.05, "III": 0.3, "IV": 1.0}
            z_min_map = {"0": 1.0, "I": 1.0, "II": 2.0, "III": 5.0, "IV": 10.0}

            z0 = z0_map[cat_code]
            z_min = z_min_map[cat_code]
            c_o = float(orography.split("co = ")[1].replace(")", ""))

            vb = c_dir * c_season * vb0

            # Roughness factor cr(z) & mean velocity vm(z)
            kr = 0.19 * (z0 / 0.05) ** 0.07
            effective_z = max(bldg_height, z_min)
            cr_z = kr * np.log(effective_z / z0)
            vm_z = cr_z * c_o * vb

            # Turbulence intensity Iv(z) & peak velocity pressure qp(z)
            kl = 1.0
            iv_z = kl / (c_o * np.log(effective_z / z0))
            air_density = 1.25  # kg/m³
            qp_z = (1 + 7 * iv_z) * 0.5 * air_density * (vm_z**2) / 1000  # in kN/m²

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Fundamental vb", f"{vb:.1f} m/s")
            m2.metric("Mean Velocity vm(z)", f"{vm_z:.2f} m/s")
            m3.metric("Turbulence Iv(z)", f"{iv_z:.3f}")
            m4.metric("Peak Pressure qp(z)", f"{qp_z:.2f} kN/m²")

            # Height profile graph
            st.markdown("**Peak Velocity Pressure Profile vs. Height z**")
            heights = np.linspace(2.0, max(bldg_height * 1.5, 30.0), 20)
            qp_profile = []
            for h in heights:
                eff_h = max(h, z_min)
                cr_h = kr * np.log(eff_h / z0)
                vm_h = cr_h * c_o * vb
                iv_h = kl / (c_o * np.log(eff_h / z0))
                qp_h = (1 + 7 * iv_h) * 0.5 * air_density * (vm_h**2) / 1000
                qp_profile.append(qp_h)

            profile_df = pd.DataFrame(
                {"Height z (m)": heights, "Peak Pressure qp(z) [kN/m²]": qp_profile}
            ).set_index("Height z (m)")
            st.line_chart(profile_df)

    # =========================================================================
    # TAB 2: SNOW LOADS (EN 1991-1-3)
    # =========================================================================
    with tab_snow:
        col_s_input, col_s_results = st.columns([1, 2])

        with col_s_input:
            st.subheader("Snow Parameters")

            sk = st.number_input("Characteristic Ground Snow sk (kN/m²)", min_value=0.2, max_value=10.0, value=1.2, step=0.1)
            roof_pitch = st.slider("Roof Pitch Angle (degrees)", min_value=0.0, max_value=70.0, value=25.0, step=1.0)

            topo_type = st.selectbox(
                "Topography Exposure",
                ["Windswept (Ce = 0.8)", "Normal (Ce = 1.0)", "Sheltered (Ce = 1.2)"],
                index=1,
            )

            thermal_coeff = st.number_input("Thermal Coefficient Ct", min_value=0.5, max_value=1.2, value=1.0, step=0.05)

        with col_s_results:
            st.subheader("Roof Snow Load Estimation")

            ce = float(topo_type.split("Ce = ")[1].replace(")", ""))

            # Shape coefficient mu1 determination (EN 1991-1-3 Table 5.2)
            if roof_pitch <= 30.0:
                mu1 = 0.8
            elif roof_pitch >= 60.0:
                mu1 = 0.0
            else:
                mu1 = 0.8 * (60.0 - roof_pitch) / 30.0

            s_roof = mu1 * ce * thermal_coeff * sk

            sm1, sm2, sm3, sm4 = st.columns(4)
            sm1.metric("Ground Snow sk", f"{sk:.2f} kN/m²")
            sm2.metric("Shape Coeff. μ1", f"{mu1:.2f}")
            sm3.metric("Exposure Ce", f"{ce:.1f}")
            sm4.metric("Design Roof Snow s", f"{s_roof:.2f} kN/m²")

            st.markdown("**Snow Load Variation by Roof Pitch**")
            pitches = np.linspace(0.0, 70.0, 25)
            snow_loads = []
            for p in pitches:
                if p <= 30.0:
                    m = 0.8
                elif p >= 60.0:
                    m = 0.0
                else:
                    m = 0.8 * (60.0 - p) / 30.0
                snow_loads.append(m * ce * thermal_coeff * sk)

            snow_df = pd.DataFrame(
                {"Roof Pitch (deg)": pitches, "Roof Snow Load s [kN/m²]": snow_loads}
            ).set_index("Roof Pitch (deg)")
            st.line_chart(snow_df)
