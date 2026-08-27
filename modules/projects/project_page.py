"""
IMAGINE Platform — Project Portfolio Interactive View
Path: modules/projects/project_page.py
App: imagine
"""

import pandas as pd
import streamlit as st
from modules.projects.projects import ProjectService


class ProjectPage:
    """Project Portfolio UI component called by streamlit_app router."""

    @classmethod
    def render(cls) -> None:
        st.title("📂 Project Portfolio & Management")
        st.caption("Manage active AEC assets, budget allocations, schedules, and site operations.")

        projects = ProjectService.get_all_projects()

        # ==============================================================================
        # 1. TOP METRICS
        # ==============================================================================
        col1, col2, col3, col4 = st.columns(4)
        total_projects = len(projects)
        active_projects = sum(1 for p in projects if p.get("status") == "active")
        total_budget_m = sum(p.get("budget", 0.0) for p in projects)
        avg_progress = (
            sum(p.get("progress_pct", 0.0) for p in projects) / total_projects
            if total_projects > 0
            else 0.0
        )

        col1.metric("Total Projects", total_projects)
        col2.metric("Active Projects", active_projects)
        col3.metric("Total Capital ($M)", f"${total_budget_m:,.1f}M")
        col4.metric("Avg Portfolio Progress", f"{avg_progress:.1f}%")

        st.divider()

        # ==============================================================================
        # 2. CONTROLS & TABULAR/CARD VIEWS
        # ==============================================================================
        tab_overview, tab_create, tab_manage = st.tabs(
            ["📊 Portfolio Overview", "➕ Register Project", "⚙️ Manage & Edit"]
        )

        # TAB 1: OVERVIEW & FILTERING
        with tab_overview:
            c_search, c_filter = st.columns([3, 1])
            search_query = c_search.text_input("🔍 Search Projects", placeholder="Search name, ID, or client...")
            category_filter = c_filter.selectbox("Filter Category", ["All", "Commercial", "Infrastructure", "Residential", "Industrial"])

            filtered = projects
            if category_filter != "All":
                filtered = [p for p in filtered if p.get("category") == category_filter]
            if search_query:
                q = search_query.lower()
                filtered = [
                    p for p in filtered
                    if q in p.get("name", "").lower()
                    or q in p.get("id", "").lower()
                    or q in p.get("client", "").lower()
                ]

            if not filtered:
                st.info("No projects match the search filter criteria.")
            else:
                for proj in filtered:
                    with st.expander(f"**{proj['id']} — {proj['name']}** ({proj['category']})", expanded=True):
                        p_col1, p_col2, p_col3 = st.columns([2, 2, 1])
                        p_col1.write(f"**Client:** {proj.get('client', 'N/A')}")
                        p_col1.write(f"**Location:** {proj.get('location', 'N/A')}")
                        
                        p_col2.write(f"**Budget:** ${proj.get('budget', 0.0):,.2f}M (€{proj.get('budget_eur', 0.0):,.0f})")
                        p_col2.write(f"**Status:** `{proj.get('status', 'active').upper()}`")

                        progress = float(proj.get("progress_pct", 0.0)) / 100.0
                        p_col3.caption("Completion Progress")
                        p_col3.progress(progress, text=f"{progress*100:.0f}%")

        # TAB 2: REGISTER NEW PROJECT
        with tab_create:
            st.subheader("Register New AEC Project")
            with st.form("create_project_form", clear_on_submit=True):
                fc1, fc2 = st.columns(2)
                p_id = fc1.text_input("Project ID", value=f"PRJ-00{len(projects) + 1}")
                p_name = fc2.text_input("Project Name", placeholder="e.g., Riverside Commercial Complex")

                fc3, fc4 = st.columns(2)
                p_client = fc3.text_input("Client Name", placeholder="e.g., Global Real Estate LLC")
                p_category = fc4.selectbox("Category", ["Commercial", "Infrastructure", "Residential", "Industrial"])

                fc5, fc6, fc7 = st.columns(3)
                p_budget = fc5.number_input("Budget ($ Millions)", min_value=0.1, value=10.0, step=0.5)
                p_location = fc6.text_input("Location", placeholder="City / District")
                p_status = fc7.selectbox("Status", ["active", "planning", "on-hold", "completed"])

                submitted = st.form_submit_button("Submit Project")
                if submitted:
                    if not p_name or not p_id:
                        st.error("Project ID and Project Name are required.")
                    else:
                        new_record = {
                            "id": p_id,
                            "name": p_name,
                            "client": p_client,
                            "category": p_category,
                            "budget": float(p_budget),
                            "budget_eur": float(p_budget) * 1_000_000.0,
                            "status": p_status,
                            "progress_pct": 0.0,
                            "location": p_location,
                        }
                        ProjectService.create_project(new_record)
                        st.success(f"Project `{p_name}` ({p_id}) created successfully!")
                        st.rerun()

        # TAB 3: MANAGE & EDIT
        with tab_manage:
            st.subheader("Edit or Delete Existing Record")
            if not projects:
                st.info("No projects available to manage.")
            else:
                target_id = st.selectbox("Select Project to Modify", [p["id"] for p in projects])
                selected_proj = ProjectService.get_project_by_id(target_id)

                if selected_proj:
                    with st.form("edit_project_form"):
                        ec1, ec2 = st.columns(2)
                        e_name = ec1.text_input("Project Name", value=selected_proj.get("name", ""))
                        e_client = ec2.text_input("Client Name", value=selected_proj.get("client", ""))

                        ec3, ec4 = st.columns(2)
                        e_budget = ec3.number_input("Budget ($M)", value=float(selected_proj.get("budget", 1.0)))
                        e_progress = ec4.slider("Progress %", 0.0, 100.0, value=float(selected_proj.get("progress_pct", 0.0)))

                        save_btn = st.form_submit_button("Save Changes")
                        if save_btn:
                            ProjectService.update_project(
                                target_id,
                                {
                                    "name": e_name,
                                    "client": e_client,
                                    "budget": float(e_budget),
                                    "progress_pct": float(e_progress),
                                },
                            )
                            st.success(f"Updated `{target_id}` successfully!")
                            st.rerun()

                    st.divider()
                    if st.button(f"🗑️ Delete Project {target_id}", type="secondary"):
                        ProjectService.delete_project(target_id)
                        st.warning(f"Deleted `{target_id}`.")
                        st.rerun()
