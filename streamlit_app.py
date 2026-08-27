# streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import requests
import json
import traceback
import random

# ---------------------------
# Configuration
# ---------------------------
USE_MOCK = True  # Set to False to use real backend API
API_BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8000/api/v1")

# ---------------------------
# Page config
# ---------------------------
st.set_page_config(
    page_title="IMAGINE Platform",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------
# Authentication (auto-login)
# ---------------------------
def check_authentication():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = True
        st.session_state.token = "dummy-token"
        st.session_state.user = "Demo User"
        st.session_state.role = "Admin"
check_authentication()

# ---------------------------
# API client functions (used if USE_MOCK is False)
# ---------------------------
def api_get(endpoint, params=None):
    if USE_MOCK:
        return None
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    url = f"{API_BASE_URL}/{endpoint}"
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API error: {e}")
        return None

def api_post(endpoint, data):
    if USE_MOCK:
        return data
    headers = {"Authorization": f"Bearer {st.session_state.token}", "Content-Type": "application/json"}
    url = f"{API_BASE_URL}/{endpoint}"
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API error: {e}")
        return None

def api_put(endpoint, data):
    if USE_MOCK:
        return data
    headers = {"Authorization": f"Bearer {st.session_state.token}", "Content-Type": "application/json"}
    url = f"{API_BASE_URL}/{endpoint}"
    try:
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API error: {e}")
        return None

def api_delete(endpoint):
    if USE_MOCK:
        return True
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    url = f"{API_BASE_URL}/{endpoint}"
    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"API error: {e}")
        return False

# ---------------------------
# Initialise mock data in session state (FIXED)
# ---------------------------
def init_mock_data():
    # Projects
    if "projects_data" not in st.session_state or not st.session_state.projects_data:
        st.session_state.projects_data = [
            {"id": 1, "name": "Green Tower", "status": "active", "budget": 12.5, "progress": 75},
            {"id": 2, "name": "Harbor Bridge", "status": "planning", "budget": 8.3, "progress": 20},
            {"id": 3, "name": "Riverside Mall", "status": "completed", "budget": 22.1, "progress": 100},
            {"id": 4, "name": "Solar Park", "status": "active", "budget": 5.7, "progress": 45},
        ]
    # BIM - Buildings
    if "buildings_data" not in st.session_state or not st.session_state.buildings_data:
        st.session_state.buildings_data = [
            {"id": 1, "name": "Tower A", "storeys": 25, "area": 15000, "ifc_version": "IFC4", "description": "Main office tower"},
            {"id": 2, "name": "Tower B", "storeys": 18, "area": 12000, "ifc_version": "IFC4", "description": "Secondary tower"},
            {"id": 3, "name": "Pavilion", "storeys": 3, "area": 2500, "ifc_version": "IFC2x3", "description": "Event space"},
        ]
        # Storeys for each building (will be stored as nested dict)
        if "storeys_data" not in st.session_state:
            st.session_state.storeys_data = {}
        for b in st.session_state.buildings_data:
            b_id = b["id"]
            if b_id not in st.session_state.storeys_data:
                st.session_state.storeys_data[b_id] = [
                    {"id": (b_id*100 + i), "level": f"Level {i}", "height": 4.0 + (i%2)*0.2, "area": 1200 - i*10}
                    for i in range(1, min(b["storeys"], 5)+1)
                ]
        # Spaces for each storey (will be stored as nested dict)
        if "spaces_data" not in st.session_state:
            st.session_state.spaces_data = {}
        space_id_counter = 1
        for b in st.session_state.buildings_data:
            b_id = b["id"]
            storeys = st.session_state.storeys_data.get(b_id, [])
            for s in storeys:
                key = f"{b_id}_{s['id']}"
                if key not in st.session_state.spaces_data:
                    st.session_state.spaces_data[key] = []
                    for i in range(1, 4):
                        st.session_state.spaces_data[key].append({
                            "id": space_id_counter,
                            "name": f"Space {i}",
                            "space_type": ["Office", "Conference", "Lobby"][i % 3],
                            "area": 20 + i * 5,
                            "height": 3.0 + (i % 2) * 0.5
                        })
                        space_id_counter += 1

    # Architecture - Zoning
    if "zoning_data" not in st.session_state or not st.session_state.zoning_data:
        st.session_state.zoning_data = [
            {"id": 1, "zone_type": "Residential", "max_height": 15, "coverage": 50, "setback": 3},
            {"id": 2, "zone_type": "Commercial", "max_height": 30, "coverage": 60, "setback": 5},
            {"id": 3, "zone_type": "Mixed-Use", "max_height": 45, "coverage": 70, "setback": 4},
        ]
    # Architecture - Room Programming
    if "room_program_data" not in st.session_state or not st.session_state.room_program_data:
        st.session_state.room_program_data = [
            {"id": 1, "room_name": "Office", "area": 20, "quantity": 10, "adjacency": "Corridor"},
            {"id": 2, "room_name": "Conference", "area": 40, "quantity": 2, "adjacency": "Lobby"},
            {"id": 3, "room_name": "Lobby", "area": 60, "quantity": 1, "adjacency": "Entrance"},
            {"id": 4, "room_name": "Restroom", "area": 10, "quantity": 4, "adjacency": "Corridor"},
        ]

    # Structural - Beams
    if "beam_data" not in st.session_state or not st.session_state.beam_data:
        st.session_state.beam_data = [
            {"id": 1, "beam_id": "B-101", "span": 6.5, "load": 45, "material": "Concrete C30/37", "status": "OK"},
            {"id": 2, "beam_id": "B-102", "span": 8.2, "load": 60, "material": "Concrete C30/37", "status": "Overstressed"},
            {"id": 3, "beam_id": "B-201", "span": 5.0, "load": 30, "material": "Steel S355", "status": "OK"},
            {"id": 4, "beam_id": "B-202", "span": 7.0, "load": 50, "material": "Steel S355", "status": "OK"},
        ]
    # Structural - Columns
    if "column_data" not in st.session_state or not st.session_state.column_data:
        st.session_state.column_data = [
            {"id": 1, "column_id": "C-1", "axial_load": 1200, "section": "400x400", "reinforcement_ratio": 1.5},
            {"id": 2, "column_id": "C-2", "axial_load": 800, "section": "300x300", "reinforcement_ratio": 1.2},
            {"id": 3, "column_id": "C-3", "axial_load": 1500, "section": "500x500", "reinforcement_ratio": 2.0},
            {"id": 4, "column_id": "C-4", "axial_load": 950, "section": "350x350", "reinforcement_ratio": 1.3},
        ]
    # Structural - Slabs
    if "slab_data" not in st.session_state or not st.session_state.slab_data:
        st.session_state.slab_data = [
            {"id": 1, "slab_id": "S1", "thickness": 200, "span": 6, "load": 5},
            {"id": 2, "slab_id": "S2", "thickness": 150, "span": 4, "load": 4},
            {"id": 3, "slab_id": "S3", "thickness": 250, "span": 7, "load": 6},
            {"id": 4, "slab_id": "S4", "thickness": 180, "span": 5, "load": 4.5},
        ]
    # Structural - Foundations
    if "foundation_data" not in st.session_state or not st.session_state.foundation_data:
        st.session_state.foundation_data = [
            {"id": 1, "foundation_type": "Pad", "capacity": 800, "depth": 1.5},
            {"id": 2, "foundation_type": "Strip", "capacity": 500, "depth": 1.0},
            {"id": 3, "foundation_type": "Pile", "capacity": 1200, "depth": 12},
            {"id": 4, "foundation_type": "Raft", "capacity": 1500, "depth": 0.8},
        ]
    # Structural - Retaining Walls
    if "retaining_data" not in st.session_state or not st.session_state.retaining_data:
        st.session_state.retaining_data = [
            {"id": 1, "wall_id": "RW-1", "height": 4.5, "thickness": 0.3, "stability": "OK"},
            {"id": 2, "wall_id": "RW-2", "height": 6.0, "thickness": 0.4, "stability": "OK"},
            {"id": 3, "wall_id": "RW-3", "height": 3.2, "thickness": 0.25, "stability": "Warning"},
        ]
    # Structural - Steel Connections
    if "connection_data" not in st.session_state or not st.session_state.connection_data:
        st.session_state.connection_data = [
            {"id": 1, "connection_type": "Moment", "bolts": "M20", "capacity": 200},
            {"id": 2, "connection_type": "Shear", "bolts": "M16", "capacity": 120},
            {"id": 3, "connection_type": "Base Plate", "bolts": "M24", "capacity": 350},
            {"id": 4, "connection_type": "Brace", "bolts": "M22", "capacity": 180},
        ]
    # MEP - Electrical
    if "electrical_data" not in st.session_state or not st.session_state.electrical_data:
        st.session_state.electrical_data = [
            {"id": 1, "panel": "MDP-1", "total_load": 250, "reserve": 20},
            {"id": 2, "panel": "MDP-2", "total_load": 180, "reserve": 15},
            {"id": 3, "panel": "MDP-3", "total_load": 90, "reserve": 25},
        ]
    # Costing - BOQ
    if "boq_data" not in st.session_state or not st.session_state.boq_data:
        st.session_state.boq_data = [
            {"id": 1, "item": "Concrete C30", "quantity": 500, "unit": "m³", "rate": 120, "total": 60000},
            {"id": 2, "item": "Steel Rebar", "quantity": 120, "unit": "t", "rate": 950, "total": 114000},
            {"id": 3, "item": "Finishes", "quantity": 300, "unit": "m²", "rate": 75, "total": 22500},
            {"id": 4, "item": "MEP", "quantity": 80, "unit": "LF", "rate": 60, "total": 4800},
            {"id": 5, "item": "Excavation", "quantity": 200, "unit": "m³", "rate": 40, "total": 8000},
        ]
    # Construction - RFIs
    if "rfi_data" not in st.session_state or not st.session_state.rfi_data:
        st.session_state.rfi_data = [
            {"id": 1, "rfi_number": "RFI-001", "subject": "Rebar spacing", "status": "Open"},
            {"id": 2, "rfi_number": "RFI-002", "subject": "Window detail", "status": "Answered"},
            {"id": 3, "rfi_number": "RFI-003", "subject": "MEP coordination", "status": "Closed"},
            {"id": 4, "rfi_number": "RFI-004", "subject": "Concrete mix", "status": "Pending"},
        ]
    # Digital Twin - Sensors
    if "sensor_data" not in st.session_state or not st.session_state.sensor_data:
        st.session_state.sensor_data = [
            {"id": 1, "sensor_id": "TEMP-01", "location": "Lobby", "value": 23.5, "unit": "°C"},
            {"id": 2, "sensor_id": "HUM-01", "location": "Lobby", "value": 42, "unit": "%"},
            {"id": 3, "sensor_id": "ENERGY-01", "location": "Main", "value": 320, "unit": "kW"},
            {"id": 4, "sensor_id": "OCC-01", "location": "Office", "value": 245, "unit": "people"},
        ]

    # Regional codes (static, not CRUD)
    if "regional_codes" not in st.session_state:
        st.session_state.regional_codes = {
            "Uganda": {"Code": "UNBC 2020", "Seismic Zone": "Zone 3", "Wind Speed": "35 m/s"},
            "Kenya": {"Code": "KBC 2015", "Seismic Zone": "Zone 2", "Wind Speed": "30 m/s"},
            "Tanzania": {"Code": "TBS 2018", "Seismic Zone": "Zone 2", "Wind Speed": "28 m/s"},
            "Rwanda": {"Code": "RBC 2019", "Seismic Zone": "Zone 3", "Wind Speed": "32 m/s"},
            "South Sudan": {"Code": "SSBC 2021", "Seismic Zone": "Zone 1", "Wind Speed": "25 m/s"},
        }

# ---------------------------
# Session state initialisation
# ---------------------------
def init_session_state():
    # Editing states
    edit_vars = [
        "editing_project", "editing_building", "editing_zoning", "editing_room",
        "editing_beam", "editing_column", "editing_slab", "editing_foundation",
        "editing_retaining", "editing_connection", "editing_electrical",
        "editing_boq", "editing_rfi", "editing_sensor"
    ]
    for var in edit_vars:
        if var not in st.session_state:
            st.session_state[var] = None

    # Data variables (will be filled with mock data)
    data_vars = [
        "projects_data", "buildings_data", "zoning_data", "room_program_data",
        "beam_data", "column_data", "slab_data", "foundation_data", "retaining_data",
        "connection_data", "electrical_data", "boq_data", "rfi_data", "sensor_data"
    ]
    for var in data_vars:
        if var not in st.session_state:
            st.session_state[var] = None

    # Load mock data if not already loaded
    if USE_MOCK:
        init_mock_data()

init_session_state()

# ---------------------------
# Helper: get data from session state (mock) or API
# ---------------------------
def get_data(key, api_endpoint=None):
    if USE_MOCK:
        return st.session_state.get(key, [])
    else:
        if api_endpoint:
            return api_get(api_endpoint)
        return st.session_state.get(key, [])

def set_data(key, data):
    st.session_state[key] = data

# ---------------------------
# Helper for generic CRUD table (mock-friendly)
# ---------------------------
def crud_table(data_key, item_name, endpoint, id_field="id", display_fields=None, edit_fields=None, add_fields=None):
    data = st.session_state.get(data_key, [])
    if not data:
        st.info(f"No {item_name} data available.")
        return

    if display_fields is None:
        display_fields = list(data[0].keys()) if data else []

    for idx, item in enumerate(data):
        cols = st.columns([2] * len(display_fields) + [1, 1])
        for i, field in enumerate(display_fields):
            with cols[i]:
                st.write(item.get(field, ''))
        with cols[-2]:
            if st.button("✏️", key=f"edit_{item_name}_{item[id_field]}"):
                st.session_state[f"editing_{item_name}"] = item
        with cols[-1]:
            if st.button("🗑️", key=f"del_{item_name}_{item[id_field]}"):
                if st.checkbox(f"Confirm delete?", key=f"confirm_{item_name}_{item[id_field]}"):
                    if USE_MOCK:
                        new_data = [d for d in data if d[id_field] != item[id_field]]
                        st.session_state[data_key] = new_data
                        st.success(f"{item_name.capitalize()} deleted!")
                        st.rerun()
                    else:
                        if api_delete(f"{endpoint}/{item[id_field]}"):
                            st.success(f"{item_name.capitalize()} deleted!")
                            st.session_state[data_key] = api_get(endpoint)
                            st.rerun()
                        else:
                            st.error("Delete failed.")

        editing_key = f"editing_{item_name}"
        if st.session_state.get(editing_key, {}).get(id_field) == item.get(id_field):
            with st.expander(f"Edit {item.get('name', item.get('level', ''))}", expanded=True):
                with st.form(key=f"edit_{item_name}_form_{item[id_field]}"):
                    edit_values = {}
                    for field, input_type in edit_fields.items():
                        if input_type == "text":
                            edit_values[field] = st.text_input(field.capitalize(), value=item.get(field, ''))
                        elif input_type == "number":
                            edit_values[field] = st.number_input(field.capitalize(), value=item.get(field, 0.0), step=0.1)
                        elif input_type == "select":
                            edit_values[field] = st.selectbox(field.capitalize(), item.get('options', []), index=item.get('options', []).index(item.get(field)) if item.get(field) in item.get('options', []) else 0)
                    if st.form_submit_button("Update"):
                        if USE_MOCK:
                            for d in data:
                                if d[id_field] == item[id_field]:
                                    for k, v in edit_values.items():
                                        d[k] = v
                                    break
                            st.session_state[data_key] = data
                            st.success(f"{item_name.capitalize()} updated!")
                            st.session_state[editing_key] = None
                            st.rerun()
                        else:
                            result = api_put(f"{endpoint}/{item[id_field]}", edit_values)
                            if result:
                                st.success(f"{item_name.capitalize()} updated!")
                                st.session_state[data_key] = api_get(endpoint)
                                st.session_state[editing_key] = None
                                st.rerun()
                            else:
                                st.error("Update failed.")
            if st.button("Cancel", key=f"cancel_{item_name}_edit_{item[id_field]}"):
                st.session_state[editing_key] = None
                st.rerun()

    with st.expander(f"➕ Add New {item_name.capitalize()}"):
        with st.form(key=f"new_{item_name}_form"):
            add_values = {}
            add_fields_to_use = add_fields if add_fields is not None else edit_fields
            for field, input_type in add_fields_to_use.items():
                if input_type == "text":
                    add_values[field] = st.text_input(field.capitalize())
                elif input_type == "number":
                    add_values[field] = st.number_input(field.capitalize(), value=0.0, step=0.1)
                elif input_type == "select":
                    add_values[field] = st.selectbox(field.capitalize(), item.get('options', []))
            if st.form_submit_button("Create"):
                if USE_MOCK:
                    new_id = max([d[id_field] for d in data]) + 1 if data else 1
                    add_values[id_field] = new_id
                    data.append(add_values)
                    st.session_state[data_key] = data
                    st.success(f"{item_name.capitalize()} created!")
                    st.rerun()
                else:
                    result = api_post(endpoint, add_values)
                    if result:
                        st.success(f"{item_name.capitalize()} created!")
                        st.session_state[data_key] = api_get(endpoint)
                        st.rerun()
                    else:
                        st.error("Creation failed.")

# ---------------------------
# Navigation Sidebar
# ---------------------------
st.sidebar.title("🏗️ IMAGINE")
st.sidebar.markdown(f"Welcome, **{st.session_state.user}**")
st.sidebar.markdown(f"Role: `{st.session_state.role}`")
if USE_MOCK:
    st.sidebar.info("⚡ Mock Mode (no backend)")
else:
    st.sidebar.info("🔗 Connected to backend")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Projects",
        "Architecture",
        "BIM",
        "Structural",
        "MEP",
        "Costing",
        "Construction",
        "Regional",
        "Digital Twin",
        "AI Assistant",
        "Analytics",
    ],
)

# ---------------------------
# PAGE: DASHBOARD
# ---------------------------
def page_dashboard():
    st.title("📊 Dashboard")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Active Projects", "12", "+2")
    col2.metric("Total Budget", "$184M", "+5%")
    col3.metric("Progress (avg)", "68%", "+12%")
    col4.metric("Open RFIs", "7", "-3")

    st.subheader("Project Health")
    if USE_MOCK:
        projects = st.session_state.projects_data
    else:
        projects = api_get("projects")
    if projects:
        df = pd.DataFrame(projects)
        if not df.empty:
            fig = px.bar(df, x="name", y="progress", color="status", text="progress")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No projects found.")
    else:
        st.warning("Could not fetch projects.")

    st.subheader("Recent Activity")
    activity = pd.DataFrame({
        "Time": [datetime.now() - timedelta(hours=i) for i in range(5)],
        "User": ["Alice", "Bob", "Charlie", "Alice", "Dave"],
        "Action": ["Updated BOQ", "Submitted RFI", "Approved revision", "Added drawing", "Closed snag"],
    })
    st.dataframe(activity, use_container_width=True)

# ---------------------------
# PAGE: PROJECTS (CRUD)
# ---------------------------
def page_projects():
    st.title("📁 Projects")
    if st.button("🔄 Refresh"):
        if not USE_MOCK:
            st.session_state.projects_data = api_get("projects")
        st.rerun()
    crud_table("projects_data", "project", "projects",
               display_fields=["name", "status", "budget", "progress"],
               edit_fields={"name": "text", "status": "text", "budget": "number", "progress": "number"},
               add_fields={"name": "text", "status": "text", "budget": "number", "progress": "number"})

# ---------------------------
# PAGE: ARCHITECTURE (Zoning and Room Program)
# ---------------------------
def page_architecture():
    st.title("📐 Architecture")
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Generative Design", "Zoning", "Site Planning", "Floor Planning", "Room Programming", "Compliance"
    ])
    with tab1:
        st.info("Generative Design: run algorithms to generate design options. (Mock)")
    with tab2:
        st.subheader("Zoning")
        if st.button("🔄 Refresh Zoning"):
            if not USE_MOCK:
                st.session_state.zoning_data = api_get("architecture/zoning")
            st.rerun()
        crud_table("zoning_data", "zoning", "architecture/zoning",
                   display_fields=["zone_type", "max_height", "coverage", "setback"],
                   edit_fields={"zone_type": "text", "max_height": "number", "coverage": "number", "setback": "number"},
                   add_fields={"zone_type": "text", "max_height": "number", "coverage": "number", "setback": "number"})
    with tab3:
        st.info("Site Planning: manage site area, slope, soil type, orientation. (Coming soon)")
    with tab4:
        st.info("Floor Planning: generate and manage floor plans. (Coming soon)")
    with tab5:
        st.subheader("Room Programming")
        if st.button("🔄 Refresh Rooms"):
            if not USE_MOCK:
                st.session_state.room_program_data = api_get("architecture/room_programming")
            st.rerun()
        crud_table("room_program_data", "room", "architecture/room_programming",
                   display_fields=["room_name", "area", "quantity", "adjacency"],
                   edit_fields={"room_name": "text", "area": "number", "quantity": "number", "adjacency": "text"},
                   add_fields={"room_name": "text", "area": "number", "quantity": "number", "adjacency": "text"})
    with tab6:
        st.info("Compliance: check against building codes. (Coming soon)")

# ---------------------------
# PAGE: BIM (Buildings, Storeys, Spaces)
# ---------------------------
def page_bim():
    st.title("🏛️ BIM")
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Buildings", "Storeys", "Spaces", "Elements", "IFC Viewer", "COBie", "Digital Twin"
    ])

    with tab1:
        st.subheader("Buildings")
        if st.button("🔄 Refresh Buildings"):
            if not USE_MOCK:
                st.session_state.buildings_data = api_get("bim/buildings")
            st.rerun()
        crud_table("buildings_data", "building", "bim/buildings",
                   display_fields=["name", "storeys", "area", "ifc_version"],
                   edit_fields={"name": "text", "storeys": "number", "area": "number", "ifc_version": "text"},
                   add_fields={"name": "text", "storeys": "number", "area": "number", "ifc_version": "text"})

    with tab2:
        st.subheader("Storeys")
        buildings = st.session_state.buildings_data
        if not buildings:
            st.warning("Please create a building first.")
            return
        building_names = {b["id"]: b["name"] for b in buildings}
        selected_building_id = st.selectbox(
            "Select Building",
            options=list(building_names.keys()),
            format_func=lambda x: building_names[x],
            key="storey_building_select"
        )
        if selected_building_id:
            if "storeys_data" not in st.session_state:
                st.session_state.storeys_data = {}
            if selected_building_id not in st.session_state.storeys_data:
                st.session_state.storeys_data[selected_building_id] = []
            storeys = st.session_state.storeys_data[selected_building_id]

            for storey in storeys:
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])
                with col1:
                    st.write(storey.get("level", ""))
                with col2:
                    st.write(storey.get("height", 0))
                with col3:
                    st.write(storey.get("area", 0))
                with col4:
                    if st.button("✏️", key=f"edit_storey_{storey['id']}"):
                        st.session_state[f"editing_storey_{selected_building_id}"] = storey
                with col5:
                    if st.button("🗑️", key=f"del_storey_{storey['id']}"):
                        if st.checkbox(f"Confirm delete?", key=f"confirm_storey_{storey['id']}"):
                            st.session_state.storeys_data[selected_building_id] = [s for s in storeys if s['id'] != storey['id']]
                            st.success("Storey deleted!")
                            st.rerun()

                editing_key = f"editing_storey_{selected_building_id}"
                if st.session_state.get(editing_key, {}).get("id") == storey.get("id"):
                    with st.expander(f"Edit {storey.get('level', '')}", expanded=True):
                        with st.form(key=f"edit_storey_form_{storey['id']}"):
                            new_level = st.text_input("Level", value=storey.get('level', ''))
                            new_height = st.number_input("Height (m)", value=storey.get('height', 0.0), step=0.1)
                            new_area = st.number_input("Area (m²)", value=storey.get('area', 0.0), step=10.0)
                            if st.form_submit_button("Update"):
                                for s in st.session_state.storeys_data[selected_building_id]:
                                    if s['id'] == storey['id']:
                                        s['level'] = new_level
                                        s['height'] = new_height
                                        s['area'] = new_area
                                        break
                                st.success("Storey updated!")
                                st.session_state[editing_key] = None
                                st.rerun()
                    if st.button("Cancel", key=f"cancel_storey_edit_{storey['id']}"):
                        st.session_state[editing_key] = None
                        st.rerun()

            with st.expander("➕ Add New Storey"):
                with st.form("new_storey_form"):
                    level = st.text_input("Level (e.g., Level 1, Ground Floor)")
                    height = st.number_input("Height (m)", step=0.1, value=3.5)
                    area = st.number_input("Area (m²)", step=10.0, value=100.0)
                    if st.form_submit_button("Create"):
                        new_id = max([s['id'] for s in storeys]) + 1 if storeys else 1
                        st.session_state.storeys_data[selected_building_id].append({
                            "id": new_id,
                            "level": level,
                            "height": height,
                            "area": area,
                            "building_id": selected_building_id
                        })
                        st.success("Storey created!")
                        st.rerun()

    with tab3:
        st.subheader("Spaces")
        buildings = st.session_state.buildings_data
        if not buildings:
            st.warning("Please create a building first.")
            return
        building_names = {b["id"]: b["name"] for b in buildings}
        selected_building_id = st.selectbox(
            "Select Building",
            options=list(building_names.keys()),
            format_func=lambda x: building_names[x],
            key="space_building_select"
        )
        if selected_building_id:
            if "storeys_data" not in st.session_state:
                st.session_state.storeys_data = {}
            if selected_building_id not in st.session_state.storeys_data:
                st.session_state.storeys_data[selected_building_id] = []
            storeys = st.session_state.storeys_data[selected_building_id]
            if not storeys:
                st.warning("Please create a storey first.")
                return
            storey_options = {s["id"]: s["level"] for s in storeys}
            selected_storey_id = st.selectbox(
                "Select Storey",
                options=list(storey_options.keys()),
                format_func=lambda x: storey_options[x],
                key="space_storey_select"
            )
            if selected_storey_id:
                if "spaces_data" not in st.session_state:
                    st.session_state.spaces_data = {}
                key = f"{selected_building_id}_{selected_storey_id}"
                if key not in st.session_state.spaces_data:
                    st.session_state.spaces_data[key] = []
                spaces = st.session_state.spaces_data[key]

                for space in spaces:
                    col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 1, 1, 1, 1])
                    with col1:
                        st.write(space.get("name", ""))
                    with col2:
                        st.write(space.get("space_type", ""))
                    with col3:
                        st.write(space.get("area", 0))
                    with col4:
                        st.write(space.get("height", 0))
                    with col5:
                        if st.button("✏️", key=f"edit_space_{space['id']}"):
                            st.session_state[f"editing_space_{key}"] = space
                    with col6:
                        if st.button("🗑️", key=f"del_space_{space['id']}"):
                            if st.checkbox(f"Confirm delete?", key=f"confirm_space_{space['id']}"):
                                st.session_state.spaces_data[key] = [s for s in spaces if s['id'] != space['id']]
                                st.success("Space deleted!")
                                st.rerun()

                    editing_key = f"editing_space_{key}"
                    if st.session_state.get(editing_key, {}).get("id") == space.get("id"):
                        with st.expander(f"Edit {space.get('name', '')}", expanded=True):
                            with st.form(key=f"edit_space_form_{space['id']}"):
                                new_name = st.text_input("Name", value=space.get('name', ''))
                                new_type = st.text_input("Space Type", value=space.get('space_type', ''))
                                new_area = st.number_input("Area (m²)", value=space.get('area', 0.0), step=5.0)
                                new_height = st.number_input("Height (m)", value=space.get('height', 0.0), step=0.1)
                                if st.form_submit_button("Update"):
                                    for s in st.session_state.spaces_data[key]:
                                        if s['id'] == space['id']:
                                            s['name'] = new_name
                                            s['space_type'] = new_type
                                            s['area'] = new_area
                                            s['height'] = new_height
                                            break
                                    st.success("Space updated!")
                                    st.session_state[editing_key] = None
                                    st.rerun()
                        if st.button("Cancel", key=f"cancel_space_edit_{space['id']}"):
                            st.session_state[editing_key] = None
                            st.rerun()

                with st.expander("➕ Add New Space"):
                    with st.form("new_space_form"):
                        name = st.text_input("Space Name")
                        space_type = st.text_input("Space Type (e.g., Office, Conference, Lobby)")
                        area = st.number_input("Area (m²)", step=5.0, value=20.0)
                        height = st.number_input("Height (m)", step=0.1, value=3.0)
                        if st.form_submit_button("Create"):
                            new_id = max([s['id'] for s in spaces]) + 1 if spaces else 1
                            st.session_state.spaces_data[key].append({
                                "id": new_id,
                                "name": name,
                                "space_type": space_type,
                                "area": area,
                                "height": height
                            })
                            st.success("Space created!")
                            st.rerun()

    with tab4:
        st.info("Elements management coming soon.")
    with tab5:
        st.info("IFC Viewer coming soon.")
    with tab6:
        st.info("COBie data management coming soon.")
    with tab7:
        st.info("Digital Twin integration coming soon.")

# ---------------------------
# PAGE: STRUCTURAL (all sub-modules)
# ---------------------------
def page_structural():
    st.title("🔩 Structural Engineering")
    tabs = st.tabs([
        "Eurocode", "Beam Design", "Column Design", "Slab Design",
        "Foundation Design", "Retaining Walls", "Steel Connections", "FEA"
    ])

    with tabs[0]:
        st.info("Eurocode parameters (mock)")

    with tabs[1]:
        st.subheader("Beam Design")
        if st.button("🔄 Refresh Beams"):
            if not USE_MOCK:
                st.session_state.beam_data = api_get("structural/beam_design")
            st.rerun()
        crud_table("beam_data", "beam", "structural/beam_design",
                   display_fields=["beam_id", "span", "load", "material", "status"],
                   edit_fields={"beam_id": "text", "span": "number", "load": "number", "material": "text", "status": "text"},
                   add_fields={"beam_id": "text", "span": "number", "load": "number", "material": "text", "status": "text"})

    with tabs[2]:
        st.subheader("Column Design")
        if st.button("🔄 Refresh Columns"):
            if not USE_MOCK:
                st.session_state.column_data = api_get("structural/column_design")
            st.rerun()
        crud_table("column_data", "column", "structural/column_design",
                   display_fields=["column_id", "axial_load", "section", "reinforcement_ratio"],
                   edit_fields={"column_id": "text", "axial_load": "number", "section": "text", "reinforcement_ratio": "number"},
                   add_fields={"column_id": "text", "axial_load": "number", "section": "text", "reinforcement_ratio": "number"})

    with tabs[3]:
        st.subheader("Slab Design")
        if st.button("🔄 Refresh Slabs"):
            if not USE_MOCK:
                st.session_state.slab_data = api_get("structural/slab_design")
            st.rerun()
        crud_table("slab_data", "slab", "structural/slab_design",
                   display_fields=["slab_id", "thickness", "span", "load"],
                   edit_fields={"slab_id": "text", "thickness": "number", "span": "number", "load": "number"},
                   add_fields={"slab_id": "text", "thickness": "number", "span": "number", "load": "number"})

    with tabs[4]:
        st.subheader("Foundation Design")
        if st.button("🔄 Refresh Foundations"):
            if not USE_MOCK:
                st.session_state.foundation_data = api_get("structural/foundation_design")
            st.rerun()
        crud_table("foundation_data", "foundation", "structural/foundation_design",
                   display_fields=["foundation_type", "capacity", "depth"],
                   edit_fields={"foundation_type": "text", "capacity": "number", "depth": "number"},
                   add_fields={"foundation_type": "text", "capacity": "number", "depth": "number"})

    with tabs[5]:
        st.subheader("Retaining Walls")
        if st.button("🔄 Refresh Retaining Walls"):
            if not USE_MOCK:
                st.session_state.retaining_data = api_get("structural/retaining_walls")
            st.rerun()
        crud_table("retaining_data", "retaining", "structural/retaining_walls",
                   display_fields=["wall_id", "height", "thickness", "stability"],
                   edit_fields={"wall_id": "text", "height": "number", "thickness": "number", "stability": "text"},
                   add_fields={"wall_id": "text", "height": "number", "thickness": "number", "stability": "text"})

    with tabs[6]:
        st.subheader("Steel Connections")
        if st.button("🔄 Refresh Connections"):
            if not USE_MOCK:
                st.session_state.connection_data = api_get("structural/steel_connections")
            st.rerun()
        crud_table("connection_data", "connection", "structural/steel_connections",
                   display_fields=["connection_type", "bolts", "capacity"],
                   edit_fields={"connection_type": "text", "bolts": "text", "capacity": "number"},
                   add_fields={"connection_type": "text", "bolts": "text", "capacity": "number"})

    with tabs[7]:
        st.info("FEA analysis coming soon.")

# ---------------------------
# PAGE: MEP
# ---------------------------
def page_mep():
    st.title("⚡ MEP")
    tabs = st.tabs(["Mechanical (HVAC)", "Electrical", "Plumbing"])
    with tabs[0]:
        st.info("HVAC load summary and energy simulation coming soon.")
    with tabs[1]:
        st.subheader("Electrical Load Analysis")
        if st.button("🔄 Refresh Electrical Data"):
            if not USE_MOCK:
                st.session_state.electrical_data = api_get("mep/electrical")
            st.rerun()
        crud_table("electrical_data", "panel", "mep/electrical",
                   display_fields=["panel", "total_load", "reserve"],
                   edit_fields={"panel": "text", "total_load": "number", "reserve": "number"},
                   add_fields={"panel": "text", "total_load": "number", "reserve": "number"})
    with tabs[2]:
        st.info("Plumbing systems coming soon.")

# ---------------------------
# PAGE: COSTING
# ---------------------------
def page_costing():
    st.title("💰 Cost Estimation")
    if st.button("🔄 Refresh BOQ"):
        if not USE_MOCK:
            st.session_state.boq_data = api_get("costing/boq")
        st.rerun()
    crud_table("boq_data", "boq_item", "costing/boq",
               display_fields=["item", "quantity", "unit", "rate", "total"],
               edit_fields={"item": "text", "quantity": "number", "unit": "text", "rate": "number", "total": "number"},
               add_fields={"item": "text", "quantity": "number", "unit": "text", "rate": "number", "total": "number"})

# ---------------------------
# PAGE: CONSTRUCTION
# ---------------------------
def page_construction():
    st.title("🚧 Construction Management")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Progress vs Planned")
        dates = pd.date_range(start="2026-01-01", end="2026-08-19", freq="W")
        planned = list(range(10, 110, 5))[:len(dates)]
        actual = [p - random.randint(0, 8) for p in planned]
        df_progress = pd.DataFrame({"Date": dates, "Planned": planned, "Actual": actual})
        st.line_chart(df_progress.set_index("Date"))
    with col2:
        st.subheader("RFI & Submittals")
        if st.button("🔄 Refresh RFIs"):
            if not USE_MOCK:
                st.session_state.rfi_data = api_get("construction/rfis")
            st.rerun()
        crud_table("rfi_data", "rfi", "construction/rfis",
                   display_fields=["rfi_number", "subject", "status"],
                   edit_fields={"rfi_number": "text", "subject": "text", "status": "text"},
                   add_fields={"rfi_number": "text", "subject": "text", "status": "text"})
    st.subheader("Site Diary")
    diary = st.text_area("Today's Log", height=150, value="2026-08-19: Completed foundation pour for Block A.")
    if st.button("Save Diary Entry"):
        st.success("Diary saved (mock).")

# ---------------------------
# PAGE: REGIONAL
# ---------------------------
def page_regional():
    st.title("🌍 Regional – East Africa Codes")
    df_codes = pd.DataFrame.from_dict(st.session_state.regional_codes, orient='index')
    st.dataframe(df_codes, use_container_width=True)
    with st.expander("Edit Country Codes"):
        for country, codes in st.session_state.regional_codes.items():
            st.markdown(f"**{country}**")
            new_code = st.text_input(f"Code ({country})", value=codes["Code"], key=f"code_{country}")
            new_seismic = st.text_input(f"Seismic Zone ({country})", value=codes["Seismic Zone"], key=f"seismic_{country}")
            new_wind = st.text_input(f"Wind Speed ({country})", value=codes["Wind Speed"], key=f"wind_{country}")
            if st.button(f"Update {country}", key=f"update_{country}"):
                st.session_state.regional_codes[country] = {
                    "Code": new_code,
                    "Seismic Zone": new_seismic,
                    "Wind Speed": new_wind,
                }
                st.success(f"Updated {country}")
                st.rerun()

# ---------------------------
# PAGE: DIGITAL TWIN
# ---------------------------
def page_digital_twin():
    st.title("🔄 Digital Twin – Live Monitoring")
    st.subheader("Sensor Data")
    if st.button("🔄 Refresh Sensors"):
        if not USE_MOCK:
            st.session_state.sensor_data = api_get("digital_twin/sensors")
        st.rerun()
    crud_table("sensor_data", "sensor", "digital_twin/sensors",
               display_fields=["sensor_id", "location", "value", "unit"],
               edit_fields={"sensor_id": "text", "location": "text", "value": "number", "unit": "text"},
               add_fields={"sensor_id": "text", "location": "text", "value": "number", "unit": "text"})

    st.subheader("Historical Energy Consumption")
    now = datetime.now()
    start_time = now - timedelta(days=7)
    times = [start_time + timedelta(hours=i) for i in range(168)]
    energy_vals = [300 + 50 * (i % 24) / 24 for i in range(168)]
    df_energy = pd.DataFrame({"Time": times, "Energy (kW)": energy_vals})
    st.line_chart(df_energy.set_index("Time"))

    if st.button("Run Predictive AI Maintenance"):
        with st.spinner("Analyzing sensor data..."):
            st.success("Prediction: No anomalies detected. Next maintenance in 14 days.")

# ---------------------------
# PAGE: AI ASSISTANT
# ---------------------------
def page_ai():
    st.title("🤖 AI Assistant - IMAGINE Architect")
    st.caption("Ask questions about your project, design, or compliance.")
    prompt = st.text_area("Your query:", "Suggest a column size for a 10-storey building in seismic zone 3.")
    if st.button("Ask AI"):
        with st.spinner("Consulting IMAGINE's knowledge base..."):
            response = """Based on EN 1998-1, for a 10-storey building in seismic zone 3 (Uganda),
            a preliminary column size of 450x450 mm with C30/37 concrete and 8#25 longitudinal bars is recommended.
            Verify with a full analysis."""
            st.success(response)
    st.subheader("RAG - Document Search")
    query = st.text_input("Search project documents:")
    if query:
        results = [
            {"Doc": "Structural_Report_v3.pdf", "Snippet": "... column design based on Eurocode ..."},
            {"Doc": "Architectural_Drawings.dwg", "Snippet": "... dimensions and zoning compliance ..."},
        ]
        st.dataframe(pd.DataFrame(results))

# ---------------------------
# PAGE: ANALYTICS
# ---------------------------
def page_analytics():
    st.title("📈 Analytics & Reporting")
    st.subheader("Portfolio KPIs")
    kpi_data = pd.DataFrame({
        "Project": ["Green Tower", "Harbor Bridge", "Riverside Mall", "Solar Park"],
        "Budget Variance (%)": [-5, 3, 0, -2],
        "Schedule Variance (days)": [12, -8, 5, -3],
        "Safety Index": [0.95, 0.88, 0.92, 0.97],
    })
    st.dataframe(kpi_data, use_container_width=True)
    st.subheader("Cost Forecast")
    forecast = pd.DataFrame({
        "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        "Actual": [120, 135, 140, 155, 160, 175],
        "Forecast": [130, 145, 155, 170, 180, 195],
    })
    st.line_chart(forecast.set_index("Month"))
    st.download_button("Export Report (CSV)", data=forecast.to_csv(), file_name="report.csv")

# ---------------------------
# Route to selected page
# ---------------------------
if page == "Dashboard":
    page_dashboard()
elif page == "Projects":
    page_projects()
elif page == "Architecture":
    page_architecture()
elif page == "BIM":
    page_bim()
elif page == "Structural":
    page_structural()
elif page == "MEP":
    page_mep()
elif page == "Costing":
    page_costing()
elif page == "Construction":
    page_construction()
elif page == "Regional":
    page_regional()
elif page == "Digital Twin":
    page_digital_twin()
elif page == "AI Assistant":
    page_ai()
elif page == "Analytics":
    page_analytics()

# ---------------------------
# Footer
# ---------------------------
st.sidebar.markdown("---")
st.sidebar.caption("IMAGINE Platform v1.0 | 2026")