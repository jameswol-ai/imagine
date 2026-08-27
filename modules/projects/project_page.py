"""
IMAGINE Projects Module

Projects UI Page

Version 24.1
"""

import pandas as pd
import streamlit as st

from modules.projects.projects import (
    ProjectService
)


class ProjectPage:

    @staticmethod
    def render_portfolio_metrics(
        projects
    ):

        metrics = (
            ProjectService
            .portfolio_metrics(
                projects
            )
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Projects",
                metrics["total_projects"]
            )

        with col2:
            st.metric(
                "Portfolio Budget",
                f"${metrics['total_budget']:,.2f}M"
            )

        with col3:
            st.metric(
                "Average Progress",
                f"{metrics['average_progress']}%"
            )

    @staticmethod
    def render_project_table(
        projects
    ):

        if not projects:
            st.info(
                "No projects available."
            )
            return

        df = pd.DataFrame(projects)

        st.dataframe(
            df,
            use_container_width=True
        )

    @staticmethod
    def render_create_project_form():

        st.subheader(
            "Create New Project"
        )

        with st.form(
            "create_project_form"
        ):

            name = st.text_input(
                "Project Name"
            )

            client = st.text_input(
                "Client"
            )

            category = st.selectbox(
                "Category",
                [
                    "Commercial",
                    "Residential",
                    "Industrial",
                    "Infrastructure",
                    "Mixed Use"
                ]
            )

            budget = st.number_input(
                "Budget (Million USD)",
                min_value=0.0,
                value=1.0,
                step=0.1
            )

            status = st.selectbox(
                "Status",
                [
                    "planning",
                    "active",
                    "completed",
                    "on_hold"
                ]
            )

            create = st.form_submit_button(
                "Create Project"
            )

            if create:

                project = (
                    ProjectService
                    .create_project(
                        name=name,
                        client=client,
                        category=category,
                        budget=budget,
                        status=status
                    )
                )

                st.session_state.projects_data.append(
                    project
                )

                st.success(
                    f"Project '{name}' created."
                )

                st.rerun()

    @staticmethod
    def render_project_details(
        projects
    ):

        if not projects:
            return

        options = {
            str(project["id"]): project["name"]
            for project in projects
        }

        selected = st.selectbox(
            "Select Project",
            options=list(options.keys()),
            format_func=lambda x: options[x]
        )

        project = (
            ProjectService.find_project(
                selected,
                projects
            )
        )

        if project:

            st.subheader(
                project["name"]
            )

            st.json(project)

    @classmethod
    def render(
        cls
    ):

        st.title(
            "📁 Project Management"
        )

        projects = (
            st.session_state.get(
                "projects_data",
                []
            )
        )

        cls.render_portfolio_metrics(
            projects
        )

        st.divider()

        tab1, tab2, tab3 = st.tabs([
            "Portfolio",
            "Project Details",
            "Create Project"
        ])

        with tab1:

            cls.render_project_table(
                projects
            )

        with tab2:

            cls.render_project_details(
                projects
            )

        with tab3:

            cls.render_create_project_form()
