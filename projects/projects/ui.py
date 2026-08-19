"""
IMAGINE
Projects Streamlit UI.

Presentation adapter for the existing asynchronous
ProjectService.

The Streamlit application calls:

    render_projects()

The existing ProjectService remains asynchronous and
is not modified by this module.
"""

from __future__ import annotations

import asyncio
from datetime import date
from typing import Any, Awaitable, Callable

import streamlit as st

from .models import ProjectStatus
from .schemas import ProjectCreate, ProjectUpdate
from .service import ProjectService


# ============================================================
# ASYNC BRIDGE
# ============================================================


def _run_async(
    operation: Callable[[], Awaitable[Any]],
) -> Any:
    """
    Execute one async ProjectService operation from Streamlit.

    Streamlit renderers are synchronous, while ProjectService
    methods are asynchronous.
    """

    try:
        return asyncio.run(operation())

    except RuntimeError as exc:
        if "asyncio.run()" not in str(exc):
            raise

        loop = asyncio.new_event_loop()

        try:
            return loop.run_until_complete(
                operation()
            )
        finally:
            loop.close()


# ============================================================
# DATABASE SESSION
# ============================================================


def _get_async_session():
    """
    Obtain the repository's async database session factory.

    This import remains local so that failure in the database
    layer does not prevent the IMAGINE application shell from
    loading.
    """

    try:
        from database.connection import (
            AsyncSessionLocal,
        )

        return AsyncSessionLocal

    except ImportError:

        try:
            from database.connection import (
                async_sessionmaker,
            )

            return async_sessionmaker

        except ImportError as exc:
            raise RuntimeError(
                "The asynchronous database session factory "
                "could not be imported."
            ) from exc


# ============================================================
# SESSION FACTORY ADAPTER
# ============================================================


async def _get_projects(
    skip: int = 0,
    limit: int = 100,
):
    """
    Load projects using the existing ProjectService.
    """

    session_factory = _get_async_session()

    async with session_factory() as db:

        return await ProjectService.get_all(
            db=db,
            skip=skip,
            limit=limit,
        )


async def _create_project(
    data: ProjectCreate,
):
    """
    Create a project using the existing service.
    """

    session_factory = _get_async_session()

    async with session_factory() as db:

        return await ProjectService.create(
            db=db,
            data=data,
        )


async def _update_project(
    project_id: str,
    data: ProjectUpdate,
):
    """
    Update a project using the existing service.
    """

    session_factory = _get_async_session()

    async with session_factory() as db:

        return await ProjectService.update(
            db=db,
            id=project_id,
            data=data,
        )


async def _delete_project(
    project_id: str,
):
    """
    Delete a project using the existing service.
    """

    session_factory = _get_async_session()

    async with session_factory() as db:

        return await ProjectService.delete(
            db=db,
            id=project_id,
        )


async def _get_dashboard_metrics():
    """
    Load dashboard metrics using the existing service.
    """

    session_factory = _get_async_session()

    async with session_factory() as db:

        return await ProjectService.get_dashboard_metrics(
            db=db,
        )


# ============================================================
# SAFE VALUE HELPERS
# ============================================================


def _value(
    obj: Any,
    field: str,
    default: Any = None,
) -> Any:
    """Safely read an object attribute."""

    return getattr(
        obj,
        field,
        default,
    )


def _project_id(
    project: Any,
) -> str:
    """Return a safe string representation of a project ID."""

    value = _value(
        project,
        "id",
        "",
    )

    return str(value)


def _status_value(
    status: Any,
) -> str:
    """Normalize enum/string project status values."""

    if status is None:
        return ProjectStatus.PLANNING.value

    value = getattr(
        status,
        "value",
        status,
    )

    return str(value)


def _status_options() -> list[str]:
    """Return status values from the actual model enum."""

    return [
        status.value
        for status in ProjectStatus
    ]


# ============================================================
# SUMMARY
# ============================================================


def _render_summary(
    projects: list[Any],
) -> None:
    """Render project summary metrics."""

    total = len(projects)

    active = sum(
        1
        for project in projects
        if _status_value(
            _value(project, "status")
        )
        == ProjectStatus.ACTIVE.value
    )

    completed = sum(
        1
        for project in projects
        if _status_value(
            _value(project, "status")
        )
        == ProjectStatus.COMPLETED.value
    )

    total_budget = sum(
        float(
            _value(
                project,
                "budget",
                0.0,
            )
            or 0.0
        )
        for project in projects
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Projects",
            total,
        )

    with col2:
        st.metric(
            "Active",
            active,
        )

    with col3:
        st.metric(
            "Completed",
            completed,
        )

    with col4:
        st.metric(
            "Total Budget",
            f"{total_budget:,.2f}",
        )


# ============================================================
# CREATE FORM
# ============================================================


def _render_create_form() -> None:
    """Render the project creation form."""

    st.subheader(
        "Create Project"
    )

    with st.form(
        "projects_create_form",
        clear_on_submit=True,
    ):

        name = st.text_input(
            "Project Name",
            key="projects_create_name",
        )

        description = st.text_area(
            "Description",
            key="projects_create_description",
        )

        status = st.selectbox(
            "Status",
            options=_status_options(),
            index=0,
            key="projects_create_status",
        )

        budget = st.number_input(
            "Budget",
            min_value=0.0,
            value=0.0,
            step=1000.0,
            key="projects_create_budget",
        )

        progress = st.number_input(
            "Progress (%)",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=1.0,
            key="projects_create_progress",
        )

        start_date = st.date_input(
            "Start Date",
            value=None,
            key="projects_create_start_date",
        )

        end_date = st.date_input(
            "End Date",
            value=None,
            key="projects_create_end_date",
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

        data = ProjectCreate(
            name=name.strip(),
            description=(
                description.strip()
                or None
            ),
            status=status,
            budget=float(budget),
            progress=float(progress),
            start_date=(
                start_date
                if isinstance(start_date, date)
                else None
            ),
            end_date=(
                end_date
                if isinstance(end_date, date)
                else None
            ),
        )

        _run_async(
            lambda: _create_project(data)
        )

        st.success(
            "Project created successfully."
        )

        st.session_state[
            "projects_refresh"
        ] = True

        st.rerun()

    except Exception as exc:

        st.error(
            "Project could not be created."
        )

        with st.expander(
            "Error details",
            expanded=False,
        ):
            st.exception(exc)


# ============================================================
# EDIT
# ============================================================


def _render_edit_form(
    project: Any,
) -> None:
    """Render the edit form for one project."""

    project_id = _project_id(
        project
    )

    with st.form(
        f"projects_edit_form_{project_id}",
    ):

        name = st.text_input(
            "Project Name",
            value=str(
                _value(
                    project,
                    "name",
                    "",
                )
                or ""
            ),
        )

        description = st.text_area(
            "Description",
            value=str(
                _value(
                    project,
                    "description",
                    "",
                )
                or ""
            ),
        )

        current_status = _status_value(
            _value(project, "status")
        )

        options = _status_options()

        status_index = (
            options.index(current_status)
            if current_status in options
            else 0
        )

        status = st.selectbox(
            "Status",
            options=options,
            index=status_index,
        )

        budget = st.number_input(
            "Budget",
            min_value=0.0,
            value=float(
                _value(
                    project,
                    "budget",
                    0.0,
                )
                or 0.0
            ),
        )

        progress = st.number_input(
            "Progress (%)",
            min_value=0.0,
            max_value=100.0,
            value=float(
                _value(
                    project,
                    "progress",
                    0.0,
                )
                or 0.0
            ),
        )

        submitted = st.form_submit_button(
            "Save Changes",
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

        data = ProjectUpdate(
            name=name.strip(),
            description=(
                description.strip()
                or None
            ),
            status=status,
            budget=float(budget),
            progress=float(progress),
        )

        updated = _run_async(
            lambda: _update_project(
                project_id,
                data,
            )
        )

        if updated is None:

            st.error(
                "The project no longer exists."
            )

            return

        st.success(
            "Project updated successfully."
        )

        st.session_state[
            "projects_edit_id"
        ] = None

        st.rerun()

    except Exception as exc:

        st.error(
            "Project could not be updated."
        )

        with st.expander(
            "Error details",
            expanded=False,
        ):
            st.exception(exc)


# ============================================================
# PROJECT LIST
# ============================================================


def _render_project_list(
    projects: list[Any],
) -> None:
    """Render the project records."""

    st.subheader(
        "Projects"
    )

    if not projects:

        st.info(
            "No projects have been created yet."
        )

        return

    for project in projects:

        project_id = _project_id(
            project
        )

        name = _value(
            project,
            "name",
            "Unnamed Project",
        )

        description = _value(
            project,
            "description",
            "",
        )

        status = _status_value(
            _value(project, "status")
        )

        budget = float(
            _value(
                project,
                "budget",
                0.0,
            )
            or 0.0
        )

        progress = float(
            _value(
                project,
                "progress",
                0.0,
            )
            or 0.0
        )

        with st.container(
            border=True,
        ):

            col1, col2, col3 = st.columns(
                [3, 2, 1]
            )

            with col1:

                st.markdown(
                    f"### {name}"
                )

                if description:

                    st.caption(
                        description
                    )

            with col2:

                st.write(
                    f"Status: **{status}**"
                )

                st.write(
                    f"Budget: {budget:,.2f}"
                )

                st.progress(
                    min(
                        max(
                            progress / 100.0,
                            0.0,
                        ),
                        1.0,
                    )
                )

                st.caption(
                    f"Progress: {progress:.1f}%"
                )

            with col3:

                if st.button(
                    "Edit",
                    key=f"projects_edit_{project_id}",
                    use_container_width=True,
                ):

                    st.session_state[
                        "projects_edit_id"
                    ] = project_id

                    st.rerun()

                if st.button(
                    "Delete",
                    key=f"projects_delete_{project_id}",
                    use_container_width=True,
                ):

                    st.session_state[
                        "projects_delete_id"
                    ] = project_id

                    st.rerun()

            if (
                st.session_state.get(
                    "projects_edit_id"
                )
                == project_id
            ):

                _render_edit_form(
                    project
                )

            if (
                st.session_state.get(
                    "projects_delete_id"
                )
                == project_id
            ):

                st.warning(
                    "Delete this project?"
                )

                confirm_col1, confirm_col2 = st.columns(2)

                with confirm_col1:

                    if st.button(
                        "Confirm Delete",
                        key=f"projects_confirm_delete_{project_id}",
                        use_container_width=True,
                    ):

                        try:

                            deleted = _run_async(
                                lambda: _delete_project(
                                    project_id
                                )
                            )

                            if deleted:

                                st.success(
                                    "Project deleted successfully."
                                )

                            else:

                                st.warning(
                                    "Project was not found."
                                )

                            st.session_state[
                                "projects_delete_id"
                            ] = None

                            st.rerun()

                        except Exception as exc:

                            st.error(
                                "Project could not be deleted."
                            )

                            with st.expander(
                                "Error details",
                                expanded=False,
                            ):
                                st.exception(exc)

                with confirm_col2:

                    if st.button(
                        "Cancel",
                        key=f"projects_cancel_delete_{project_id}",
                        use_container_width=True,
                    ):

                        st.session_state[
                            "projects_delete_id"
                        ] = None

                        st.rerun()


# ============================================================
# MAIN RENDERER
# ============================================================


def render_projects() -> None:
    """
    Zero-argument Streamlit renderer.

    This is the function expected by streamlit_app.py.
    """

    st.title(
        "Projects"
    )

    st.caption(
        "Project lifecycle and project records."
    )

    try:

        projects = _run_async(
            lambda: _get_projects(
                skip=0,
                limit=1000,
            )
        )

    except Exception as exc:

        st.error(
            "The Projects module could not load its data."
        )

        with st.expander(
            "Complete Projects error",
            expanded=True,
        ):
            st.exception(exc)

        return

    if projects is None:
        projects = []

    _render_summary(
        projects
    )

    st.divider()

    create_col, refresh_col = st.columns(2)

    with create_col:

        _render_create_form()

    with refresh_col:

        st.subheader(
            "Data"
        )

        if st.button(
            "Refresh Projects",
            use_container_width=True,
        ):

            st.session_state[
                "projects_edit_id"
            ] = None

            st.session_state[
                "projects_delete_id"
            ] = None

            st.rerun()

    st.divider()

    _render_project_list(
        projects
    )