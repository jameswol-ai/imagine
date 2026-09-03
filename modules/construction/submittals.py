"""Submittal register and review workspace."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pandas as pd
import plotly.express as px
import streamlit as st


class SubmittalService:
    @staticmethod
    def create_submittal(title: str, discipline: str) -> dict:
        if not title.strip():
            raise ValueError("Submittal title is required")
        return {"id": str(uuid.uuid4()), "submittal_no": f"SUB-{str(uuid.uuid4())[:8].upper()}", "title": title.strip(), "discipline": discipline, "status": "Submitted", "comments": "", "created_at": datetime.now(timezone.utc).isoformat()}

    @staticmethod
    def approve(submittal: dict) -> dict:
        result = dict(submittal); result["status"] = "Approved"; return result

    @staticmethod
    def reject(submittal: dict, comments: str) -> dict:
        result = dict(submittal); result["status"] = "Rejected"; result["comments"] = comments; return result


def render() -> None:
    st.subheader("Submittals")
    st.caption("Material, shop-drawing and technical-submittal register with review status.")
    if "submittal_rows" not in st.session_state:
        st.session_state.submittal_rows = [SubmittalService.create_submittal("Concrete mix design", "Structural"), SubmittalService.create_submittal("Air-conditioning equipment", "MEP")]
    with st.form("submittal_form"):
        a, b = st.columns(2)
        title = a.text_input("Title")
        discipline = b.selectbox("Discipline", ["Architecture", "Structural", "MEP", "Civil", "Other"])
        add = st.form_submit_button("Add submittal")
    if add:
        if not title.strip(): st.error("Enter a submittal title.")
        else: st.session_state.submittal_rows.append(SubmittalService.create_submittal(title, discipline)); st.success("Submittal added.")
    data = pd.DataFrame(st.session_state.submittal_rows)
    st.dataframe(data[["submittal_no", "title", "discipline", "status", "comments", "created_at"]], use_container_width=True, hide_index=True)
    counts = data["status"].value_counts().rename_axis("Status").reset_index(name="Count")
    st.plotly_chart(px.pie(counts, names="Status", values="Count", title="Submittal review status"), use_container_width=True)
