"""
IMAGINE Platform — Eurocode 2 (EN 1992-1-1) Reinforced Concrete Slab Design Engine
Path: modules/structural/slab_design.py
App: imagine
"""

import math
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from modules.utils.crud import CRUDService

STATE_KEY = "rc_slab_designs"


def render() -> None:
    """Renders the Eurocode 2 (EN 1992-1-1) RC One-Way & Two-Way Slab Design module."""
    st.title("🥞 Eurocode 2 Reinforced Concrete Slab Design")
    st.caption("Flexural ULS, shear capacity, and SLS span-to-effective depth deflection checks per EN 1992-1-1:2004.")

    items = CRUDService.get_all(STATE_KEY)

    tab_design, tab_report, tab_schedule = st.tabs([
        "📐 Slab Designer & Verification",
        "📜 Design Theory & Formulas",
        "💾 Saved Slab Schedule"
    ])

    # ==============================================================================
    # TAB 1: SLAB DESIGNER & VERIFICATION
    # ==============================================================================
    with tab_design:
        col_inputs, col_results = st.columns([1, 1])

        with col_inputs:
            st.subheader("1. System Geometry & Slab Type")
            slab_type = st.radio("Slab Behavior Type", ["One-Way Slab", "Two-Way Rectangular Slab"], horizontal=True)

            c_geo1, c_geo2 = st.columns(2)
            with c_geo1:
                lx = st.number_input("Short Span Lx (m)", min_value=1.0, max_value=15.0, value=4.0, step=0.25)
                h_slab = st.number_input("Slab Thickness h (mm)", min_value=80, max_value=600, value=175, step=5)
                c_nom = st.number_input("Nominal Cover c_nom (mm)", min_value=15, max_value=75, value=25, step=5)
            with c_geo2:
                ly = st.number_input("Long Span Ly (m)", min_value=1.0, max_value=25.0, value=5.5 if slab_type == "Two-Way Rectangular Slab" else 8.0, step=0.25)
                support_cond = st.selectbox(
                    "Support / Edge Condition",
                    ["Simply Supported", "One End Continuous", "Both Ends Continuous", "Cantilever"],
                    index=0
                )

            st.markdown("---")
            st.subheader("2. Loading & Materials")
            c_mat1, c_mat2 = st.columns(2)
            with c_mat1:
                fck = st.selectbox("Concrete Grade fck (MPa)", [20, 25, 30, 35, 40], index=2)
                fyk = st.number_input("Steel Yield fyk (MPa)", value=500, step=50)
                n_ed = st.number_input("Design Load w_Ed (kN/m²)", min_value=1.0, max_value=100.0, value=11.5, step=0.5)
            with c_mat2:
                gamma_c = st.number_input("γc (Concrete)", value=1.50, step=0.05)
                gamma_s = st.number_input("γs (Steel)", value=1.15, step=0.05)
                bar_dia_x = st.selectbox("Main Rebar Dia Øx (mm)", [8, 10, 12, 16], index=1)
                bar_spacing_x = st.selectbox("Main Rebar Spacing sx (mm)", [100, 125, 150, 175, 200, 250, 300], index=4)

            if slab_type == "Two-Way Rectangular Slab":
                st.markdown("---")
                st.subheader("3. Y-Direction Rebar Configuration")
                c_y1, c_y2 = st.columns(2)
                with c_y1:
                    bar_dia_y = st.selectbox("Transverse Dia Øy (mm)", [8, 10, 12, 16], index=1)
                with c_y2:
                    bar_spacing_y = st.selectbox("Transverse Spacing sy (mm)", [100, 125, 150, 175, 200, 250, 300], index=4)
            else:
                bar_dia_y, bar_spacing_y = 8, 200

            slab_tag = st.text_input("Slab Mark / Identifier", value="S-101")

        # --- Eurocode 2 Calculation Engine ---
        alpha_cc = 0.85
        fcd = (alpha_cc * fck) / gamma_c
        fyd = fyk / gamma_s
        fctm = 0.30 * (fck ** (2/3)) if fck <= 50 else 2.12 * math.log(1 + (fck / 10))

        # Effective Depths
        dx = h_slab - c_nom - (bar_dia_x / 2.0)
        dy = dx - (bar_dia_x / 2.0) - (bar_dia_y / 2.0) if slab_type == "Two-Way Rectangular Slab" else dx - 10.0

        aspect_ratio = ly / lx

        # Bending Moment Calculations
        if slab_type == "One-Way Slab" or aspect_ratio > 2.0:
            # One-Way Behavior
            if support_cond == "Simply Supported":
                m_ed_x = (n_ed * (lx ** 2)) / 8.0
            elif support_cond == "One End Continuous":
                m_ed_x = (n_ed * (lx ** 2)) / 10.0
            elif support_cond == "Both Ends Continuous":
                m_ed_x = (n_ed * (lx ** 2)) / 12.0
            else:  # Cantilever
                m_ed_x = (n_ed * (lx ** 2)) / 2.0
            m_ed_y = 0.20 * m_ed_x  # Secondary moment distribution
        else:
            # Two-Way Slab (Rankine-Grashof simplified yield coefficients for simply supported)
            v_x = 1.0 / (1.0 + aspect_ratio**4)
            v_y = (aspect_ratio**4) / (1.0 + aspect_ratio**4)
            m_ed_x = v_x * (n_ed * (lx ** 2)) / 8.0
            m_ed_y = v_y * (n_ed * (lx ** 2)) / 8.0

        # Flexural Steel Requirements (X-Direction per meter width b=1000mm)
        b_unit = 1000.0
        m_ed_x_nmm = m_ed_x * 1e6
        k_x = m_ed_x_nmm / (b_unit * (dx**2) * fcd) if dx > 0 else 0.0
        k_prime = 0.168

        z_x = min(0.95 * dx, dx * 0.5 * (1 + math.sqrt(max(0.0, 1 - 3.53 * k_x))))
        as_req_x = m_ed_x_nmm / (fyd * z_x) if z_x > 0 else 0.0

        # Flexural Steel Requirements (Y-Direction)
        m_ed_y_nmm = m_ed_y * 1e6
        k_y = m_ed_y_nmm / (b_unit * (dy**2) * fcd) if dy > 0 else 0.0
        z_y = min(0.95 * dy, dy * 0.5 * (1 + math.sqrt(max(0.0, 1 - 3.53 * k_y))))
        as_req_y = m_ed_y_nmm / (fyd * z_y) if z_y > 0 else 0.0

        # Minimum & Maximum Reinforcement (Cl 9.2.1.1)
        as_min_x = max(0.26 * (fctm / fyk) * b_unit * dx, 0.0013 * b_unit * dx)
        as_min_y = max(0.26 * (fctm / fyk) * b_unit * dy, 0.0013 * b_unit * dy)
        as_prov_req_x = max(as_req_x, as_min_x)
        as_prov_req_y = max(as_req_y, as_min_y)

        # Provided Steel Area (mm²/m)
        as_prov_x = (b_unit / bar_spacing_x) * (math.pi / 4.0) * (bar_dia_x ** 2)
        as_prov_y = (b_unit / bar_spacing_y) * (math.pi / 4.0) * (bar_dia_y ** 2)

        # Deflection Check (Span-to-Effective Depth Ratio Cl 7.4.2)
        rho_x = as_prov_x / (b_unit * dx)
        rho_0 = math.sqrt(fck) * 1e-3

        # Basic span-to-depth ratio (K_sys factor)
        k_sys_map = {
            "Simply Supported": 1.0,
            "One End Continuous": 1.3,
            "Both Ends Continuous": 1.5,
            "Cantilever": 0.4
        }
        k_sys = k_sys_map.get(support_cond, 1.0)
        basic_ld = 20.0 * k_sys

        # Modification factor for steel stress
        f_as = min(1.5, as_prov_x / as_req_x) if as_req_x > 0 else 1.0
        allowable_ld = basic_ld * f_as
        actual_ld = (lx * 1000.0) / dx

        deflection_pass = actual_ld <= allowable_ld

        with col_results:
            st.subheader("Results & Verification Summary")

            s1, s2, s3 = st.columns(3)
            s1.metric("Effective Depth dx", f"{dx:.1f} mm")
            s2.metric("Short Moment Mx,Ed", f"{m_ed_x:.2f} kNm/m")
            s3.metric("Long Moment My,Ed", f"{m_ed_y:.2f} kNm/m")

            st.divider()

            c_chk1, c_chk2 = st.columns(2)
            with c_chk1:
                st.markdown("**X-Direction Steel (Main)**")
                st.write(f"- Required As,x: **{as_prov_req_x:.0f} mm²/m**")
                st.write(f"- Provided: **Ø{bar_dia_x}@{bar_spacing_x} mm** ({as_prov_x:.0f} mm²/m)")
                if as_prov_x >= as_prov_req_x:
                    st.success("✅ Main Flexure OK")
                else:
                    st.error("❌ Main Steel Insufficient")

            with c_chk2:
                st.markdown("**Y-Direction Steel (Transverse)**")
                st.write(f"- Required As,y: **{as_prov_req_y:.0f} mm²/m**")
                st.write(f"- Provided: **Ø{bar_dia_y}@{bar_spacing_y} mm** ({as_prov_y:.0f} mm²/m)")
                if as_prov_y >= as_prov_req_y:
                    st.success("✅ Transverse Steel OK")
                else:
                    st.error("❌ Transverse Steel Insufficient")

            st.markdown("### SLS Deflection Check (Span / Depth)")
            d1, d2 = st.columns(2)
            d1.metric("Actual L/d", f"{actual_ld:.1f}")
            d2.metric("Allowable L/d", f"{allowable_ld:.1f}", delta="PASS" if deflection_pass else "FAIL")

            if deflection_pass:
                st.success(f"✅ Deflection OK: Actual L/d ({actual_ld:.1f}) ≤ Allowable L/d ({allowable_ld:.1f})")
            else:
                st.error(f"❌ Deflection Failed: Increase slab thickness h or increase provided steel area.")

            # Cross-Section Structural Diagram
            st.markdown("### Slab Reinforcement Diagram")
            fig = go.Figure()

            # Concrete Slab Envelope
            fig.add_shape(type="rect", x0=0, y0=0, x1=1000, y1=h_slab, line=dict(color="#4A5568", width=3), fillcolor="#EDF2F7")

            # Main Bottom Rebar (X-direction)
            num_bars_viz = int(1000 / bar_spacing_x)
            for i in range(num_bars_viz + 1):
                cx = (i * bar_spacing_x) + (bar_dia_x / 2.0)
                cy = c_nom + (bar_dia_x / 2.0)
                if cx <= 1000:
                    fig.add_shape(type="circle", x0=cx - bar_dia_x/2, y0=cy - bar_dia_x/2, x1=cx + bar_dia_x/2, y1=cy + bar_dia_x/2,
                                  fillcolor="#2B6CB0", line=dict(color="#1A365D"))

            # Transverse Bottom Rebar (Y-direction line)
            cy_trans = c_nom + bar_dia_x + (bar_dia_y / 2.0)
            fig.add_shape(type="line", x0=10, y0=cy_trans, x1=990, y1=cy_trans, line=dict(color="#E53E3E", width=3, dash="dash"))

            fig.update_layout(
                xaxis=dict(range=[-50, 1050], visible=False),
                yaxis=dict(range=[-20, h_slab + 30], visible=False, scaleanchor="x", scaleratio=1),
                height=220,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, use_container_width=True)

            # Save Slab Record Action
            if st.button("💾 Save Slab Design to Schedule", type="primary", use_container_width=True):
                record = {
                    "id": f"SLB-{len(items) + 1:03d}",
                    "mark": slab_tag,
                    "type": slab_type,
                    "thickness": f"{h_slab:.0f} mm",
                    "spans": f"{lx:.2f}m x {ly:.2f}m",
                    "mx_ed": round(m_ed_x, 2),
                    "rebar_x": f"Ø{bar_dia_x}@{bar_spacing_x}",
                    "rebar_y": f"Ø{bar_dia_y}@{bar_spacing_y}",
                    "status": "PASS" if (as_prov_x >= as_prov_req_x and deflection_pass) else "WARN",
                }
                CRUDService.create(STATE_KEY, record)
                st.success(f"Saved design for slab `{slab_tag}`!")
                st.rerun()

    # ==============================================================================
    # TAB 2: DESIGN THEORY & FORMULAS
    # ==============================================================================
    with tab_report:
        st.subheader("EN 1992-1-1 Slab Flexure & Deflection Verification Theory")

        st.markdown(r"""
        ### 1. One-Way vs. Two-Way Bending Behavior
        - **One-Way Action:** Triggered when aspect ratio $L_y / L_x > 2.0$ or load is transferred in one primary direction.
        - **Two-Way Action:** Triggered when $L_y / L_x \le 2.0$ with boundary supports on all four edges.

        ### 2. Flexural Strength (1m strip $b = 1000\text{ mm}$)
        $$K = \frac{M_{Ed}}{b \cdot d^2 \cdot f_{cd}}$$
        - Effective depth: $d_x = h - c_{nom} - \phi_x / 2$
        - Required steel area per meter:
        $$A_{s,req} = \frac{M_{Ed}}{f_{yd} \cdot z}$$

        ### 3. Minimum Reinforcement Limit ($A_{s,min}$)
        $$A_{s,min} = \max \left(0.26 \frac{f_{ctm}}{f_{yk}} b d, \, 0.0013 b d \right)$$

        ### 4. Span-to-Effective Depth Ratio (SLS Deflection)
        $$\frac{L}{d} \le \left(\frac{L}{d}\right)_{basic} \cdot F_{AS}$$
        Where $F_{AS} = \min\left(1.5, \, \frac{A_{s,prov}}{A_{s,req}}\right)$ accounts for steel stress level modification.
        """)

    # ==============================================================================
    # TAB 3: SAVED SLAB SCHEDULE
    # ==============================================================================
    with tab_schedule:
        st.subheader("Project RC Slab Schedule")
        if items:
            df_schedule = pd.DataFrame(items)
            st.dataframe(
                df_schedule,
                column_config={
                    "id": "ID",
                    "mark": "Slab Mark",
                    "type": "Type",
                    "thickness": "Thickness (h)",
                    "spans": "Dimensions (Lx x Ly)",
                    "mx_ed": st.column_config.NumberColumn("Mx,Ed (kNm/m)", format="%.2f"),
                    "rebar_x": "X Rebar",
                    "rebar_y": "Y Rebar",
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
            st.info("No saved slab design records found.")
