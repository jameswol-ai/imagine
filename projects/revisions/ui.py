"""Streamlit UI for project revision records."""
from __future__ import annotations

import streamlit as st


def _session():
    from database.connection import SessionLocal
    return SessionLocal()


def render_revisions() -> None:
    st.title("Revisions")
    st.caption("Project revision history and controlled change records.")
    try:
        from database.bootstrap import ensure_schema
        ensure_schema()
        from projects.model_registry import Project
        from projects.revisions.schemas import RevisionCreate
        from projects.revisions.service import create_revision, delete_revision, list_revisions, update_revision
    except Exception as exc:
        st.error("Revisions could not be initialized.")
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
        selected_id = st.selectbox("Project", list(project_map), format_func=lambda v: f"{project_map[v].name} ({v})", key="revisions_project_id")
        project = project_map[selected_id]
        st.success(f"Project: {project.name}")

        with st.form("revisions_create_form", clear_on_submit=True):
            description = st.text_area("Revision Description", max_chars=255)
            created_by = st.number_input("Created By User ID", min_value=1, value=1, step=1)
            submitted = st.form_submit_button("Create Revision", type="primary", use_container_width=True)
        if submitted:
            try:
                if not description.strip(): raise ValueError("Revision description is required.")
                payload = RevisionCreate(project_id=project.id, description=description.strip(), created_by=int(created_by))
                create_revision(db, project_id=payload.project_id, description=payload.description, created_by=payload.created_by)
                st.success("Revision created successfully."); st.rerun()
            except Exception as exc:
                db.rollback(); st.error(f"Revision could not be created: {exc}")

        revisions = list_revisions(db, project.id)
        st.subheader("Revision Records")
        if not revisions:
            st.info("No revisions exist for this project.")
            return
        st.dataframe([{"ID": r.id, "Description": r.description, "Created By": r.created_by, "Created": r.created_at} for r in revisions], use_container_width=True, hide_index=True)
        revision_map = {f"#{r.id} | {r.description}": r for r in revisions}
        selected = revision_map[st.selectbox("Revision", list(revision_map), key="revision_update_select")]
        with st.form("revision_update_form"):
            new_description = st.text_area("Description", value=selected.description, max_chars=255)
            save = st.form_submit_button("Save Revision", use_container_width=True)
        if save:
            try:
                if not new_description.strip(): raise ValueError("Revision description is required.")
                update_revision(db, selected.id, new_description.strip()); st.success("Revision updated successfully."); st.rerun()
            except Exception as exc:
                db.rollback(); st.error(f"Revision could not be updated: {exc}")
        if st.button("Delete Selected Revision", use_container_width=True):
            try:
                delete_revision(db, selected.id); st.success("Revision deleted successfully."); st.rerun()
            except Exception as exc:
                db.rollback(); st.error(f"Revision could not be deleted: {exc}")
    except Exception as exc:
        if db is not None: db.rollback()
        st.error("Revision records could not be loaded.")
        with st.expander("Complete error", expanded=True): st.exception(exc)
    finally:
        if db is not None: db.close()
