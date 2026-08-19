"""
IMAGINE
Project Workflows Streamlit UI.
"""

from __future__ import annotations

from typing import Any

import streamlit as st


def _get_attr(
    obj: Any,
    name: str,
    default: Any = None,
) -> Any:

    return getattr(
        obj,
        name,
        default,
    )


def _status_value(
    value: Any,
) -> str:

    if value is None:
        return "unknown"

    return str(
        getattr(
            value,
            "value",
            value,
        )
    )


def _session():

    from database.connection import (
        SessionLocal,
    )

    return SessionLocal()


def render_workflows() -> None:

    st.title(
        "Workflows"
    )

    st.caption(
        "Project workflow steps and assignments."
    )

    try:

        from projects.workflows.schemas import (
            WorkflowCreate,
        )

        from projects.workflows.service import (
            create_workflow,
            list_workflows,
        )

    except Exception as exc:

        st.error(
            "Workflows could not be loaded."
        )

        with st.expander(
            "Complete import traceback",
            expanded=True,
        ):
            st.exception(exc)

        return

    project_id = st.number_input(
        "Project ID",
        min_value=1,
        value=1,
        step=1,
        key="workflows_project_id",
    )

    st.subheader(
        "Create Workflow Step"
    )

    with st.form(
        "workflows_create_form"
    ):

        step = st.text_input(
            "Workflow Step"
        )

        assigned_to = st.number_input(
            "Assigned To User ID",
            min_value=0,
            value=0,
            step=1,
        )

        submitted = st.form_submit_button(
            "Create Workflow Step",
            use_container_width=True,
        )

    if submitted:

        if not step.strip():

            st.error(
                "Workflow step is required."
            )

        else:

            db = None

            try:

                assigned_value = (
                    int(assigned_to)
                    if int(assigned_to) > 0
                    else None
                )

                payload = WorkflowCreate(
                    project_id=int(
                        project_id
                    ),
                    step=step.strip(),
                    assigned_to=assigned_value,
                )

                db = _session()

                create_workflow(
                    db=db,
                    project_id=payload.project_id,
                    step=payload.step,
                    assigned_to=payload.assigned_to,
                )

                st.success(
                    "Workflow step created successfully."
                )

                st.rerun()

            except Exception as exc:

                if db is not None:

                    db.rollback()

                st.error(
                    "Workflow step could not be created."
                )

                with st.expander(
                    "Complete error",
                    expanded=True,
                ):
                    st.exception(exc)

            finally:

                if db is not None:

                    db.close()

    st.divider()

    db = None

    try:

        db = _session()

        workflows = list_workflows(
            db=db,
            project_id=int(
                project_id
            ),
        )

        workflows = list(
            workflows or []
        )

        st.subheader(
            "Workflow Records"
        )

        if not workflows:

            st.info(
                "No workflow steps exist for this project."
            )

            return

        rows = []

        for workflow in workflows:

            rows.append(
                {
                    "ID": _get_attr(
                        workflow,
                        "id",
                    ),
                    "Project ID": _get_attr(
                        workflow,
                        "project_id",
                    ),
                    "Step": _get_attr(
                        workflow,
                        "step",
                        "",
                    ),
                    "Status": _status_value(
                        _get_attr(
                            workflow,
                            "status",
                        )
                    ),
                    "Assigned To": _get_attr(
                        workflow,
                        "assigned_to",
                    ),
                    "Created": _get_attr(
                        workflow,
                        "created_at",
                        "",
                    ),
                }
            )

        st.dataframe(
            rows,
            use_container_width=True,
            hide_index=True,
        )

    except Exception as exc:

        st.error(
            "Workflow records could not be loaded."
        )

        with st.expander(
            "Complete error",
            expanded=True,
        ):
            st.exception(exc)

    finally:

        if db is not None:

            db.close()