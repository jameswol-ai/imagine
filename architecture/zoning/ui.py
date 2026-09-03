"""Zoning and land-use screening workspace."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st


def render_zoning() -> None:
    """Run a preliminary zoning envelope and land-use screening assessment."""
    st.title("Zoning & Land-Use Compliance")
    st.caption("Traceable FAR, coverage, height and parking screening. Authority-specific zoning rules must be verified before approval.")

    left, right = st.columns([1, 2], gap="large")
    with left:
        district = st.selectbox("Zoning district", ["Mixed-use", "Commercial", "Residential", "Light industrial"], key="zoning_district_code")
        lot_area = st.number_input("Lot area (m²)", min_value=100.0, value=5000.0, step=100.0, key="zoning_lot_area")
        proposed_gfa = st.number_input("Proposed GFA (m²)", min_value=0.0, value=12000.0, step=250.0, key="zoning_proposed_gfa")
        max_far = st.number_input("Maximum FAR", min_value=0.1, value=4.5, step=0.1, key="zoning_max_far")
        footprint = st.number_input("Proposed footprint (m²)", min_value=0.0, value=1800.0, step=50.0, key="zoning_footprint")
        max_coverage = st.slider("Maximum site coverage (%)", 1, 100, 70, key="zoning_max_coverage")
        proposed_height = st.number_input("Proposed height (m)", min_value=0.0, value=35.0, step=1.0, key="zoning_proposed_height")
        max_height = st.number_input("Maximum height (m)", min_value=1.0, value=45.0, step=1.0, key="zoning_max_height")
        parking_rate = st.number_input("Parking rate (spaces / 100 m² GFA)", min_value=0.0, value=1.5, step=0.25, key="zoning_parking_rate")
        provided_parking = st.number_input("Provided parking spaces", min_value=0, value=180, step=5, key="zoning_provided_parking")
        audit = st.button("Run zoning screening", type="primary", use_container_width=True, key="zoning_audit_btn")

    far_used = proposed_gfa / lot_area if lot_area else 0.0
    coverage_used = 100.0 * footprint / lot_area if lot_area else 0.0
    parking_required = int(round(proposed_gfa / 100.0 * parking_rate))
    checks = [
        ("FAR", far_used <= max_far, f"{far_used:.2f} / {max_far:.2f}"),
        ("Coverage", coverage_used <= max_coverage, f"{coverage_used:.1f}% / {max_coverage}%"),
        ("Height", proposed_height <= max_height, f"{proposed_height:.1f} / {max_height:.1f} m"),
        ("Parking", provided_parking >= parking_required, f"{provided_parking} / {parking_required} spaces"),
    ]

    with right:
        st.subheader("Screening Results")
        if audit:
            passed = sum(ok for _, ok, _ in checks)
            if passed == len(checks):
                st.success(f"Screening complete for {district}: {passed}/{len(checks)} checks pass.")
            else:
                st.warning(f"Screening complete for {district}: {passed}/{len(checks)} checks pass. Review failed items before progressing.")
        else:
            st.info("Adjust the proposal inputs and run the screening to evaluate the current design envelope.")

        st.dataframe(pd.DataFrame([
            {"Check": name, "Proposed / Required": value, "Status": "PASS" if ok else "REVIEW"}
            for name, ok, value in checks
        ]), use_container_width=True, hide_index=True)

        chart = pd.DataFrame({"Metric": ["FAR", "Coverage", "Height"], "Used": [far_used, coverage_used, proposed_height], "Limit": [max_far, max_coverage, max_height]})
        fig = px.bar(chart, x="Metric", y=["Used", "Limit"], barmode="group", height=330, title="Proposal vs screening limits")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Development Capacity")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Maximum GFA", f"{lot_area * max_far:,.0f} m²")
        c2.metric("Maximum footprint", f"{lot_area * max_coverage / 100.0:,.0f} m²")
        c3.metric("Parking required", parking_required)
        c4.metric("Open site", f"{max(0.0, lot_area - footprint):,.0f} m²")

        st.caption("FAR, coverage, height and parking values are user-supplied screening constraints, not legal determinations.")
