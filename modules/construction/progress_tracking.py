"""Construction progress and schedule-monitoring workspace."""
from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import plotly.express as px
import streamlit as st


class ProgressTrackingService:
    @staticmethod
    def create_progress_record(activity: str, planned: float, actual: float) -> dict:
        if not activity.strip() or not 0 <= planned <= 100 or not 0 <= actual <= 100:
            raise ValueError("Activity is required and progress must be between 0 and 100")
        variance = actual - planned
        return {"activity": activity.strip(), "planned_percent": planned, "actual_percent": actual, "variance": variance, "date": datetime.now(timezone.utc).isoformat()}

    @staticmethod
    def schedule_status(variance: float) -> str:
        if variance >= 0:
            return "On Track"
        if variance >= -10:
            return "Minor Delay"
        return "Critical Delay"


def render() -> None:
    st.subheader("Planning / Scheduling / Progress")
    st.caption("Progress-control workspace for activity-level planned versus actual performance. Baselines and critical-path logic should come from the approved programme.")
    if "progress_rows" not in st.session_state:
        st.session_state.progress_rows = pd.DataFrame([
            {"Activity": "Site mobilisation", "Planned %": 100.0, "Actual %": 100.0},
            {"Activity": "Substructure", "Planned %": 65.0, "Actual %": 55.0},
            {"Activity": "Superstructure", "Planned %": 30.0, "Actual %": 22.0},
        ])
    edited = st.data_editor(st.session_state.progress_rows, num_rows="dynamic", use_container_width=True, hide_index=True, key="progress_editor")
    st.session_state.progress_rows = edited.copy()
    records = []
    for row in edited.fillna(0).to_dict("records"):
        activity = str(row.get("Activity", "")).strip()
        if not activity:
            continue
        planned = float(row.get("Planned %", 0) or 0)
        actual = float(row.get("Actual %", 0) or 0)
        record = ProgressTrackingService.create_progress_record(activity, planned, actual)
        record["status"] = ProgressTrackingService.schedule_status(record["variance"])
        records.append(record)
    data = pd.DataFrame(records)
    if data.empty:
        st.info("Add an activity to begin progress tracking.")
        return
    x, y, z = st.columns(3)
    x.metric("Activities", len(data))
    y.metric("Average actual", f"{data['actual_percent'].mean():.1f}%")
    z.metric("Critical delays", int((data["status"] == "Critical Delay").sum()))
    chart = data.melt(id_vars=["activity"], value_vars=["planned_percent", "actual_percent"], var_name="Measure", value_name="Progress")
    st.plotly_chart(px.bar(chart, x="activity", y="Progress", color="Measure", barmode="group", title="Planned vs actual progress"), use_container_width=True)
    st.dataframe(data, use_container_width=True, hide_index=True)
