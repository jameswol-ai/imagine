# build_modules.py
import os

BASE = "modules"

# Template for each module file
MODULE_TEMPLATE = '''import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import random

# Mock data (will be imported from utils later)
# For now, we'll use session state directly

def render():
    st.info("📦 This module is under development. Coming soon.")
'''

# Advanced templates for specific modules
DASHBOARD_TEMPLATE = '''import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

def render():
    st.title("📊 Dashboard")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Active Projects", "12", "+2")
    col2.metric("Total Budget", "$184M", "+5%")
    col3.metric("Progress (avg)", "68%", "+12%")
    col4.metric("Open RFIs", "7", "-3")

    st.subheader("Project Health")
    projects = st.session_state.get("projects_data", [])
    if projects:
        df = pd.DataFrame(projects)
        fig = px.bar(df, x="name", y="progress", color="status", text="progress")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No projects found.")

    st.subheader("Recent Activity")
    activity = pd.DataFrame({
        "Time": [datetime.now() - timedelta(hours=i) for i in range(5)],
        "User": ["Alice", "Bob", "Charlie", "Alice", "Dave"],
        "Action": ["Updated BOQ", "Submitted RFI", "Approved revision", "Added drawing", "Closed snag"],
    })
    st.dataframe(activity, use_container_width=True)
'''

PROJECTS_TEMPLATE = '''import streamlit as st
from modules.utils.crud import crud_table

def render():
    st.title("📁 Projects")
    if st.button("🔄 Refresh"):
        st.rerun()
    crud_table(
        data_key="projects_data",
        item_name="project",
        endpoint="projects",
        display_fields=["name", "status", "budget", "progress"],
        edit_fields={"name": "text", "status": "text", "budget": "number", "progress": "number"},
        add_fields={"name": "text", "status": "text", "budget": "number", "progress": "number"}
    )
'''

BIM_BUILDINGS_TEMPLATE = '''import streamlit as st
from modules.utils.crud import crud_table

def render():
    st.subheader("Buildings")
    if st.button("🔄 Refresh Buildings"):
        st.rerun()
    crud_table(
        data_key="buildings_data",
        item_name="building",
        endpoint="bim/buildings",
        display_fields=["name", "storeys", "area", "ifc_version"],
        edit_fields={"name": "text", "storeys": "number", "area": "number", "ifc_version": "text"},
        add_fields={"name": "text", "storeys": "number", "area": "number", "ifc_version": "text"}
    )
'''

# This is a generic CRUD template for other modules
CRUD_TEMPLATE = '''import streamlit as st
from modules.utils.crud import crud_table

def render():
    st.subheader("{title}")
    if st.button(f"🔄 Refresh {title}"):
        st.rerun()
    crud_table(
        data_key="{data_key}",
        item_name="{item_name}",
        endpoint="{endpoint}",
        display_fields={display_fields},
        edit_fields={edit_fields},
        add_fields={add_fields}
    )
'''

# Map each module to its specific configuration
MODULE_CONFIGS = {
    "bim/storeys": {
        "title": "Storeys",
        "data_key": "storeys_data",  # This will be handled differently – we'll keep it simple
        "item_name": "storey",
        "endpoint": "bim/storeys",
        "display_fields": ["level", "height", "area"],
        "edit_fields": {"level": "text", "height": "number", "area": "number"},
        "add_fields": {"level": "text", "height": "number", "area": "number"}
    },
    "bim/spaces": {
        "title": "Spaces",
        "data_key": "spaces_data",
        "item_name": "space",
        "endpoint": "bim/spaces",
        "display_fields": ["name", "space_type", "area", "height"],
        "edit_fields": {"name": "text", "space_type": "text", "area": "number", "height": "number"},
        "add_fields": {"name": "text", "space_type": "text", "area": "number", "height": "number"}
    },
    "structural/beam_design": {
        "title": "Beam Design",
        "data_key": "beam_data",
        "item_name": "beam",
        "endpoint": "structural/beam_design",
        "display_fields": ["beam_id", "span", "load", "material", "status"],
        "edit_fields": {"beam_id": "text", "span": "number", "load": "number", "material": "text", "status": "text"},
        "add_fields": {"beam_id": "text", "span": "number", "load": "number", "material": "text", "status": "text"}
    },
    "structural/column_design": {
        "title": "Column Design",
        "data_key": "column_data",
        "item_name": "column",
        "endpoint": "structural/column_design",
        "display_fields": ["column_id", "axial_load", "section", "reinforcement_ratio"],
        "edit_fields": {"column_id": "text", "axial_load": "number", "section": "text", "reinforcement_ratio": "number"},
        "add_fields": {"column_id": "text", "axial_load": "number", "section": "text", "reinforcement_ratio": "number"}
    },
    "structural/slab_design": {
        "title": "Slab Design",
        "data_key": "slab_data",
        "item_name": "slab",
        "endpoint": "structural/slab_design",
        "display_fields": ["slab_id", "thickness", "span", "load"],
        "edit_fields": {"slab_id": "text", "thickness": "number", "span": "number", "load": "number"},
        "add_fields": {"slab_id": "text", "thickness": "number", "span": "number", "load": "number"}
    },
    "structural/foundation_design": {
        "title": "Foundation Design",
        "data_key": "foundation_data",
        "item_name": "foundation",
        "endpoint": "structural/foundation_design",
        "display_fields": ["foundation_type", "capacity", "depth"],
        "edit_fields": {"foundation_type": "text", "capacity": "number", "depth": "number"},
        "add_fields": {"foundation_type": "text", "capacity": "number", "depth": "number"}
    },
    "structural/retaining_walls": {
        "title": "Retaining Walls",
        "data_key": "retaining_data",
        "item_name": "retaining",
        "endpoint": "structural/retaining_walls",
        "display_fields": ["wall_id", "height", "thickness", "stability"],
        "edit_fields": {"wall_id": "text", "height": "number", "thickness": "number", "stability": "text"},
        "add_fields": {"wall_id": "text", "height": "number", "thickness": "number", "stability": "text"}
    },
    "structural/steel_connections": {
        "title": "Steel Connections",
        "data_key": "connection_data",
        "item_name": "connection",
        "endpoint": "structural/steel_connections",
        "display_fields": ["connection_type", "bolts", "capacity"],
        "edit_fields": {"connection_type": "text", "bolts": "text", "capacity": "number"},
        "add_fields": {"connection_type": "text", "bolts": "text", "capacity": "number"}
    },
    "costing/boq": {
        "title": "Bill of Quantities",
        "data_key": "boq_data",
        "item_name": "boq_item",
        "endpoint": "costing/boq",
        "display_fields": ["item", "quantity", "unit", "rate", "total"],
        "edit_fields": {"item": "text", "quantity": "number", "unit": "text", "rate": "number", "total": "number"},
        "add_fields": {"item": "text", "quantity": "number", "unit": "text", "rate": "number", "total": "number"}
    },
    "construction/rfis": {
        "title": "RFIs",
        "data_key": "rfi_data",
        "item_name": "rfi",
        "endpoint": "construction/rfis",
        "display_fields": ["rfi_number", "subject", "status"],
        "edit_fields": {"rfi_number": "text", "subject": "text", "status": "text"},
        "add_fields": {"rfi_number": "text", "subject": "text", "status": "text"}
    },
    "digital_twin/sensors": {
        "title": "Sensors",
        "data_key": "sensor_data",
        "item_name": "sensor",
        "endpoint": "digital_twin/sensors",
        "display_fields": ["sensor_id", "location", "value", "unit"],
        "edit_fields": {"sensor_id": "text", "location": "text", "value": "number", "unit": "text"},
        "add_fields": {"sensor_id": "text", "location": "text", "value": "number", "unit": "text"}
    },
    "mep/electrical": {
        "title": "Electrical Panels",
        "data_key": "electrical_data",
        "item_name": "panel",
        "endpoint": "mep/electrical",
        "display_fields": ["panel", "total_load", "reserve"],
        "edit_fields": {"panel": "text", "total_load": "number", "reserve": "number"},
        "add_fields": {"panel": "text", "total_load": "number", "reserve": "number"}
    },
    "architecture/zoning": {
        "title": "Zoning",
        "data_key": "zoning_data",
        "item_name": "zoning",
        "endpoint": "architecture/zoning",
        "display_fields": ["zone_type", "max_height", "coverage", "setback"],
        "edit_fields": {"zone_type": "text", "max_height": "number", "coverage": "number", "setback": "number"},
        "add_fields": {"zone_type": "text", "max_height": "number", "coverage": "number", "setback": "number"}
    },
    "architecture/room_programming": {
        "title": "Room Programming",
        "data_key": "room_program_data",
        "item_name": "room",
        "endpoint": "architecture/room_programming",
        "display_fields": ["room_name", "area", "quantity", "adjacency"],
        "edit_fields": {"room_name": "text", "area": "number", "quantity": "number", "adjacency": "text"},
        "add_fields": {"room_name": "text", "area": "number", "quantity": "number", "adjacency": "text"}
    }
}

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)

def build_modules():
    # 1. Create utils folder with crud.py and mock_data.py
    os.makedirs("modules/utils", exist_ok=True)

    # crud.py – the generic CRUD helper (adjusted from monolithic version)
    crud_code = '''
import streamlit as st
import pandas as pd

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
                    # Mock delete: just remove from session state
                    new_data = [d for d in data if d[id_field] != item[id_field]]
                    st.session_state[data_key] = new_data
                    st.success(f"{item_name.capitalize()} deleted!")
                    st.rerun()

        editing_key = f"editing_{item_name}"
        if editing_key in st.session_state and st.session_state[editing_key] is not None:
            editing_item = st.session_state[editing_key]
            if isinstance(editing_item, dict) and editing_item.get(id_field) == item.get(id_field):
                with st.expander(f"Edit {item.get('name', item.get('level', ''))}", expanded=True):
                    with st.form(key=f"edit_{item_name}_form_{item[id_field]}"):
                        edit_values = {}
                        if edit_fields is None:
                            edit_fields = {field: "text" for field in display_fields}
                        for field, input_type in edit_fields.items():
                            if input_type == "text":
                                edit_values[field] = st.text_input(field.capitalize(), value=item.get(field, ''))
                            elif input_type == "number":
                                edit_values[field] = st.number_input(field.capitalize(), value=item.get(field, 0.0), step=0.1)
                            elif input_type == "select":
                                options = item.get('options', [])
                                current = item.get(field, options[0] if options else '')
                                edit_values[field] = st.selectbox(field.capitalize(), options, index=options.index(current) if current in options else 0)
                        if st.form_submit_button("Update"):
                            for d in data:
                                if d[id_field] == item[id_field]:
                                    for k, v in edit_values.items():
                                        d[k] = v
                                    break
                            st.session_state[data_key] = data
                            st.success(f"{item_name.capitalize()} updated!")
                            st.session_state[editing_key] = None
                            st.rerun()
                if st.button("Cancel", key=f"cancel_{item_name}_edit_{item[id_field]}"):
                    st.session_state[editing_key] = None
                    st.rerun()

    with st.expander(f"➕ Add New {item_name.capitalize()}"):
        with st.form(key=f"new_{item_name}_form"):
            add_values = {}
            add_fields_to_use = add_fields if add_fields is not None else edit_fields
            if add_fields_to_use is None:
                add_fields_to_use = {field: "text" for field in display_fields}
            for field, input_type in add_fields_to_use.items():
                if input_type == "text":
                    add_values[field] = st.text_input(field.capitalize())
                elif input_type == "number":
                    add_values[field] = st.number_input(field.capitalize(), value=0.0, step=0.1)
                elif input_type == "select":
                    options = data[0].get('options', []) if data else []
                    add_values[field] = st.selectbox(field.capitalize(), options)
            if st.form_submit_button("Create"):
                new_id = max([d[id_field] for d in data]) + 1 if data else 1
                add_values[id_field] = new_id
                data.append(add_values)
                st.session_state[data_key] = data
                st.success(f"{item_name.capitalize()} created!")
                st.rerun()
'''
    create_file("modules/utils/crud.py", crud_code)

    # mock_data.py – initialise all mock data
    mock_code = '''
import streamlit as st

def init_mock_data():
    # Projects
    if "projects_data" not in st.session_state or not st.session_state.projects_data:
        st.session_state.projects_data = [
            {"id": 1, "name": "Green Tower", "status": "Active", "budget": 12.5, "progress": 75},
            {"id": 2, "name": "Harbor Bridge", "status": "Planning", "budget": 8.3, "progress": 20},
            {"id": 3, "name": "Riverside Mall", "status": "Completed", "budget": 22.1, "progress": 100},
            {"id": 4, "name": "Solar Park", "status": "Active", "budget": 5.7, "progress": 45},
        ]
    # Buildings
    if "buildings_data" not in st.session_state or not st.session_state.buildings_data:
        st.session_state.buildings_data = [
            {"id": 1, "name": "Tower A", "storeys": 25, "area": 15000, "ifc_version": "IFC4"},
            {"id": 2, "name": "Tower B", "storeys": 18, "area": 12000, "ifc_version": "IFC4"},
            {"id": 3, "name": "Pavilion", "storeys": 3, "area": 2500, "ifc_version": "IFC2x3"},
        ]
    # Storeys (nested)
    if "storeys_data" not in st.session_state:
        st.session_state.storeys_data = {}
    for b in st.session_state.buildings_data:
        b_id = b["id"]
        if b_id not in st.session_state.storeys_data:
            st.session_state.storeys_data[b_id] = [
                {"id": (b_id*100 + i), "level": f"Level {i}", "height": 4.0 + (i%2)*0.2, "area": 1200 - i*10}
                for i in range(1, min(b["storeys"], 5)+1)
            ]
    # Spaces
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

    # Other mock data
    if "zoning_data" not in st.session_state or not st.session_state.zoning_data:
        st.session_state.zoning_data = [
            {"id": 1, "zone_type": "Residential", "max_height": 15, "coverage": 50, "setback": 3},
            {"id": 2, "zone_type": "Commercial", "max_height": 30, "coverage": 60, "setback": 5},
            {"id": 3, "zone_type": "Mixed-Use", "max_height": 45, "coverage": 70, "setback": 4},
        ]
    if "room_program_data" not in st.session_state or not st.session_state.room_program_data:
        st.session_state.room_program_data = [
            {"id": 1, "room_name": "Office", "area": 20, "quantity": 10, "adjacency": "Corridor"},
            {"id": 2, "room_name": "Conference", "area": 40, "quantity": 2, "adjacency": "Lobby"},
            {"id": 3, "room_name": "Lobby", "area": 60, "quantity": 1, "adjacency": "Entrance"},
            {"id": 4, "room_name": "Restroom", "area": 10, "quantity": 4, "adjacency": "Corridor"},
        ]
    if "beam_data" not in st.session_state or not st.session_state.beam_data:
        st.session_state.beam_data = [
            {"id": 1, "beam_id": "B-101", "span": 6.5, "load": 45, "material": "Concrete C30/37", "status": "OK"},
            {"id": 2, "beam_id": "B-102", "span": 8.2, "load": 60, "material": "Concrete C30/37", "status": "Overstressed"},
            {"id": 3, "beam_id": "B-201", "span": 5.0, "load": 30, "material": "Steel S355", "status": "OK"},
            {"id": 4, "beam_id": "B-202", "span": 7.0, "load": 50, "material": "Steel S355", "status": "OK"},
        ]
    if "column_data" not in st.session_state or not st.session_state.column_data:
        st.session_state.column_data = [
            {"id": 1, "column_id": "C-1", "axial_load": 1200, "section": "400x400", "reinforcement_ratio": 1.5},
            {"id": 2, "column_id": "C-2", "axial_load": 800, "section": "300x300", "reinforcement_ratio": 1.2},
            {"id": 3, "column_id": "C-3", "axial_load": 1500, "section": "500x500", "reinforcement_ratio": 2.0},
            {"id": 4, "column_id": "C-4", "axial_load": 950, "section": "350x350", "reinforcement_ratio": 1.3},
        ]
    if "slab_data" not in st.session_state or not st.session_state.slab_data:
        st.session_state.slab_data = [
            {"id": 1, "slab_id": "S1", "thickness": 200, "span": 6, "load": 5},
            {"id": 2, "slab_id": "S2", "thickness": 150, "span": 4, "load": 4},
            {"id": 3, "slab_id": "S3", "thickness": 250, "span": 7, "load": 6},
            {"id": 4, "slab_id": "S4", "thickness": 180, "span": 5, "load": 4.5},
        ]
    if "foundation_data" not in st.session_state or not st.session_state.foundation_data:
        st.session_state.foundation_data = [
            {"id": 1, "foundation_type": "Pad", "capacity": 800, "depth": 1.5},
            {"id": 2, "foundation_type": "Strip", "capacity": 500, "depth": 1.0},
            {"id": 3, "foundation_type": "Pile", "capacity": 1200, "depth": 12},
            {"id": 4, "foundation_type": "Raft", "capacity": 1500, "depth": 0.8},
        ]
    if "retaining_data" not in st.session_state or not st.session_state.retaining_data:
        st.session_state.retaining_data = [
            {"id": 1, "wall_id": "RW-1", "height": 4.5, "thickness": 0.3, "stability": "OK"},
            {"id": 2, "wall_id": "RW-2", "height": 6.0, "thickness": 0.4, "stability": "OK"},
            {"id": 3, "wall_id": "RW-3", "height": 3.2, "thickness": 0.25, "stability": "Warning"},
        ]
    if "connection_data" not in st.session_state or not st.session_state.connection_data:
        st.session_state.connection_data = [
            {"id": 1, "connection_type": "Moment", "bolts": "M20", "capacity": 200},
            {"id": 2, "connection_type": "Shear", "bolts": "M16", "capacity": 120},
            {"id": 3, "connection_type": "Base Plate", "bolts": "M24", "capacity": 350},
            {"id": 4, "connection_type": "Brace", "bolts": "M22", "capacity": 180},
        ]
    if "electrical_data" not in st.session_state or not st.session_state.electrical_data:
        st.session_state.electrical_data = [
            {"id": 1, "panel": "MDP-1", "total_load": 250, "reserve": 20},
            {"id": 2, "panel": "MDP-2", "total_load": 180, "reserve": 15},
            {"id": 3, "panel": "MDP-3", "total_load": 90, "reserve": 25},
        ]
    if "boq_data" not in st.session_state or not st.session_state.boq_data:
        st.session_state.boq_data = [
            {"id": 1, "item": "Concrete C30", "quantity": 500, "unit": "m³", "rate": 120, "total": 60000},
            {"id": 2, "item": "Steel Rebar", "quantity": 120, "unit": "t", "rate": 950, "total": 114000},
            {"id": 3, "item": "Finishes", "quantity": 300, "unit": "m²", "rate": 75, "total": 22500},
            {"id": 4, "item": "MEP", "quantity": 80, "unit": "LF", "rate": 60, "total": 4800},
            {"id": 5, "item": "Excavation", "quantity": 200, "unit": "m³", "rate": 40, "total": 8000},
        ]
    if "rfi_data" not in st.session_state or not st.session_state.rfi_data:
        st.session_state.rfi_data = [
            {"id": 1, "rfi_number": "RFI-001", "subject": "Rebar spacing", "status": "Open"},
            {"id": 2, "rfi_number": "RFI-002", "subject": "Window detail", "status": "Answered"},
            {"id": 3, "rfi_number": "RFI-003", "subject": "MEP coordination", "status": "Closed"},
            {"id": 4, "rfi_number": "RFI-004", "subject": "Concrete mix", "status": "Pending"},
        ]
    if "sensor_data" not in st.session_state or not st.session_state.sensor_data:
        st.session_state.sensor_data = [
            {"id": 1, "sensor_id": "TEMP-01", "location": "Lobby", "value": 23.5, "unit": "°C"},
            {"id": 2, "sensor_id": "HUM-01", "location": "Lobby", "value": 42, "unit": "%"},
            {"id": 3, "sensor_id": "ENERGY-01", "location": "Main", "value": 320, "unit": "kW"},
            {"id": 4, "sensor_id": "OCC-01", "location": "Office", "value": 245, "unit": "people"},
        ]
'''
    create_file("modules/utils/mock_data.py", mock_code)

    # 2. Create the main module files
    # Dashboard
    create_file("modules/dashboard/dashboard.py", DASHBOARD_TEMPLATE)

    # Projects
    create_file("modules/projects/project_page.py", PROJECTS_TEMPLATE)

    # BIM - Buildings (special)
    create_file("modules/bim/buildings.py", BIM_BUILDINGS_TEMPLATE)

    # Other BIM modules (storeys, spaces, ifc_export) – use generic CRUD with custom configs
    # We'll generate them using the CRUD_TEMPLATE with specific configs.

    # For storeys, spaces, we need custom handling because they are nested.
    # For now, we'll create placeholder implementations that show a message.
    # But we can implement them fully later.

    # Let's make a simple storeys page that reads from session state.
    storeys_code = '''
import streamlit as st

def render():
    st.subheader("Storeys")
    buildings = st.session_state.get("buildings_data", [])
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
        storeys = st.session_state.get("storeys_data", {}).get(selected_building_id, [])
        if not storeys:
            st.info("No storeys for this building.")
            return
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
                        # delete
                        st.session_state.storeys_data[selected_building_id] = [s for s in storeys if s['id'] != storey['id']]
                        st.success("Storey deleted!")
                        st.rerun()
            # Edit logic (simplified)
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
        # Add new storey
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
'''
    create_file("modules/bim/storeys.py", storeys_code)

    # Spaces (simpler: use the same pattern as storeys but with building -> storey selection)
    spaces_code = '''
import streamlit as st

def render():
    st.subheader("Spaces")
    buildings = st.session_state.get("buildings_data", [])
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
        storeys = st.session_state.get("storeys_data", {}).get(selected_building_id, [])
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
            key = f"{selected_building_id}_{selected_storey_id}"
            spaces = st.session_state.get("spaces_data", {}).get(key, [])
            if not spaces:
                st.info("No spaces for this storey.")
                return
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
'''
    create_file("modules/bim/spaces.py", spaces_code)

    # IFC Export - placeholder
    create_file("modules/bim/ifc_export.py", MODULE_TEMPLATE)

    # Architecture synthesis - placeholder (can be extended)
    create_file("modules/architecture/synthesis.py", MODULE_TEMPLATE)

    # Now generate all other CRUD modules using the template
    for module_path, config in MODULE_CONFIGS.items():
        # Skip those we've already created manually
        if module_path in ["bim/storeys", "bim/spaces"]:
            continue
        folder, file = module_path.split("/")
        file_path = f"modules/{folder}/{file}.py"
        title = config["title"]
        data_key = config["data_key"]
        item_name = config["item_name"]
        endpoint = config["endpoint"]
        display_fields = config["display_fields"]
        edit_fields = config["edit_fields"]
        add_fields = config["add_fields"]
        content = CRUD_TEMPLATE.format(
            title=title,
            data_key=data_key,
            item_name=item_name,
            endpoint=endpoint,
            display_fields=display_fields,
            edit_fields=edit_fields,
            add_fields=add_fields
        )
        create_file(file_path, content)

    # Additional stubs for modules that don't have CRUD (e.g., eurocode, analysis, hvac, etc.)
    stubs = [
        "modules/structural/eurocode.py",
        "modules/mep/analysis.py",
        "modules/mep/hvac.py",
        "modules/mep/plumbing.py",
        "modules/mep/energy_simulation.py",
        "modules/costing/procurement.py",
        "modules/costing/forex.py",
        "modules/costing/escalation.py",
        "modules/costing/risk_analysis.py",
        "modules/governance/approvals.py",
        "modules/construction/submittals.py",
        "modules/construction/site_diary.py",
        "modules/construction/progress_tracking.py",
        "modules/construction/snagging.py",
        "modules/documents/documents.py",
        "modules/documents/revisions.py",
        "modules/documents/drawing_register.py",
        "modules/documents/specifications.py",
        "modules/documents/transmittals.py",
        "modules/analytics/portfolio.py",
        "modules/analytics/reporting.py",
        "modules/analytics/forecasting.py",
        "modules/analytics/kpis.py",
        "modules/digital_twin/assets.py",
        "modules/digital_twin/telemetry.py",
        "modules/digital_twin/maintenance.py",
        "modules/digital_twin/predictive_ai.py",
        "modules/ai/architect.py",
        "modules/ai/engineer.py",
        "modules/ai/mep.py",
        "modules/ai/qs.py",
        "modules/ai/project_manager.py",
    ]
    for stub in stubs:
        create_file(stub, MODULE_TEMPLATE)

    print("✅ All modules built successfully!")

if __name__ == "__main__":
    build_modules()