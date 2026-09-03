"""Streamlit UI for project approval records."""
from __future__ import annotations

import streamlit as st


def _session():
    from database.connection import SessionLocal
    return SessionLocal()


def render_approvals() -> None:
    st.title("Approvals")
    st.caption("Project approval records and authorization workflow.")
    try:
        from database.bootstrap import ensure_schema
        ensure_schema()
        from projects.model_registry import Project
        from projects.approvals.schemas import ApprovalCreate
        from projects.approvals.service import create_approval, delete_approval, list_approvals, update_approval
    except Exception as exc:
        st.error("Approvals could not be initialized.")
        with st.expander("Complete error", expanded=True): st.exception(exc)
        return

    db = None
    try:
        db = _session()
        projects = db.query(Project).order_by(Project.name).all()
        if not projects:
            st.info("Create a project first from the Projects module.")
            return
        project_map = {str(p.id): p for p in projects}
        selected_id = st.selectbox("Project", list(project_map), format_func=lambda v: f"{project_map[v].name} ({v})", key="approvals_project_id")
        project = project_map[selected_id]
        st.success(f"Project: {project.name}")

        with st.form("approvals_create_form", clear_on_submit=True):
            approver_id = st.number_input("Approver User ID", min_value=1, value=1, step=1)
            comment = st.text_area("Comment", max_chars=255)
            submitted = st.form_submit_button("Create Approval", type="primary", use_container_width=True)
        if submitted:
            try:
                payload = ApprovalCreate(project_id=project.id, approver_id=int(approver_id), comment=comment.strip() or None)
                create_approval(db, project_id=payload.project_id, approver_id=payload.approver_id, comment=payload.comment)
                st.success("Approval created successfully.")
                st.rerun()
            except Exception as exc:
                db.rollback(); st.error(f"Approval could not be created: {exc}")

        approvals = list_approvals(db, project.id)
        st.subheader("Approval Records")
        if not approvals:
            st.info("No approval records exist for this project.")
            return
        st.dataframe([{"ID": a.id, "Status": a.status, "Approver ID": a.approver_id, "Comment": a.comment or "", "Created": a.created_at} for a in approvals], use_container_width=True, hide_index=True)
        approval_map = {f"#{a.id} | {a.status}": a for a in approvals}
        selected = approval_map[st.selectbox("Approval", list(approval_map), key="approval_update_select")]
        with st.form("approval_update_form"):
            statuses = ["pending", "approved", "rejected", "cancelled"]
            current = str(selected.status)
            new_status = st.selectbox("Status", statuses, index=statuses.index(current) if current in statuses else 0)
            new_comment = st.text_area("Comment", value=selected.comment or "", max_chars=255)
            save = st.form_submit_button("Save Approval", use_container_width=True)
        if save:
            try:
                update_approval(db, selected.id, new_status, new_comment.strip() or None)
                st.success("Approval updated successfully."); st.rerun()
            except Exception as exc:
                db.rollback(); st.error(f"Approval could not be updated: {exc}")
        if st.button("Delete Selected Approval", use_container_width=True):
            try:
                delete_approval(db, selected.id); st.success("Approval deleted successfully."); st.rerun()
            except Exception as exc:
                db.rollback(); st.error(f"Approval could not be deleted: {exc}")
    except Exception as exc:
        if db is not None: db.rollback()
        st.error("Approval records could not be loaded.")
        with st.expander("Complete error", expanded=True): st.exception(exc)
    finally:
        if db is not None: db.close()
