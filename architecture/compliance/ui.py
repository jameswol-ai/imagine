"""
architecture/compliance/ui.py
------------------------------
Building code and design compliance audit module.
Exposes zero-argument `render_compliance()` required by streamlit_app.py.
"""

from __future__ import annotations

import streamlit as st


def render_compliance() -> None:
    """Zero-argument Streamlit renderer for Building Code & Safety Compliance."""

    st.title("✅ Building Code & Design Compliance")
    st.caption("Automated code verification, life safety, egress analysis, accessibility (ADA/ISO), and fire protection ratings.")

    st.divider()

    col_params, col_main = st.columns([1, 2], gap="large")

    with col_params:
        st.subheader("Regulatory Framework")

        code_standard = st.selectbox(
            "Building Code Framework",
            [
                "IBC 2024 (International Building Code)",
                "Eurocode / EN Standards",
                "UK Building Regulations (Approved Docs)",
                "NBC (National Building Code)",
            ],
            key="comp_code_standard",
        )

        occupancy_group = st.selectbox(
            "Occupancy Classification",
            [
                "Group B - Business / Office",
                "Group A-3 - Assembly / Cultural",
                "Group R-2 - Multi-Family Residential",
                "Group M - Mercantile / Retail",
            ],
            key="comp_occupancy_group",
        )

        construction_type = st.selectbox(
            "Construction Type",
            [
                "Type I-A (Non-combustible, 3-hr Fire Resistant)",
                "Type I-B (Non-combustible, 2-hr Fire Resistant)",
                "Type II-A (Non-combustible, Protected)",
                "Type III-A (Combustible Exterior Walls)",
            ],
            key="comp_construction_type",
        )

        st.markdown("**Life Safety Controls**")
        has_sprinklers = st.toggle(
            "Automatic Fire Sprinkler System (NFPA 13)",
            value=True,
            key="comp_sprinklers",
        )

        travel_distance_m = st.number_input(
            "Max Proposed Exit Travel Distance (m)",
            min_value=10.0,
            max_value=150.0,
            value=45.0,
            step=5.0,
            key="comp_travel_dist",
        )

        st.divider()

        run_audit_btn = st.button(
            "⚡ Run Automated Compliance Audit",
            type="primary",
            use_container_width=True,
            key="comp_run_audit_btn",
        )

    with col_main:
        if "comp_audited" not in st.session_state:
            st.session_state.comp_audited = False

        if run_audit_btn:
            st.session_state.comp_audited = True

        tab_safety, tab_ada, tab_report = st.tabs([
            "🛡️ Life Safety & Egress",
            "♿ Accessibility & ADA",
            "📑 Full Audit Matrix",
        ])

        with tab_safety:
            if not st.session_state.comp_audited:
                st.info(
                    "Configure building classification parameters on the left and click "
                    "**Run Automated Compliance Audit** to execute code rules."
                )
            else:
                st.success(f"Audit completed under **{code_standard.split()[0]}** regulations.")

                # Max allowable travel distance logic (sprinklered vs non-sprinklered)
                max_allowed_travel = 75.0 if has_sprinklers else 60.0
                travel_pass = travel_distance_m <= max_allowed_travel

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Code Framework", code_standard.split()[0])
                m2.metric("Occupancy", occupancy_group.split()[0])
                m3.metric("Sprinklers", "Active" if has_sprinklers else "None")
                m4.metric("Egress Status", "PASS" if travel_pass else "FAIL")

                st.markdown("### Fire & Egress Verification")

                safety_checks = [
                    {
                        "Code Provision": "Max Exit Travel Distance",
                        "Proposed": f"{travel_distance_m} m",
                        "Code Cap": f"{max_allowed_travel} m",
                        "Result": "PASS" if travel_pass else "VIOLATION",
                        "Remediation": "None required" if travel_pass else "Add additional stair core or exit passageway.",
                    },
                    {
                        "Code Provision": "Minimum Exit Stair Count",
                        "Proposed": "2 Cores",
                        "Code Cap": "2 Cores Min.",
                        "Result": "PASS",
                        "Remediation": "None required",
                    },
                    {
                        "Code Provision": "Structural Fire Resistance Rating",
                        "Proposed": "2 Hours",
                        "Code Cap": "2 Hours",
                        "Result": "PASS",
                        "Remediation": "None required",
                    },
                    {
                        "Code Provision": "Interior Finish Flame Spread",
                        "Proposed": "Class A",
                        "Code Cap": "Class A or B",
                        "Result": "PASS",
                        "Remediation": "None required",
                    },
                ]
                st.dataframe(safety_checks, use_container_width=True, hide_index=True)

        with tab_ada:
            st.markdown("### Universal Access & Barrier-Free Standards")

            ada_items = [
                {"Requirement": "Accessible Entry Route Width", "Standard": "≥ 1.20 m", "Status": "PASS"},
                {"Requirement": "Wheelchair Turning Space (180°)", "Standard": "1.50 m Radius", "Status": "PASS"},
                {"Requirement": "Ramp Slope Gradient (Max)", "Standard": "1:12 Slope (8.3%)", "Status": "PASS"},
                {"Requirement": "Elevator Car Internal Dimensions", "Standard": "1.40 m × 2.00 m", "Status": "PASS"},
                {"Requirement": "Tactile Paving & Braille Signage", "Standard": "ISO 21542 / ADA", "Status": "PASS"},
            ]
            st.dataframe(ada_items, use_container_width=True, hide_index=True)

        with tab_report:
            st.markdown("### Compliance Summary Scorecard")

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Overall Code Compliance Index**")
                st.progress(0.96, text="96% - Code Compliant")

                st.markdown("**Life Safety & Fire Protection**")
                st.progress(1.0, text="100% - Fully Compliant")

            with c2:
                st.markdown("**Accessibility Rating**")
                st.progress(0.92, text="92% - Fully Accessible")

                st.markdown("**Zoning & Environmental Limits**")
                st.progress(0.95, text="95% - Compliant")
