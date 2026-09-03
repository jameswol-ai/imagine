"""Database-backed Streamlit UI for the IMAGINE Projects workspace."""

from __future__ import annotations

from typing import Any

import streamlit as st


def _ensure_schema() -> None:
    from database.bootstrap import ensure_schema

    ensure_schema()


def _session():
    from database.connection import SessionLocal

    return SessionLocal()


def _project_rows(projects: list[Any]) -> list[dict[str, Any]]:
    rows = []
    for project in projects:
        status = getattr(getattr(project, "status", None), "value", getattr(project, "status", ""))
        rows.append(
            {
                "ID": str(getattr(project, "id", "")),
                "Name": getattr(project, "name", ""),
                "Status": str(status),
                "Budget": float(getattr(project, "budget", 0.0) or 0.0),
                "Progress %": float(getattr(project, "progress", 0.0) or 0.0),
                "Client ID": getattr(project, "client_id", None) or "",
                "Start": getattr(project, "start_date", None) or "",
                "End": getattr(project, "end_date", None) or "",
            }
        )
    return rows


def render_projects() -> None:
    """Render production-oriented Project CRUD and workspace controls."""
    st.title("Project Workspace")
    st.caption("Project lifecycle, database records, budget, progress and client allocation.")

    try:
        _ensure_schema()
        from projects.projects.schemas import ProjectCreate, ProjectStatus, ProjectUpdate
        from projects.projects.service import ProjectService
    except Exception as exc:
        st.error("Projects could not be initialized.")
        with st.expander("Complete error", expanded=True):
            st.exception(exc)
        return

    db = None
    try:
        db = _session()
        projects = ProjectService.get_all_sync(db, limit=10000)

        active_count = sum(
            1 for p in projects
            if getattr(getattr(p, "status", None), "value", getattr(p, "status", "")) == "active"
        )
        completed_count = sum(
            1 for p in projects
            if getattr(getattr(p, "status", None), "value", getattr(p, "status", "")) == "completed"
        )
        total_budget = sum(float(getattr(p, "budget", 0.0) or 0.0) for p in projects)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Projects", len(projects))
        m2.metric("Active", active_count)
        m3.metric("Completed", completed_count)
        m4.metric("Portfolio Budget", f"{total_budget:,.2f}")

        tab_projects, tab_create, tab_update, tab_delete = st.tabs(
            ["Project Register", "Create Project", "Update Project", "Delete Project"]
        )

        with tab_projects:
            if projects:
                st.dataframe(_project_rows(projects), use_container_width=True, hide_index=True)
            else:
                st.info("No projects are registered yet. Create the first project from the Create Project tab.")

        with tab_create:
            with st.form("projects_create_form", clear_on_submit=True):
                name = st.text_input("Project Name", max_chars=255)
                description = st.text_area("Description")
                status = st.selectbox("Status", list(ProjectStatus), format_func=lambda x: x.value.replace("_", " ").title())
                budget = st.number_input("Budget", min_value=0.0, value=0.0, step=1000.0)
                progress = st.number_input("Progress %", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
                client_id_raw = st.text_input("Client / Organization ID (optional)", help="organizations.id is an integer.")
                start_date = st.text_input("Start Date (optional)", placeholder="2026-09-01")
                end_date = st.text_input("End Date (optional)", placeholder="2027-09-01")
                submitted = st.form_submit_button("Create Project", type="primary", use_container_width=True)

            if submitted:
                if not name.strip():
                    st.error("Project name is required.")
                else:
                    client_id = None
                    if client_id_raw.strip():
                        try:
                            client_id = int(client_id_raw.strip())
                            if client_id < 1:
                                raise ValueError
                        except ValueError:
                            st.error("Client / Organization ID must be a positive integer.")
                            client_id = -1

                    if client_id != -1:
                        try:
                            payload = ProjectCreate(
                                name=name.strip(),
                                description=description.strip() or None,
                                status=status,
                                budget=budget,
                                progress=progress,
                                client_id=client_id,
                                start_date=start_date.strip() or None,
                                end_date=end_date.strip() or None,
                            )
                            ProjectService.create_sync(db, payload)
                            st.success("Project created successfully.")
                            st.rerun()
                        except Exception as exc:
                            db.rollback()
                            st.error("Project could not be created.")
                            with st.expander("Complete error", expanded=True):
                                st.exception(exc)

        with tab_update:
            project_ids = [str(getattr(p, "id")) for p in projects]
            if not project_ids:
                st.info("Create a project before updating one.")
            else:
                selected_id = st.selectbox("Project", project_ids, key="project_update_id")
                selected = ProjectService.get_sync(db, selected_id)
                if selected is not None:
                    current_status = getattr(getattr(selected, "status", None), "value", getattr(selected, "status", "planning"))
                    status_values = [x.value for x in ProjectStatus]
                    current_index = status_values.index(current_status) if current_status in status_values else 0
                    with st.form("projects_update_form"):
                        new_name = st.text_input("Project Name", value=getattr(selected, "name", ""))
                        new_description = st.text_area("Description", value=getattr(selected, "description", "") or "")
                        new_status = st.selectbox("Status", status_values, index=current_index)
                        new_budget = st.number_input("Budget", min_value=0.0, value=float(getattr(selected, "budget", 0.0) or 0.0), step=1000.0)
                        new_progress = st.number_input("Progress %", min_value=0.0, max_value=100.0, value=float(getattr(selected, "progress", 0.0) or 0.0), step=1.0)
                        update_submitted = st.form_submit_button("Save Changes", type="primary", use_container_width=True)

                    if update_submitted:
                        try:
                            payload = ProjectUpdate(
                                name=new_name.strip(),
                                description=new_description.strip() or None,
                                status=ProjectStatus(new_status),
                                budget=new_budget,
                                progress=new_progress,
                            )
                            ProjectService.update_sync(db, selected_id, payload)
                            st.success("Project updated successfully.")
                            st.rerun()
                        except Exception as exc:
                            db.rollback()
                            st.error("Project could not be updated.")
                            with st.expander("Complete error", expanded=True):
                                st.exception(exc)

        with tab_delete:
            project_ids = [str(getattr(p, "id")) for p in projects]
            if not project_ids:
                st.info("There are no projects to delete.")
            else:
                delete_id = st.selectbox("Project to delete", project_ids, key="project_delete_id")
                confirm = st.checkbox("I understand that this deletes the project and its approval/revision records.")
                if st.button("Delete Project", type="secondary", disabled=not confirm, use_container_width=True):
                    try:
                        deleted = ProjectService.delete_sync(db, delete_id)
                        if deleted:
                            st.success("Project deleted successfully.")
                            st.rerun()
                        else:
                            st.warning("Project was not found.")
                    except Exception as exc:
                        db.rollback()
                        st.error("Project could not be deleted.")
                        with st.expander("Complete error", expanded=True):
                            st.exception(exc)

    except Exception as exc:
        if db is not None:
            db.rollback()
        st.error("Project workspace could not be loaded.")
        with st.expander("Complete error", expanded=True):
            st.exception(exc)
    finally:
        if db is not None:
            db.close()
