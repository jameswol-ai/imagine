"""
IMAGINE Platform — Building Spatial Hierarchy Registry
Path: modules/bim/buildings.py
App: imagine
"""

import pandas as pd
import plotly.express as px
import streamlit as st
def render():
    st.header("🏛️ BIM - Buildings")
    st.table(st.session_state.buildings_data)
from modules.utils.crud import CRUDService

STATE_KEY = "bim_buildings"


def render() -> None:
    """Renders the building hierarchy management interface."""
    st.title("🏢 Building Registry & Spatial Hierarchy")
    st.caption("Define top-level building entities, site envelopes, gross floor areas, and floor counts.")

    # Seed demo data if missing
    items = CRUDService.get_all(STATE_KEY)
    if not items:
        _initialize_demo_buildings()
        items = CRUDService.get_all(STATE_KEY)

    df_buildings = pd.DataFrame(items) if items else pd.DataFrame(columns=[
        "id", "building_code", "name", "typology", "gross_area_m2", "levels_count", "height_m", "status"
    ])

    tab_directory, tab_add, tab_analytics = st.tabs([
        "🏢 Building Directory",
        "➕ Register Building",
        "📊 Spatial Analytics"
    ])

    # ==============================================================================
    # TAB 1: BUILDING DIRECTORY
    # ==============================================================================
    with tab_directory:
        m1, m2, m3, m4 = st.columns(4)
        total_bldgs = len(df_buildings)
        total_gfa = df_buildings["gross_area_m2"].sum() if not df_buildings.empty else 0.0
        avg_levels = df_buildings["levels_count"].mean() if not df_buildings.empty else 0.0
        active_bldgs = len(df_buildings[df_buildings["status"] == "Active Construction"]) if not df_buildings.empty else 0

        m1.metric("Total Buildings", f"{total_bldgs}")
        m2.metric("Gross Floor Area", f"{total_gfa:,.0f} m²")
        m3.metric("Avg Storeys", f"{avg_levels:.1f}")
        m4.metric("Active Projects", f"{active_bldgs}")

        st.divider()

        if not df_buildings.empty:
            st.dataframe(
                df_buildings,
                column_config={
                    "id": "ID",
                    "building_code": "Building Code",
                    "name": "Building Name",
                    "typology": "Typology",
                    "gross_area_m2": st.column_config.NumberColumn("GFA (m²)", format="%.2f m²"),
                    "levels_count": st.column_config.NumberColumn("Levels", format="%d"),
                    "height_m": st.column_config.NumberColumn("Height (m)", format="%.2f m"),
                    "status": "Lifecycle Status",
                },
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No buildings registered.")

    # ==============================================================================
    # TAB 2: REGISTER BUILDING
    # ==============================================================================
    with tab_add:
        col_form, col_del = st.columns([2, 1])

        with col_form:
            st.subheader("Add New Building Entity")
            with st.form("add_building_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    code = st.text_input("Building Code", value=f"BLDG-0{len(items) + 1}")
                    name = st.text_input("Building Name", value="Innovation Tower")
                    typology = st.selectbox("Typology", ["Commercial Office", "Residential", "Mixed-Use", "Industrial", "Healthcare"])
                with c2:
                    gfa = st.number_input("Gross Floor Area (m²)", min_value=100.0, value=12500.0, step=500.0)
                    levels = st.number_input("Number of Levels", min_value=1, value=12, step=1)
                    height = st.number_input("Total Height (m)", min_value=3.0, value=48.0, step=1.0)
                    status = st.selectbox("Lifecycle Status", ["Concept Design", "Detailed Design", "Active Construction", "Commissioned"])

                submitted = st.form_submit_button("➕ Register Building", type="primary")
                if submitted:
                    new_bldg = {
                        "id": f"BLDG-{len(items) + 1:03d}",
                        "building_code": code,
                        "name": name,
                        "typology": typology,
                        "gross_area_m2": float(gfa),
                        "levels_count": int(levels),
                        "height_m": float(height),
                        "status": status,
                    }
                    CRUDService.create(STATE_KEY, new_bldg)
                    st.success(f"Registered `{name}` (`{code}`) successfully!")
                    st.rerun()

        with col_del:
            st.subheader("Manage Records")
            if items:
                bldg_ids = [it["id"] for it in items]
                selected_del = st.selectbox("Select Building ID to Remove", bldg_ids)
                if st.button("🗑️ Delete Selected Building"):
                    CRUDService.delete(STATE_KEY, selected_del)
                    st.warning(f"Removed building `{selected_del}`.")
                    st.rerun()

                st.markdown("---")
                if st.button("RESET Reset to Demo Data"):
                    st.session_state[STATE_KEY] = []
                    _initialize_demo_buildings()
                    st.rerun()

    # ==============================================================================
    # TAB 3: SPATIAL ANALYTICS
    # ==============================================================================
    with tab_analytics:
        if not df_buildings.empty:
            ca1, ca2 = st.columns(2)
            with ca1:
                st.subheader("Gross Floor Area Distribution")
                fig_gfa = px.bar(
                    df_buildings,
                    x="name",
                    y="gross_area_m2",
                    color="typology",
                    labels={"gross_area_m2": "GFA (m²)", "name": "Building Name"},
                )
                fig_gfa.update_layout(
                    height=350,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#CBD5E0"),
                    margin=dict(l=10, r=10, t=10, b=10),
                )
                st.plotly_chart(fig_gfa, use_container_width=True)

            with ca2:
                st.subheader("Building Heights vs Storeys")
                fig_scat = px.scatter(
                    df_buildings,
                    x="levels_count",
                    y="height_m",
                    size="gross_area_m2",
                    color="status",
                    hover_name="name",
                    labels={"levels_count": "Number of Levels", "height_m": "Height (m)"},
                )
                fig_scat.update_layout(
                    height=350,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#CBD5E0"),
                    margin=dict(l=10, r=10, t=10, b=10),
                )
                st.plotly_chart(fig_scat, use_container_width=True)


def _initialize_demo_buildings() -> None:
    demo_buildings = [
        {
            "id": "BLDG-001",
            "building_code": "BLDG-A",
            "name": "Alpha Tower",
            "typology": "Commercial Office",
            "gross_area_m2": 18500.0,
            "levels_count": 16,
            "height_m": 64.0,
            "status": "Active Construction",
        },
        {
            "id": "BLDG-002",
            "building_code": "BLDG-B",
            "name": "Beta Residences",
            "typology": "Residential",
            "gross_area_m2": 12000.0,
            "levels_count": 8,
            "height_m": 28.5,
            "status": "Detailed Design",
        },
        {
            "id": "BLDG-003",
            "building_code": "BLDG-C",
            "name": "Gamma Podium & Retail",
            "typology": "Mixed-Use",
            "gross_area_m2": 6400.0,
            "levels_count": 3,
            "height_m": 14.0,
            "status": "Concept Design",
        },
    ]
    st.session_state[STATE_KEY] = demo_buildings
