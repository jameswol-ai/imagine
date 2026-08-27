"""
IMAGINE Platform — Eurocode 2 (EN 1992-1-1) Reinforced Concrete Beam Design Engine
Path: modules/structural/beam_design.py
App: imagine
"""

import math
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from modules.utils.crud import CRUDService

STATE_KEY = "rc_beam_designs"


def render() -> None:
    """Renders the Eurocode 2 (EN 1992-1-1) RC Beam Flexural and Shear Design module."""
    st.title("🧱 Eurocode 2 Reinforced Concrete Beam Design")
    st.caption("Ultimate Limit State (ULS) flexural and shear design verification according to BS EN 1992-1-1:2004.")

    items = CRUDService.get_all(STATE_KEY)

    tab_design, tab_report, tab_schedule = st.tabs([
        "📐 Beam Designer & ULS Verification",
        "📜 Design Theory & Formulas",
        "💾 Saved Beam Schedule"
    ])

    # ==============================================================================
    # TAB 1: BEAM DESIGNER & VERIFICATION
    # ==============================================================================
    with tab_design:
        col_inputs, col_results = st.columns([1, 1])

        with col_inputs:
            st.subheader("1. Section & Material Parameters")
            c_sec1, c_sec2 = st.columns(2)
            with c_sec1:
                b = st.number_input("Width b (mm)", min_value=100, max_value=2000, value=300, step=25)
                h = st.number_input("Overall Depth h (mm)", min_value=150, max_value=3000, value=500, step=25)
                c_nom = st.number_input("Nominal Cover c_nom (mm)", min_value=15, max_value=100, value=35, step=5)
            with c_sec2:
                bar_dia = st.selectbox("Main Rebar Dia Ø (mm)", [12, 16, 20, 25, 32], index=2)
                link_dia = st.selectbox("Shear Link Dia Øw (mm)", [8, 10, 12], index=1)
                num_legs = st.selectbox("Shear Link Legs", [2, 4], index=0)

            st.markdown("---")
            st.subheader("2. Material Grades & Partial Factors")
            c_mat1, c_mat2 = st.columns(2)
            with c_mat1:
                fck = st.selectbox("Concrete Grade fck (MPa)", [20, 25, 30, 35, 40, 50], index=2)
                gamma_c = st.number_input("γc (Concrete)", value=1.50, step=0.05)
            with c_mat2:
                fyk = st.number_input("Steel Yield fyk (MPa)", value=500, step=50)
                gamma_s = st.number_input("γs (Steel)", value=1.15, step=0.05)

            st.markdown("---")
            st.subheader("3. Ultimate Internal Actions (ULS)")
            c_act1, c_act2 = st.columns(2)
            with c_act1:
                m_ed = st.number_input("Design Moment M_Ed (kNm)", min_value=0.0, value=175.0, step=10.0)
            with c_act2:
                v_ed = st.number_input("Design Shear V_Ed (kN)", min_value=0.0, value=120.0, step=5.0)

            beam_tag = st.text_input("Beam Mark / Identifier", value=f"B-101")

        # --- ULS Design Calculation Engine ---
        # Effective depth calculation
        d = h - c_nom - link_dia - (bar_dia / 2.0)
        d_prime = c_nom + link_dia + (bar_dia / 2.0)

        # Design strengths
        alpha_cc = 0.85
        fcd = (alpha_cc * fck) / gamma_c
        fyd = fyk / gamma_s
        fctm = 0.30 * (fck ** (2/3)) if fck <= 50 else 2.12 * math.log(1 + (fck / 10))

        # Flexural Check
        m_ed_nmm = m_ed * 1e6
        k_val = m_ed_nmm / (b * (d**2) * fcd) if d > 0 else 0.0
        k_prime = 0.168  # Standard redistribution limit (δ = 1.0)

        if k_val <= k_prime:
            flexure_mode = "Singly Reinforced Section"
            z = min(0.95 * d, d * 0.5 * (1 + math.sqrt(max(0.0, 1 - 3.53 * k_val))))
            as_req = m_ed_nmm / (fyd * z) if z > 0 else 0.0
            as2_req = 0.0
        else:
            flexure_mode = "Doubly Reinforced Section (Compression Steel Required)"
            z = 0.82 * d
            m_rd_lim = k_prime * b * (d**2) * fcd
            delta_m = m_ed_nmm - m_rd_lim
            as2_req = delta_m / (fyd * (d - d_prime)) if (d - d_prime) > 0 else 0.0
            as_req = (m_rd_lim / (fyd * z)) + as2_req

        # Min / Max Reinforcement Check
        as_min = max(0.26 * (fctm / fyk) * b * d, 0.0013 * b * d)
        as_max = 0.04 * b * h
        as_prov_req = max(as_req, as_min)

        # Bar selection logic for bottom tension steel
        bar_area = (math.pi / 4.0) * (bar_dia ** 2)
        n_bars_req = math.ceil(as_prov_req / bar_area)
        as_provided = n_bars_req * bar_area

        # Shear Check (EN 1992-1-1 Cl. 6.2)
        v_ed_n = v_ed * 1000.0
        cot_theta = 2.5  # Standard variable strut angle selection (21.8 deg)
        sin_theta = 1.0 / math.sqrt(1 + cot_theta**2)
        cos_theta = cot_theta * sin_theta
        nu1 = 0.6 * (1 - (fck / 250.0))
        v_rd_max = (b * z * nu1 * fcd) / (cot_theta + (1.0 / cot_theta))
        
        # Link spacing calculation
        asw_single_link = num_legs * (math.pi / 4.0) * (link_dia ** 2)
        s_req = (asw_single_link * z * fyd * cot_theta) / v_ed_n if v_ed_n > 0 else 300.0
        s_max = min(0.75 * d, 300.0)
        s_provided = max(50.0, min(math.floor(s_req / 25.0) * 25.0, s_max))

        with col_results:
            st.subheader("Results & Verification Summary")

            r1, r2, r3 = st.columns(3)
            r1.metric("Effective Depth d", f"{d:.1f} mm")
            r2.metric("K Parameter", f"{k_val:.4f}", delta="≤ 0.168 Pass" if k_val <= k_prime else "Doubly Reinf.", delta_color="normal" if k_val <= k_prime else "off")
            r3.metric("Lever Arm z", f"{z:.1f} mm")

            st.markdown(f"**Flexural Mode:** `{flexure_mode}`")

            if k_val > k_prime:
                st.warning(f"⚠️ K ({k_val:.3f}) > K' ({k_prime}). Compression steel is required: A's,req = {as2_req:.0f} mm²")

            st.divider()

            c_as1, c_as2 = st.columns(2)
            with c_as1:
                st.markdown("**Flexural Reinforcement**")
                st.write(f"- Required As: **{as_req:.0f} mm²**")
                st.write(f"- Minimum As,min: **{as_min:.0f} mm²**")
                st.write(f"- Selected: **{n_bars_req} H{bar_dia}** ({as_provided:.0f} mm²)")
                if as_provided >= as_prov_req:
                    st.success("✅ Flexural Capacity OK")
                else:
                    st.error("❌ Insufficient Flexural Steel")

            with c_as2:
                st.markdown("**Shear Reinforcement**")
                st.write(f"- Max Shear Capacity VRd,max: **{v_rd_max / 1000.0:.1f} kN**")
                st.write(f"- Required Link Spacing: **{s_req:.0f} mm**")
                st.write(f"- Selected Links: **H{link_dia} @ {int(s_provided)} mm c/c** ({num_legs} legs)")
                if v_ed_n <= v_rd_max:
                    st.success("✅ Shear Compression Strut OK")
                else:
                    st.error("❌ Concrete Strut Crushed (Increase Section Size)")

            # Cross-Section Visualization Diagram
            st.markdown("### Cross-Section Geometry")
            fig = go.Figure()

            # Concrete outline
            fig.add_shape(type="rect", x0=0, y0=0, x1=b, y1=h, line=dict(color="#4A5568", width=3), fillcolor="#EDF2F7")

            # Stirrup outline
            link_offset = c_nom
            fig.add_shape(type="rect", x0=link_offset, y0=link_offset, x1=b - link_offset, y1=h - link_offset,
                          line=dict(color="#E53E3E", width=2, dash="dash"))

            # Rebar placement (Bottom)
            spacing = (b - 2 * (c_nom + link_dia) - bar_dia) / max(1, (n_bars_req - 1)) if n_bars_req > 1 else 0
            for i in range(n_bars_req):
                cx = c_nom + link_dia + (bar_dia / 2.0) + (i * spacing) if n_bars_req > 1 else b / 2.0
                cy = c_nom + link_dia + (bar_dia / 2.0)
                fig.add_shape(type="circle", x0=cx - bar_dia/2, y0=cy - bar_dia/2, x1=cx + bar_dia/2, y1=cy + bar_dia/2,
                              fillcolor="#2B6CB0", line=dict(color="#1A365D"))

            # Top hanger bars
            for cx in [c_nom + link_dia + 6, b - (c_nom + link_dia + 6)]:
                cy = h - (c_nom + link_dia + 6)
                fig.add_shape(type="circle", x0=cx - 6, y0=cy - 6, x1=cx + 6, y1=cy + 6,
                              fillcolor="#718096", line=dict(color="#2D3748"))

            fig.update_layout(
                xaxis=dict(range=[-30, b + 30], visible=False),
                yaxis=dict(range=[-30, h + 30], visible=False, scaleanchor="x", scaleratio=1),
                height=300,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, use_container_width=True)

            # Save Design Action
            if st.button("💾 Save Design to Schedule", type="primary", use_container_width=True):
                record = {
                    "id": f"RC-{len(items) + 1:03d}",
                    "mark": beam_tag,
                    "section": f"{b:.0f}x{h:.0f} mm",
                    "m_ed": m_ed,
                    "v_ed": v_ed,
                    "as_req": round(as_req, 1),
                    "rebar_prov": f"{n_bars_req}H{bar_dia}",
                    "links_prov": f"H{link_dia}@{int(s_provided)}",
                    "status": "PASS" if (k_val <= k_prime and v_ed_n <= v_rd_max) else "WARN",
                }
                CRUDService.create(STATE_KEY, record)
                st.success(f"Saved design for `{beam_tag}` successfully!")
                st.rerun()

    # ==============================================================================
    # TAB 2: DESIGN THEORY & FORMULAS
    # ==============================================================================
    with tab_report:
        st.subheader("EN 1992-1-1 ULS Bending & Shear Verification Theory")

        st.markdown(r"""
        ### 1. Design Compressive Strength of Concrete ($f_{cd}$)
        $$f_{cd} = \frac{\alpha_{cc} \cdot f_{ck}}{\gamma_c}$$
        Where $\alpha_{cc} = 0.85$ is the coefficient taking into account long-term effects on compressive strength and $\gamma_c = 1.5$.

        ### 2. Normalized Bending Moment ($K$)
        $$K = \frac{M_{Ed}}{b \cdot d^2 \cdot f_{cd}}$$
        - If $K \le K' = 0.168$, tension reinforcement only is required.
        - The lever arm $z$ is given by:
        $$z = \min\left(0.95d, \, 0.5d \left(1 + \sqrt{1 - 3.53K}\right)\right)$$
        - Required tension steel area:
        $$A_{s,req} = \frac{M_{Ed}}{f_{yd} \cdot z}$$

        ### 3. Minimum Reinforcement Limit ($A_{s,min}$)
        $$A_{s,min} = \max \left(0.26 \frac{f_{ctm}}{f_{yk}} b d, \, 0.0013 b d \right)$$

        ### 4. Shear Resistance of Links ($V_{Rd,sy}$)
        $$V_{Rd,s} = \frac{A_{sw}}{s} \cdot z \cdot f_{ywd} \cdot \cot \theta$$
        Where $\theta$ is the angle of concrete compression struts ($21.8^\circ \le \theta \le 45^\circ$).
        """)

    # ==============================================================================
    # TAB 3: SAVED BEAM SCHEDULE
    # ==============================================================================
    with tab_schedule:
        st.subheader("Project RC Beam Schedule")
        if items:
            df_schedule = pd.DataFrame(items)
            st.dataframe(
                df_schedule,
                column_config={
                    "id": "ID",
                    "mark": "Beam Mark",
                    "section": "Section (b x h)",
                    "m_ed": st.column_config.NumberColumn("M_Ed (kNm)", format="%.1f"),
                    "v_ed": st.column_config.NumberColumn("V_Ed (kN)", format="%.1f"),
                    "as_req": st.column_config.NumberColumn("Req As (mm²)", format="%.0f"),
                    "rebar_prov": "Tension Rebar",
                    "links_prov": "Shear Links",
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
            st.info("No saved beam design records found.")
