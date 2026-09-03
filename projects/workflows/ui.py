"""Streamlit UI for project workflow records."""
from __future__ import annotations

import streamlit as st


def _session():
    from database.connection import SessionLocal
    return SessionLocal()


def render_workflows() -> None:
    st.title("Workflows")
    st.caption("Project workflow steps, ownership, status and progress.")

    try:
        from database.bootstrap import ensure_schema
        ensure_schema()
        from projects.model_registry import Project
        from projects.workflows.schemas import WorkflowCreate
        from projects.workflows.service import (
            VALID_STATUSES, create_workflow, delete_workflow, list_workflows, update_workflow,
        )
    except Exception as exc:
        st.error("Workflows could not be initialized.")
        with st.expander("Complete error", expanded=True):
            st.exception(exc)
        return

    db = None
    try:
        db = _session()
        projects = db.query(Project).order_by(Project.name).all()
        if not projects:
            st.info("Create a project first from the Projects module.")
            return

        project_map = {str(p.id): p for p in projects}
        selected_id = st.selectbox(
            "Project", list(project_map),
            format_func=lambda value: f"{project_map[value].name} ({value})",
            key="workflows_project_id",
        )
        project = project_map[selected_id]
        st.success(f"Project: {project.name}")

        workflows = list_workflows(db, project.id)
        completed = sum(str(w.status) == "completed" for w in workflows)
        in_progress = sum(str(w.status) == "in_progress" for w in workflows)
        m1, m2, m3 = st.columns(3)
        m1.metric("Steps", len(workflows))
        m2.metric("In progress", in_progress)
        m3.metric("Completed", completed)

        with st.form("workflows_create_form", clear_on_submit=True):
            step = st.text_input("Workflow Step", max_chars=100)
            assigned_to = st.number_input("Assigned To User ID", min_value=0, value=0, step=1)
            submitted = st.form_submit_button("Create Workflow Step", type="primary", use_container_width=True)
        if submitted:
            try:
                payload = WorkflowCreate(project_id=project.id, step=step.strip(), assigned_to=int(assigned_to) or None)
                create_workflow(db, payload.project_id, payload.step, payload.assigned_to)
                st.success("Workflow step created successfully.")
                st.rerun()
            except Exception as exc:
                db.rollback()
                st.error(f"Workflow step could not be created: {exc}")

        if not workflows:
            st.info("No workflow steps exist for this project.")
            return

        st.subheader("Workflow Records")
        st.dataframe([
            {"ID": w.id, "Step": w.step, "Status": w.status, "Assigned To": w.assigned_to or "Unassigned", "Created": w.created_at}
            for w in workflows
        ], use_container_width=True, hide_index=True)

        workflow_map = {f"#{w.id} | {w.step}": w for w in workflows}
        selected_label = st.selectbox("Workflow step", list(workflow_map), key="workflow_update_select")
        selected = workflow_map[selected_label]
        with st.form("workflow_update_form"):
            new_step = st.text_input("Step", value=selected.step)
            new_status = st.selectbox("Status", VALID_STATUSES, index=VALID_STATUSES.index(selected.status) if selected.status in VALID_STATUSES else 0)
            new_assigned = st.number_input("Assigned To User ID", min_value=0, value=int(selected.assigned_to or 0), step=1)
            save = st.form_submit_button("Save Workflow Step", use_container_width=True)
        if save:
            try:
                update_workflow(db, selected.id, step=new_step.strip(), status=new_status, assigned_to=int(new_assigned) or None)
                st.success("Workflow step updated successfully.")
                st.rerun()
            except Exception as exc:
                db.rollback()
                st.error(f"Workflow step could not be updated: {exc}")

        if st.button("Delete Selected Workflow Step", use_container_width=True):
            try:
                delete_workflow(db, selected.id)
                st.success("Workflow step deleted successfully.")
                st.rerun()
            except Exception as exc:
                db.rollback()
                st.error(f"Workflow step could not be deleted: {exc}")
    except Exception as exc:
        if db is not None:
            db.rollback()
        st.error("Workflow records could not be loaded.")
        with st.expander("Complete error", expanded=True):
            st.exception(exc)
    finally:
        if db is not None:
            db.close()
