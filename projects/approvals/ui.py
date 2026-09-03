"""Database-backed Streamlit UI for project approvals."""

from __future__ import annotations

from typing import Any
from uuid import UUID

import streamlit as st


def _ensure_schema() -> None:
    from database.bootstrap import ensure_schema

    ensure_schema()


def _get_attr(obj: Any, name: str, default: Any = None) -> Any:
    return getattr(obj, name, default)


def _status_value(value: Any) -> str:
    return str(getattr(value, "value", value or "unknown"))


def _session():
    from database.connection import SessionLocal

    return SessionLocal()


def _parse_project_id(value: str) -> UUID | None:
    try:
        return UUID(value.strip()) if value.strip() else None
    except ValueError:
        return None


def render_approvals() -> None:
    st.title("Approvals")
    st.caption("Project approval records and authorization workflow.")

    try:
        _ensure_schema()
        from projects.approvals.schemas import ApprovalCreate
        from projects.approvals.service import (
            create_approval,
            delete_approval,
            list_approvals,
            update_approval,
        )
    except Exception as exc:
        st.error("Approvals could not be initialized.")
        with st.expander("Complete import error", expanded=True):
            st.exception(exc)
        return

    project_id_text = st.text_input(
        "Project ID",
        key="approvals_project_id",
        placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
        help="Enter the UUID of an existing project.",
    )
    project_id = _parse_project_id(project_id_text)

    if project_id_text.strip() and project_id is None:
        st.error("Project ID must be a valid UUID.")
        return

    if project_id is None:
        st.info("Enter a valid Project UUID to manage approval records.")
        return

    db = None
    try:
        db = _session()
        from projects.model_registry import Project

        project = db.get(Project, project_id)
        if project is None:
            st.warning("No project exists with that UUID. Create the project first from the Projects module.")
            return

        st.success(f"Project: {project.name}")

        st.subheader("Create Approval")
        with st.form("approvals_create_form", clear_on_submit=True):
            approver_id = st.number_input("Approver ID", min_value=1, value=1, step=1)
            comment = st.text_area("Comment", max_chars=255)
            submitted = st.form_submit_button("Create Approval", type="primary", use_container_width=True)

        if submitted:
            try:
                payload = ApprovalCreate(
                    project_id=project_id,
                    approver_id=int(approver_id),
                    comment=comment.strip() or None,
                )
                create_approval(
                    db,
                    project_id=payload.project_id,
                    approver_id=payload.approver_id,
                    comment=payload.comment,
                )
                st.success("Approval created successfully.")
                st.rerun()
            except Exception as exc:
                db.rollback()
                st.error("Approval could not be created.")
                with st.expander("Complete error", expanded=True):
                    st.exception(exc)

        st.divider()
        approvals = list_approvals(db, project_id)
        st.subheader("Approval Records")

        if not approvals:
            st.info("No approval records exist for this project.")
            return

        rows = [
            {
                "ID": a.id,
                "Status": _status_value(a.status),
                "Approver ID": a.approver_id,
                "Comment": a.comment or "",
                "Created": a.created_at,
            }
            for a in approvals
        ]
        st.dataframe(rows, use_container_width=True, hide_index=True)

        st.subheader("Update Approval")
        approval_map = {f"#{a.id} | {_status_value(a.status)}": a for a in approvals}
        selected_label = st.selectbox("Approval", list(approval_map), key="approval_update_select")
        selected = approval_map[selected_label]
        with st.form("approval_update_form"):
            new_status = st.selectbox("Status", ["pending", "approved", "rejected", "cancelled"], index=["pending", "approved", "rejected", "cancelled"].index(_status_value(selected.status)) if _status_value(selected.status) in {"pending", "approved", "rejected", "cancelled"} else 0)
            new_comment = st.text_area("Comment", value=selected.comment or "", max_chars=255)
            save = st.form_submit_button("Save Approval", use_container_width=True)
        if save:
            try:
                update_approval(db, selected.id, new_status, new_comment.strip() or None)
                st.success("Approval updated successfully.")
                st.rerun()
            except Exception as exc:
                db.rollback()
                st.error("Approval could not be updated.")
                with st.expander("Complete error", expanded=True):
                    st.exception(exc)

        if st.button("Delete Selected Approval", use_container_width=True):
            try:
                delete_approval(db, selected.id)
                st.success("Approval deleted successfully.")
                st.rerun()
            except Exception as exc:
                db.rollback()
                st.error("Approval could not be deleted.")
                with st.expander("Complete error", expanded=True):
                    st.exception(exc)

    except Exception as exc:
        if db is not None:
            db.rollback()
        st.error("Approval records could not be loaded.")
        with st.expander("Complete error", expanded=True):
            st.exception(exc)
    finally:
        if db is not None:
            db.close()
