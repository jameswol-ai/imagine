"""Procurement package planning workspace."""
from __future__ import annotations

from datetime import datetime, timezone
import uuid

import pandas as pd
import plotly.express as px
import streamlit as st


class ProcurementService:
    @staticmethod
    def create_package(name: str, value: float, package_type: str) -> dict:
        if not name.strip() or value < 0:
            raise ValueError("Package name is required and value must be non-negative")
        return {"id": str(uuid.uuid4()), "name": name.strip(), "value": value, "package_type": package_type, "status": "Planned", "contractor": "", "created_at": datetime.now(timezone.utc).isoformat()}

    @staticmethod
    def award_package(package: dict, contractor: str) -> dict:
        if not contractor.strip():
            raise ValueError("Contractor is required")
        package = dict(package)
        package["contractor"] = contractor.strip()
        package["status"] = "Awarded"
        return package


def render() -> None:
    st.subheader("Procurement")
    st.caption("Package-level procurement planning linked conceptually to the BOQ. This workspace does not issue a contractual award.")
    if "procurement_packages" not in st.session_state:
        st.session_state.procurement_packages = [
            ProcurementService.create_package("Civil Works", 750_000.0, "Works"),
            ProcurementService.create_package("MEP Services", 420_000.0, "Services"),
        ]
    with st.form("procurement_package_form"):
        a, b, c = st.columns(3)
        name = a.text_input("Package name")
        value = b.number_input("Budget value", min_value=0.0, step=10_000.0)
        package_type = c.selectbox("Package type", ["Works", "Goods", "Services", "Consultancy"])
        submitted = st.form_submit_button("Add package")
    if submitted:
        if not name.strip():
            st.error("Enter a package name.")
        else:
            st.session_state.procurement_packages.append(ProcurementService.create_package(name, value, package_type))
            st.success("Procurement package added.")
    data = pd.DataFrame(st.session_state.procurement_packages)
    if data.empty:
        st.info("No procurement packages yet.")
        return
    st.dataframe(data[["name", "package_type", "value", "status", "contractor", "created_at"]], use_container_width=True, hide_index=True)
    st.plotly_chart(px.bar(data, x="name", y="value", color="status", title="Procurement package values"), use_container_width=True)
