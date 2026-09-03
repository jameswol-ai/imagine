"""Database-backed Streamlit UI for project revisions."""

from __future__ import annotations

from typing import Any
from uuid import UUID

import streamlit as st


def _ensure_schema() -> None:
    from database.bootstrap import ensure_schema

    ensure_schema()


def _session():
    from database.connection import SessionLocal

    return SessionLocal()


def _parse_project_id(value: str) -> UUID | None:
    try:
        return UUID(value.strip()) if value.strip() else None
    except ValueError:
        return None


def _get_attr(obj: Any, name: str, default: Any = None) -> Any:
    return getattr(obj, name, default)


def render_revisions() -> None:
    st.title("Revisions")
    st.caption("Project revision history and controlled change records.")

    try:
        _ensure_schema()
        from projects.revisions.schemas import RevisionCreate
        from projects.revisions.service import (
            create_revision,
            delete_revision,
            list_revisions,
            update_revision,
        )
    except Exception as exc:
        st.error("Revisions could not be initialized.")
        with st.expander("Complete import error", expanded=True):
            st.exception(exc)
        return

    project_id_text = st.text_input(
        "Project ID",
        key="revisions_project_id",
        placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
        help="Enter the UUID of an existing project.",
    )
    project_id = _parse_project_id(project_id_text)

    if project_id_text.strip() and project_id is None:
        st.error("Project ID must be a valid UUID.")
        return

    if project_id is None:
        st.info("Enter a valid Project UUID to manage revision records.")
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

        st.subheader("Create Revision")
        with st.form("revisions_create_form", clear_on_submit=True):
            description = st.text_area("Revision Description", max_chars=255)
            created_by = st.number_input("Created By User ID", min_value=1, value=1, step=1)
            submitted = st.form_submit_button("Create Revision", type="primary", use_container_width=True)

        if submitted:
            if not description.strip():
                st.error("Revision description is required.")
            else:
                try:
                    payload = RevisionCreate(
                        project_id=project_id,
                        description=description.strip(),
                        created_by=int(created_by),
                    )
                    create_revision(
                        db,
                        project_id=payload.project_id,
                        description=payload.description,
                        created_by=payload.created_by,
                    )
                    st.success("Revision created successfully.")
                    st.rerun()
                except Exception as exc:
                    db.rollback()
                    st.error("Revision could not be created.")
                    with st.expander("Complete error", expanded=True):
                        st.exception(exc)

        st.divider()
        revisions = list_revisions(db, project_id)
        st.subheader("Revision Records")

        if not revisions:
            st.info("No revisions exist for this project.")
            return

        st.dataframe(
            [
                {
                    "ID": r.id,
                    "Description": r.description,
                    "Created By": r.created_by,
                    "Created": _get_attr(r, "created_at", ""),
                }
                for r in revisions
            ],
            use_container_width=True,
            hide_index=True,
        )

        revision_map = {f"#{r.id} | {r.description}": r for r in revisions}
        selected_label = st.selectbox("Revision", list(revision_map), key="revision_update_select")
        selected = revision_map[selected_label]

        st.subheader("Update Revision")
        with st.form("revision_update_form"):
            new_description = st.text_area("Description", value=selected.description, max_chars=255)
            save = st.form_submit_button("Save Revision", use_container_width=True)
        if save:
            if not new_description.strip():
                st.error("Revision description is required.")
            else:
                try:
                    update_revision(db, selected.id, new_description.strip())
                    st.success("Revision updated successfully.")
                    st.rerun()
                except Exception as exc:
                    db.rollback()
                    st.error("Revision could not be updated.")
                    with st.expander("Complete error", expanded=True):
                        st.exception(exc)

        if st.button("Delete Selected Revision", use_container_width=True):
            try:
                delete_revision(db, selected.id)
                st.success("Revision deleted successfully.")
                st.rerun()
            except Exception as exc:
                db.rollback()
                st.error("Revision could not be deleted.")
                with st.expander("Complete error", expanded=True):
                    st.exception(exc)

    except Exception as exc:
        if db is not None:
            db.rollback()
        st.error("Revision records could not be loaded.")
        with st.expander("Complete error", expanded=True):
            st.exception(exc)
    finally:
        if db is not None:
            db.close()
