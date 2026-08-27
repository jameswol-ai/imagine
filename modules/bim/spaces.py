"""
IMAGINE Platform — Spatial Allocations & Room Directory
Path: modules/bim/spaces.py
App: imagine
"""

import pandas as pd
import plotly.express as px
import streamlit as st
from modules.utils.crud import CRUDService

STATE_KEY = "bim_spaces"
BLDG_KEY = "bim_buildings"


def render() -> None:
    """Renders the space allocations and spatial program manager."""
    st.title("🧩 Space Allocations & Spatial Program")
    st.caption("Manage internal spatial entities, area schedules, room functions, and occupancy loads.")

    # Seed demo data if missing
    spaces = CRUDService.get_all(STATE_KEY)
    if not spaces:
        _initialize_demo_spaces()
        spaces = CRUDService.get_all(STATE_KEY)

    buildings = CRUDService.get_all(BLDG_KEY)
    bldg_options = {b["id"]: f"{b['name']} ({b['building_code']})" for b in buildings} if buildings else {"BLDG-001": "Alpha Tower"}

    df_spaces = pd.DataFrame(spaces) if spaces else pd.DataFrame(columns=[
        "id", "space_code", "name", "building_id", "level", "usage_type", "net_area_m2", "capacity"
    ])

    tab_list, tab_add, tab_analytics = st.tabs([
        "📋 Space Inventory",
        "➕ Allocate Space",
        "📈 Spatial Allocation Charts"
    ])

    # ==============================================================================
    # TAB 1: SPACE INVENTORY
    # ==============================================================================
    with tab_list:
        m1, m2, m3, m4 = st.columns(4)
        total_spaces = len(df_spaces)
        total_net_area = df_spaces["net_area_m2"].sum() if not df_spaces.empty else 0.0
        total_cap = df_spaces["capacity"].sum() if not df_spaces.empty else 0
        avg_space_size = total_net_area / total_spaces if total_spaces > 0 else 0.0

        m1.metric("Total Spaces", f"{total_spaces}")
        m2.metric("Total Net Usable Area", f"{total_net_area:,.1f} m²")
        m3.metric("Total Design Capacity", f"{total_cap} occupants")
        m4.metric("Avg Space Area", f"{avg_space_size:.1f} m²")

        st.divider()

        if not df_spaces.empty:
            c_filter, c_search = st.columns([1, 2])
            with c_filter:
                usages = ["All"] + list(df_spaces["usage_type"].unique())
                sel_usage = st.selectbox("Filter by Usage Type", usages)
            with c_search:
                q = st.text_input("Search Space Code or Name", "")

            filtered = df_spaces.copy()
            if sel_usage != "All":
                filtered = filtered[filtered["usage_type"] == sel_usage]
            if q:
                filtered = filtered[
                    filtered["name"].str.contains(q, case=False, na=False) |
                    filtered["space_code"].str.contains(q, case=False, na=False)
                ]

            st.dataframe(
                filtered,
                column_config={
                    "id": "ID",
                    "space_code": "Space Code",
                    "name": "Space Name",
                    "building_id": "Building ID",
                    "level": "Level / Storey",
                    "usage_type": "Usage Type",
                    "net_area_m2": st.column_config.NumberColumn("Net Area (m²)", format="%.2f m²"),
                    "capacity": st.column_config.NumberColumn("Max Capacity", format="%d pax"),
                },
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No spatial allocations registered.")

    # ==============================================================================
    # TAB 2: ALLOCATE SPACE
    # ==============================================================================
    with tab_add:
        col_form, col_del = st.columns([2, 1])

        with col_form:
            st.subheader("Create New Space Entity")
            with st.form("add_space_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    code = st.text_input("Space Code", value=f"SPC-{len(spaces) + 1:03d}")
                    name = st.text_input("Space Name", value="Executive Boardroom")
                    selected_bldg = st.selectbox("Target Building", list(bldg_options.keys()), format_func=lambda x: bldg_options.get(x, x))
                    level = st.selectbox("Level", ["Level 00 (Ground)", "Level 01", "Level 02", "Level 03", "Level 04", "Roof Level"])
                with c2:
                    usage = st.selectbox("Usage Category", ["Office / Workstation", "Meeting / Conference", "Circulation / Core", "MEP / Plant", "Restroom / Wet", "Retail / Dining"])
                    area = st.number_input("Net Area (m²)", min_value=1.0, value=45.0, step=5.0)
                    cap = st.number_input("Design Occupancy (Persons)", min_value=0, value=16, step=1)

                submitted = st.form_submit_button("➕ Save Space Entity", type="primary")
                if submitted:
                    new_spc = {
                        "id": f"SPC-{len(spaces) + 1:03d}",
                        "space_code": code,
                        "name": name,
                        "building_id": selected_bldg,
                        "level": level,
                        "usage_type": usage,
                        "net_area_m2": float(area),
                        "capacity": int(cap),
                    }
                    CRUDService.create(STATE_KEY, new_spc)
                    st.success(f"Registered space `{name}` (`{code}`) successfully!")
                    st.rerun()

        with col_del:
            st.subheader("Manage Space Records")
            if spaces:
                spc_ids = [s["id"] for s in spaces]
                selected_del = st.selectbox("Select Space ID to Delete", spc_ids)
                if st.button("🗑️ Delete Selected Space"):
                    CRUDService.delete(STATE_KEY, selected_del)
                    st.warning(f"Removed space `{selected_del}`.")
                    st.rerun()

                st.markdown("---")
                if st.button("RESET Reset to Demo Data"):
                    st.session_state[STATE_KEY] = []
                    _initialize_demo_spaces()
                    st.rerun()

    # ==============================================================================
    # TAB 3: SPATIAL ALLOCATION CHARTS
    # ==============================================================================
    with tab_analytics:
        if not df_spaces.empty:
            ca1, ca2 = st.columns(2)

            with ca1:
                st.subheader("Area Allocation by Usage Type")
                fig_tree = px.treemap(
                    df_spaces,
                    path=["usage_type", "name"],
                    values="net_area_m2",
                    color="net_area_m2",
                    color_continuous_scale="Viridis",
                )
                fig_tree.update_layout(
                    height=350,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#CBD5E0"),
                    margin=dict(l=10, r=10, t=10, b=10),
                )
                st.plotly_chart(fig_tree, use_container_width=True)

            with ca2:
                st.subheader("Occupancy Capacity by Storey")
                cap_chart = df_spaces.groupby("level")["capacity"].sum().reset_index()
                fig_bar = px.bar(
                    cap_chart,
                    x="level",
                    y="capacity",
                    labels={"level": "Storey Level", "capacity": "Design Occupants"},
                    color_discrete_sequence=["#38A169"],
                )
                fig_bar.update_layout(
                    height=350,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#CBD5E0"),
                    margin=dict(l=10, r=10, t=10, b=10),
                )
                st.plotly_chart(fig_bar, use_container_width=True)


def _initialize_demo_spaces() -> None:
    demo_spaces = [
        {
            "id": "SPC-001",
            "space_code": "OFF-101",
            "name": "Open Plan Workspace A",
            "building_id": "BLDG-001",
            "level": "Level 01",
            "usage_type": "Office / Workstation",
            "net_area_m2": 350.0,
            "capacity": 45,
        },
        {
            "id": "SPC-002",
            "space_code": "CONF-102",
            "name": "Main Auditorium",
            "building_id": "BLDG-001",
            "level": "Level 01",
            "usage_type": "Meeting / Conference",
            "net_area_m2": 180.0,
            "capacity": 90,
        },
        {
            "id": "SPC-003",
            "space_code": "MEP-001",
            "name": "Chiller & Transformer Room",
            "building_id": "BLDG-001",
            "level": "Level 00 (Ground)",
            "usage_type": "MEP / Plant",
            "net_area_m2": 220.0,
            "capacity": 4,
        },
        {
            "id": "SPC-004",
            "space_code": "CORE-101",
            "name": "Central Elevator Lobby",
            "building_id": "BLDG-001",
            "level": "Level 01",
            "usage_type": "Circulation / Core",
            "net_area_m2": 95.0,
            "capacity": 20,
        },
    ]
    st.session_state[STATE_KEY] = demo_spaces
