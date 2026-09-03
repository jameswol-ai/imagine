"""RFI register and response-tracking workspace."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import date
import pandas as pd
import plotly.express as px
import streamlit as st


@dataclass
class RFI:
    rfi_id: str
    subject: str
    status: str
    priority: str
    due_date: str


class RFIEngine:
    def run(self, rfis: list[RFI] | None = None) -> dict:
        rfis = rfis or []
        open_count = sum(x.status.casefold() not in {"closed", "answered"} for x in rfis)
        overdue = sum(x.status.casefold() not in {"closed", "answered"} and x.due_date < date.today().isoformat() for x in rfis)
        return {"count": len(rfis), "open": open_count, "overdue": overdue}


def render() -> None:
    st.subheader("Request for Information Register")
    st.caption("Track project RFIs, priorities, response status and due dates.")
    if "rfi_rows" not in st.session_state:
        st.session_state.rfi_rows = pd.DataFrame([
            {"RFI ID": "RFI-001", "Subject": "Structural opening", "Status": "Open", "Priority": "High", "Due Date": date.today().isoformat()},
            {"RFI ID": "RFI-002", "Subject": "Door schedule", "Status": "Answered", "Priority": "Normal", "Due Date": date.today().isoformat()},
        ])
    edited = st.data_editor(st.session_state.rfi_rows, num_rows="dynamic", use_container_width=True, hide_index=True)
    rfis = [RFI(str(r["RFI ID"]), str(r["Subject"]), str(r["Status"]), str(r["Priority"]), str(r["Due Date"])) for r in edited.fillna("").to_dict("records") if str(r.get("RFI ID", "")).strip()]
    result = RFIEngine().run(rfis)
    a, b, c = st.columns(3)
    a.metric("RFIs", result["count"])
    b.metric("Open", result["open"])
    c.metric("Overdue", result["overdue"])
    df = pd.DataFrame([asdict(x) for x in rfis])
    if not df.empty:
        counts = df["Status"].value_counts().rename_axis("Status").reset_index(name="Count")
        fig = px.pie(counts, names="Status", values="Count", title="RFI status")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, use_container_width=True, hide_index=True)
