"""Database-backed Streamlit UI for the IMAGINE Projects workspace."""

from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st


def _ensure_schema() -> None:
    from database.bootstrap import ensure_schema

    ensure_schema()


def _session():
    from database.connection import SessionLocal

    return SessionLocal()


def _status_value(value: Any) -> str:
    return str(getattr(value, "value", value or "unknown")).strip().lower()


def _project_rows(projects: list[Any], organizations: dict[int, str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for project in projects:
        client_id = getattr(project, "client_id", None)
        rows.append(
            {
                "ID": str(getattr(project, "id", "")),
                "Name": getattr(project, "name", ""),
                "Status": _status_value(getattr(project, "status", "")).replace("_", " ").title(),
                "Budget": float(getattr(project, "budget", 0.0) or 0.0),
                "Progress %": float(getattr(project, "progress", 0.0) or 0.0),
                "Client": organizations.get(client_id, str(client_id) if client_id else "Unassigned"),
                "Start": getattr(project, "start_date", None) or "",
                "End": getattr(project, "end_date", None) or "",
            }
        )
    return rows


def _parse_date(value: str) -> str | None:
    value = value.strip()
    if not value:
        return None
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError:
        raise ValueError("Date must use YYYY-MM-DD format.")


def render_projects() -> None:
    """Render the database-backed Projects workspace."""
    st.title("Project Workspace")
    st.caption("Project lifecycle, portfolio health, budgets, progress and client allocation.")

    try:
        _ensure_schema()
        from projects.model_registry import Organization
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
        organizations = {
            int(org.id): org.name
            for org in db.query(Organization).order_by(Organization.name).all()
        }

        statuses = [_status_value(getattr(p, "status", "")) for p in projects]
        total_budget = sum(float(getattr(p, "budget", 0.0) or 0.0) for p in projects)
        average_progress = sum(float(getattr(p, "progress", 0.0) or 0.0) for p in projects) / len(projects) if projects else 0.0
        active_count = statuses.count("active")
        completed_count = statuses.count("completed")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Projects", len(projects))
        m2.metric("Active", active_count)
        m3.metric("Completed", completed_count)
        m4.metric("Average Progress", f"{average_progress:.1f}%")

        tab_overview, tab_create, tab_update, tab_delete = st.tabs(
            ["Portfolio", "Create Project", "Update Project", "Delete Project"]
        )

        with tab_overview:
            if not projects:
                st.info("No projects are registered yet. Create the first project from Create Project.")
            else:
                rows = _project_rows(projects, organizations)
                df = pd.DataFrame(rows)
                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("Project Progress")
                    chart = px.bar(df.sort_values("Progress %"), x="Progress %", y="Name", orientation="h", range_x=[0, 100])
                    st.plotly_chart(chart, use_container_width=True)
                with c2:
                    st.subheader("Status Distribution")
                    status_df = df["Status"].value_counts().rename_axis("Status").reset_index(name="Projects")
                    chart = px.pie(status_df, names="Status", values="Projects", hole=0.45)
                    st.plotly_chart(chart, use_container_width=True)

                st.subheader("Portfolio Register")
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.caption(f"Portfolio budget: {total_budget:,.2f}")

        with tab_create:
            client_options = {0: "Unassigned", **organizations}
            with st.form("projects_create_form", clear_on_submit=True):
                name = st.text_input("Project Name", max_chars=255)
                description = st.text_area("Description")
                status = st.selectbox("Status", list(ProjectStatus), format_func=lambda x: x.value.replace("_", " ").title())
                budget = st.number_input("Budget", min_value=0.0, value=0.0, step=1000.0)
                progress = st.number_input("Progress %", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
                client_id = st.selectbox("Client / Organization", list(client_options), format_func=lambda x: client_options[x])
                start_date = st.text_input("Start Date", placeholder="2026-09-01")
                end_date = st.text_input("End Date", placeholder="2027-09-01")
                submitted = st.form_submit_button("Create Project", type="primary", use_container_width=True)

            if submitted:
                try:
                    if not name.strip():
                        raise ValueError("Project name is required.")
                    start = _parse_date(start_date)
                    end = _parse_date(end_date)
                    if start and end and end < start:
                        raise ValueError("End Date cannot be earlier than Start Date.")
                    payload = ProjectCreate(
                        name=name.strip(), description=description.strip() or None, status=status,
                        budget=budget, progress=progress, client_id=client_id or None,
                        start_date=start, end_date=end,
                    )
                    ProjectService.create_sync(db, payload)
                    st.success("Project created successfully.")
                    st.rerun()
                except Exception as exc:
                    db.rollback()
                    st.error(f"Project could not be created: {exc}")

        with tab_update:
            project_ids = [str(getattr(p, "id")) for p in projects]
            if not project_ids:
                st.info("Create a project before updating one.")
            else:
                selected_id = st.selectbox(
                    "Project", project_ids, key="project_update_id",
                    format_func=lambda value: next((getattr(p, "name", value) for p in projects if str(getattr(p, "id")) == value), value),
                )
                selected = ProjectService.get_sync(db, selected_id)
                if selected is not None:
                    current_status = _status_value(getattr(selected, "status", "planning"))
                    status_values = [x.value for x in ProjectStatus]
                    current_index = status_values.index(current_status) if current_status in status_values else 0
                    client_options = {0: "Unassigned", **organizations}
                    current_client = getattr(selected, "client_id", None) or 0
                    if current_client not in client_options:
                        client_options[current_client] = f"Organization #{current_client}"
                    with st.form("projects_update_form"):
                        new_name = st.text_input("Project Name", value=getattr(selected, "name", ""))
                        new_description = st.text_area("Description", value=getattr(selected, "description", "") or "")
                        new_status = st.selectbox("Status", status_values, index=current_index)
                        new_budget = st.number_input("Budget", min_value=0.0, value=float(getattr(selected, "budget", 0.0) or 0.0), step=1000.0)
                        new_progress = st.number_input("Progress %", min_value=0.0, max_value=100.0, value=float(getattr(selected, "progress", 0.0) or 0.0), step=1.0)
                        new_client = st.selectbox("Client / Organization", list(client_options), index=list(client_options).index(current_client), format_func=lambda x: client_options[x])
                        new_start = st.text_input("Start Date", value=getattr(selected, "start_date", "") or "")
                        new_end = st.text_input("End Date", value=getattr(selected, "end_date", "") or "")
                        update_submitted = st.form_submit_button("Save Changes", type="primary", use_container_width=True)

                    if update_submitted:
                        try:
                            start = _parse_date(new_start)
                            end = _parse_date(new_end)
                            if start and end and end < start:
                                raise ValueError("End Date cannot be earlier than Start Date.")
                            payload = ProjectUpdate(
                                name=new_name.strip(), description=new_description.strip() or None,
                                status=ProjectStatus(new_status), budget=new_budget, progress=new_progress,
                                client_id=new_client or None, start_date=start, end_date=end,
                            )
                            ProjectService.update_sync(db, selected_id, payload)
                            st.success("Project updated successfully.")
                            st.rerun()
                        except Exception as exc:
                            db.rollback()
                            st.error(f"Project could not be updated: {exc}")

        with tab_delete:
            project_ids = [str(getattr(p, "id")) for p in projects]
            if not project_ids:
                st.info("There are no projects to delete.")
            else:
                delete_id = st.selectbox(
                    "Project to delete", project_ids, key="project_delete_id",
                    format_func=lambda value: next((getattr(p, "name", value) for p in projects if str(getattr(p, "id")) == value), value),
                )
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
                        st.error(f"Project could not be deleted: {exc}")
    except Exception as exc:
        if db is not None:
            db.rollback()
        st.error("Project workspace could not be loaded.")
        with st.expander("Complete error", expanded=True):
            st.exception(exc)
    finally:
        if db is not None:
            db.close()
