"""
IMAGINE Dashboard Module

Portfolio Dashboard
KPIs
Project Health
Recent Activity

Version 24.1
"""

from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st


class DashboardPage:

    @staticmethod
    def calculate_metrics(projects):

        if not projects:
            return {
                "active_projects": 0,
                "total_budget": 0,
                "average_progress": 0
            }

        active_projects = len(
            [
                p for p in projects
                if p.get("status") == "active"
            ]
        )

        total_budget = sum(
            p.get("budget", 0)
            for p in projects
        )

        average_progress = round(
            sum(
                p.get("progress", 0)
                for p in projects
            ) / len(projects),
            1
        )

        return {
            "active_projects": active_projects,
            "total_budget": total_budget,
            "average_progress": average_progress
        }

    @staticmethod
    def render_kpis(projects):

        metrics = (
            DashboardPage
            .calculate_metrics(projects)
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Active Projects",
                metrics["active_projects"]
            )

        with col2:
            st.metric(
                "Total Budget",
                f"${metrics['total_budget']:,.1f}M"
            )

        with col3:
            st.metric(
                "Average Progress",
                f"{metrics['average_progress']}%"
            )

        with col4:
            st.metric(
                "Open RFIs",
                7
            )

    @staticmethod
    def render_project_health(projects):

        st.subheader(
            "Project Health"
        )

        if not projects:
            st.info(
                "No projects available."
            )
            return

        df = pd.DataFrame(projects)

        if df.empty:
            st.info(
                "No project information found."
            )
            return

        fig = px.bar(
            df,
            x="name",
            y="progress",
            color="status",
            text="progress",
            title="Project Progress"
        )

        fig.update_layout(
            height=450
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    @staticmethod
    def render_recent_activity():

        st.subheader(
            "Recent Activity"
        )

        activity = pd.DataFrame({
            "Time": [
                datetime.now()
                - timedelta(hours=i)
                for i in range(5)
            ],
            "User": [
                "Alice",
                "Bob",
                "Charlie",
                "Alice",
                "Dave"
            ],
            "Action": [
                "Updated BOQ",
                "Submitted RFI",
                "Approved Revision",
                "Added Drawing",
                "Closed Snag"
            ]
        })

        st.dataframe(
            activity,
            use_container_width=True
        )

    @classmethod
    def render(
        cls,
        projects
    ):

        st.title(
            "📊 Portfolio Dashboard"
        )

        cls.render_kpis(
            projects
        )

        st.divider()

        cls.render_project_health(
            projects
        )

        st.divider()

        cls.render_recent_activity()
