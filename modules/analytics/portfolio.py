"""Portfolio analytics workspace."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st


class PortfolioAnalytics:
    @staticmethod
    def summary(projects: list[dict]) -> dict[str, float]:
        return {
            "total_projects": len(projects),
            "active_projects": sum(str(p.get("status", "")).casefold() == "active" for p in projects),
            "total_budget": sum(float(p.get("budget", 0) or 0) for p in projects),
        }


def render() -> None:
    st.subheader("Portfolio")
    st.caption("Portfolio-level project distribution and budget analysis from available project records.")
    projects = st.session_state.get("projects_data", [])
    result = PortfolioAnalytics.summary(projects)
    a, b, c = st.columns(3)
    a.metric("Projects", int(result["total_projects"]))
    b.metric("Active", int(result["active_projects"]))
    c.metric("Total budget", f"{result['total_budget']:,.2f}")
    if not projects:
        st.info("No project records are currently available.")
        return
    frame = pd.DataFrame(projects)
    if "status" in frame.columns:
        counts = frame["status"].astype(str).value_counts().rename_axis("Status").reset_index(name="Projects")
        st.plotly_chart(px.bar(counts, x="Status", y="Projects", title="Portfolio status"), use_container_width=True)
    if "name" in frame.columns and "budget" in frame.columns:
        budget = frame[["name", "budget"]].copy()
        budget["budget"] = pd.to_numeric(budget["budget"], errors="coerce").fillna(0)
        budget = budget.rename(columns={"name": "Project", "budget": "Budget"})
        st.plotly_chart(px.bar(budget, x="Project", y="Budget", title="Budget by project"), use_container_width=True)
    st.dataframe(frame, hide_index=True, use_container_width=True)


__all__ = ["PortfolioAnalytics", "render"]
