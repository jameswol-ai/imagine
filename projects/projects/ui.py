from __future__ import annotations

import asyncio
import traceback
from typing import Any, Awaitable, Callable

import streamlit as st

# ============================================================
# DATABASE / ASYNC SESSION
# ============================================================

from database.connection import AsyncSessionLocal

# ============================================================
# SQLALCHEMY MODEL REGISTRATION
#
# Import every model referenced by Project, Approval, and
# Revision relationships before SQLAlchemy configures mappers.
#
# These imports intentionally remain unused in this module.
# They exist to register the mapped classes with the shared
# SQLAlchemy declarative registry.
# ============================================================

from database.models.organization import Organization  # noqa: F401
from database.models.user import User  # noqa: F401

from projects.approvals.models import Approval  # noqa: F401
from projects.revisions.models import Revision  # noqa: F401

from projects.projects.models import Project  # noqa: F401

# ============================================================
# PROJECT SERVICE
# ============================================================

from projects.projects.service import ProjectService

# ============================================================
# PROJECT SCHEMAS
# ============================================================

from projects.projects.schemas import (
    ProjectCreate,
    ProjectUpdate,
)


# ============================================================
# ASYNC RUNNER
# ============================================================

def _run_async(
    operation: Callable[[], Awaitable[Any]],
) -> Any:
    """
    Execute an async operation from the synchronous Streamlit
    renderer.

    Streamlit invokes the renderer synchronously, while the
    Projects service layer remains asynchronous.
    """

    return asyncio.run(operation())


# ============================================================
# SESSION FACTORY
# ============================================================

def _get_async_session():
    """
    Return the application's shared asynchronous SQLAlchemy
    session factory.

    The Projects service requires AsyncSession, so this must
    not be replaced with the synchronous SessionLocal.
    """

    if AsyncSessionLocal is None:
        raise RuntimeError(
            "The asynchronous database session factory "
            "could not be imported."
        )

    return AsyncSessionLocal


# ============================================================
# SERVICE OPERATIONS
# ============================================================

async def _get_projects() -> list[Any]:
    """
    Retrieve all projects using the existing asynchronous
    ProjectService contract.
    """

    session_factory = _get_async_session()

    async with session_factory() as db:
        return await ProjectService.get_all(db=db)


async def _create_project(
    data: ProjectCreate,
) -> Any:
    """
    Create a project using the existing asynchronous service
    contract.
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
) -> Any:
    """
    Update a project using the existing asynchronous service
    contract.
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
) -> bool:
    """
    Delete a project using the existing asynchronous service
    contract.
    """

    session_factory = _get_async_session()

    async with session_factory() as db:
        return await ProjectService.delete(
            db=db,
            id=project_id,
        )


# ============================================================
# STREAMLIT RENDERER
# ============================================================

def render_projects() -> None:
    """
    Zero-argument Streamlit renderer for the Projects module.

    The renderer intentionally owns no database/session state.
    It obtains a fresh async session for each service operation.
    """

    st.title("Projects")
    st.caption("Project lifecycle and project records.")

    # --------------------------------------------------------
    # LOAD PROJECTS
    # --------------------------------------------------------

    try:
        projects = _run_async(_get_projects)

    except Exception:
        st.error(
            "The Projects module could not load its data."
        )

        with st.expander(
            "Complete Projects error",
            expanded=True,
        ):
            st.exception(
                RuntimeError(
                    "Failed to load Projects data."
                )
            )

            st.code(
                traceback.format_exc(),
                language="text",
            )

        return

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    total_projects = len(projects)

    st.metric(
        "Projects",
        total_projects,
    )

    st.divider()

    # --------------------------------------------------------
    # CREATE
    # --------------------------------------------------------

    with st.expander(
        "Create Project",
        expanded=False,
    ):
        with st.form(
            "projects_create_form",
            clear_on_submit=True,
        ):
            name = st.text_input(
                "Project name",
                key="projects_create_name",
            )

            description = st.text_area(
                "Description",
                key="projects_create_description",
            )

            status = st.text_input(
                "Status",
                value="planning",
                key="projects_create_status",
            )

            budget = st.number_input(
                "Budget",
                min_value=0.0,
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
                "Start date",
                key="projects_create_start_date",
            )

            end_date = st.date_input(
                "End date",
                key="projects_create_end_date",
            )

            submitted = st.form_submit_button(
                "Create Project",
                type="primary",
            )

        if submitted:

            if not name.strip():
                st.warning(
                    "Project name is required."
                )

            else:
                try:
                    data = ProjectCreate(
                        name=name.strip(),
                        description=description.strip()
                        or None,
                        status=status.strip()
                        or "planning",
                        budget=budget,
                        progress=progress,
                        start_date=start_date,
                        end_date=end_date,
                    )

                    _run_async(
                        lambda: _create_project(data)
                    )

                    st.success(
                        "Project created successfully."
                    )

                    st.rerun()

                except Exception:
                    st.error(
                        "The project could not be created."
                    )

                    with st.expander(
                        "Create error",
                        expanded=True,
                    ):
                        st.code(
                            traceback.format_exc(),
                            language="text",
                        )

    # --------------------------------------------------------
    # PROJECT LIST
    # --------------------------------------------------------

    if not projects:
        st.info(
            "No projects have been created yet."
        )
        return

    for project in projects:

        project_id = str(
            getattr(project, "id", "")
        )

        project_name = getattr(
            project,
            "name",
            "Unnamed project",
        )

        with st.container(
            border=True,
        ):
            st.subheader(
                str(project_name)
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                st.write(
                    f"**ID:** {project_id}"
                )

            with col2:
                st.write(
                    f"**Status:** "
                    f"{getattr(project, 'status', 'N/A')}"
                )

            with col3:
                st.write(
                    f"**Progress:** "
                    f"{getattr(project, 'progress', 0)}%"
                )

            description = getattr(
                project,
                "description",
                None,
            )

            if description:
                st.write(description)

            # ------------------------------------------------
            # EDIT
            # ------------------------------------------------

            with st.expander(
                "Edit",
                expanded=False,
            ):
                edit_name = st.text_input(
                    "Project name",
                    value=str(
                        getattr(
                            project,
                            "name",
                            "",
                        )
                    ),
                    key=f"projects_edit_name_{project_id}",
                )

                edit_description = st.text_area(
                    "Description",
                    value=str(
                        getattr(
                            project,
                            "description",
                            ""
                        )
                        or ""
                    ),
                    key=f"projects_edit_description_{project_id}",
                )

                edit_status = st.text_input(
                    "Status",
                    value=str(
                        getattr(
                            project,
                            "status",
                            "planning",
                        )
                    ),
                    key=f"projects_edit_status_{project_id}",
                )

                edit_budget = st.number_input(
                    "Budget",
                    min_value=0.0,
                    value=float(
                        getattr(
                            project,
                            "budget",
                            0,
                        )
                        or 0
                    ),
                    step=1000.0,
                    key=f"projects_edit_budget_{project_id}",
                )

                edit_progress = st.number_input(
                    "Progress (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(
                        getattr(
                            project,
                            "progress",
                            0,
                        )
                        or 0
                    ),
                    step=1.0,
                    key=f"projects_edit_progress_{project_id}",
                )

                if st.button(
                    "Save Changes",
                    key=f"projects_save_{project_id}",
                    type="primary",
                ):
                    try:
                        data = ProjectUpdate(
                            name=edit_name.strip(),
                            description=(
                                edit_description.strip()
                                or None
                            ),
                            status=(
                                edit_status.strip()
                                or "planning"
                            ),
                            budget=edit_budget,
                            progress=edit_progress,
                        )

                        _run_async(
                            lambda: _update_project(
                                project_id,
                                data,
                            )
                        )

                        st.success(
                            "Project updated successfully."
                        )

                        st.rerun()

                    except Exception:
                        st.error(
                            "The project could not be updated."
                        )

                        with st.expander(
                            "Update error",
                            expanded=True,
                        ):
                            st.code(
                                traceback.format_exc(),
                                language="text",
                            )

            # ------------------------------------------------
            # DELETE
            # ------------------------------------------------

            if st.button(
                "Delete Project",
                key=f"projects_delete_{project_id}",
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
                        st.rerun()
                    else:
                        st.warning(
                            "Project was not found."
                        )

                except Exception:
                    st.error(
                        "The project could not be deleted."
                    )

                    with st.expander(
                        "Delete error",
                        expanded=True,
                    ):
                        st.code(
                            traceback.format_exc(),
                            language="text",
                        )