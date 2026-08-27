# streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import requests
import json
import traceback

# ---------------------------
# Page config
# ---------------------------
st.set_page_config(
    page_title="IMAGINE Platform",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------
# API configuration
# ---------------------------
API_BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8000/api/v1")

# ---------------------------
# Authentication
# ---------------------------
def login(username, password):
    try:
        response = requests.post(f"{API_BASE_URL}/auth/token", data={
            "username": username,
            "password": password
        })
        if response.status_code == 200:
            data = response.json()
            return data["access_token"]
        else:
            st.error("Login failed. Check credentials.")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the backend. Is it running?")
        return None

def check_authentication():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.token = None
        st.session_state.user = None
        st.session_state.role = None

    if not st.session_state.authenticated:
        with st.sidebar:
            st.subheader("🔐 Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Sign In"):
                token = login(username, password)
                if token:
                    st.session_state.authenticated = True
                    st.session_state.token = token
                    st.session_state.user = username
                    st.session_state.role = "Project Manager"  # placeholder
                    st.rerun()
        st.stop()

check_authentication()

# ---------------------------
# API client functions
# ---------------------------
def api_get(endpoint, params=None):
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
# Session state initialisation
# ---------------------------
def init_session_state():
    # Projects
    if "editing_project" not in st.session_state:
        st.session_state.editing_project = None
    if "projects_data" not in st.session_state:
        st.session_state.projects_data = None
    
    # BIM
    if "editing_building" not in st.session_state:
        st.session_state.editing_building = None
    if "buildings_data" not in st.session_state:
        st.session_state.buildings_data = None
    # Storeys and Spaces are dynamic; they will be created as needed.

    # Architecture
    if "editing_zoning" not in st.session_state:
        st.session_state.editing_zoning = None
    if "zoning_data" not in st.session_state:
        st.session_state.zoning_data = None
    if "editing_room" not in st.session_state:
        st.session_state.editing_room = None
    if "room_program_data" not in st.session_state:
        st.session_state.room_program_data = None

    # Structural
    if "editing_beam" not in st.session_state:
        st.session_state.editing_beam = None
    if "beam_data" not in st.session_state:
        st.session_state.beam_data = None
    if "editing_column" not in st.session_state:
        st.session_state.editing_column = None
    if "column_data" not in st.session_state:
        st.session_state.column_data = None
    if "editing_slab" not in st.session_state:
        st.session_state.editing_slab = None
    if "slab_data" not in st.session_state:
        st.session_state.slab_data = None
    if "editing_foundation" not in st.session_state:
        st.session_state.editing_foundation = None
    if "foundation_data" not in st.session_state:
        st.session_state.foundation_data = None
    if "editing_retaining" not in st.session_state:
        st.session_state.editing_retaining = None
    if "retaining_data" not in st.session_state:
        st.session_state.retaining_data = None
    if "editing_connection" not in st.session_state:
        st.session_state.editing_connection = None
    if "connection_data" not in st.session_state:
        st.session_state.connection_data = None

    # MEP
    if "editing_electrical" not in st.session_state:
        st.session_state.editing_electrical = None
    if "electrical_data" not in st.session_state:
        st.session_state.electrical_data = None

    # Costing
    if "editing_boq" not in st.session_state:
        st.session_state.editing_boq = None
    if "boq_data" not in st.session_state:
        st.session_state.boq_data = None

    # Construction
    if "editing_rfi" not in st.session_state:
        st.session_state.editing_rfi = None
    if "rfi_data" not in st.session_state:
        st.session_state.rfi_data = None

    # Digital Twin
    if "editing_sensor" not in st.session_state:
        st.session_state.editing_sensor = None
    if "sensor_data" not in st.session_state:
        st.session_state.sensor_data = None

init_session_state()

# ---------------------------
# Navigation Sidebar
# ---------------------------
st.sidebar.title("🏗️ IMAGINE")
st.sidebar.markdown(f"Welcome, **{st.session_state.user}**")
st.sidebar.markdown(f"Role: `{st.session_state.role}`")
if st.sidebar.button("Sign Out"):
    st.session_state.authenticated = False
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.role = None
    st.rerun()

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
# Helper function for CRUD table (generic)
# ---------------------------
def crud_table(data, item_name, endpoint, id_field="id", display_fields=None, edit_fields=None, add_fields=None):
    """
    Generic function to display a list of items with edit/delete.
    data: list of dicts
    item_name: singular name for labels
    endpoint: API endpoint prefix (e.g., "projects")
    id_field: primary key field name
    display_fields: list of field names to show in columns (if None, show all)
    edit_fields: dict mapping field names to input types for edit form
    add_fields: dict for add form (if None, same as edit_fields)
    """
    if display_fields is None:
        display_fields = list(data[0].keys()) if data else []

    # Show list with edit/delete
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
                    if api_delete(f"{endpoint}/{item[id_field]}"):
                        st.success(f"{item_name.capitalize()} deleted!")
                        # Refresh data
                        st.session_state[f"{item_name}_data"] = api_get(endpoint)
                        st.rerun()
                    else:
                        st.error("Delete failed.")

        # Edit form
        if st.session_state.get(f"editing_{item_name}", {}).get(id_field) == item.get(id_field):
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
                        result = api_put(f"{endpoint}/{item[id_field]}", edit_values)
                        if result:
                            st.success(f"{item_name.capitalize()} updated!")
                            st.session_state[f"{item_name}_data"] = api_get(endpoint)
                            st.session_state[f"editing_{item_name}"] = None
                            st.rerun()
                        else:
                            st.error("Update failed.")
            if st.button("Cancel", key=f"cancel_{item_name}_edit_{item[id_field]}"):
                st.session_state[f"editing_{item_name}"] = None
                st.rerun()

    # Add new item
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
                result = api_post(endpoint, add_values)
                if result:
                    st.success(f"{item_name.capitalize()} created!")
                    st.session_state[f"{item_name}_data"] = api_get(endpoint)
                    st.rerun()
                else:
                    st.error("Creation failed.")

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
    projects = api_get("projects")
    if projects:
        df = pd.DataFrame(projects)
        if not df.empty:
            fig = px.bar(df, x="name", y="progress", color="status", text="progress")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No projects found.")
    else:
        st.warning("Could not fetch projects. Is the backend running?")

    st.subheader("Recent Activity")
    activity = pd.DataFrame({
        "Time": [datetime.now() - timedelta(hours=i) for i in range(5)],
        "User": ["Alice", "Bob", "Charlie", "Alice", "Dave"],
        "Action": ["Updated BOQ", "Submitted RFI", "Approved revision", "Added drawing", "Closed snag"],
    })
    st.dataframe(activity, use_container_width=True)

# ---------------------------
# PAGE: PROJECTS (already full CRUD, kept as is)
# ---------------------------
def page_projects():
    st.title("📁 Projects")
    if st.button("🔄 Refresh Projects"):
        st.session_state.projects_data = api_get("projects")
        st.rerun()
    if st.session_state.projects_data is None:
        st.session_state.projects_data = api_get("projects")
    projects = st.session_state.projects_data
    if projects is None:
        st.warning("No projects found or API error.")
        return
    # Use helper or custom display – we'll keep the existing custom code for projects
    for idx, project in enumerate(projects):
        col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 2, 1, 1])
        with col1:
            st.markdown(f"**{project['name']}**")
        with col2:
            st.write(project.get('status', 'N/A'))
        with col3:
            st.write(f"${project.get('budget', 0):.2f}M")
        with col4:
            st.write(f"{project.get('progress', 0)}%")
        with col5:
            if st.button("✏️", key=f"edit_{project['id']}"):
                st.session_state.editing_project = project
        with col6:
            if st.button("🗑️", key=f"del_{project['id']}"):
                if st.checkbox(f"Confirm delete {project['name']}?", key=f"confirm_{project['id']}"):
                    if api_delete(f"projects/{project['id']}"):
                        st.success("Project deleted!")
                        st.session_state.projects_data = [p for p in st.session_state.projects_data if p['id'] != project['id']]
                        st.rerun()
                    else:
                        st.error("Delete failed.")
        if st.session_state.get("editing_project", {}).get("id") == project.get("id"):
            with st.expander(f"Edit {project['name']}", expanded=True):
                with st.form(key=f"edit_form_{project['id']}"):
                    new_name = st.text_input("Name", value=project['name'])
                    new_status = st.selectbox("Status", ["planning", "active", "on_hold", "completed"], index=["planning", "active", "on_hold", "completed"].index(project.get('status', 'planning')))
                    new_budget = st.number_input("Budget (M USD)", value=project.get('budget', 0.0), step=0.1)
                    new_progress = st.slider("Progress %", 0, 100, project.get('progress', 0))
                    if st.form_submit_button("Update"):
                        updated = {
                            "name": new_name,
                            "status": new_status,
                            "budget": new_budget,
                            "progress": new_progress
                        }
                        result = api_put(f"projects/{project['id']}", updated)
                        if result:
                            st.success("Project updated!")
                            st.session_state.projects_data = api_get("projects")
                            st.session_state.editing_project = None
                            st.rerun()
                        else:
                            st.error("Update failed.")
            if st.button("Cancel", key=f"cancel_edit_{project['id']}"):
                st.session_state.editing_project = None
                st.rerun()
    with st.expander("➕ Add New Project"):
        with st.form("new_project_form"):
            name = st.text_input("Project Name")
            status = st.selectbox("Status", ["planning", "active", "on_hold", "completed"])
            budget = st.number_input("Budget (M USD)", min_value=0.0, step=0.1)
            progress = st.slider("Progress %", 0, 100, 0)
            if st.form_submit_button("Create"):
                new_data = {
                    "name": name,
                    "status": status,
                    "budget": budget,
                    "progress": progress
                }
                result = api_post("projects", new_data)
                if result:
                    st.success("Project created!")
                    st.session_state.projects_data = api_get("projects")
                    st.rerun()
                else:
                    st.error("Creation failed.")

# ---------------------------
# PAGE: ARCHITECTURE (full CRUD for Zoning and Room Programming)
# ---------------------------
def page_architecture():
    st.title("📐 Architecture")
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Generative Design", "Zoning", "Site Planning", "Floor Planning", "Room Programming", "Compliance"
    ])

    with tab1:
        st.info("Generative Design: run algorithms to generate design options. (Coming soon with AI integration)")
        # Placeholder for generative design interface
        if st.button("Run Generative Design"):
            st.success("Generative design simulation started. (Mock)")

    with tab2:
        st.subheader("Zoning")
        # Load zoning data
        if st.button("🔄 Refresh Zoning"):
            st.session_state.zoning_data = api_get("architecture/zoning")
            st.rerun()
        if st.session_state.zoning_data is None:
            st.session_state.zoning_data = api_get("architecture/zoning")
        zoning = st.session_state.zoning_data
        if zoning is None:
            st.warning("No zoning data found.")
            return
        # Use generic CRUD helper
        crud_table(zoning, "zoning", "architecture/zoning",
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
            st.session_state.room_program_data = api_get("architecture/room_programming")
            st.rerun()
        if st.session_state.room_program_data is None:
            st.session_state.room_program_data = api_get("architecture/room_programming")
        rooms = st.session_state.room_program_data
        if rooms is None:
            st.warning("No room program data found.")
            return
        crud_table(rooms, "room", "architecture/room_programming",
                   display_fields=["room_name", "area", "quantity", "adjacency"],
                   edit_fields={"room_name": "text", "area": "number", "quantity": "number", "adjacency": "text"},
                   add_fields={"room_name": "text", "area": "number", "quantity": "number", "adjacency": "text"})

    with tab6:
        st.info("Compliance: check against building codes. (Coming soon)")

# ---------------------------
# PAGE: BIM (already has full CRUD for Buildings, Storeys, Spaces)
# ---------------------------
def page_bim():
    st.title("🏛️ BIM")
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Buildings", "Storeys", "Spaces", "Elements", "IFC Viewer", "COBie", "Digital Twin"
    ])

    with tab1:
        st.subheader("Buildings")
        if st.button("🔄 Refresh Buildings"):
            st.session_state.buildings_data = api_get("bim/buildings")
            st.rerun()
        if st.session_state.buildings_data is None:
            st.session_state.buildings_data = api_get("bim/buildings")
        buildings = st.session_state.buildings_data
        if buildings is None:
            st.warning("No buildings found.")
            return
        for building in buildings:
            col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 2, 1, 1, 1])
            with col1:
                st.markdown(f"**{building.get('name', 'Unnamed')}**")
            with col2:
                st.write(building.get('storeys', 'N/A'))
            with col3:
                st.write(f"{building.get('area', 0)} m²")
            with col4:
                st.write(building.get('ifc_version', 'N/A'))
            with col5:
                if st.button("✏️", key=f"edit_building_{building['id']}"):
                    st.session_state.editing_building = building
            with col6:
                if st.button("🗑️", key=f"del_building_{building['id']}"):
                    if st.checkbox(f"Confirm delete {building.get('name', 'this building')}?", key=f"confirm_building_{building['id']}"):
                        if api_delete(f"bim/buildings/{building['id']}"):
                            st.success("Building deleted!")
                            st.session_state.buildings_data = [b for b in st.session_state.buildings_data if b['id'] != building['id']]
                            st.rerun()
                        else:
                            st.error("Delete failed.")
            if st.session_state.get("editing_building", {}).get("id") == building.get("id"):
                with st.expander(f"Edit {building.get('name', '')}", expanded=True):
                    with st.form(key=f"edit_building_form_{building['id']}"):
                        new_name = st.text_input("Name", value=building.get('name', ''))
                        new_storeys = st.number_input("Storeys", value=building.get('storeys', 0), step=1, min_value=0)
                        new_area = st.number_input("Area (m²)", value=building.get('area', 0.0), step=10.0)
                        new_ifc = st.text_input("IFC Version", value=building.get('ifc_version', ''))
                        new_desc = st.text_area("Description", value=building.get('description', ''))
                        if st.form_submit_button("Update"):
                            updated = {
                                "name": new_name,
                                "storeys": new_storeys,
                                "area": new_area,
                                "ifc_version": new_ifc,
                                "description": new_desc
                            }
                            result = api_put(f"bim/buildings/{building['id']}", updated)
                            if result:
                                st.success("Building updated!")
                                st.session_state.buildings_data = api_get("bim/buildings")
                                st.session_state.editing_building = None
                                st.rerun()
                            else:
                                st.error("Update failed.")
                if st.button("Cancel", key=f"cancel_building_edit_{building['id']}"):
                    st.session_state.editing_building = None
                    st.rerun()
        with st.expander("➕ Add New Building"):
            with st.form("new_building_form"):
                name = st.text_input("Name")
                storeys = st.number_input("Storeys", step=1, min_value=1, value=1)
                area = st.number_input("Area (m²)", step=10.0, value=100.0)
                ifc_version = st.text_input("IFC Version", value="IFC4")
                description = st.text_area("Description")
                if st.form_submit_button("Create"):
                    new_data = {
                        "name": name,
                        "storeys": storeys,
                        "area": area,
                        "ifc_version": ifc_version,
                        "description": description
                    }
                    result = api_post("bim/buildings", new_data)
                    if result:
                        st.success("Building created!")
                        st.session_state.buildings_data = api_get("bim/buildings")
                        st.rerun()
                    else:
                        st.error("Creation failed.")

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
            if st.button("🔄 Refresh Storeys", key="refresh_storeys"):
                st.session_state[f"storeys_{selected_building_id}"] = api_get(f"bim/buildings/{selected_building_id}/storeys")
                st.rerun()
            storeys_key = f"storeys_{selected_building_id}"
            if storeys_key not in st.session_state or st.session_state.get(storeys_key) is None:
                st.session_state[storeys_key] = api_get(f"bim/buildings/{selected_building_id}/storeys")
            storeys = st.session_state.get(storeys_key, [])
            if storeys is None:
                st.warning("Could not load storeys.")
                return
            for storey in storeys:
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])
                with col1:
                    st.markdown(f"**{storey.get('level', 'Unnamed')}**")
                with col2:
                    st.write(f"{storey.get('height', 0)} m")
                with col3:
                    st.write(f"{storey.get('area', 0)} m²")
                with col4:
                    if st.button("✏️", key=f"edit_storey_{storey['id']}"):
                        st.session_state[f"editing_storey_{selected_building_id}"] = storey
                with col5:
                    if st.button("🗑️", key=f"del_storey_{storey['id']}"):
                        if st.checkbox(f"Confirm delete {storey.get('level', 'this storey')}?", key=f"confirm_storey_{storey['id']}"):
                            if api_delete(f"bim/storeys/{storey['id']}"):
                                st.success("Storey deleted!")
                                st.session_state[storeys_key] = api_get(f"bim/buildings/{selected_building_id}/storeys")
                                st.rerun()
                            else:
                                st.error("Delete failed.")
                editing_key = f"editing_storey_{selected_building_id}"
                if st.session_state.get(editing_key, {}).get("id") == storey.get("id"):
                    with st.expander(f"Edit {storey.get('level', '')}", expanded=True):
                        with st.form(key=f"edit_storey_form_{storey['id']}"):
                            new_level = st.text_input("Level", value=storey.get('level', ''))
                            new_height = st.number_input("Height (m)", value=storey.get('height', 0.0), step=0.1)
                            new_area = st.number_input("Area (m²)", value=storey.get('area', 0.0), step=10.0)
                            if st.form_submit_button("Update"):
                                updated = {
                                    "level": new_level,
                                    "height": new_height,
                                    "area": new_area,
                                    "building_id": selected_building_id
                                }
                                result = api_put(f"bim/storeys/{storey['id']}", updated)
                                if result:
                                    st.success("Storey updated!")
                                    st.session_state[storeys_key] = api_get(f"bim/buildings/{selected_building_id}/storeys")
                                    st.session_state[editing_key] = None
                                    st.rerun()
                                else:
                                    st.error("Update failed.")
                    if st.button("Cancel", key=f"cancel_storey_edit_{storey['id']}"):
                        st.session_state[editing_key] = None
                        st.rerun()
            with st.expander("➕ Add New Storey"):
                with st.form("new_storey_form"):
                    level = st.text_input("Level (e.g., Level 1, Ground Floor)")
                    height = st.number_input("Height (m)", step=0.1, value=3.5)
                    area = st.number_input("Area (m²)", step=10.0, value=100.0)
                    if st.form_submit_button("Create"):
                        new_data = {
                            "level": level,
                            "height": height,
                            "area": area,
                            "building_id": selected_building_id
                        }
                        result = api_post("bim/storeys", new_data)
                        if result:
                            st.success("Storey created!")
                            st.session_state[storeys_key] = api_get(f"bim/buildings/{selected_building_id}/storeys")
                            st.rerun()
                        else:
                            st.error("Creation failed.")

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
            storeys_key = f"storeys_{selected_building_id}"
            if storeys_key not in st.session_state or st.session_state.get(storeys_key) is None:
                st.session_state[storeys_key] = api_get(f"bim/buildings/{selected_building_id}/storeys")
            storeys = st.session_state.get(storeys_key, [])
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
                if st.button("🔄 Refresh Spaces", key="refresh_spaces"):
                    st.session_state[f"spaces_{selected_storey_id}"] = api_get(f"bim/storeys/{selected_storey_id}/spaces")
                    st.rerun()
                spaces_key = f"spaces_{selected_storey_id}"
                if spaces_key not in st.session_state or st.session_state.get(spaces_key) is None:
                    st.session_state[spaces_key] = api_get(f"bim/storeys/{selected_storey_id}/spaces")
                spaces = st.session_state.get(spaces_key, [])
                if spaces is None:
                    st.warning("Could not load spaces.")
                    return
                for space in spaces:
                    col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 1, 1, 1, 1])
                    with col1:
                        st.markdown(f"**{space.get('name', 'Unnamed')}**")
                    with col2:
                        st.write(space.get('space_type', 'N/A'))
                    with col3:
                        st.write(f"{space.get('area', 0)} m²")
                    with col4:
                        st.write(f"{space.get('height', 0)} m")
                    with col5:
                        if st.button("✏️", key=f"edit_space_{space['id']}"):
                            st.session_state[f"editing_space_{selected_storey_id}"] = space
                    with col6:
                        if st.button("🗑️", key=f"del_space_{space['id']}"):
                            if st.checkbox(f"Confirm delete {space.get('name', 'this space')}?", key=f"confirm_space_{space['id']}"):
                                if api_delete(f"bim/spaces/{space['id']}"):
                                    st.success("Space deleted!")
                                    st.session_state[spaces_key] = api_get(f"bim/storeys/{selected_storey_id}/spaces")
                                    st.rerun()
                                else:
                                    st.error("Delete failed.")
                    editing_key = f"editing_space_{selected_storey_id}"
                    if st.session_state.get(editing_key, {}).get("id") == space.get("id"):
                        with st.expander(f"Edit {space.get('name', '')}", expanded=True):
                            with st.form(key=f"edit_space_form_{space['id']}"):
                                new_name = st.text_input("Space Name", value=space.get('name', ''))
                                new_type = st.text_input("Space Type (e.g., Office, Conference)", value=space.get('space_type', ''))
                                new_area = st.number_input("Area (m²)", value=space.get('area', 0.0), step=5.0)
                                new_height = st.number_input("Height (m)", value=space.get('height', 0.0), step=0.1)
                                if st.form_submit_button("Update"):
                                    updated = {
                                        "name": new_name,
                                        "space_type": new_type,
                                        "area": new_area,
                                        "height": new_height,
                                        "storey_id": selected_storey_id,
                                        "building_id": selected_building_id
                                    }
                                    result = api_put(f"bim/spaces/{space['id']}", updated)
                                    if result:
                                        st.success("Space updated!")
                                        st.session_state[spaces_key] = api_get(f"bim/storeys/{selected_storey_id}/spaces")
                                        st.session_state[editing_key] = None
                                        st.rerun()
                                    else:
                                        st.error("Update failed.")
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
                            new_data = {
                                "name": name,
                                "space_type": space_type,
                                "area": area,
                                "height": height,
                                "storey_id": selected_storey_id,
                                "building_id": selected_building_id
                            }
                            result = api_post("bim/spaces", new_data)
                            if result:
                                st.success("Space created!")
                                st.session_state[spaces_key] = api_get(f"bim/storeys/{selected_storey_id}/spaces")
                                st.rerun()
                            else:
                                st.error("Creation failed.")

    with tab4:
        st.info("Elements management coming soon.")
    with tab5:
        st.info("IFC Viewer coming soon.")
    with tab6:
        st.info("COBie data management coming soon.")
    with tab7:
        st.info("Digital Twin integration coming soon.")

# ---------------------------
# PAGE: STRUCTURAL (full CRUD for all sub-modules)
# ---------------------------
def page_structural():
    st.title("🔩 Structural Engineering")
    tabs = st.tabs([
        "Eurocode", "Beam Design", "Column Design", "Slab Design",
        "Foundation Design", "Retaining Walls", "Steel Connections", "FEA"
    ])

    with tabs[0]:
        st.subheader("Eurocode Parameters")
        st.info("Eurocode load combinations and material factors will be managed here.")
        # Placeholder for Eurocode settings

    with tabs[1]:
        st.subheader("Beam Design")
        if st.button("🔄 Refresh Beams"):
            st.session_state.beam_data = api_get("structural/beam_design")
            st.rerun()
        if st.session_state.beam_data is None:
            st.session_state.beam_data = api_get("structural/beam_design")
        beams = st.session_state.beam_data
        if beams is None:
            st.warning("No beam data found.")
            return
        crud_table(beams, "beam", "structural/beam_design",
                   display_fields=["beam_id", "span", "load", "material", "status"],
                   edit_fields={"beam_id": "text", "span": "number", "load": "number", "material": "text", "status": "text"},
                   add_fields={"beam_id": "text", "span": "number", "load": "number", "material": "text", "status": "text"})

    with tabs[2]:
        st.subheader("Column Design")
        if st.button("🔄 Refresh Columns"):
            st.session_state.column_data = api_get("structural/column_design")
            st.rerun()
        if st.session_state.column_data is None:
            st.session_state.column_data = api_get("structural/column_design")
        columns = st.session_state.column_data
        if columns is None:
            st.warning("No column data found.")
            return
        crud_table(columns, "column", "structural/column_design",
                   display_fields=["column_id", "axial_load", "section", "reinforcement_ratio"],
                   edit_fields={"column_id": "text", "axial_load": "number", "section": "text", "reinforcement_ratio": "number"},
                   add_fields={"column_id": "text", "axial_load": "number", "section": "text", "reinforcement_ratio": "number"})

    with tabs[3]:
        st.subheader("Slab Design")
        if st.button("🔄 Refresh Slabs"):
            st.session_state.slab_data = api_get("structural/slab_design")
            st.rerun()
        if st.session_state.slab_data is None:
            st.session_state.slab_data = api_get("structural/slab_design")
        slabs = st.session_state.slab_data
        if slabs is None:
            st.warning("No slab data found.")
            return
        crud_table(slabs, "slab", "structural/slab_design",
                   display_fields=["slab_id", "thickness", "span", "load"],
                   edit_fields={"slab_id": "text", "thickness": "number", "span": "number", "load": "number"},
                   add_fields={"slab_id": "text", "thickness": "number", "span": "number", "load": "number"})

    with tabs[4]:
        st.subheader("Foundation Design")
        if st.button("🔄 Refresh Foundations"):
            st.session_state.foundation_data = api_get("structural/foundation_design")
            st.rerun()
        if st.session_state.foundation_data is None:
            st.session_state.foundation_data = api_get("structural/foundation_design")
        foundations = st.session_state.foundation_data
        if foundations is None:
            st.warning("No foundation data found.")
            return
        crud_table(foundations, "foundation", "structural/foundation_design",
                   display_fields=["foundation_type", "capacity", "depth"],
                   edit_fields={"foundation_type": "text", "capacity": "number", "depth": "number"},
                   add_fields={"foundation_type": "text", "capacity": "number", "depth": "number"})

    with tabs[5]:
        st.subheader("Retaining Walls")
        if st.button("🔄 Refresh Retaining Walls"):
            st.session_state.retaining_data = api_get("structural/retaining_walls")
            st.rerun()
        if st.session_state.retaining_data is None:
            st.session_state.retaining_data = api_get("structural/retaining_walls")
        retaining = st.session_state.retaining_data
        if retaining is None:
            st.warning("No retaining wall data found.")
            return
        crud_table(retaining, "retaining", "structural/retaining_walls",
                   display_fields=["wall_id", "height", "thickness", "stability"],
                   edit_fields={"wall_id": "text", "height": "number", "thickness": "number", "stability": "text"},
                   add_fields={"wall_id": "text", "height": "number", "thickness": "number", "stability": "text"})

    with tabs[6]:
        st.subheader("Steel Connections")
        if st.button("🔄 Refresh Connections"):
            st.session_state.connection_data = api_get("structural/steel_connections")
            st.rerun()
        if st.session_state.connection_data is None:
            st.session_state.connection_data = api_get("structural/steel_connections")
        connections = st.session_state.connection_data
        if connections is None:
            st.warning("No connection data found.")
            return
        crud_table(connections, "connection", "structural/steel_connections",
                   display_fields=["connection_type", "bolts", "capacity"],
                   edit_fields={"connection_type": "text", "bolts": "text", "capacity": "number"},
                   add_fields={"connection_type": "text", "bolts": "text", "capacity": "number"})

    with tabs[7]:
        st.subheader("Finite Element Analysis")
        st.info("Run FEA simulations and view results here. (Coming soon)")

# ---------------------------
# PAGE: MEP (HVAC, Electrical, Plumbing)
# ---------------------------
def page_mep():
    st.title("⚡ MEP")
    tabs = st.tabs(["Mechanical (HVAC)", "Electrical", "Plumbing"])

    with tabs[0]:
        st.subheader("HVAC Load Summary")
        st.info("Display HVAC loads and run energy simulations. (Coming soon)")

    with tabs[1]:
        st.subheader("Electrical Load Analysis")
        if st.button("🔄 Refresh Electrical Data"):
            st.session_state.electrical_data = api_get("mep/electrical")
            st.rerun()
        if st.session_state.electrical_data is None:
            st.session_state.electrical_data = api_get("mep/electrical")
        electrical = st.session_state.electrical_data
        if electrical is None:
            st.warning("No electrical data found.")
            return
        crud_table(electrical, "panel", "mep/electrical",
                   display_fields=["panel", "total_load", "reserve"],
                   edit_fields={"panel": "text", "total_load": "number", "reserve": "number"},
                   add_fields={"panel": "text", "total_load": "number", "reserve": "number"})

    with tabs[2]:
        st.subheader("Plumbing Systems")
        st.info("Water supply, drainage, stormwater, and firefighting. (Coming soon)")

# ---------------------------
# PAGE: COSTING (BOQ CRUD)
# ---------------------------
def page_costing():
    st.title("💰 Cost Estimation")
    if st.button("🔄 Refresh BOQ"):
        st.session_state.boq_data = api_get("costing/boq")
        st.rerun()
    if st.session_state.boq_data is None:
        st.session_state.boq_data = api_get("costing/boq")
    boq = st.session_state.boq_data
    if boq is None:
        st.warning("No BOQ data found.")
        return
    st.subheader("Bill of Quantities")
    crud_table(boq, "boq_item", "costing/boq",
               display_fields=["item", "quantity", "unit", "rate", "total"],
               edit_fields={"item": "text", "quantity": "number", "unit": "text", "rate": "number", "total": "number"},
               add_fields={"item": "text", "quantity": "number", "unit": "text", "rate": "number", "total": "number"})

# ---------------------------
# PAGE: CONSTRUCTION (RFI CRUD)
# ---------------------------
def page_construction():
    st.title("🚧 Construction Management")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Progress vs Planned")
        # Placeholder chart
        dates = pd.date_range(start="2026-01-01", end="2026-08-19", freq="W")
        planned = list(range(10, 110, 5))[:len(dates)]
        actual = [p - random.randint(0, 8) for p in planned]
        df_progress = pd.DataFrame({"Date": dates, "Planned": planned, "Actual": actual})
        st.line_chart(df_progress.set_index("Date"))
    with col2:
        st.subheader("RFI & Submittals")
        if st.button("🔄 Refresh RFIs"):
            st.session_state.rfi_data = api_get("construction/rfis")
            st.rerun()
        if st.session_state.rfi_data is None:
            st.session_state.rfi_data = api_get("construction/rfis")
        rfi = st.session_state.rfi_data
        if rfi is None:
            st.warning("No RFI data found.")
            return
        crud_table(rfi, "rfi", "construction/rfis",
                   display_fields=["rfi_number", "subject", "status"],
                   edit_fields={"rfi_number": "text", "subject": "text", "status": "text"},
                   add_fields={"rfi_number": "text", "subject": "text", "status": "text"})

    st.subheader("Site Diary")
    diary = st.text_area("Today's Log", height=150, value="2026-08-19: Completed foundation pour for Block A.")
    if st.button("Save Diary Entry"):
        st.success("Diary saved (mock).")

# ---------------------------
# PAGE: REGIONAL (edit country codes)
# ---------------------------
def page_regional():
    st.title("🌍 Regional – East Africa Codes")
    if "regional_codes" not in st.session_state:
        # Load from API or use default
        st.session_state.regional_codes = {
            "Uganda": {"Code": "UNBC 2020", "Seismic Zone": "Zone 3", "Wind Speed": "35 m/s"},
            "Kenya": {"Code": "KBC 2015", "Seismic Zone": "Zone 2", "Wind Speed": "30 m/s"},
            "Tanzania": {"Code": "TBS 2018", "Seismic Zone": "Zone 2", "Wind Speed": "28 m/s"},
            "Rwanda": {"Code": "RBC 2019", "Seismic Zone": "Zone 3", "Wind Speed": "32 m/s"},
            "South Sudan": {"Code": "SSBC 2021", "Seismic Zone": "Zone 1", "Wind Speed": "25 m/s"},
        }
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
# PAGE: DIGITAL TWIN (sensor CRUD)
# ---------------------------
def page_digital_twin():
    st.title("🔄 Digital Twin – Live Monitoring")
    st.subheader("Sensor Data")
    if st.button("🔄 Refresh Sensors"):
        st.session_state.sensor_data = api_get("digital_twin/sensors")
        st.rerun()
    if st.session_state.sensor_data is None:
        st.session_state.sensor_data = api_get("digital_twin/sensors")
    sensors = st.session_state.sensor_data
    if sensors is None:
        st.warning("No sensor data found.")
        return
    crud_table(sensors, "sensor", "digital_twin/sensors",
               display_fields=["sensor_id", "location", "value", "unit"],
               edit_fields={"sensor_id": "text", "location": "text", "value": "number", "unit": "text"},
               add_fields={"sensor_id": "text", "location": "text", "value": "number", "unit": "text"})

    st.subheader("Historical Energy Consumption")
    # Show placeholder chart
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
            # We can later call the actual AI endpoint, e.g., api_post("ai/ask", {"query": prompt})
            response = """Based on EN 1998-1, for a 10-storey building in seismic zone 3 (Uganda),
            a preliminary column size of 450x450 mm with C30/37 concrete and 8#25 longitudinal bars is recommended.
            Verify with a full analysis."""
            st.success(response)

    st.subheader("RAG - Document Search")
    query = st.text_input("Search project documents:")
    if query:
        # Placeholder results; can call api_get("ai/search?q=...")
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
    # Try to fetch from API if available
    kpi_data = api_get("analytics/kpis")
    if kpi_data:
        df = pd.DataFrame(kpi_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Use mock data for KPIs")
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