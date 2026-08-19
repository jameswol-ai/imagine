"""
IMAGINE Projects Streamlit UI.
"""

from __future__ import annotations

import asyncio
from datetime import date
from typing import Any

import streamlit as st


def _run_async(coro: Any) -> Any:
    """
    Execute an async service operation from Streamlit.

    Streamlit executes this renderer synchronously, while the
    Projects service uses AsyncSession and async methods.
    """

    try:
        return asyncio.run(coro)

    except RuntimeError as exc:

        if "asyncio.run() cannot be called" not in str(exc):
            raise

        loop = asyncio.new_event_loop()

        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()


def _get_async_session_factory():
    """
    Resolve the project's AsyncSession factory without changing
    the existing service contract.
    """

    try:
        from database.async_connection import (
            AsyncSessionLocal,
        )

        return AsyncSessionLocal

    except ImportError:

        st.error(
            "Projects requires an asynchronous database session "
            "factory at database.async_connection.AsyncSessionLocal."
        )

        st.info(
            "The existing ProjectService uses AsyncSession and "
            "cannot safely be called with the synchronous SessionLocal."
        )

        return None


def _load_services():
    from projects.projects.dashboard import (
        aggregate_project_metrics,
    )

    from projects.projects.schemas import (
        ProjectCreate,
        ProjectStatus,
        ProjectUpdate,
    )

    from projects.projects.service import (
        ProjectService,
    )

    return (
        ProjectService,
        ProjectCreate,
        ProjectUpdate,
        ProjectStatus,
        aggregate_project_metrics,
    )


async def _list_projects():
    (
        ProjectService,
        _,
        _,
        _,
        _,
    ) = _load_services()

    session_factory = _get_async_session_factory()

    if session_factory is None:
        return []

    async with session_factory() as db:

        return await ProjectService.get_all(
            db=db,
            skip=0,
            limit=1000,
        )


async def _create_project(data):
    (
        ProjectService,
        ProjectCreate,
        _,
        _,
        _,
    ) = _load_services()

    session_factory = _get_async_session_factory()

    if session_factory is None:
        return None

    payload = ProjectCreate(
        **data
    )

    async with session_factory() as db:

        return await ProjectService.create(
            db=db,
            data=payload,
        )


async def _delete_project(project_id):
    (
        ProjectService,
        _,
        _,
        _,
        _,
    ) = _load_services()

    session_factory = _get_async_session_factory()

    if session_factory is None:
        return False

    async with session_factory() as db:

        return await ProjectService.delete(
            db=db,
            id=str(project_id),
        )


def _render_project_create_form() -> None:

    st.subheader("Create Project")

    with st.form("projects_create_form"):

        name = st.text_input(
            "Project Name"
        )

        description = st.text_area(
            "Description"
        )

        status = st.selectbox(
            "Status",
            [
                "planning",
                "active",
                "on_hold",
                "completed",
                "cancelled",
            ],
        )

        budget = st.number_input(
            "Budget",
            min_value=0.0,
            step=1000.0,
        )

        progress = st.number_input(
            "Progress (%)",
            min_value=0.0,
            max_value=100.0,
            step=1.0,
        )

        start_date = st.date_input(
            "Start Date",
            value=date.today(),
        )

        end_date = st.date_input(
            "End Date",
            value=date.today(),
        )

        submitted = st.form_submit_button(
            "Create Project",
            use_container_width=True,
        )

    if not submitted:
        return

    if not name.strip():

        st.error(
            "Project name is required."
        )

        return

    try:

        project = _run_async(
            _create_project(
                {
                    "name": name.strip(),
                    "description": (
                        description.strip()
                        or None
                    ),
                    "status": status,
                    "budget": budget,
                    "progress": progress,
                    "start_date": start_date,
                    "end_date": end_date,
                }
            )
        )

        if project is not None:

            st.success(
                f"Project '{project.name}' created."
            )

            st.rerun()

    except Exception as exc:

        st.error(
            "Project could not be created."
        )

        with st.expander(
            "Complete error",
            expanded=True,
        ):
            st.exception(exc)


def render_projects() -> None:
    """
    Zero-argument Streamlit renderer for Projects.
    """

    st.title("Projects")

    st.caption(
        "Project lifecycle, budgets, progress and project records."
    )

    try:

        projects = _run_async(
            _list_projects()
        )

    except Exception as exc:

        st.error(
            "Projects could not be loaded."
        )

        with st.expander(
            "Complete error",
            expanded=True,
        ):
            st.exception(exc)

        return

    total = len(projects)

    active = sum(
        getattr(project.status, "value", project.status)
        == "active"
        for project in projects
    )

    completed = sum(
        getattr(project.status, "value", project.status)
        == "completed"
        for project in projects
    )

    budget = sum(
        float(
            getattr(project, "budget", 0) or 0
        )
        for project in projects
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Projects",
            total,
        )

    with c2:
        st.metric(
            "Active",
            active,
        )

    with c3:
        st.metric(
            "Completed",
            completed,
        )

    with c4:
        st.metric(
            "Total Budget",
            f"{budget:,.2f}",
        )

    st.divider()

    tab1, tab2 = st.tabs(
        [
            "Projects",
            "Create Project",
        ]
    )

    with tab1:

        if not projects:

            st.info(
                "No projects have been created yet."
            )

        else:

            rows = []

            for project in projects:

                rows.append(
                    {
                        "ID": str(project.id),
                        "Name": project.name,
                        "Status": getattr(
                            project.status,
                            "value",
                            project.status,
                        ),
                        "Budget": project.budget,
                        "Progress": project.progress,
                        "Start Date": project.start_date,
                        "End Date": project.end_date,
                    }
                )

            st.dataframe(
                rows,
                use_container_width=True,
                hide_index=True,
            )

            project_ids = [
                str(project.id)
                for project in projects
            ]

            selected = st.selectbox(
                "Select Project",
                project_ids,
            )

            if selected:

                if st.button(
                    "Delete Selected Project",
                    key="projects_delete",
                ):

                    try:

                        deleted = _run_async(
                            _delete_project(
                                selected
                            )
                        )

                        if deleted:

                            st.success(
                                "Project deleted."
                            )

                            st.rerun()

                        else:

                            st.warning(
                                "Project was not found."
                            )

                    except Exception as exc:

                        st.error(
                            "Project could not be deleted."
                        )

                        with st.expander(
                            "Complete error",
                            expanded=True,
                        ):
                            st.exception(exc)

    with tab2:

        _render_project_create_form()