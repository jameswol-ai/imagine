"""
IMAGINE Platform — Eurocode 2 (EN 1992-1-1 Clause 6.4) Punching Shear Engine
Path: modules/structural/punching_shear.py
App: imagine
"""

import math
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

try:
    from modules.utils.crud import CRUDService
except ImportError:
    # Local fallback helper if crud utility is not yet loaded
    class CRUDService:
        @staticmethod
        def get_all(key):
            return st.session_state.get(key, [])

        @staticmethod
        def create(key, item):
            if key not in st.session_state:
                st.session_state[key] = []
            st.session_state[key].append(item)

        @staticmethod
        def delete(key, item_id):
            if key in st.session_state:
                st.session_state[key] = [
                    x for x in st.session_state[key] if x.get("id") != item_id
                ]


STATE_KEY = "punching_shear_verifications"


def render() -> None:
    """Renders the Eurocode 2 Punching Shear Verification module for Slabs and Footings."""
    st.title("🛡️ Eurocode 2 Punching Shear Verification")
    st.caption(
        "EN 1992-1-1 §6.4 verification at column perimeter (u₀), control perimeter (u₁ = 2d), and shear reinforcement perimeters."
    )

    items = CRUDService.get_all(STATE_KEY)

    tab_design, tab_theory, tab_schedule = st.tabs(
        [
            "📐 Punching Shear Check",
            "📜 Design Principles & Clause 6.4 Formulas",
            "💾 Saved Verification Records",
        ]
    )

    # ==============================================================================
    # TAB 1: DESIGNER & VERIFICATION
    # ==============================================================================
    with tab_design:
        col_in, col_out = st.columns([1, 1])

        with col_in:
            st.subheader("1. Structural Member & Column Geometry")
            member_type = st.radio(
                "Member Type",
                ["Flat Slab", "Foundation Footing"],
                horizontal=True,
            )
            col_shape = st.selectbox(
                "Column Cross-Section", ["Rectangular Internal", "Circular Internal"]
            )

            c_g1, c_g2 = st.columns(2)
            with c_g1:
                if col_shape == "Rectangular Internal":
                    c1 = st.number_input(
                        "Column Width c₁ (x-dir, mm)",
                        min_value=150,
                        max_value=2000,
                        value=400,
                        step=50,
                    )
                    c2 = st.number_input(
                        "Column Depth c₂ (y-dir, mm)",
                        min_value=150,
                        max_value=2000,
                        value=400,
                        step=50,
                    )
                    dia_col = None
                else:
                    dia_col = st.number_input(
                        "Column Diameter D (mm)",
                        min_value=150,
                        max_value=2000,
                        value=450,
                        step=50,
                    )
                    c1, c2 = dia_col, dia_col

                h_slab = st.number_input(
                    "Slab / Pad Thickness h (mm)",
                    min_value=150,
                    max_value=1500,
                    value=250,
                    step=25,
                )

            with c_g2:
                c_nom = st.number_input(
                    "Nominal Cover c_nom (mm)",
                    min_value=20,
                    max_value=100,
                    value=30,
                    step=5,
                )
                bar_dx = st.selectbox("Rebar Diameter x-dir (mm)", [12, 16, 20, 25], index=1)
                bar_dy = st.selectbox("Rebar Diameter y-dir (mm)", [12, 16, 20, 25], index=1)

            st.markdown("---")
            st.subheader("2. Loading & Reinforcement Ratios")
            c_m1, c_m2 = st.columns(2)
            with c_m1:
                ved = st.number_input(
                    "Design Shear Force V_Ed (kN)",
                    min_value=10.0,
                    max_value=10000.0,
                    value=650.0,
                    step=25.0,
                )
                beta = st.number_input(
                    "Eccentricity Factor β (Clause 6.4.3)",
                    min_value=1.00,
                    max_value=1.60,
                    value=1.15,
                    step=0.05,
                    help="Default β=1.15 for internal columns, 1.4 for edge columns, 1.5 for corner columns.",
                )
                fck = st.selectbox("Concrete Grade fck (MPa)", [25, 30, 35, 40, 50], index=1)

            with c_m2:
                rho_lx = st.number_input(
                    "Flexural Tension Rebar Ratio ρ_lx (%)",
                    min_value=0.10,
                    max_value=2.00,
                    value=0.75,
                    step=0.05,
                )
                rho_ly = st.number_input(
                    "Flexural Tension Rebar Ratio ρ_ly (%)",
                    min_value=0.10,
                    max_value=2.00,
                    value=0.75,
                    step=0.05,
                )
                fywd = st.number_input(
                    "Shear Steel Design Yield f_ywd (MPa)",
                    min_value=200,
                    max_value=500,
                    value=435,
                    step=15,
                )

            element_tag = st.text_input("Element Mark / ID", value="SLAB-P1")

        # --- Eurocode 2 Calculation Engine ---
        # Effective Depths
        dx = h_slab - c_nom - (bar_dx / 2.0)
        dy = h_slab - c_nom - bar_dx - (bar_dy / 2.0)
        d_eff = (dx + dy) / 2.0  # mm

        # Concrete Strength Parameters
        gamma_c = 1.5
        fcd = 0.85 * fck / gamma_c
        nu = 0.6 * (1.0 - (fck / 250.0))

        # Perimeters u0 and u1
        if col_shape == "Rectangular Internal":
            u0 = 2.0 * (c1 + c2)
            u1 = u0 + 2.0 * math.pi * (2.0 * d_eff)
        else:
            u0 = math.pi * dia_col
            u1 = math.pi * (dia_col + 4.0 * d_eff)

        # 1. Check maximum shear stress at column perimeter u0
        v_ed0 = (beta * (ved * 1000.0)) / (u0 * d_eff)  # MPa
        v_rd_max = 0.5 * nu * fcd  # MPa
        util_u0 = v_ed0 / v_rd_max

        # 2. Check concrete punching shear capacity at u1 (2d)
        rho_l = min(math.sqrt((rho_lx / 100.0) * (rho_ly / 100.0)), 0.02)
        k_scale = min(1.0 + math.sqrt(200.0 / d_eff), 2.0)
        c_rdc = 0.18 / gamma_c
        vmin = 0.035 * (k_scale**1.5) * math.sqrt(fck)

        v_rdc = max(
            c_rdc * k_scale * ((100.0 * rho_l * fck) ** (1.0 / 3.0)), vmin
        )  # MPa

        v_ed1 = (beta * (ved * 1000.0)) / (u1 * d_eff)  # MPa
        util_u1 = v_ed1 / v_rdc

        needs_links = util_u1 > 1.0

        # Outer perimeter where shear reinforcement is no longer needed (u_out)
        u_out_req = (beta * (ved * 1000.0)) / (v_rdc * d_eff)

        with col_out:
            st.subheader("Verification Results Summary")

            m1, m2, m3 = st.columns(3)
            m1.metric("Effective Depth d", f"{d_eff:.1f} mm")
            m2.metric("Stress at u₀ (v_Ed0)", f"{v_ed0:.2f} MPa", delta=f"{util_u0*100:.1f}% Limit")
            m3.metric("Stress at u₁ (v_Ed1)", f"{v_ed1:.2f} MPa", delta=f"{util_u1*100:.1f}% Concrete Cap")

            st.divider()

            # Status Cards
            c_st1, c_st2 = st.columns(2)
            with c_st1:
                st.markdown("**1. Crushing Check at Column Perimeter (u₀)**")
                st.write(f"- $v_{{Ed,0}}$ = **{v_ed0:.2f} MPa**")
                st.write(f"- $v_{{Rd,max}}$ = **{v_rd_max:.2f} MPa**")
                if util_u0 <= 1.0:
                    st.success("✅ Concrete Crushing Limit OK")
                else:
                    st.error("❌ Concrete Crushing Failure — Increase Slab Depth / Column Size")

            with c_st2:
                st.markdown("**2. Concrete Punching Capacity at 2d (u₁)**")
                st.write(f"- $v_{{Ed,1}}$ = **{v_ed1:.2f} MPa**")
                st.write(f"- $v_{{Rd,c}}$ = **{v_rdc:.2f} MPa**")
                if not needs_links:
                    st.success("✅ No Punching Shear Reinforcement Required")
                else:
                    st.warning("⚠️ Shear Reinforcement (Links/Studs) Required")

            # Link Design if Required
            if needs_links and util_u0 <= 1.0:
                st.markdown("### 3. Required Shear Reinforcement (Clause 6.4.5)")
                # Required steel per perimeter row
                sr = 0.75 * d_eff  # radial spacing
                v_ed_link = v_ed1
                # Asw/sr calculation per unit perimeter
                asw_per_s = ((v_ed_link - 0.75 * v_rdc) * u1 * d_eff) / (1.5 * fywd)
                asw_per_s = max(asw_per_s, 0.08 * math.sqrt(fck) * u1 / (1.5 * fywd))
                st.info(f"💡 Provide minimum total link area **$A_{{sw}}$ = {asw_per_s:.0f} mm²** distributed within $1.5d$ of column face at radial spacing $s_r \\le {sr:.0f}$ mm.")

            # 2D Interactive Perimeter Diagram
            st.markdown("### Control Perimeters Visualizer")
            fig = go.Figure()

            # Plot Column u0
            if col_shape == "Rectangular Internal":
                half_c1, half_c2 = c1 / 2.0, c2 / 2.0
                fig.add_shape(
                    type="rect",
                    x0=-half_c1,
                    y0=-half_c2,
                    x1=half_c1,
                    y1=half_c2,
                    line=dict(color="#E53E3E", width=3),
                    fillcolor="rgba(229, 62, 62, 0.2)",
                    name="Perimeter u0",
                )
                # Outer perimeter u1 (2d rounded corner box approximation)
                r_2d = 2.0 * d_eff
                fig.add_shape(
                    type="rect",
                    x0=-(half_c1 + r_2d),
                    y0=-(half_c2 + r_2d),
                    x1=half_c1 + r_2d,
                    y1=half_c2 + r_2d,
                    line=dict(color="#3182CE", width=2, dash="dash"),
                    name="Perimeter u1 (2d)",
                )
                range_lim = max(half_c1 + r_2d, half_c2 + r_2d) * 1.3
            else:
                rad_col = dia_col / 2.0
                fig.add_shape(
                    type="circle",
                    x0=-rad_col,
                    y0=-rad_col,
                    x1=rad_col,
                    y1=rad_col,
                    line=dict(color="#E53E3E", width=3),
                    fillcolor="rgba(229, 62, 62, 0.2)",
                )
                rad_u1 = rad_col + 2.0 * d_eff
                fig.add_shape(
                    type="circle",
                    x0=-rad_u1,
                    y0=-rad_u1,
                    x1=rad_u1,
                    y1=rad_u1,
                    line=dict(color="#3182CE", width=2, dash="dash"),
                )
                range_lim = rad_u1 * 1.3

            fig.update_layout(
                xaxis=dict(title="X (mm)", range=[-range_lim, range_lim]),
                yaxis=dict(
                    title="Y (mm)",
                    range=[-range_lim, range_lim],
                    scaleanchor="x",
                    scaleratio=1,
                ),
                height=300,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#CBD5E0"),
            )
            st.plotly_chart(fig, use_container_width=True)

            # Save verification record
            if st.button("💾 Save Verification Record", type="primary", use_container_width=True):
                status_str = "PASS (No Links)" if not needs_links and util_u0 <= 1.0 else ("PASS (Links Req.)" if util_u0 <= 1.0 else "FAIL (Crushing)")
                rec = {
                    "id": f"PCH-{len(items)+1:03d}",
                    "mark": element_tag,
                    "type": f"{member_type} ({h_slab}mm)",
                    "ved": round(ved, 1),
                    "ved0_util": f"{util_u0*100:.1f}%",
                    "ved1_util": f"{util_u1*100:.1f}%",
                    "status": status_str,
                }
                CRUDService.create(STATE_KEY, rec)
                st.success(f"Saved record `{element_tag}`!")
                st.rerun()

    # ==============================================================================
    # TAB 2: DESIGN THEORY & VERIFICATION RULES
    # ==============================================================================
    with tab_theory:
        st.subheader("EN 1992-1-1 Section 6.4 Punching Shear Theory")

        st.markdown(r"""
        ### 1. Control Perimeters
        - **Column Perimeter ($u_0$):** For internal rectangular columns: $u_0 = 2(c_1 + c_2)$.
        - **Basic Control Perimeter ($u_1$):** Located at distance $2d$ from the loaded area perimeter with rounded corners:
          $$u_1 = u_0 + 2\pi(2d)$$

        ### 2. Maximum Punching Shear Stress at Column Face ($u_0$)
        $$v_{Ed,0} = \frac{\beta \cdot V_{Ed}}{u_0 \cdot d} \le v_{Rd,max} = 0.5 \cdot \nu \cdot f_{cd}$$
        Where $\nu = 0.6 \left(1 - \frac{f_{ck}}{250}\right)$.

        ### 3. Concrete Punching Resistance at $u_1$ ($2d$)
        $$v_{Rd,c} = C_{Rd,c} \cdot k \cdot \left(100 \cdot \rho_l \cdot f_{ck}\right)^{1/3} \ge v_{min}$$
        Where:
        - $k = 1 + \sqrt{\frac{200}{d}} \le 2.0$
        - $\rho_l = \sqrt{\rho_{lx} \cdot \rho_{ly}} \le 0.02$
        - $v_{min} = 0.035 \cdot k^{3/2} \cdot f_{ck}^{1/2}$

        ### 4. Shear Reinforcement Design
        When $v_{Ed,1} > v_{Rd,c}$, shear links or studs must be supplied, providing resistance:
        $$v_{Rd,cs} = 0.75 v_{Rd,c} + 1.5 \left(\frac{d}{s_r}\right) A_{sw} f_{ywd,ef} \left(\frac{1}{u_1 d}\right) \sin\alpha$$
        """)

    # ==============================================================================
    # TAB 3: SAVED SCHEDULE
    # ==============================================================================
    with tab_schedule:
        st.subheader("Punching Shear Verification Schedule")
        if items:
            df_rec = pd.DataFrame(items)
            st.dataframe(
                df_rec,
                column_config={
                    "id": "ID",
                    "mark": "Element Mark",
                    "type": "Member Type",
                    "ved": st.column_config.NumberColumn("V_Ed (kN)", format="%.1f"),
                    "ved0_util": "u₀ Stress Ratio",
                    "ved1_util": "u₁ Stress Ratio",
                    "status": "Verification Status",
                },
                use_container_width=True,
                hide_index=True,
            )

            c_d1, c_d2 = st.columns([2, 1])
            with c_d2:
                sel_id = st.selectbox("Select ID to Delete", df_rec["id"].tolist())
                if st.button("🗑️ Delete Selected Record"):
                    CRUDService.delete(STATE_KEY, sel_id)
                    st.rerun()
        else:
            st.info("No punching shear verification records saved yet.")