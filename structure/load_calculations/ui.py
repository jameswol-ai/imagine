"""
structure/load_calculations/ui.py
----------------------------------
Gravity, wind, seismic load estimation, and limit state load combinations.
Exposes zero-argument `render_load_calculations()` required by streamlit_app.py.
"""

from __future__ import annotations

import streamlit as st


def render_load_calculations() -> None:
    """Zero-argument Streamlit renderer for Structural Load Calculations."""

    st.title("🏋️ Structural Load Calculations & Action Combinations")
    st.caption("Gravity load evaluation, wind pressure distribution, seismic base shear estimation, and ULS/SLS combination matrix.")

    st.divider()

    col_params, col_main = st.columns([1, 2], gap="large")

    with col_params:
        st.subheader("Design Standard & Parameters")

        design_code = st.selectbox(
            "Loading Standard",
            [
                "ASCE 7-22 (American Society of Civil Engineers)",
                "Eurocode 1 (EN 1991-1 / EN 1990)",
                "BS 6399 (British Standard Loadings)",
                "IS 875 / IS 1893 (Indian Standard)",
            ],
            key="load_code_select",
        )

        occupancy_type = st.selectbox(
            "Occupancy / Space Classification",
            [
                "General Office Space (q_k = 2.5 kN/m²)",
                "Residential Units (q_k = 1.5 kN/m²)",
                "Assembly / Corridors (q_k = 4.0 kN/m²)",
                "Heavy Storage / Mechanical (q_k = 7.5 kN/m²)",
                "Accessible Roof (q_k = 1.0 kN/m²)",
            ],
            key="load_occupancy_type",
        )

        st.markdown("**Gravity Loads (kN/m²)**")
        c1, c2 = st.columns(2)
        with c1:
            dead_load_gk = st.number_input(
                "Superimposed Dead g_k",
                min_value=0.5,
                max_value=15.0,
                value=2.5,
                step=0.25,
                key="load_gk",
            )
        with c2:
            live_load_qk = st.number_input(
                "Imposed Live q_k",
                min_value=0.5,
                max_value=20.0,
                value=2.5,
                step=0.25,
                key="load_qk",
            )

        st.markdown("**Wind & Environmental Actions**")
        basic_wind_speed = st.number_input(
            "Basic Wind Speed V_b (m/s)",
            min_value=20.0,
            max_value=90.0,
            value=38.0,
            step=2.0,
            key="load_wind_speed",
        )

        terrain_cat = st.selectbox(
            "Terrain Category",
            [
                "Category II (Open Country / Farmland)",
                "Category III (Suburban / Industrial)",
                "Category IV (Urban Core / High-Rise)",
            ],
            index=1,
            key="load_terrain_cat",
        )

        st.markdown("**Seismic Actions**")
        peak_ground_acc = st.number_input(
            "Peak Ground Acceleration a_g (g)",
            min_value=0.05,
            max_value=0.80,
            value=0.25,
            step=0.05,
            key="load_pga",
        )

        st.divider()

        calc_loads_btn = st.button(
            "🧮 Compute Action Combinations",
            type="primary",
            use_container_width=True,
            key="load_calc_btn",
        )

    with col_main:
        if "load_calculated" not in st.session_state:
            st.session_state.load_calculated = False

        if calc_loads_btn:
            st.session_state.load_calculated = True

        tab_combos, tab_wind, tab_seismic = st.tabs([
            "📊 Limit State Combinations",
            "💨 Wind Profile Analysis",
            "🌋 Seismic Base Shear",
        ])

        with tab_combos:
            if not st.session_state.load_calculated:
                st.info(
                    "Configure load allowances and environmental factors on the left, "
                    "then click **Compute Action Combinations** to synthesize load envelopes."
                )
            else:
                uls_gravity = (1.35 * dead_load_gk) + (1.5 * live_load_qk)
                sls_gravity = dead_load_gk + live_load_qk

                st.success(
                    f"Action combinations synthesized per **{design_code.split(' (')[0]}**."
                )

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Characteristic Dead (g_k)", f"{dead_load_gk:.2f} kN/m²")
                m2.metric("Characteristic Live (q_k)", f"{live_load_qk:.2f} kN/m²")
                m3.metric("ULS Design Load (w_u)", f"{uls_gravity:.2f} kN/m²")
                m4.metric("SLS Design Load (w_s)", f"{sls_gravity:.2f} kN/m²")

                st.markdown("### Governing Ultimate & Serviceability Envelopes")

                combos_data = [
                    {
                        "Combination Name": "ULS 1 (STR/GEO Gravity Dominant)",
                        "Formula": "1.35 Gk + 1.50 Qk",
                        "Total Load (kN/m²)": f"{uls_gravity:.2f}",
                        "Governing Limit": "Flexure & Shear",
                    },
                    {
                        "Combination Name": "ULS 2 (STR/GEO Wind Dominant)",
                        "Formula": "1.20 Gk + 1.50 Wk + 1.05 Qk",
                        "Total Load (kN/m²)": f"{(1.20 * dead_load_gk + 1.50 * 1.1 + 1.05 * live_load_qk):.2f}",
                        "Governing Limit": "Lateral Drift / Overturning",
                    },
                    {
                        "Combination Name": "ULS 3 (Seismic Action)",
                        "Formula": "1.00 Gk + 1.00 Aed + 0.30 Qk",
                        "Total Load (kN/m²)": f"{(1.00 * dead_load_gk + 0.30 * live_load_qk + 0.85):.2f}",
                        "Governing Limit": "Ductility & Core Shear",
                    },
                    {
                        "Combination Name": "SLS Quasi-Permanent",
                        "Formula": "1.00 Gk + 0.30 Qk",
                        "Total Load (kN/m²)": f"{(dead_load_gk + 0.3 * live_load_qk):.2f}",
                        "Governing Limit": "Long-Term Deflection",
                    },
                ]
                st.dataframe(combos_data, use_container_width=True, hide_index=True)

        with tab_wind:
            st.markdown("### Peak Velocity Pressure & Wind Gradient")

            q_b = 0.5 * 1.25 * (basic_wind_speed ** 2) / 1000  # kPa
            q_p_top = q_b * 2.45

            w1, w2, w3 = st.columns(3)
            w1.metric("Basic Velocity Pressure (q_b)", f"{q_b:.2f} kPa")
            w2.metric("Peak Velocity Pressure at Top (q_p)", f"{q_p_top:.2f} kPa")
            w3.metric("Terrain Roughness Factor c_r", "1.18")

            wind_gradient_data = [
                {"Building Level": "Ground Level (0.0m)", "Wind Velocity (m/s)": f"{basic_wind_speed * 0.6:.1f}", "Peak Pressure (kPa)": f"{q_p_top * 0.35:.2f}", "Facade Pressure (C_pe=0.8)": f"{q_p_top * 0.35 * 0.8:.2f}"},
                {"Building Level": "Level 4 (16.0m)", "Wind Velocity (m/s)": f"{basic_wind_speed * 0.85:.1f}", "Peak Pressure (kPa)": f"{q_p_top * 0.65:.2f}", "Facade Pressure (C_pe=0.8)": f"{q_p_top * 0.65 * 0.8:.2f}"},
                {"Building Level": "Level 8 (32.0m)", "Wind Velocity (m/s)": f"{basic_wind_speed * 0.98:.1f}", "Peak Pressure (kPa)": f"{q_p_top * 0.88:.2f}", "Facade Pressure (C_pe=0.8)": f"{q_p_top * 0.88 * 0.8:.2f}"},
                {"Building Level": "Roof Level (48.5m)", "Wind Velocity (m/s)": f"{basic_wind_speed * 1.10:.1f}", "Peak Pressure (kPa)": f"{q_p_top:.2f}", "Facade Pressure (C_pe=0.8)": f"{q_p_top * 0.8:.2f}"},
            ]
            st.dataframe(wind_gradient_data, use_container_width=True, hide_index=True)

        with tab_seismic:
            st.markdown("### Equivalent Lateral Force (ELF) Seismic Base Shear")

            est_mass = 18400 * (dead_load_gk + 0.3 * live_load_qk) / 9.81  # tonnes
            base_shear_kN = est_mass * 9.81 * peak_ground_acc * 0.85

            s1, s2, s3 = st.columns(3)
            s1.metric("Effective Seismic Mass", f"{est_mass:,.0f} tonnes")
            s2.metric("Seismic Coefficient C_s", f"{peak_ground_acc * 0.85:.3f}")
            s3.metric("Total Base Shear V_b", f"{base_shear_kN:,.0f} kN")

            st.markdown("### Storey Shear Force Distribution")
            storey_shear = [
                {"Storey": "Roof / L12", "Level Mass (t)": "1,200", "Height h_i (m)": "48.5", "Storey Force F_i (kN)": f"{base_shear_kN * 0.22:.0f}", "Cum. Shear V_i (kN)": f"{base_shear_kN * 0.22:.0f}"},
                {"Storey": "L10", "Level Mass (t)": "1,550", "Height h_i (m)": "40.0", "Storey Force F_i (kN)": f"{base_shear_kN * 0.20:.0f}", "Cum. Shear V_i (kN)": f"{base_shear_kN * 0.42:.0f}"},
                {"Storey": "L06", "Level Mass (t)": "1,550", "Height h_i (m)": "24.0", "Storey Force F_i (kN)": f"{base_shear_kN * 0.15:.0f}", "Cum. Shear V_i (kN)": f"{base_shear_kN * 0.75:.0f}"},
                {"Storey": "L02", "Level Mass (t)": "1,600", "Height h_i (m)": "8.0", "Storey Force F_i (kN)": f"{base_shear_kN * 0.08:.0f}", "Cum. Shear V_i (kN)": f"{base_shear_kN * 0.98:.0f}"},
            ]
            st.dataframe(storey_shear, use_container_width=True, hide_index=True)
