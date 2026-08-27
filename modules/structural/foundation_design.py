"""
IMAGINE Platform — Eurocode 7 & 2 (EN 1997-1 / EN 1992-1-1) Pad Footing Design Engine
Path: modules/structural/foundation_design.py
App: imagine
"""

import math
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from modules.utils.crud import CRUDService

STATE_KEY = "pad_footing_designs"


def render() -> None:
    """Renders the Eurocode 7 & 2 Shallow Pad Footing Design and Verification module."""
    st.title("🔲 Eurocode 7 & 2 Shallow Pad Footing Design")
    st.caption("Geotechnical bearing pressure (EN 1997-1) and structural flexure/shear verification (EN 1992-1-1).")

    items = CRUDService.get_all(STATE_KEY)

    tab_design, tab_report, tab_schedule = st.tabs([
        "📐 Footing Designer & Verification",
        "📜 Design Theory & Verification Rules",
        "💾 Saved Footing Schedule"
    ])

    # ==============================================================================
    # TAB 1: FOOTING DESIGNER & VERIFICATION
    # ==============================================================================
    with tab_design:
        col_inputs, col_results = st.columns([1, 1])

        with col_inputs:
            st.subheader("1. Footing Geometry & Column Setup")
            c_geo1, c_geo2 = st.columns(2)
            with c_geo1:
                b_pad = st.number_input("Footing Width B (x-dir, m)", min_value=0.8, max_value=10.0, value=2.2, step=0.1)
                l_pad = st.number_input("Footing Length L (y-dir, m)", min_value=0.8, max_value=10.0, value=2.2, step=0.1)
                h_pad = st.number_input("Footing Depth H (mm)", min_value=300, max_value=2000, value=600, step=50)
            with c_geo2:
                c_x = st.number_input("Column Width cx (mm)", min_value=150, max_value=1500, value=400, step=50)
                c_y = st.number_input("Column Depth cy (mm)", min_value=150, max_value=1500, value=400, step=50)
                c_nom = st.number_input("Nominal Cover c_nom (mm)", min_value=35, max_value=100, value=50, step=5)

            st.markdown("---")
            st.subheader("2. Soil & Material Parameters")
            c_mat1, c_mat2 = st.columns(2)
            with c_mat1:
                q_allow = st.number_input("Allowable Bearing Capacity q_allow (kPa)", min_value=50.0, max_value=1000.0, value=200.0, step=10.0)
                gamma_soil = st.number_input("Soil Unit Weight γ_soil (kN/m³)", value=18.0, step=0.5)
                fck = st.selectbox("Concrete Grade fck (MPa)", [20, 25, 30, 35, 40], index=2)
            with c_mat2:
                fyk = st.number_input("Steel Yield fyk (MPa)", value=500, step=50)
                gamma_c = st.number_input("γc (Concrete)", value=1.50, step=0.05)
                gamma_s = st.number_input("γs (Steel)", value=1.15, step=0.05)

            st.markdown("---")
            st.subheader("3. Loads & Reinforcement")
            c_ld1, c_ld2 = st.columns(2)
            with c_ld1:
                n_ed = st.number_input("Design Axial Load N_Ed (kN)", min_value=10.0, value=950.0, step=50.0)
                m_edx = st.number_input("Design Moment M_Ed,x (kNm)", value=65.0, step=5.0)
                m_edy = st.number_input("Design Moment M_Ed,y (kNm)", value=30.0, step=5.0)
            with c_ld2:
                bar_dia = st.selectbox("Rebar Diameter Ø (mm)", [12, 16, 20, 25], index=1)
                bar_spacing = st.selectbox("Rebar Spacing s (mm)", [100, 125, 150, 175, 200, 250], index=3)

            footing_tag = st.text_input("Footing Mark / Identifier", value="F-101")

        # --- Eurocode 7 & 2 Calculation Engine ---
        alpha_cc = 0.85
        fcd = (alpha_cc * fck) / gamma_c
        fyd = fyk / gamma_s
        fctm = 0.30 * (fck ** (2/3)) if fck <= 50 else 2.12 * math.log(1 + (fck / 10))

        # Effective Depth
        d_eff = h_pad - c_nom - bar_dia

        # Self-weight & total vertical load
        sw_pad = b_pad * l_pad * (h_pad / 1000.0) * 25.0  # Concrete self-weight (kN)
        n_total = n_ed + 1.35 * sw_pad

        # Eccentricities
        e_x = (m_edx / n_total) if n_total > 0 else 0.0
        e_y = (m_edy / n_total) if n_total > 0 else 0.0

        # Bearing Pressure Distribution (Gross Contact Stress)
        area_pad = b_pad * l_pad
        sigma_avg = n_total / area_pad
        sigma_max = sigma_avg * (1.0 + (6.0 * abs(e_x) / b_pad) + (6.0 * abs(e_y) / l_pad))
        sigma_min = sigma_avg * (1.0 - (6.0 * abs(e_x) / b_pad) - (6.0 * abs(e_y) / l_pad))

        bearing_util = sigma_max / q_allow if q_allow > 0 else 1.0

        # Flexural Moment at Column Face (Critical Section x-dir cantilever projection)
        a_x = (b_pad - (c_x / 1000.0)) / 2.0
        m_ed_crit = (sigma_max * (a_x ** 2) / 2.0) * l_pad  # kNm across length L

        # Flexural Steel Check per meter width
        m_ed_per_m = m_ed_crit / l_pad
        k_val = (m_ed_per_m * 1e6) / (1000.0 * (d_eff**2) * fcd) if d_eff > 0 else 0.0
        z_lever = min(0.95 * d_eff, d_eff * 0.5 * (1 + math.sqrt(max(0.0, 1 - 3.53 * k_val))))
        as_req = (m_ed_per_m * 1e6) / (fyd * z_lever) if z_lever > 0 else 0.0

        as_min = max(0.26 * (fctm / fyk) * 1000.0 * d_eff, 0.0013 * 1000.0 * d_eff)
        as_prov = (1000.0 / bar_spacing) * (math.pi / 4.0) * (bar_dia ** 2)
        as_target = max(as_req, as_min)

        # One-Way Shear at Section d_eff from Column Face
        v_ed_oneway = sigma_max * max(0.0, a_x - (d_eff / 1000.0)) * l_pad  # kN
        v_rd_c = max(0.12 * (1 + math.sqrt(200.0 / d_eff)) * ((100 * (as_prov / (1000 * d_eff)) * fck) ** (1/3)), 0.035 * (1 + math.sqrt(200.0 / d_eff))**(1.5) * math.sqrt(fck)) * 1000.0 * d_eff / 1000.0  # kN/m
        v_rd_c_tot = v_rd_c * l_pad

        one_way_shear_pass = v_ed_oneway <= v_rd_c_tot

        with col_results:
            st.subheader("Results & Geotechnical Summary")

            m1, m2, m3 = st.columns(3)
            m1.metric("Max Soil Pressure q_max", f"{sigma_max:.1f} kPa", delta=f"{bearing_util * 100:.1f}% Capacity")
            m2.metric("Min Soil Pressure q_min", f"{max(0.0, sigma_min):.1f} kPa")
            m3.metric("Pad Self-Weight", f"{sw_pad:.1f} kN")

            st.divider()

            st.markdown("### Structural Verification Checks")
            k1, k2 = st.columns(2)
            with k1:
                st.markdown("**Bearing & Eccentricity**")
                st.write(f"- Eccentricity $e_x$: **{e_x * 1000:.1f} mm** (Limit: {b_pad * 1000 / 6:.0f} mm)")
                st.write(f"- Eccentricity $e_y$: **{e_y * 1000:.1f} mm** (Limit: {l_pad * 1000 / 6:.0f} mm)")
                if bearing_util <= 1.0 and sigma_min >= 0:
                    st.success("✅ Soil Capacity OK (No Tension)")
                else:
                    st.warning("⚠️ Soil Overstress or Partial Tension Base")

            with k2:
                st.markdown("**Flexure & Shear ULS**")
                st.write(f"- Required Steel: **{as_target:.0f} mm²/m**")
                st.write(f"- Provided Steel: **Ø{bar_dia}@{bar_spacing} mm** ({as_prov:.0f} mm²/m)")
                st.write(f"- One-Way Shear $V_{{Ed}}$: **{v_ed_oneway:.1f} kN** (Cap: {v_rd_c_tot:.1f} kN)")
                if as_prov >= as_target and one_way_shear_pass:
                    st.success("✅ Reinforcement & Shear OK")
                else:
                    st.error("❌ Reinforcement or Shear Check Failed")

            # Interactive Soil Contact Pressure & Footing Plan Diagram
            st.markdown("### Footing Geometry & Contact Stress Profile")
            fig = go.Figure()

            # Footing outline
            fig.add_shape(type="rect", x0=0, y0=0, x1=b_pad, y1=l_pad, line=dict(color="#2B6CB0", width=3), fillcolor="rgba(43, 108, 176, 0.1)")

            # Column outline centered
            cx_m, cy_m = c_x / 1000.0, c_y / 1000.0
            x_col_0 = (b_pad - cx_m) / 2.0
            y_col_0 = (l_pad - cy_m) / 2.0
            fig.add_shape(type="rect", x0=x_col_0, y0=y_col_0, x1=x_col_0 + cx_m, y1=y_col_0 + cy_m, line=dict(color="#E53E3E", width=2), fillcolor="#CBD5E0")

            fig.update_layout(
                xaxis=dict(title="Width B (m)", range=[-0.2, b_pad + 0.2]),
                yaxis=dict(title="Length L (m)", range=[-0.2, l_pad + 0.2], scaleanchor="x", scaleratio=1),
                height=280,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#CBD5E0"),
            )
            st.plotly_chart(fig, use_container_width=True)

            # Save Footing Record Action
            if st.button("💾 Save Footing Design to Schedule", type="primary", use_container_width=True):
                record = {
                    "id": f"FTG-{len(items) + 1:03d}",
                    "mark": footing_tag,
                    "dims": f"{b_pad:.2f}m x {l_pad:.2f}m x {h_pad}mm",
                    "n_total": round(n_total, 1),
                    "q_max": round(sigma_max, 1),
                    "rebar": f"Ø{bar_dia}@{bar_spacing} B.W.",
                    "status": "PASS" if (bearing_util <= 1.0 and as_prov >= as_target and one_way_shear_pass) else "WARN",
                }
                CRUDService.create(STATE_KEY, record)
                st.success(f"Saved design for footing `{footing_tag}`!")
                st.rerun()

    # ==============================================================================
    # TAB 2: DESIGN THEORY & FORMULAS
    # ==============================================================================
    with tab_report:
        st.subheader("EN 1997-1 & EN 1992-1-1 Foundation Verification Principles")

        st.markdown(r"""
        ### 1. Soil Bearing Pressure Distribution (Trapezoidal/Triangular)
        $$\sigma_{max/min} = \frac{N_{total}}{B \cdot L} \left( 1 \pm \frac{6 e_x}{B} \pm \frac{6 e_y}{L} \right)$$
        Where $e_x = M_{Ed,x} / N_{total}$ and $e_y = M_{Ed,y} / N_{total}$.

        ### 2. Middle-Third Rule for No Base Tension
        $$e_x \le \frac{B}{6} \quad \text{and} \quad e_y \le \frac{L}{6}$$

        ### 3. Critical Bending Moment at Column Face
        $$M_{Ed,crit} = \frac{\sigma_{max} \cdot a_x^2}{2} \cdot L$$
        Where $a_x = \frac{B - c_x}{2}$ is the cantilever overhang distance.

        ### 4. One-Way Shear Resistance ($V_{Rd,c}$) at $d_{eff}$ from Column Face
        $$v_{Rd,c} = C_{Rd,c} \, k \left( 100 \, \rho_l \, f_{ck} \right)^{1/3} \ge v_{min}$$
        Where $k = 1 + \sqrt{\frac{200}{d_{eff}}} \le 2.0$.
        """)

    # ==============================================================================
    # TAB 3: SAVED FOOTING SCHEDULE
    # ==============================================================================
    with tab_schedule:
        st.subheader("Project Pad Footing Schedule")
        if items:
            df_schedule = pd.DataFrame(items)
            st.dataframe(
                df_schedule,
                column_config={
                    "id": "ID",
                    "mark": "Footing Mark",
                    "dims": "Dimensions (B x L x H)",
                    "n_total": st.column_config.NumberColumn("N_total (kN)", format="%.1f"),
                    "q_max": st.column_config.NumberColumn("q_max (kPa)", format="%.1f"),
                    "rebar": "Bottom Rebar",
                    "status": "Status",
                },
                use_container_width=True,
                hide_index=True,
            )

            col_sc1, col_sc2 = st.columns([2, 1])
            with col_sc2:
                selected_del = st.selectbox("Select Record ID to Delete", df_schedule["id"].tolist())
                if st.button("🗑️ Delete Record"):
                    CRUDService.delete(STATE_KEY, selected_del)
                    st.rerun()
        else:
            st.info("No saved footing design records found.")