# modules/dashboard/dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

def render():
    st.title("📊 Overview Dashboard")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Active Projects", "12", "+2")
    col2.metric("Total Budget", "$184M", "+5%")
    col3.metric("Progress (avg)", "68%", "+12%")
    col4.metric("Open RFIs", "7", "-3")

    st.subheader("Project Health")
    projects = st.session_state.get("projects_data", [])
    if projects:
        df = pd.DataFrame(projects)
        fig = px.bar(df, x="name", y="progress", color="status", text="progress")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No projects found.")

    st.subheader("Recent Activity")
    activity = pd.DataFrame({
        "Time": [datetime.now() - timedelta(hours=i) for i in range(5)],
        "User": ["Alice", "Bob", "Charlie", "Alice", "Dave"],
        "Action": ["Updated BOQ", "Submitted RFI", "Approved revision", "Added drawing", "Closed snag"],
    })
    st.dataframe(activity, use_container_width=True)