"""Portfolio KPI dashboard based on transparent project metrics."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st


class KPIEngine:
    def run(self, projects: list[dict] | None = None) -> dict[str, float]:
        projects = projects or []
        budget = sum(float(p.get("budget", 0) or 0) for p in projects)
        progress = [float(p.get("progress", 0) or 0) for p in projects]
        average_progress = sum(progress) / len(progress) if progress else 0.0
        active = sum(str(p.get("status", "")).casefold() == "active" for p in projects)
        return {"portfolio_budget": budget, "average_progress": average_progress, "active_projects": float(active), "project_count": float(len(projects))}


def render() -> None:
    st.subheader("Portfolio KPIs")
    st.caption("Live session/project metrics where available. Empty portfolios are shown as empty, not fabricated.")
    projects = st.session_state.get("projects_data", [])
    result = KPIEngine().run(projects)
    a, b, c, d = st.columns(4)
    a.metric("Projects", int(result["project_count"]))
    b.metric("Active", int(result["active_projects"]))
    c.metric("Average progress", f"{result['average_progress']:.1f}%")
    d.metric("Portfolio budget", f"{result['portfolio_budget']:,.2f}")
    if not projects:
        st.info("No project KPI records are currently available.")
        return
    df = pd.DataFrame(projects)
    if "progress" in df and "name" in df:
        chart = df[["name", "progress"]].rename(columns={"name": "Project", "progress": "Progress"})
        fig = px.bar(chart, x="Project", y="Progress", range_y=[0, 100], title="Project progress")
        st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df, use_container_width=True, hide_index=True)
