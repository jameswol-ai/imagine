"""Snagging and defects register workspace."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pandas as pd
import plotly.express as px
import streamlit as st


class SnaggingService:
    @staticmethod
    def create_snag(location: str, description: str, priority: str = "Medium") -> dict:
        if not location.strip() or not description.strip():
            raise ValueError("Location and description are required")
        return {"id": str(uuid.uuid4()), "snag_no": f"SNG-{str(uuid.uuid4())[:8].upper()}", "location": location.strip(), "description": description.strip(), "priority": priority, "status": "Open", "created_at": datetime.now(timezone.utc).isoformat(), "closed_by": ""}

    @staticmethod
    def close_snag(snag: dict, closed_by: str) -> dict:
        result = dict(snag); result["status"] = "Closed"; result["closed_by"] = closed_by; return result


def render() -> None:
    st.subheader("Snagging & Defects")
    st.caption("Track construction defects from identification through close-out.")
    if "snag_rows" not in st.session_state:
        st.session_state.snag_rows = [
            SnaggingService.create_snag("Level 1 corridor", "Paint finish incomplete", "Low"),
            SnaggingService.create_snag("Plant room", "Pipe support requires adjustment", "High"),
        ]
    with st.form("snag_form"):
        a, b, c = st.columns(3)
        location = a.text_input("Location")
        description = b.text_input("Defect description")
        priority = c.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
        add = st.form_submit_button("Add snag")
    if add:
        if not location.strip() or not description.strip(): st.error("Enter both location and description.")
        else: st.session_state.snag_rows.append(SnaggingService.create_snag(location, description, priority)); st.success("Snag added.")
    data = pd.DataFrame(st.session_state.snag_rows)
    x, y, z = st.columns(3)
    x.metric("Total", len(data)); y.metric("Open", int((data["status"] == "Open").sum())); z.metric("High / Critical", int(data["priority"].isin(["High", "Critical"]).sum()))
    st.dataframe(data[["snag_no", "location", "description", "priority", "status", "closed_by"]], use_container_width=True, hide_index=True)
    counts = data["priority"].value_counts().rename_axis("Priority").reset_index(name="Count")
    st.plotly_chart(px.bar(counts, x="Priority", y="Count", title="Snags by priority"), use_container_width=True)
