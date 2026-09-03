"""Digital-twin asset register with operational health indicators."""
from __future__ import annotations

from datetime import date
import pandas as pd
import plotly.express as px
import streamlit as st


class AssetEngine:
    def run(self, assets: list[dict] | None = None) -> dict[str, int]:
        assets = assets or []
        operational = sum(str(x.get("status", "")).casefold() in {"operational", "active"} for x in assets)
        maintenance = sum(str(x.get("status", "")).casefold() in {"maintenance", "service due"} for x in assets)
        return {"total": len(assets), "operational": operational, "maintenance": maintenance}


def render() -> None:
    st.subheader("Digital Twin Asset Register")
    st.caption("Asset inventory and operational-status screening. Connect telemetry sources for live condition monitoring.")
    if "asset_rows" not in st.session_state:
        st.session_state.asset_rows = pd.DataFrame([
            {"Asset ID": "MEP-001", "Asset": "Chiller", "System": "HVAC", "Status": "Operational", "Criticality": "High", "Next Service": date.today().isoformat()},
            {"Asset ID": "ELEC-001", "Asset": "Main switchboard", "System": "Electrical", "Status": "Operational", "Criticality": "High", "Next Service": date.today().isoformat()},
        ])
    edited = st.data_editor(st.session_state.asset_rows, num_rows="dynamic", use_container_width=True, hide_index=True)
    records = edited.fillna("").to_dict("records")
    result = AssetEngine().run(records)
    a, b, c = st.columns(3)
    a.metric("Assets", result["total"])
    b.metric("Operational", result["operational"])
    c.metric("Maintenance", result["maintenance"])
    if records:
        df = pd.DataFrame(records)
        if "System" in df and "Status" in df:
            chart = df.groupby(["System", "Status"], dropna=False).size().reset_index(name="Count")
            fig = px.bar(chart, x="System", y="Count", color="Status", barmode="stack", title="Asset health by system")
            st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, use_container_width=True, hide_index=True)
