"""
IMAGINE Project Workflows Streamlit UI.
"""

from __future__ import annotations

import streamlit as st


def render_workflows() -> None:

    st.title("Workflows")

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

        from database.connection import (
            SessionLocal,
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
        step=1,
        key="workflow_project_id",
    )

    with st.form("workflow_form"):

        step = st.text_input(
            "Workflow Step"
        )

        assigned_to = st.number_input(
            "Assigned To",
            min_value=0,
            step=1,
            value=0,
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

            db = SessionLocal()

            try:

                payload = WorkflowCreate(
                    project_id=int(project_id),
                    step=step.strip(),
                    assigned_to=(
                        int(assigned_to)
                        if assigned_to
                        else None
                    ),
                )

                create_workflow(
                    db=db,
                    project_id=payload.project_id,
                    step=payload.step,
                    assigned_to=payload.assigned_to,
                )

                st.success(
                    "Workflow step created."
                )

                st.rerun()

            except Exception as exc:

                db.rollback()

                st.error(
                    "Workflow could not be created."
                )

                with st.expander(
                    "Complete error",
                    expanded=True,
                ):
                    st.exception(exc)

            finally:
                db.close()

    st.divider()

    db = SessionLocal()

    try:

        workflows = list_workflows(
            db=db,
            project_id=int(project_id),
        )

        st.dataframe(
            [
                {
                    "ID": item.id,
                    "Project": item.project_id,
                    "Step": item.step,
                    "Status": item.status,
                    "Assigned To": item.assigned_to,
                }
                for item in workflows
            ],
            use_container_width=True,
            hide_index=True,
        )

    except Exception as exc:

        st.error(
            "Workflows could not be listed."
        )

        with st.expander(
            "Complete error",
            expanded=True,
        ):
            st.exception(exc)

    finally:
        db.close()