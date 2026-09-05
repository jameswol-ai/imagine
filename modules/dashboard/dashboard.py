"""Executive dashboard for the IMAGINE application shell."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st


def render() -> None:
    st.subheader("Executive Dashboard")
    st.caption("Portfolio-level view using data currently available to the IMAGINE session.")

    projects = st.session_state.get("projects_data", [])
    frame = pd.DataFrame(projects) if projects else pd.DataFrame()

    if frame.empty:
        a, b, c, d = st.columns(4)
        a.metric("Projects", 0)
        b.metric("Active", 0)
        c.metric("Portfolio budget", "0.00")
        d.metric("Average progress", "0.0%")
        st.info("No project records are currently available. Create a project to populate the executive dashboard.")
        return

    progress = pd.to_numeric(frame.get("progress", pd.Series(dtype=float)), errors="coerce").fillna(0)
    budget = pd.to_numeric(frame.get("budget", pd.Series(dtype=float)), errors="coerce").fillna(0)
    status = frame.get("status", pd.Series([""] * len(frame))).astype(str)

    a, b, c, d = st.columns(4)
    a.metric("Projects", len(frame))
    b.metric("Active", int(status.str.casefold().eq("active").sum()))
    c.metric("Portfolio budget", f"{budget.sum():,.2f}")
    d.metric("Average progress", f"{progress.mean():.1f}%")

    if "name" in frame.columns:
        chart = pd.DataFrame({"Project": frame["name"].astype(str), "Progress": progress})
        st.plotly_chart(px.bar(chart, x="Project", y="Progress", range_y=[0, 100], title="Project progress"), use_container_width=True)

    left, right = st.columns(2)
    with left:
        if "status" in frame.columns:
            counts = status.value_counts().rename_axis("Status").reset_index(name="Projects")
            st.plotly_chart(px.pie(counts, names="Status", values="Projects", title="Project status"), use_container_width=True)
    with right:
        if "name" in frame.columns:
            chart = pd.DataFrame({"Project": frame["name"].astype(str), "Budget": budget})
            st.plotly_chart(px.bar(chart, x="Project", y="Budget", title="Budget by project"), use_container_width=True)

    st.dataframe(frame, hide_index=True, use_container_width=True)


__all__ = ["render"]
