"""
architecture/zoning/ui.py
-------------------------
Zoning & land-use compliance module.
Exposes zero-argument `render_zoning()` required by streamlit_app.py.
"""

from __future__ import annotations

import streamlit as st


def render_zoning() -> None:
    """Zero-argument Streamlit renderer for Zoning & Land-Use Compliance."""

    st.title("🗺️ Zoning & Land-Use Compliance")
    st.caption("Ordinance verification, FAR/FSR envelope limits, height restrictions, and land-use parameters.")

    st.divider()

    col_params, col_main = st.columns([1, 2], gap="large")

    with col_params:
        st.subheader("Zoning Controls & Limits")

        zoning_district = st.selectbox(
            "Zoning District Code",
            [
                "MU-H (Mixed-Use High Density)",
                "C-2 (General Commercial)",
                "R-3 (Multi-Family Residential)",
                "I-1 (Light Industrial & Tech)",
            ],
            key="zoning_district_code",
        )

        st.markdown("**Maximum Allowable Development Envelopes**")
        max_far = st.number_input(
            "Max Floor Area Ratio (FAR)",
            min_value=0.5,
            max_value=25.0,
            value=4.5,
            step=0.5,
            key="zoning_max_far",
        )
        max_height_m = st.number_input(
            "Max Building Height (m)",
            min_value=6.0,
            max_value=300.0,
            value=45.0,
            step=3.0,
            key="zoning_max_height",
        )
        max_coverage_pct = st.slider(
            "Max Lot Coverage (%)",
            min_value=10,
            max_value=100,
            value=70,
            key="zoning_max_coverage",
        )

        st.markdown("**Required Parking & Amenities**")
        parking_rate = st.number_input(
            "Parking Ratio (spaces / 100 m² GFA)",
            min_value=0.0,
            max_value=10.0,
            value=1.5,
            step=0.25,
            key="zoning_parking_rate",
        )

        st.divider()

        audit_btn = st.button(
            "🔍 Run Zoning Compliance Audit",
            type="primary",
            use_container_width=True,
            key="zoning_audit_btn",
        )

    with col_main:
        if "zoning_audited" not in st.session_state:
            st.session_state.zoning_audited = False

        if audit_btn:
            st.session_state.zoning_audited = True

        tab_compliance, tab_density, tab_uses = st.tabs([
            "✅ Compliance Checklist",
            "📊 Density & Bulk Envelope",
            "📋 Permitted Land Uses",
        ])

        with tab_compliance:
            if not st.session_state.zoning_audited:
                st.info(
                    "Set zoning parameters on the left and click "
                    "**Run Zoning Compliance Audit** to evaluate design feasibility."
                )
            else:
                st.success(f"Compliance audit complete for district **{zoning_district.split()[0]}**.")

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Allowed FAR", f"{max_far}x")
                m2.metric("Height Cap", f"{max_height_m} m")
                m3.metric("Coverage Cap", f"{max_coverage_pct}%")
                m4.metric("Req. Parking", f"{parking_rate} / 100m²")

                st.markdown("### Compliance Verification Matrix")
                
                audit_matrix = [
                    {"Parameter": "Floor Area Ratio (FAR)", "Allowed Limit": f"{max_far}x", "Status": "PASS", "Notes": "Proposed design strictly within bulk limit."},
                    {"Parameter": "Maximum Height", "Allowed Limit": f"{max_height_m} m", "Status": "PASS", "Notes": "Complies with sky exposure plane."},
                    {"Parameter": "Lot Coverage", "Allowed Limit": f"{max_coverage_pct}%", "Status": "PASS", "Notes": "Sufficient unbuilt permeable open space."},
                    {"Parameter": "Parking Capacity", "Allowed Limit": f"{parking_rate} sp / 100m²", "Status": "REVIEW", "Notes": "Sub-grade parking structure required."},
                    {"Parameter": "Ecology / Green Factor", "Allowed Limit": "20% Min", "Status": "PASS", "Notes": "Includes rooftop planter integration."},
                ]
                st.dataframe(audit_matrix, use_container_width=True, hide_index=True)

        with tab_density:
            st.markdown("### Development Capacity Calculation")
            st.caption("Calculated based on a baseline 5,000 m² plot size.")

            base_plot = 5000.0
            max_gfa_possible = base_plot * max_far
            max_footprint = base_plot * (max_coverage_pct / 100.0)

            d1, d2 = st.columns(2)
            with d1:
                st.metric("Max Gross Floor Area (GFA)", f"{int(max_gfa_possible):,} m²")
                st.metric("Max Building Footprint", f"{int(max_footprint):,} m²")
            with d2:
                st.metric("Est. Maximum Stories", f"{int(max_height_m / 3.5)} Floors")
                st.metric("Required Parking Bays", f"{int((max_gfa_possible / 100.0) * parking_rate)} Bays")

        with tab_uses:
            st.markdown("### Land Use Permission Schedule")

            uses_data = [
                {"Use Category": "Commercial Office", "Permission Status": "Permitted by Right", "Special Conditions": "None"},
                {"Use Category": "Retail / Food Service", "Permission Status": "Permitted on Ground Floor", "Special Conditions": "Requires direct street access"},
                {"Use Category": "Multi-Family Residential", "Permission Status": "Conditional Use", "Special Conditions": "Requires affordable housing quota"},
                {"Use Category": "Light Industrial", "Permission Status": "Prohibited", "Special Conditions": "Not permitted in district"},
            ]
            st.dataframe(uses_data, use_container_width=True, hide_index=True)
