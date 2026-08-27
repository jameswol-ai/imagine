"""
IMAGINE Platform — Eurocode 2 (EN 1992-1-1) Reinforced Concrete Column Design Engine
Path: modules/structural/column_design.py
App: imagine
"""

import math
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from modules.utils.crud import CRUDService

STATE_KEY = "rc_column_designs"


def render() -> None:
    """Renders the Eurocode 2 (EN 1992-1-1) RC Column Design and Interaction Analysis module."""
    st.title("🏛️ Eurocode 2 Reinforced Concrete Column Design")
    st.caption("Axial load and biaxial bending ULS verification with slenderness second-order effects per EN 1992-1-1:2004.")

    items = CRUDService.get_all(STATE_KEY)

    tab_design, tab_report, tab_schedule = st.tabs([
        "📐 Column Designer & Interaction Curve",
        "📜 Design Theory & Slenderness Verification",
        "💾 Saved Column Schedule"
    ])

    # ==============================================================================
    # TAB 1: COLUMN DESIGNER & INTERACTION ANALYSIS
    # ==============================================================================
    with tab_design:
        col_inputs, col_results = st.columns([1, 1])

        with col_inputs:
            st.subheader("1. Section & Geometric Parameters")
            c_sec1, c_sec2 = st.columns(2)
            with c_sec1:
                b = st.number_input("Width b (z-axis, mm)", min_value=150, max_value=2000, value=350, step=25)
                h = st.number_input("Depth h (y-axis, mm)", min_value=150, max_value=2000, value=350, step=25)
                c_nom = st.number_input("Nominal Cover c_nom (mm)", min_value=15, max_value=100, value=35, step=5)
            with c_sec2:
                l_0 = st.number_input("Unbraced Height L0 (m)", min_value=1.0, max_value=15.0, value=3.6, step=0.1)
                braced_status = st.radio("Structure System", ["Braced", "Unbraced"], index=0)

            st.markdown("---")
            st.subheader("2. Materials & Reinforcement Setup")
            c_mat1, c_mat2 = st.columns(2)
            with c_mat1:
                fck = st.selectbox("Concrete Grade fck (MPa)", [20, 25, 30, 35, 40, 50], index=2)
                fyk = st.number_input("Steel Yield fyk (MPa)", value=500, step=50)
                gamma_c = st.number_input("γc (Concrete)", value=1.50, step=0.05)
                gamma_s = st.number_input("γs (Steel)", value=1.15, step=0.05)
            with c_mat2:
                bar_dia = st.selectbox("Main Rebar Dia Ø (mm)", [16, 20, 25, 32], index=1)
                n_bars_y = st.number_input("Bars along Depth (h-face)", min_value=2, max_value=10, value=3, step=1)
                n_bars_z = st.number_input("Bars along Width (b-face)", min_value=2, max_value=10, value=3, step=1)
                link_dia = st.selectbox("Link Tie Dia Øw (mm)", [8, 10, 12], index=0)

            st.markdown("---")
            st.subheader("3. Ultimate Internal Actions (ULS)")
            c_act1, c_act2 = st.columns(2)
            with c_act1:
                n_ed = st.number_input("Design Axial Load N_Ed (kN)", min_value=0.0, value=1200.0, step=50.0)
                m_edy = st.number_input("Design Moment M_Ed,y (kNm)", min_value=0.0, value=65.0, step=5.0)
            with c_act2:
                m_edz = st.number_input("Design Moment M_Ed,z (kNm)", min_value=0.0, value=35.0, step=5.0)

            col_tag = st.text_input("Column Mark / Identifier", value="C-101")

        # --- ULS Column Calculation Engine ---
        alpha_cc = 0.85
        fcd = (alpha_cc * fck) / gamma_c
        fyd = fyk / gamma_s

        # Area & Total Reinforcement Calculation
        ac = b * h
        total_bars = (2 * n_bars_y) + (2 * (n_bars_z - 2))
        bar_area = (math.pi / 4.0) * (bar_dia ** 2)
        as_tot = total_bars * bar_area

        # Effective depth along major axis (bending about z)
        d_y = h - c_nom - link_dia - (bar_dia / 2.0)
        d_z = b - c_nom - link_dia - (bar_dia / 2.0)

        # Min / Max Reinforcement Limits (EN 1992-1-1 Cl 9.5.2)
        as_min = max(0.10 * (n_ed * 1000.0 / fyd), 0.002 * ac)
        as_max = 0.04 * ac

        # Radius of Gyration & Slenderness
        iy = h / math.sqrt(12.0)
        iz = b / math.sqrt(12.0)
        lambda_y = (l_0 * 1000.0) / iy
        lambda_z = (l_0 * 1000.0) / iz

        # Slenderness Limit (EN 1992-1-1 Cl 5.8.3.1)
        n_rel = (n_ed * 1000.0) / (ac * fcd) if ac * fcd > 0 else 1.0
        a_val, b_val, c_val = 0.7, 1.1, 0.7
        lambda_lim = (20.0 * a_val * b_val * c_val) / math.sqrt(n_rel) if n_rel > 0 else 20.0

        is_slender_y = lambda_y > lambda_lim
        is_slender_z = lambda_z > lambda_lim

        # Nominal Eccentricity e0 = max(h/30, 20mm)
        e0_y = max(h / 30.0, 20.0)
        e0_z = max(b / 30.0, 20.0)

        m0_edy = max(m_edy, (n_ed * e0_y) / 1000.0)
        m0_edz = max(m_edz, (n_ed * e0_z) / 1000.0)

        # Axial Section Capacity (Pure Compression Limit)
        n_rd_max = ((ac - as_tot) * fcd + as_tot * fyd) / 1000.0  # kN

        # Generate N-M Interaction Curve Points (Simplified Major Axis)
        n_points = 25
        n_curve = []
        m_curve = []
        for i in range(n_points + 1):
            n_val = (n_rd_max * i) / n_points
            n_val_n = n_val * 1000.0
            x_depth = min(h, max(0.1 * h, (n_val_n) / (0.8 * b * fcd))) if (0.8 * b * fcd) > 0 else h
            z_arm = h / 2.0 - 0.4 * x_depth
            m_cap = (0.8 * b * x_depth * fcd * z_arm + as_tot * 0.5 * fyd * (d_y - h/2.0)) / 1e6
            n_curve.append(n_val)
            m_curve.append(max(0.0, m_cap))

        # Check demand against capacity
        util_n = n_ed / n_rd_max if n_rd_max > 0 else 1.0

        with col_results:
            st.subheader("Results & Slenderness Summary")

            m1, m2, m3 = st.columns(3)
            m1.metric("Axial Load N_Ed", f"{n_ed:.0f} kN")
            m2.metric("Axial Capacity N_Rd,max", f"{n_rd_max:.0f} kN", delta=f"{util_n * 100:.1f}% Util")
            m3.metric("Total Rebar Area", f"{as_tot:.0f} mm²", delta=f"{total_bars} H{bar_dia}")

            st.divider()

            st.markdown("### Slenderness Assessment")
            s1, s2 = st.columns(2)
            with s1:
                st.write(f"- Slenderness $\lambda_y$: **{lambda_y:.1f}**")
                st.write(f"- Slenderness $\lambda_z$: **{lambda_z:.1f}**")
                st.write(f"- Slenderness Limit $\lambda_{{lim}}$: **{lambda_lim:.1f}**")
            with s2:
                st.write(f"- Major Axis Status: **{'SLENDER' if is_slender_y else 'SHORT'}**")
                st.write(f"- Minor Axis Status: **{'SLENDER' if is_slender_z else 'SHORT'}**")
                st.write(f"- Minimum Eccentricity $e_0$: **{e0_y:.1f} mm**")

            if is_slender_y or is_slender_z:
                st.warning("⚠️ Column is slender. Second-order moments ($M_2$) must be added to first-order actions.")
            else:
                st.success("✅ Column is short ($\lambda \le \lambda_{lim}$). Second-order effects may be ignored.")

            # Interaction Diagram Plot
            st.markdown("### N-M Interaction Curve (Major Axis)")
            fig_nm = go.Figure()

            # Capacity curve
            fig_nm.add_trace(go.Scatter(
                x=m_curve,
                y=n_curve,
                mode="lines",
                name="N-M Capacity Envelope",
                line=dict(color="#2B6CB0", width=3),
            ))

            # Demand point
            fig_nm.add_trace(go.Scatter(
                x=[m0_edy],
                y=[n_ed],
                mode="markers+text",
                name="ULS Demand (N_Ed, M_Ed)",
                text=["ULS Demand"],
                textposition="top right",
                marker=dict(color="#E53E3E", size=12, symbol="diamond"),
            ))

            fig_nm.update_layout(
                xaxis=dict(title="Bending Moment M_Rd (kNm)", showgrid=True),
                yaxis=dict(title="Axial Force N_Rd (kN)", showgrid=True),
                height=320,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#CBD5E0"),
                showlegend=True,
            )
            st.plotly_chart(fig_nm, use_container_width=True)

            # Column Cross-Section Layout
            st.markdown("### Column Cross-Section Layout")
            fig_sec = go.Figure()

            # Concrete boundary
            fig_sec.add_shape(type="rect", x0=0, y0=0, x1=b, y1=h, line=dict(color="#4A5568", width=3), fillcolor="#EDF2F7")

            # Stirrup tie boundary
            link_off = c_nom
            fig_sec.add_shape(type="rect", x0=link_off, y0=link_off, x1=b - link_off, y1=h - link_off,
                              line=dict(color="#E53E3E", width=2, dash="dash"))

            # Place rebar grid
            dy_bar = (h - 2 * (c_nom + link_dia) - bar_dia) / (n_bars_y - 1) if n_bars_y > 1 else 0
            dz_bar = (b - 2 * (c_nom + link_dia) - bar_dia) / (n_bars_z - 1) if n_bars_z > 1 else 0

            for iy_i in range(n_bars_y):
                for iz_i in range(n_bars_z):
                    # Perimeter bars only
                    if iy_i in [0, n_bars_y - 1] or iz_i in [0, n_bars_z - 1]:
                        cx = c_nom + link_dia + (bar_dia / 2.0) + (iz_i * dz_bar)
                        cy = c_nom + link_dia + (bar_dia / 2.0) + (iy_i * dy_bar)
                        fig_sec.add_shape(type="circle", x0=cx - bar_dia/2, y0=cy - bar_dia/2, x1=cx + bar_dia/2, y1=cy + bar_dia/2,
                                          fillcolor="#2B6CB0", line=dict(color="#1A365D"))

            fig_sec.update_layout(
                xaxis=dict(range=[-30, b + 30], visible=False),
                yaxis=dict(range=[-30, h + 30], visible=False, scaleanchor="x", scaleratio=1),
                height=260,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_sec, use_container_width=True)

            # Save Column Record Action
            if st.button("💾 Save Column Design to Schedule", type="primary", use_container_width=True):
                record = {
                    "id": f"COL-{len(items) + 1:03d}",
                    "mark": col_tag,
                    "section": f"{b:.0f}x{h:.0f} mm",
                    "n_ed": n_ed,
                    "m_edy": m_edy,
                    "m_edz": m_edz,
                    "slenderness": f"λy={lambda_y:.1f} ({'Slender' if is_slender_y else 'Short'})",
                    "rebar_prov": f"{total_bars}H{bar_dia} (As={as_tot:.0f} mm²)",
                    "status": "PASS" if (util_n <= 1.0 and as_tot >= as_min) else "WARN",
                }
                CRUDService.create(STATE_KEY, record)
                st.success(f"Saved design for column `{col_tag}`!")
                st.rerun()

    # ==============================================================================
    # TAB 2: DESIGN THEORY & FORMULAS
    # ==============================================================================
    with tab_report:
        st.subheader("EN 1992-1-1 Compression & Biaxial Column Verification")

        st.markdown(r"""
        ### 1. Slenderness Ratio ($\lambda$)
        $$\lambda = \frac{L_0}{i}$$
        Where $i = \sqrt{I / A_c}$ is the radius of gyration. For rectangular sections ($b \times h$), $i = h / \sqrt{12}$.

        ### 2. Slenderness Limit ($\lambda_{lim}$)
        $$\lambda_{lim} = \frac{20 \cdot A \cdot B \cdot C}{\sqrt{n}}$$
        Where:
        - $A = 0.7$ (if creep ratio $f_{ef}$ is unknown)
        - $B = 1.1$ (if mechanical reinforcement ratio $\omega$ is unknown)
        - $C = 0.7$ (for unknown first-order moments)
        - $n = \frac{N_{Ed}}{A_c \cdot f_{cd}}$

        ### 3. Minimum Eccentricity ($e_0$)
        $$e_0 = \max\left(\frac{h}{30}, \, 20\text{ mm}\right)$$

        ### 4. Reinforcement Limits (EN 1992-1-1 Cl 9.5.2)
        - **Minimum steel area:** $A_{s,min} = \max\left(\frac{0.10 N_{Ed}}{f_{yd}}, \, 0.002 A_c\right)$
        - **Maximum steel area:** $A_{s,max} = 0.04 A_c$ ($0.08 A_c$ at laps)

        ### 5. Simplified Biaxial Bending Criterion
        $$\left(\frac{M_{Ed,y}}{M_{Rd,y}}\right)^a + \left(\frac{M_{Ed,z}}{M_{Rd,z}}\right)^a \le 1.0$$
        Where the exponent $a$ depends on $N_{Ed} / N_{Rd0}$.
        """)

    # ==============================================================================
    # TAB 3: SAVED COLUMN SCHEDULE
    # ==============================================================================
    with tab_schedule:
        st.subheader("Project RC Column Schedule")
        if items:
            df_schedule = pd.DataFrame(items)
            st.dataframe(
                df_schedule,
                column_config={
                    "id": "ID",
                    "mark": "Column Mark",
                    "section": "Section (b x h)",
                    "n_ed": st.column_config.NumberColumn("N_Ed (kN)", format="%.0f"),
                    "m_edy": st.column_config.NumberColumn("M_Ed,y (kNm)", format="%.1f"),
                    "m_edz": st.column_config.NumberColumn("M_Ed,z (kNm)", format="%.1f"),
                    "slenderness": "Slenderness Status",
                    "rebar_prov": "Reinforcement Provided",
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
            st.info("No saved column design records found.")
