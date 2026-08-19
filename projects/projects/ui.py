"""
projects/projects/ui.py
------------------------
Central project repository, BIM file management, revision tracking, and team collaboration.
Exposes zero-argument `render_projects()` required by streamlit_app.py.
"""

from __future__ import annotations

import streamlit as st


def render_projects() -> None:
    """Zero-argument Streamlit renderer for Project Management & Workspace."""

    st.title("📁 Project Workspace & Repository")
    st.caption("Centralized BIM project management, structural model versioning, revision history, and team role allocation.")

    st.divider()

    col_params, col_main = st.columns([1, 2], gap="large")

    with col_params:
        st.subheader("Active Workspace Controls")

        selected_project = st.selectbox(
            "Select Project",
            [
                "PRJ-2026-001 | StudioHome HQ Tower",
                "PRJ-2026-002 | Horizon Residential Complex",
                "PRJ-2026-003 | Civic Center Atrium",
                "PRJ-2026-004 | Riverside Eco Bridge",
            ],
            key="proj_select",
        )

        project_stage = st.selectbox(
            "Design Stage",
            [
                "Concept Design (RIBA Stage 2)",
                "Spatial Coordination (RIBA Stage 3)",
                "Technical Design / FEA (RIBA Stage 4)",
                "Construction Documentation",
            ],
            index=2,
            key="proj_stage",
        )

        st.markdown("**BIM Model Sync Status**")
        st.caption("Connected Central Repository: Revit Server / IFC Cloud")
        
        sync_freq = st.radio(
            "Auto-Sync Interval",
            ["Real-time", "Hourly", "Manual Sync"],
            index=0,
            key="proj_sync_freq",
            horizontal=True,
        )

        st.divider()

        c1, c2 = st.columns(2)
        with c1:
            st.button(
                "➕ New Project",
                use_container_width=True,
                key="proj_new_btn",
            )
        with c2:
            st.button(
                "☁️ Sync Central",
                type="primary",
                use_container_width=True,
                key="proj_sync_btn",
            )

    with col_main:
        if "proj_loaded" not in st.session_state:
            st.session_state.proj_loaded = True

        tab_overview, tab_models, tab_revisions, tab_team = st.tabs([
            "📌 Project Overview",
            "🧊 BIM & Geometry Files",
            "📜 Revision History",
            "👥 Team & Roles",
        ])

        with tab_overview:
            st.success(f"Loaded **{selected_project.split(' | ')[1]}** ({selected_project.split(' | ')[0]})")

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Gross Floor Area", "18,400 m²")
            m2.metric("Building Height", "48.5 m (12 Storeys)")
            m3.metric("Lead Typology", "Mixed-Use Office")
            m4.metric("Active Revision", "v2.4.1")

            st.markdown("### Project Metadata")
            meta_data = [
                {"Parameter": "Client", "Value": "Metro Development Corp"},
                {"Parameter": "Site Location", "Value": "Sector 4, Central Business District"},
                {"Parameter": "Building Code", "Value": "IBC 2024 / Eurocode 2 & 3"},
                {"Parameter": "Structural System", "Value": "RC Core with Post-Tensioned Slabs"},
                {"Parameter": "Target Sustainability Rating", "Value": "LEED Platinum / BREEAM Outstanding"},
            ]
            st.dataframe(meta_data, use_container_width=True, hide_index=True)

        with tab_models:
            st.markdown("### Linked Structural & Architectural Models")

            models_data = [
                {"File Name": "StudioHome_HQ_ARC_v2.4.ifc", "Format": "IFC4", "Size": "142 MB", "Author": "Arch Studio", "Status": "Synced (10m ago)"},
                {"File Name": "StudioHome_HQ_STR_v2.4.rvt", "Format": "Revit 2026", "Size": "210 MB", "Author": "Structure AI", "Status": "Synced (10m ago)"},
                {"File Name": "StudioHome_HQ_MEP_v2.1.ifc", "Format": "IFC4", "Size": "98 MB", "Author": "MEP Consultants", "Status": "Pending Sync"},
                {"File Name": "FEA_Mesh_Floor12.json", "Format": "JSON / SAF", "Size": "14 MB", "Author": "Analysis Engine", "Status": "Synced (2h ago)"},
            ]
            st.dataframe(models_data, use_container_width=True, hide_index=True)

        with tab_revisions:
            st.markdown("### Version Control & Model Commits")

            commits = [
                {"Version": "v2.4.1", "Date": "2026-08-19", "Author": "Structural AI", "Commit Message": "Updated column grid spacing to 8.4m and adjusted core wall thickness."},
                {"Version": "v2.4.0", "Date": "2026-08-18", "Author": "Lead Architect", "Commit Message": "Revised penthouse floor plan layout and expanded atrium void."},
                {"Version": "v2.3.2", "Date": "2026-08-15", "Author": "Code Compliance Engine", "Commit Message": "Egress stair travel distance check validated - compliant."},
                {"Version": "v2.3.0", "Date": "2026-08-10", "Author": "Lead Structural Eng", "Commit Message": "Initial FEA slab thickness optimization run completed."},
            ]
            st.dataframe(commits, use_container_width=True, hide_index=True)

        with tab_team:
            st.markdown("### Assigned Project Members & Stakeholders")

            team_data = [
                {"Name": "Alex Chen", "Role": "Principal Architect / Project Director", "Access Level": "Admin / Approver"},
                {"Name": "Elena Rostova", "Role": "Lead Structural Engineer", "Access Level": "Full Edit"},
                {"Name": "StudioHome AI", "Role": "Automated FEA & Compliance Engine", "Access Level": "System Integration"},
                {"Name": "Marcus Vance", "Role": "BIM Coordinator", "Access Level": "Full Edit"},
            ]
            st.dataframe(team_data, use_container_width=True, hide_index=True)
