"""
IMAGINE
Projects Streamlit UI.

The Projects service is asynchronous and requires AsyncSession.

This module deliberately keeps the Streamlit renderer zero-argument
so it can be registered directly with the IMAGINE application shell.
"""

from __future__ import annotations

import asyncio
import inspect
import os
from datetime import date
from typing import Any

import streamlit as st


# ============================================================
# SAFE VALUE HELPERS
# ============================================================


def _value(
    obj: Any,
    name: str,
    default: Any = None,
) -> Any:
    """Safely read an attribute from an ORM/schema object."""

    try:
        return getattr(
            obj,
            name,
            default,
        )
    except Exception:
        return default


def _enum_value(
    value: Any,
    default: str = "unknown",
) -> str:
    """Normalize enum/string values for Streamlit."""

    if value is None:
        return default

    raw = getattr(
        value,
        "value",
        value,
    )

    if raw is None:
        return default

    return str(raw)


def _display_date(
    value: Any,
) -> str:
    """Safely format date/datetime/string values."""

    if value is None:
        return ""

    try:
        return value.isoformat()
    except Exception:
        return str(value)


def _display_uuid(
    value: Any,
) -> str:
    """Safely display UUID-like identifiers."""

    if value is None:
        return ""

    return str(value)


# ============================================================
# ASYNC EXECUTION
# ============================================================


def _run_async(
    awaitable: Any,
) -> Any:
    """
    Run an async operation from Streamlit.

    Streamlit normally executes the page synchronously.
    This helper also handles environments where an event loop
    already exists.
    """

    if not inspect.isawaitable(awaitable):
        return awaitable

    try:

        return asyncio.run(
            awaitable
        )

    except RuntimeError as exc:

        if (
            "asyncio.run() cannot be called"
            not in str(exc)
        ):
            raise

        loop = asyncio.new_event_loop()

        try:

            return loop.run_until_complete(
                awaitable
            )

        finally:

            loop.close()


# ============================================================
# ASYNC SESSION FACTORY
# ============================================================


def _get_async_session_factory():
    """
    Resolve the repository's async session factory.

    The current repository's database/connection.py exposes
    SessionLocal, not AsyncSessionLocal. Therefore this function
    does not incorrectly substitute the synchronous session.

    When AsyncSessionLocal is added to the database layer, this
    renderer will use it automatically.
    """

    try:

        from database.async_connection import (
            AsyncSessionLocal,
        )

        return AsyncSessionLocal

    except ImportError:

        return None


# ============================================================
# SERVICE LOADING
# ============================================================


def _load_project_dependencies():

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
    )


# ============================================================
# ASYNC SERVICE OPERATIONS
# ============================================================


async def _list_projects():

    (
        ProjectService,
        _,
        _,
        _,
    ) = _load_project_dependencies()

    session_factory = (
        _get_async_session_factory()
    )

    if session_factory is None:

        raise RuntimeError(
            "Projects requires "
            "database.async_connection.AsyncSessionLocal. "
            "The current repository only exposes "
            "database.connection.SessionLocal."
        )

    async with session_factory() as db:

        return await ProjectService.get_all(
            db=db,
            skip=0,
            limit=1000,
        )


async def _create_project(
    data: dict[str, Any],
):

    (
        ProjectService,
        ProjectCreate,
        _,
        _,
    ) = _load_project_dependencies()

    session_factory = (
        _get_async_session_factory()
    )

    if session_factory is None:

        raise RuntimeError(
            "AsyncSessionLocal is not available."
        )

    payload = ProjectCreate(
        **data
    )

    async with session_factory() as db:

        return await ProjectService.create(
            db=db,
            data=payload,
        )


async def _update_project(
    project_id: str,
    data: dict[str, Any],
):

    (
        ProjectService,
        _,
        ProjectUpdate,
        _,
    ) = _load_project_dependencies()

    session_factory = (
        _get_async_session_factory()
    )

    if session_factory is None:

        raise RuntimeError(
            "AsyncSessionLocal is not available."
        )

    payload = ProjectUpdate(
        **data
    )

    async with session_factory() as db:

        return await ProjectService.update(
            db=db,
            id=project_id,
            data=payload,
        )


async def _delete_project(
    project_id: str,
):

    (
        ProjectService,
        _,
        _,
        _,
    ) = _load_project_dependencies()

    session_factory = (
        _get_async_session_factory()
    )

    if session_factory is None:

        raise RuntimeError(
            "AsyncSessionLocal is not available."
        )

    async with session_factory() as db:

        return await ProjectService.delete(
            db=db,
            id=project_id,
        )


# ============================================================
# STATUS OPTIONS
# ============================================================


def _status_options(
    ProjectStatus,
) -> list[Any]:
    """
    Return enum members without assuming enum naming style.
    """

    try:

        values = list(
            ProjectStatus
        )

        if values:
            return values

    except Exception:
        pass

    return []


def _status_label(
    value: Any,
) -> str:

    return _enum_value(
        value,
        "unknown",
    ).replace(
        "_",
        " ",
    ).title()


# ============================================================
# CREATE FORM
# ============================================================


def _render_create_form() -> None:

    (
        _,
        ProjectCreate,
        _,
        ProjectStatus,
    ) = _load_project_dependencies()

    st.subheader(
        "Create Project"
    )

    statuses = _status_options(
        ProjectStatus
    )

    if statuses:

        status_values = [
            getattr(
                status,
                "value",
                str(status),
            )
            for status in statuses
        ]

    else:

        status_values = [
            "planning",
            "active",
            "on_hold",
            "completed",
            "cancelled",
        ]

    with st.form(
        "projects_create_form",
        clear_on_submit=False,
    ):

        name = st.text_input(
            "Project Name"
        )

        description = st.text_area(
            "Description"
        )

        selected_status = st.selectbox(
            "Status",
            status_values,
        )

        budget = st.number_input(
            "Budget",
            min_value=0.0,
            value=0.0,
            step=1000.0,
        )

        progress = st.number_input(
            "Progress (%)",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=1.0,
        )

        start_date = st.date_input(
            "Start Date",
            value=None,
        )

        end_date = st.date_input(
            "End Date",
            value=None,
        )

        client_id = st.text_input(
            "Client ID",
            help="Optional UUID of the client organization.",
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

    data: dict[str, Any] = {
        "name": name.strip(),
        "description": (
            description.strip()
            or None
        ),
        "status": selected_status,
        "budget": float(budget),
        "progress": float(progress),
        "start_date": (
            start_date
            if isinstance(
                start_date,
                date,
            )
            else None
        ),
        "end_date": (
            end_date
            if isinstance(
                end_date,
                date,
            )
            else None
        ),
    }

    if client_id.strip():

        data["client_id"] = (
            client_id.strip()
        )

    try:

        project = _run_async(
            _create_project(
                data
            )
        )

        st.success(
            "Project created successfully."
        )

        st.session_state[
            "projects_last_created"
        ] = _display_uuid(
            _value(
                project,
                "id",
            )
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

            st.exception(
                exc
            )


# ============================================================
# PROJECT TABLE
# ============================================================


def _render_project_list(
    projects: list[Any],
) -> None:

    st.subheader(
        "Projects"
    )

    if not projects:

        st.info(
            "No projects have been created yet."
        )

        return

    rows = []

    for project in projects:

        rows.append(
            {
                "ID": _display_uuid(
                    _value(
                        project,
                        "id",
                    )
                ),
                "Name": _value(
                    project,
                    "name",
                    "",
                ),
                "Status": _status_label(
                    _value(
                        project,
                        "status",
                    )
                ),
                "Budget": float(
                    _value(
                        project,
                        "budget",
                        0.0,
                    )
                    or 0.0
                ),
                "Progress": float(
                    _value(
                        project,
                        "progress",
                        0.0,
                    )
                    or 0.0
                ),
                "Start Date": _display_date(
                    _value(
                        project,
                        "start_date",
                    )
                ),
                "End Date": _display_date(
                    _value(
                        project,
                        "end_date",
                    )
                ),
            }
        )

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# EDIT / DELETE
# ============================================================


def _render_project_actions(
    projects: list[Any],
) -> None:

    if not projects:
        return

    ids = [
        _display_uuid(
            _value(
                project,
                "id",
            )
        )
        for project in projects
    ]

    valid_ids = [
        project_id
        for project_id in ids
        if project_id
    ]

    if not valid_ids:
        return

    st.subheader(
        "Project Actions"
    )

    selected_id = st.selectbox(
        "Project",
        valid_ids,
        key="projects_selected_id",
    )

    selected_project = next(
        (
            project
            for project in projects
            if _display_uuid(
                _value(
                    project,
                    "id",
                )
            )
            == selected_id
        ),
        None,
    )

    if selected_project is None:

        st.warning(
            "The selected project is no longer available."
        )

        return

    (
        _,
        _,
        ProjectUpdate,
        ProjectStatus,
    ) = _load_project_dependencies()

    current_name = _value(
        selected_project,
        "name",
        "",
    )

    current_description = _value(
        selected_project,
        "description",
        "",
    )

    current_budget = float(
        _value(
            selected_project,
            "budget",
            0.0,
        )
        or 0.0
    )

    current_progress = float(
        _value(
            selected_project,
            "progress",
            0.0,
        )
        or 0.0
    )

    current_status = _enum_value(
        _value(
            selected_project,
            "status",
        ),
        "planning",
    )

    statuses = [
        getattr(
            status,
            "value",
            str(status),
        )
        for status in _status_options(
            ProjectStatus
        )
    ]

    if current_status not in statuses:

        statuses.insert(
            0,
            current_status,
        )

    with st.form(
        "projects_update_form"
    ):

        name = st.text_input(
            "Name",
            value=str(
                current_name
            ),
        )

        description = st.text_area(
            "Description",
            value=str(
                current_description
                or ""
            ),
        )

        status = st.selectbox(
            "Status",
            statuses,
            index=statuses.index(
                current_status
            ),
        )

        budget = st.number_input(
            "Budget",
            min_value=0.0,
            value=current_budget,
            step=1000.0,
        )

        progress = st.number_input(
            "Progress (%)",
            min_value=0.0,
            max_value=100.0,
            value=max(
                0.0,
                min(
                    100.0,
                    current_progress,
                ),
            ),
            step=1.0,
        )

        update_submitted = (
            st.form_submit_button(
                "Save Changes",
                use_container_width=True,
            )
        )

    if update_submitted:

        if not name.strip():

            st.error(
                "Project name is required."
            )

            return

        try:

            updated = _run_async(
                _update_project(
                    selected_id,
                    {
                        "name": name.strip(),
                        "description": (
                            description.strip()
                            or None
                        ),
                        "status": status,
                        "budget": float(
                            budget
                        ),
                        "progress": float(
                            progress
                        ),
                    },
                )
            )

            if updated is None:

                st.warning(
                    "Project was not found."
                )

            else:

                st.success(
                    "Project updated successfully."
                )

                st.rerun()

        except Exception as exc:

            st.error(
                "Project could not be updated."
            )

            with st.expander(
                "Complete error",
                expanded=True,
            ):
                st.exception(exc)

    if st.button(
        "Delete Selected Project",
        key="projects_delete_selected",
        use_container_width=True,
    ):

        try:

            deleted = _run_async(
                _delete_project(
                    selected_id
                )
            )

            if deleted:

                st.success(
                    "Project deleted successfully."
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


# ============================================================
# MAIN RENDERER
# ============================================================


def render_projects() -> None:
    """
    Zero-argument Streamlit renderer.
    """

    st.title(
        "Projects"
    )

    st.caption(
        "Project lifecycle, budgets, progress and project records."
    )

    session_factory = (
        _get_async_session_factory()
    )

    if session_factory is None:

        st.error(
            "Projects cannot connect to the database yet."
        )

        st.warning(
            "ProjectService requires AsyncSession, "
            "but the current database layer exposes "
            "only synchronous SessionLocal."
        )

        st.info(
            "The Projects service contract has been preserved. "
            "Add database.async_connection.AsyncSessionLocal "
            "before enabling database operations here."
        )

        return

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

    projects = list(
        projects or []
    )

    total = len(
        projects
    )

    active = sum(
        _enum_value(
            _value(
                project,
                "status",
            )
        )
        == "active"
        for project in projects
    )

    completed = sum(
        _enum_value(
            _value(
                project,
                "status",
            )
        )
        == "completed"
        for project in projects
    )

    budget = sum(
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
            f"{budget:,.2f}",
        )

    st.divider()

    tab1, tab2, tab3 = st.tabs(
        [
            "Project List",
            "Create Project",
            "Manage Project",
        ]
    )

    with tab1:
        _render_project_list(
            projects
        )

    with tab2:
        _render_create_form()

    with tab3:
        _render_project_actions(
            projects
        )