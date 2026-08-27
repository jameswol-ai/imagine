"""
IMAGINE Projects Module UI
Path: Modules/projects/project_page.py
App: imagine
"""

import pandas as pd
import plotly.express as px
import streamlit as st
from Modules.projects.projects import ProjectService


class ProjectPage:

    @staticmethod
    def render_portfolio_metrics(projects):
        metrics = ProjectService.portfolio_metrics(projects)
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Projects", metrics["total_projects"])
        with col2:
            st.metric("Portfolio Budget", f"${metrics['total_budget']:,.2f}M")
        with col3:
            st.metric("Average Progress", f"{metrics['average_progress']}%")

    @staticmethod
    def render_project_table(projects):
        if not projects:
            st.info("No projects available.")
            return

        df = pd.DataFrame(projects)
        st.dataframe(df, use_container_width=True)

    @staticmethod
    def render_create_project_form():
        st.subheader("Create New Project")

        with st.form("create_project_form"):
            name = st.text_input("Project Name")
            client = st.text_input("Client")
            category = st.selectbox(
                "Category",
                ["Commercial", "Residential", "Industrial", "Infrastructure", "Mixed Use"],
            )
            budget = st.number_input("Budget (Million USD)", min_value=0.0, value=1.0, step=0.1)
            status = st.selectbox("Status", ["planning", "active", "completed", "on_hold"])

            create = st.form_submit_button("Create Project")

            if create:
                project = ProjectService.create_project(
                    name=name,
                    client=client,
                    category=category,
                    budget=budget,
                    status=status,
                )

                if "projects_data" not in st.session_state:
                    st.session_state.projects_data = []

                st.session_state.projects_data.append(project)
                st.success(f"Project '{name}' created.")
                st.rerun()

    @staticmethod
    def render_gantt_chart(project_id: str):
        """Renders an interactive Plotly Gantt chart for project milestones."""
        df_milestones = ProjectService.get_project_milestones(project_id)

        fig = px.timeline(
            df_milestones,
            x_start="Start",
            x_end="Finish",
            y="Task",
            color="Phase",
            title="Project Execution Timeline & Milestones",
            hover_data=["Completion"],
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(
            height=320,
            margin=dict(l=10, r=10, t=40, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#CBD5E0"),
        )
        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def render_structural_history(project_id: str):
        """Renders linked Eurocode structural calculation history."""
        all_calcs = st.session_state.get("structural_calcs", [])
        project_calcs = ProjectService.get_project_calculations(project_id, all_calcs)

        if not project_calcs:
            st.info("No structural calculations logged for this project yet.")
            return

        # Summary Metrics
        passed = sum(1 for c in project_calcs if c.get("status") == "Passed")
        warnings = sum(1 for c in project_calcs if c.get("status") == "Warning")
        failed = sum(1 for c in project_calcs if c.get("status") == "Failed")

        m1, m2, m3 = st.columns(3)
        m1.metric("Passed Checks", passed)
        m2.metric("Warnings (U.C. > 0.90)", warnings)
        m3.metric("Failed Checks", failed)

        # Detailed Table
        df_calcs = pd.DataFrame(project_calcs)
        cols_to_show = ["id", "code", "element_name", "status", "unity_check", "updated_at"]
        st.dataframe(
            df_calcs[cols_to_show],
            column_config={
                "id": "Calc ID",
                "code": "Standard",
                "element_name": "Structural Element",
                "unity_check": st.column_config.NumberColumn("Unity Check (η)", format="%.2f"),
                "status": st.column_config.TextColumn("Status"),
                "updated_at": "Timestamp",
            },
            use_container_width=True,
            hide_index=True,
        )

    @classmethod
    def render_project_details(cls, projects):
        if not projects:
            st.info("No projects available to view.")
            return

        options = {str(project["id"]): project["name"] for project in projects}
        selected_id = st.selectbox(
            "Select Project",
            options=list(options.keys()),
            format_func=lambda x: options[x],
        )

        project = ProjectService.find_project(selected_id, projects)

        if project:
            st.subheader(f"📌 {project['name']}")
            st.caption(f"ID: **{project['id']}** | Category: **{project.get('category', project.get('typology', 'N/A'))}**")

            # Integrated Detail Sub-Tabs
            det_tab1, det_tab2, det_tab3 = st.tabs([
                "📅 Milestones Gantt Chart",
                "🧱 Structural Calculations",
                "⚙️ Raw Metadata",
            ])

            with det_tab1:
                cls.render_gantt_chart(project["id"])

            with det_tab2:
                cls.render_structural_history(project["id"])

            with det_tab3:
                st.json(project)

    @classmethod
    def render(cls):
        st.title("📁 Project Management")

        # Synchronize state keys smoothly
        if "projects_data" not in st.session_state:
            st.session_state.projects_data = st.session_state.get("projects", [])

        projects = st.session_state.projects_data

        cls.render_portfolio_metrics(projects)
        st.divider()

        tab1, tab2, tab3 = st.tabs(["Portfolio", "Project Details", "Create Project"])

        with tab1:
            cls.render_project_table(projects)

        with tab2:
            cls.render_project_details(projects)

        with tab3:
            cls.render_create_project_form()
