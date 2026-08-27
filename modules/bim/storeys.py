"""
IMAGINE Platform — Storeys & Levels Management Engine
Path: modules/bim/storeys.py
App: imagine
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from modules.utils.crud import CRUDService

STATE_KEY = "bim_storeys"
BLDG_KEY = "bim_buildings"


def render() -> None:
    """Renders the building storey levels and elevation profile module."""
    st.title("🏬 Storey Levels & Elevation Schedule")
    st.caption("Manage storey heights, floor elevations, vertical spatial partitioning, and level schedules.")

    items = CRUDService.get_all(STATE_KEY)
    if not items:
        _initialize_demo_storeys()
        items = CRUDService.get_all(STATE_KEY)

    buildings = CRUDService.get_all(BLDG_KEY)
    bldg_options = {b["id"]: f"{b['name']} ({b['building_code']})" for b in buildings} if buildings else {"BLDG-001": "Alpha Tower"}

    df_storeys = pd.DataFrame(items) if items else pd.DataFrame(columns=[
        "id", "storey_code", "building_id", "name", "elevation_m", "height_m", "description"
    ])

    tab_schedule, tab_manage, tab_profile = st.tabs([
        "📜 Storey Schedule",
        "➕ Add / Manage Levels",
        "📊 Vertical Elevation Profile"
    ])

    # ==============================================================================
    # TAB 1: STOREY SCHEDULE
    # ==============================================================================
    with tab_schedule:
        m1, m2, m3, m4 = st.columns(4)
        total_storeys = len(df_storeys)
        max_elev = df_storeys["elevation_m"].max() if not df_storeys.empty else 0.0
        avg_height = df_storeys["height_m"].mean() if not df_storeys.empty else 0.0
        total_building_height = (max_elev + df_storeys[df_storeys["elevation_m"] == max_elev]["height_m"].values[0]) if not df_storeys.empty else 0.0

        m1.metric("Total Storeys", f"{total_storeys}")
        m2.metric("Max Floor Elevation", f"{max_elev:.2f} m")
        m3.metric("Avg Storey Height", f"{avg_height:.2f} m")
        m4.metric("Top Apex Elevation", f"{total_building_height:.2f} m")

        st.divider()

        if not df_storeys.empty:
            c_filter, c_search = st.columns([1, 2])
            with c_filter:
                b_filter = st.selectbox("Filter by Building", ["All"] + list(bldg_options.values()))
            with c_search:
                q = st.text_input("Search Storey Name or Code", "")

            filtered = df_storeys.copy()
            if b_filter != "All":
                b_id = [k for k, v in bldg_options.items() if v == b_filter]
                if b_id:
                    filtered = filtered[filtered["building_id"] == b_id[0]]
            if q:
                filtered = filtered[
                    filtered["name"].str.contains(q, case=False, na=False) |
                    filtered["storey_code"].str.contains(q, case=False, na=False)
                ]

            st.dataframe(
                filtered.sort_values(by="elevation_m", ascending=False),
                column_config={
                    "id": "ID",
                    "storey_code": "Storey Code",
                    "building_id": "Building ID",
                    "name": "Level Name",
                    "elevation_m": st.column_config.NumberColumn("Elevation (m)", format="%.2f m"),
                    "height_m": st.column_config.NumberColumn("Floor-to-Floor Height (m)", format="%.2f m"),
                    "description": "Functional Purpose",
                },
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No storeys registered.")

    # ==============================================================================
    # TAB 2: ADD / MANAGE LEVELS
    # ==============================================================================
    with tab_manage:
        col_add, col_del = st.columns([2, 1])

        with col_add:
            st.subheader("Add New Storey Level")
            with st.form("add_storey_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    code = st.text_input("Storey Code", value=f"L{len(items):02d}")
                    name = st.text_input("Level Name", value=f"Level 0{len(items)}")
                    selected_bldg = st.selectbox("Building", list(bldg_options.keys()), format_func=lambda x: bldg_options.get(x, x))
                with c2:
                    last_elev = df_storeys["elevation_m"].max() + df_storeys["height_m"].iloc[-1] if not df_storeys.empty else 0.0
                    elevation = st.number_input("Floor Elevation (m)", value=float(last_elev), step=0.5)
                    height = st.number_input("Floor-to-Floor Height (m)", min_value=2.0, value=3.80, step=0.1)
                    desc = st.text_input("Description / Usage", value="Office Workstation Area")

                submitted = st.form_submit_button("➕ Register Storey", type="primary")
                if submitted:
                    new_storey = {
                        "id": f"STRY-{len(items) + 1:03d}",
                        "storey_code": code,
                        "building_id": selected_bldg,
                        "name": name,
                        "elevation_m": float(elevation),
                        "height_m": float(height),
                        "description": desc,
                    }
                    CRUDService.create(STATE_KEY, new_storey)
                    st.success(f"Registered level `{name}` successfully!")
                    st.rerun()

        with col_del:
            st.subheader("Manage Records")
            if items:
                stry_ids = [s["id"] for s in items]
                selected_del = st.selectbox("Select Storey ID to Remove", stry_ids)
                if st.button("🗑️ Delete Selected Storey"):
                    CRUDService.delete(STATE_KEY, selected_del)
                    st.warning(f"Removed storey `{selected_del}`.")
                    st.rerun()

                st.markdown("---")
                if st.button("RESET Reset to Demo Data"):
                    st.session_state[STATE_KEY] = []
                    _initialize_demo_storeys()
                    st.rerun()

    # ==============================================================================
    # TAB 3: VERTICAL ELEVATION PROFILE
    # ==============================================================================
    with tab_profile:
        if not df_storeys.empty:
            st.subheader("Vertical Massing & Storey Stacking Profile")
            sorted_df = df_storeys.sort_values(by="elevation_m", ascending=True).copy()
            sorted_df["top_elevation"] = sorted_df["elevation_m"] + sorted_df["height_m"]

            fig = go.Figure()

            for _, row in sorted_df.iterrows():
                fig.add_trace(go.Bar(
                    x=[1],
                    y=[row["height_m"]],
                    base=row["elevation_m"],
                    name=f"{row['storey_code']} — {row['name']}",
                    text=f"<b>{row['name']}</b> ({row['elevation_m']:.1f}m - {row['top_elevation']:.1f}m)",
                    textposition="inside",
                    hoverinfo="text+name",
                ))

            fig.update_layout(
                barmode="stack",
                height=450,
                xaxis=dict(showticklabels=False, title="Vertical Section Profile"),
                yaxis=dict(title="Elevation Above Finished Floor (m)", showgrid=True),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#CBD5E0"),
                showlegend=True,
                margin=dict(l=10, r=10, t=10, b=10),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No storeys available to visualize.")


def _initialize_demo_storeys() -> None:
    demo_storeys = [
        {
            "id": "STRY-001",
            "storey_code": "L00",
            "building_id": "BLDG-001",
            "name": "Ground Level 00",
            "elevation_m": 0.0,
            "height_m": 4.50,
            "description": "Main Entrance Lobby & Reception",
        },
        {
            "id": "STRY-002",
            "storey_code": "L01",
            "building_id": "BLDG-001",
            "name": "Level 01",
            "elevation_m": 4.50,
            "height_m": 3.80,
            "description": "Open Workspace & Conference Center",
        },
        {
            "id": "STRY-003",
            "storey_code": "L02",
            "building_id": "BLDG-001",
            "name": "Level 02",
            "elevation_m": 8.30,
            "height_m": 3.80,
            "description": "Executive Suites & Boardroom",
        },
        {
            "id": "STRY-004",
            "storey_code": "L03",
            "building_id": "BLDG-001",
            "name": "Level 03 — Plant Room",
            "elevation_m": 12.10,
            "height_m": 4.20,
            "description": "MEP Mechanical Floor & Air Handlers",
        },
    ]
    st.session_state[STATE_KEY] = demo_storeys
