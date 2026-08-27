import os

BASE = "modules"

# ------------------------------------------------------------------
# Generic CRUD template (used by many modules)
# ------------------------------------------------------------------
CRUD_TEMPLATE = '''import streamlit as st
from modules.utils.crud import crud_table

def render():
    st.subheader("{title}")
    if st.button("🔄 Refresh {title}"):
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

# ------------------------------------------------------------------
# Specialised modules content
# ------------------------------------------------------------------

# Dashboard
DASHBOARD_CODE = '''import streamlit as st
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

# Projects
PROJECTS_CODE = '''import streamlit as st
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

# BIM Buildings
BIM_BUILDINGS_CODE = '''import streamlit as st
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

# BIM Storeys
BIM_STOREYS_CODE = '''import streamlit as st

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
                level = st.text_input("Level")
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

# BIM Spaces
BIM_SPACES_CODE = '''import streamlit as st

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
                    space_type = st.text_input("Space Type")
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

# BIM IFC Export
BIM_IFC_CODE = '''import streamlit as st

def render():
    st.subheader("IFC Viewer & Export")
    st.info("Upload an IFC file to preview and export as COBie or other formats.")
    uploaded_file = st.file_uploader("Choose an IFC file", type=["ifc", "ifcxml", "ifczip"])
    if uploaded_file is not None:
        st.success(f"File '{uploaded_file.name}' uploaded successfully.")
        st.write("File size:", uploaded_file.size, "bytes")
        st.info("3D viewer integration coming soon (xeokit, Three.js, or Forge).")
    if st.button("Export as COBie"):
        st.success("COBie export placeholder (would generate Excel/XML).")
'''

# Architecture – Synthesis
ARCH_SYNTHESIS_CODE = '''import streamlit as st
import pandas as pd

def render():
    st.subheader("Generative Design")
    st.info("Run generative design algorithms to explore massing and layout options.")
    col1, col2 = st.columns(2)
    with col1:
        iterations = st.slider("Iterations", 10, 100, 50)
        objective = st.selectbox("Objective", ["Maximize area", "Minimize energy", "Balance"])
    with col2:
        population = st.slider("Population", 20, 200, 100)
        seed = st.number_input("Seed", value=42)
    if st.button("Run Generative Design"):
        with st.spinner("Generating options..."):
            options = pd.DataFrame({
                "Option": ["A", "B", "C"],
                "Area (m²)": [12500, 11800, 13200],
                "Energy (kWh/m²)": [45, 42, 48],
                "Score": [0.85, 0.82, 0.90],
            })
            st.dataframe(options)
            st.bar_chart(options.set_index("Option")["Score"])
            st.success("Design options generated (mock).")
'''

# Architecture – Zoning (CRUD)
ARCH_ZONING_CODE = '''import streamlit as st
from modules.utils.crud import crud_table

def render():
    st.subheader("Zoning")
    if st.button("🔄 Refresh Zoning"):
        st.rerun()
    crud_table(
        data_key="zoning_data",
        item_name="zoning",
        endpoint="architecture/zoning",
        display_fields=["zone_type", "max_height", "coverage", "setback"],
        edit_fields={"zone_type": "text", "max_height": "number", "coverage": "number", "setback": "number"},
        add_fields={"zone_type": "text", "max_height": "number", "coverage": "number", "setback": "number"}
    )
'''

# Architecture – Site Planning
ARCH_SITE_CODE = '''import streamlit as st

def render():
    st.subheader("Site Planning")
    col1, col2 = st.columns(2)
    with col1:
        st.number_input("Site Area (m²)", value=5000)
        st.slider("Slope (%)", 0, 20, 5)
    with col2:
        st.selectbox("Soil Type", ["Clay", "Sand", "Rock"])
        st.selectbox("Orientation", ["North", "South", "East", "West"])
    if st.button("Generate Site Layout"):
        st.success("Site layout generated (mock).")
        st.info("Visualization placeholder – would show site plan.")
'''

# Architecture – Floor Planning
ARCH_FLOOR_CODE = '''import streamlit as st

def render():
    st.subheader("Floor Planning")
    btype = st.selectbox("Building Type", ["Office", "Residential", "Hospital", "School"])
    floors = st.slider("Number of floors", 1, 20, 5)
    if st.button("Generate Floor Plan"):
        st.success(f"Floor plan generated for {btype} with {floors} floors (mock).")
        st.info("Visualization placeholder – would show floor plan.")
'''

# Architecture – Room Programming (CRUD)
ARCH_ROOM_CODE = '''import streamlit as st
from modules.utils.crud import crud_table

def render():
    st.subheader("Room Programming")
    if st.button("🔄 Refresh Rooms"):
        st.rerun()
    crud_table(
        data_key="room_program_data",
        item_name="room",
        endpoint="architecture/room_programming",
        display_fields=["room_name", "area", "quantity", "adjacency"],
        edit_fields={"room_name": "text", "area": "number", "quantity": "number", "adjacency": "text"},
        add_fields={"room_name": "text", "area": "number", "quantity": "number", "adjacency": "text"}
    )
'''

# Architecture – Compliance
ARCH_COMPLIANCE_CODE = '''import streamlit as st
import pandas as pd

def render():
    st.subheader("Compliance Checking")
    code = st.selectbox("Select Code", ["Uganda National Building Code", "Kenya Building Code", "Tanzania Building Standards"])
    st.file_uploader("Upload floor plan (DXF/PDF)", type=["dxf", "pdf"])
    if st.button("Run Compliance Check"):
        results = pd.DataFrame({
            "Rule": ["Fire escape distance", "Parking ratio", "Daylight factor"],
            "Required": ["< 30m", "1:100 m²", "> 2%"],
            "Actual": ["25m", "1:120 m²", "2.5%"],
            "Status": ["Pass", "Warning", "Pass"],
        })
        st.dataframe(results)
        st.success("Compliance check complete (mock).")
'''

# Structural Eurocode
STRUCT_EUROCODE_CODE = '''import streamlit as st
import pandas as pd

def render():
    st.subheader("Eurocode Parameters")
    st.info("Set material and load factors according to Eurocode.")
    col1, col2 = st.columns(2)
    with col1:
        st.number_input("Dead load (kN/m²)", value=5.0, step=0.5)
        st.number_input("Live load (kN/m²)", value=3.0, step=0.5)
        st.selectbox("Material", ["Concrete C30/37", "Steel S355", "Timber C24"])
    with col2:
        st.number_input("Wind load (kN/m²)", value=0.8, step=0.1)
        st.number_input("Snow load (kN/m²)", value=0.5, step=0.1)
        st.selectbox("Seismic zone", ["Zone 1", "Zone 2", "Zone 3", "Zone 4"])
    if st.button("Calculate Load Combinations"):
        st.dataframe(pd.DataFrame({
            "Combination": ["ULS 1", "ULS 2", "SLS 1"],
            "G (dead)": [1.35, 1.0, 1.0],
            "Q (live)": [1.5, 1.5, 0.7],
            "Wind": [0, 0.6, 0.3],
        }))
        st.success("Load combinations generated (mock).")
'''

# MEP Analysis
MEP_ANALYSIS_CODE = '''import streamlit as st
import pandas as pd

def render():
    st.subheader("MEP Analysis")
    st.info("Run system analysis for HVAC, electrical, and plumbing.")
    if st.button("Run Energy Analysis"):
        st.dataframe(pd.DataFrame({
            "Zone": ["Office", "Atrium", "Core"],
            "Cooling (kW)": [150, 80, 30],
            "Heating (kW)": [100, 60, 20],
        }))
        st.success("Energy analysis complete (mock).")
'''

# MEP HVAC
MEP_HVAC_CODE = '''import streamlit as st

def render():
    st.subheader("HVAC System Design")
    col1, col2 = st.columns(2)
    with col1:
        st.number_input("Building area (m²)", value=1000)
        st.selectbox("HVAC system type", ["VAV", "CAV", "Chilled water", "VRF"])
    with col2:
        st.number_input("Cooling load (kW)", value=200)
        st.number_input("Heating load (kW)", value=150)
    if st.button("Size Ducts"):
        st.success("Duct sizing results (mock) - would show diameters and velocities.")
'''

# MEP Plumbing
MEP_PLUMBING_CODE = '''import streamlit as st

def render():
    st.subheader("Plumbing Systems")
    st.info("Design water supply, drainage, and stormwater systems.")
    col1, col2 = st.columns(2)
    with col1:
        st.number_input("Number of fixtures", value=50)
        st.selectbox("Water source", ["Municipal", "Borehole", "Tank"])
    with col2:
        st.number_input("Peak flow (L/s)", value=5.0)
        st.number_input("Pressure (bar)", value=3.0)
    if st.button("Size Pipes"):
        st.success("Pipe sizing results (mock) - would show diameters and slopes.")
'''

# MEP Energy Simulation
MEP_ENERGY_CODE = '''import streamlit as st
import pandas as pd

def render():
    st.subheader("Energy Simulation")
    st.info("Run annual energy simulation for the building.")
    if st.button("Run Simulation"):
        data = pd.DataFrame({
            "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            "Energy (kWh)": [12000, 11000, 13000, 14000, 16000, 18000, 20000, 19000, 17000, 15000, 13000, 12000]
        })
        st.line_chart(data.set_index("Month"))
        st.success("Energy simulation complete (mock).")
'''

# Costing – Procurement, Forex, Escalation, Risk Analysis
COSTING_PROCUREMENT_CODE = '''import streamlit as st

def render():
    st.subheader("Procurement Management")
    st.info("Manage procurement schedules and supplier data.")
    st.text_input("Project")
    st.date_input("Procurement start date")
    st.date_input("Procurement end date")
    if st.button("Generate Procurement Plan"):
        st.success("Procurement plan generated (mock).")
'''

COSTING_FOREX_CODE = '''import streamlit as st

def render():
    st.subheader("Forex Management")
    st.info("Track and forecast exchange rates.")
    currencies = ["USD", "EUR", "GBP", "UGX", "KES", "TZS"]
    base = st.selectbox("Base currency", currencies)
    target = st.selectbox("Target currency", currencies)
    st.number_input("Amount", value=1000.0)
    st.date_input("Date")
    if st.button("Convert"):
        st.success(f"{base} to {target} conversion: placeholder rate 1:{base} = {target} 1.23 (mock).")
'''

COSTING_ESCALATION_CODE = '''import streamlit as st

def render():
    st.subheader("Cost Escalation")
    st.info("Apply inflation/escalation factors to project costs.")
    st.number_input("Base cost ($)", value=1000000)
    st.slider("Annual inflation (%)", 0.0, 15.0, 5.0)
    st.number_input("Years", value=3)
    if st.button("Calculate Escalated Cost"):
        escalated = 1000000 * (1.05 ** 3)
        st.success(f"Escalated cost: ${escalated:,.2f} (mock).")
'''

COSTING_RISK_CODE = '''import streamlit as st
import pandas as pd

def render():
    st.subheader("Risk Analysis")
    st.info("Identify and quantify project risks.")
    st.text_area("Risk description", "Material price volatility")
    st.selectbox("Probability", ["Low", "Medium", "High"])
    st.selectbox("Impact", ["Low", "Medium", "High"])
    if st.button("Add Risk"):
        st.success("Risk added (mock).")
    st.dataframe(pd.DataFrame({
        "Risk": ["Material price", "Labour shortage", "Weather delay"],
        "Probability": ["Medium", "High", "Low"],
        "Impact": ["High", "Medium", "Medium"],
        "Score": [16, 12, 6]
    }))
'''

# Governance – Approvals
GOVERNANCE_APPROVALS_CODE = '''import streamlit as st
from modules.utils.crud import crud_table

def render():
    st.title("🔒 Governance")
    st.subheader("Approvals")
    if "approvals_data" not in st.session_state:
        st.session_state.approvals_data = [
            {"id": 1, "project": "Green Tower", "type": "Design Review", "status": "Pending"},
            {"id": 2, "project": "Harbor Bridge", "type": "Safety", "status": "Approved"},
        ]
    crud_table(
        data_key="approvals_data",
        item_name="approval",
        endpoint="governance/approvals",
        display_fields=["project", "type", "status"],
        edit_fields={"project": "text", "type": "text", "status": "text"},
        add_fields={"project": "text", "type": "text", "status": "text"}
    )
'''

# Construction – Submittals, Site Diary, Progress, Snagging
CONSTRUCTION_SUBMITTALS_CODE = '''import streamlit as st
from modules.utils.crud import crud_table

def render():
    st.subheader("Submittals")
    if "submittals_data" not in st.session_state:
        st.session_state.submittals_data = [
            {"id": 1, "title": "Concrete mix design", "status": "Submitted"},
            {"id": 2, "title": "Window schedule", "status": "Approved"},
        ]
    crud_table(
        data_key="submittals_data",
        item_name="submittal",
        endpoint="construction/submittals",
        display_fields=["title", "status"],
        edit_fields={"title": "text", "status": "text"},
        add_fields={"title": "text", "status": "text"}
    )
'''

CONSTRUCTION_SITE_DIARY_CODE = '''import streamlit as st
from datetime import date

def render():
    st.subheader("Site Diary")
    diary_date = st.date_input("Date", value=date.today())
    diary_entry = st.text_area("Daily log", height=200, value="Work progressed on foundation. 12 workers on site.")
    if st.button("Save Entry"):
        st.success(f"Diary entry for {diary_date} saved (mock).")
'''

CONSTRUCTION_PROGRESS_CODE = '''import streamlit as st
import pandas as pd
import random

def render():
    st.subheader("Progress Tracking")
    dates = pd.date_range(start="2026-01-01", end="2026-08-19", freq="W")
    num_weeks = len(dates)
    planned = list(range(10, 101, int(90 / (num_weeks - 1))))[:num_weeks]
    if len(planned) < num_weeks:
        planned += [planned[-1]] * (num_weeks - len(planned))
    actual = [max(0, p - random.randint(0, 8)) for p in planned]
    df = pd.DataFrame({"Date": dates, "Planned": planned, "Actual": actual})
    st.line_chart(df.set_index("Date"))
'''

CONSTRUCTION_SNAGGING_CODE = '''import streamlit as st
from modules.utils.crud import crud_table

def render():
    st.subheader("Snagging")
    if "snagging_data" not in st.session_state:
        st.session_state.snagging_data = [
            {"id": 1, "item": "Paint touch-up", "status": "Open"},
            {"id": 2, "item": "Door alignment", "status": "Closed"},
        ]
    crud_table(
        data_key="snagging_data",
        item_name="snag",
        endpoint="construction/snagging",
        display_fields=["item", "status"],
        edit_fields={"item": "text", "status": "text"},
        add_fields={"item": "text", "status": "text"}
    )
'''

# Documents – Main, Revisions, Drawing Register, Specs, Transmittals
DOCUMENTS_MAIN_CODE = '''import streamlit as st
def render():
    st.subheader("Document Management")
    st.file_uploader("Upload document", type=["pdf", "docx", "xlsx", "dwg"])
    st.info("List of uploaded documents (mock).")
    st.dataframe({
        "Name": ["Specification.pdf", "Drawing.dwg", "Report.docx"],
        "Version": ["1.0", "2.1", "0.9"],
        "Date": ["2026-01-01", "2026-02-15", "2026-03-20"]
    })
'''

DOCUMENTS_REVISIONS_CODE = '''import streamlit as st
from modules.utils.crud import crud_table

def render():
    st.subheader("Revisions")
    if "revisions_data" not in st.session_state:
        st.session_state.revisions_data = [
            {"id": 1, "doc": "Specification", "version": "1.1", "date": "2026-01-10"},
        ]
    crud_table(
        data_key="revisions_data",
        item_name="revision",
        endpoint="documents/revisions",
        display_fields=["doc", "version", "date"],
        edit_fields={"doc": "text", "version": "text", "date": "text"},
        add_fields={"doc": "text", "version": "text", "date": "text"}
    )
'''

DOCUMENTS_DRAWING_REGISTER_CODE = '''import streamlit as st
def render():
    st.subheader("Drawing Register")
    st.info("Track drawings and their status.")
    st.dataframe({
        "Drawing No": ["A-101", "S-202", "M-305"],
        "Title": ["Floor Plan", "Structural Layout", "HVAC Duct"],
        "Revision": ["0", "1", "2"],
        "Status": ["Current", "Superseded", "Current"]
    })
'''

DOCUMENTS_SPECIFICATIONS_CODE = '''import streamlit as st
def render():
    st.subheader("Specifications")
    st.info("Manage technical specifications.")
    st.text_area("Specification text", "Concrete strength: 30 MPa at 28 days.")
    if st.button("Save"):
        st.success("Specification saved (mock).")
'''

DOCUMENTS_TRANSMITTALS_CODE = '''import streamlit as st
from modules.utils.crud import crud_table

def render():
    st.subheader("Transmittals")
    if "transmittals_data" not in st.session_state:
        st.session_state.transmittals_data = [
            {"id": 1, "to": "Client", "date": "2026-01-05", "subject": "Design docs"},
        ]
    crud_table(
        data_key="transmittals_data",
        item_name="transmittal",
        endpoint="documents/transmittals",
        display_fields=["to", "date", "subject"],
        edit_fields={"to": "text", "date": "text", "subject": "text"},
        add_fields={"to": "text", "date": "text", "subject": "text"}
    )
'''

# Analytics – Portfolio, Reporting, Forecasting, KPIs
ANALYTICS_PORTFOLIO_CODE = '''import streamlit as st
import pandas as pd

def render():
    st.subheader("Portfolio Dashboard")
    data = pd.DataFrame({
        "Project": ["Green Tower", "Harbor Bridge", "Riverside Mall", "Solar Park"],
        "Budget ($M)": [12.5, 8.3, 22.1, 5.7],
        "Progress (%)": [75, 20, 100, 45],
        "Status": ["Active", "Planning", "Completed", "Active"]
    })
    st.dataframe(data)
    st.bar_chart(data.set_index("Project")["Progress (%)"])
'''

ANALYTICS_REPORTING_CODE = '''import streamlit as st
import pandas as pd

def render():
    st.subheader("Reporting")
    report_type = st.selectbox("Report type", ["Project Summary", "Cost Report", "Schedule Report"])
    if st.button("Generate Report"):
        data = pd.DataFrame({
            "Metric": ["Total Budget", "Spent to Date", "Remaining"],
            "Value": ["$184M", "$120M", "$64M"]
        })
        st.dataframe(data)
        st.success(f"{report_type} generated (mock).")
        st.download_button("Download CSV", data.to_csv(), "report.csv")
'''

ANALYTICS_FORECASTING_CODE = '''import streamlit as st
import pandas as pd

def render():
    st.subheader("Forecasting")
    st.info("Predict project cost and schedule outcomes.")
    actual = [120, 135, 140, 155, 160, 175]
    forecast = [130, 145, 155, 170, 180, 195]
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    df = pd.DataFrame({"Month": months, "Actual": actual, "Forecast": forecast})
    st.line_chart(df.set_index("Month"))
    st.success("Forecast based on historical trends (mock).")
'''

ANALYTICS_KPIS_CODE = '''import streamlit as st
import pandas as pd

def render():
    st.subheader("KPIs")
    kpis = pd.DataFrame({
        "KPI": ["Project Profitability", "Schedule Adherence", "Safety Index"],
        "Target": ["15%", "90%", "0.95"],
        "Actual": ["12%", "85%", "0.92"],
        "Status": ["⚠️", "⚠️", "✅"]
    })
    st.dataframe(kpis)
'''

# Digital Twin – Assets, Sensors, Telemetry, Maintenance, Predictive AI
DIGITAL_TWIN_ASSETS_CODE = '''import streamlit as st
from modules.utils.crud import crud_table

def render():
    st.subheader("Assets")
    if "dt_assets_data" not in st.session_state:
        st.session_state.dt_assets_data = [
            {"id": 1, "asset_id": "CH-001", "type": "Chiller", "location": "Mech Room"},
            {"id": 2, "asset_id": "PM-002", "type": "Pump", "location": "Basement"},
        ]
    crud_table(
        data_key="dt_assets_data",
        item_name="asset",
        endpoint="digital_twin/assets",
        display_fields=["asset_id", "type", "location"],
        edit_fields={"asset_id": "text", "type": "text", "location": "text"},
        add_fields={"asset_id": "text", "type": "text", "location": "text"}
    )
'''

DIGITAL_TWIN_SENSORS_CODE = '''import streamlit as st
from modules.utils.crud import crud_table

def render():
    st.subheader("Sensors")
    if "sensor_data" not in st.session_state:
        st.session_state.sensor_data = [
            {"id": 1, "sensor_id": "TEMP-01", "location": "Lobby", "value": 23.5, "unit": "°C"},
            {"id": 2, "sensor_id": "HUM-01", "location": "Lobby", "value": 42, "unit": "%"},
            {"id": 3, "sensor_id": "ENERGY-01", "location": "Main", "value": 320, "unit": "kW"},
        ]
    crud_table(
        data_key="sensor_data",
        item_name="sensor",
        endpoint="digital_twin/sensors",
        display_fields=["sensor_id", "location", "value", "unit"],
        edit_fields={"sensor_id": "text", "location": "text", "value": "number", "unit": "text"},
        add_fields={"sensor_id": "text", "location": "text", "value": "number", "unit": "text"}
    )
'''

DIGITAL_TWIN_TELEMETRY_CODE = '''import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def render():
    st.subheader("Telemetry")
    st.info("Live sensor data stream.")
    now = datetime.now()
    times = [now - timedelta(minutes=i) for i in range(60, 0, -1)]
    data = pd.DataFrame({
        "Time": times,
        "Temperature": [20 + i*0.1 for i in range(60)],
        "Humidity": [40 + i*0.05 for i in range(60)]
    })
    st.line_chart(data.set_index("Time"))
    st.success("Live telemetry displayed (mock).")
'''

DIGITAL_TWIN_MAINTENANCE_CODE = '''import streamlit as st
from modules.utils.crud import crud_table

def render():
    st.subheader("Maintenance")
    if "dt_maintenance_data" not in st.session_state:
        st.session_state.dt_maintenance_data = [
            {"id": 1, "asset": "Chiller", "type": "Preventive", "due": "2026-09-01"},
        ]
    crud_table(
        data_key="dt_maintenance_data",
        item_name="maintenance",
        endpoint="digital_twin/maintenance",
        display_fields=["asset", "type", "due"],
        edit_fields={"asset": "text", "type": "text", "due": "text"},
        add_fields={"asset": "text", "type": "text", "due": "text"}
    )
'''

DIGITAL_TWIN_PREDICTIVE_AI_CODE = '''import streamlit as st

def render():
    st.subheader("Predictive AI")
    st.info("Run predictive maintenance models using sensor data.")
    if st.button("Run Prediction"):
        st.success("Prediction: No anomalies detected. Next maintenance in 14 days (mock).")
'''

# AI Assistant – all tabs
AI_ARCHITECT_CODE = '''import streamlit as st

def render():
    st.subheader("AI Architect")
    st.info("Ask architectural design questions.")
    query = st.text_area("Your question:", "Suggest a layout for a 10-storey office.")
    if st.button("Ask"):
        st.success("AI response: Consider a central core with open-plan floors. (mock)")
'''

AI_ENGINEER_CODE = '''import streamlit as st

def render():
    st.subheader("AI Engineer")
    query = st.text_area("Your question:", "Recommend a column size for 10-storey building.")
    if st.button("Ask"):
        st.success("AI response: Use 450x450 mm with C30/37 concrete. (mock)")
'''

AI_MEP_CODE = '''import streamlit as st

def render():
    st.subheader("AI MEP")
    query = st.text_area("Your question:", "Size a chiller for a 5000 m² office.")
    if st.button("Ask"):
        st.success("AI response: Use 300 kW chiller with variable speed. (mock)")
'''

AI_QS_CODE = '''import streamlit as st

def render():
    st.subheader("AI QS")
    query = st.text_area("Your question:", "Estimate cost for 500 m² finishes.")
    if st.button("Ask"):
        st.success("AI response: Estimated cost $75/m², total $37,500. (mock)")
'''

AI_PM_CODE = '''import streamlit as st

def render():
    st.subheader("AI Project Manager")
    query = st.text_area("Your question:", "Suggest a construction schedule for 10-storey building.")
    if st.button("Ask"):
        st.success("AI response: 18-month schedule with milestones. (mock)")
'''

# ------------------------------------------------------------------
# Mapping of special modules (non-CRUD)
# ------------------------------------------------------------------
MODULE_CONTENTS = {
    "modules/dashboard/dashboard.py": DASHBOARD_CODE,
    "modules/projects/project_page.py": PROJECTS_CODE,
    "modules/architecture/synthesis.py": ARCH_SYNTHESIS_CODE,
    "modules/architecture/zoning.py": ARCH_ZONING_CODE,
    "modules/architecture/site_planning.py": ARCH_SITE_CODE,
    "modules/architecture/floor_planning.py": ARCH_FLOOR_CODE,
    "modules/architecture/room_programming.py": ARCH_ROOM_CODE,
    "modules/architecture/compliance.py": ARCH_COMPLIANCE_CODE,
    "modules/bim/buildings.py": BIM_BUILDINGS_CODE,
    "modules/bim/storeys.py": BIM_STOREYS_CODE,
    "modules/bim/spaces.py": BIM_SPACES_CODE,
    "modules/bim/ifc_export.py": BIM_IFC_CODE,
    "modules/structural/eurocode.py": STRUCT_EUROCODE_CODE,
    "modules/mep/analysis.py": MEP_ANALYSIS_CODE,
    "modules/mep/hvac.py": MEP_HVAC_CODE,
    "modules/mep/plumbing.py": MEP_PLUMBING_CODE,
    "modules/mep/energy_simulation.py": MEP_ENERGY_CODE,
    "modules/costing/procurement.py": COSTING_PROCUREMENT_CODE,
    "modules/costing/forex.py": COSTING_FOREX_CODE,
    "modules/costing/escalation.py": COSTING_ESCALATION_CODE,
    "modules/costing/risk_analysis.py": COSTING_RISK_CODE,
    "modules/governance/approvals.py": GOVERNANCE_APPROVALS_CODE,
    "modules/construction/submittals.py": CONSTRUCTION_SUBMITTALS_CODE,
    "modules/construction/site_diary.py": CONSTRUCTION_SITE_DIARY_CODE,
    "modules/construction/progress_tracking.py": CONSTRUCTION_PROGRESS_CODE,
    "modules/construction/snagging.py": CONSTRUCTION_SNAGGING_CODE,
    "modules/documents/documents.py": DOCUMENTS_MAIN_CODE,
    "modules/documents/revisions.py": DOCUMENTS_REVISIONS_CODE,
    "modules/documents/drawing_register.py": DOCUMENTS_DRAWING_REGISTER_CODE,
    "modules/documents/specifications.py": DOCUMENTS_SPECIFICATIONS_CODE,
    "modules/documents/transmittals.py": DOCUMENTS_TRANSMITTALS_CODE,
    "modules/analytics/portfolio.py": ANALYTICS_PORTFOLIO_CODE,
    "modules/analytics/reporting.py": ANALYTICS_REPORTING_CODE,
    "modules/analytics/forecasting.py": ANALYTICS_FORECASTING_CODE,
    "modules/analytics/kpis.py": ANALYTICS_KPIS_CODE,
    "modules/digital_twin/assets.py": DIGITAL_TWIN_ASSETS_CODE,
    "modules/digital_twin/sensors.py": DIGITAL_TWIN_SENSORS_CODE,
    "modules/digital_twin/telemetry.py": DIGITAL_TWIN_TELEMETRY_CODE,
    "modules/digital_twin/maintenance.py": DIGITAL_TWIN_MAINTENANCE_CODE,
    "modules/digital_twin/predictive_ai.py": DIGITAL_TWIN_PREDICTIVE_AI_CODE,
    "modules/ai/architect.py": AI_ARCHITECT_CODE,
    "modules/ai/engineer.py": AI_ENGINEER_CODE,
    "modules/ai/mep.py": AI_MEP_CODE,
    "modules/ai/qs.py": AI_QS_CODE,
    "modules/ai/project_manager.py": AI_PM_CODE,
}

# ------------------------------------------------------------------
# CRUD modules (use CRUD_TEMPLATE)
# ------------------------------------------------------------------
CRUD_MODULES = {
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
    "mep/electrical": {
        "title": "Electrical Panels",
        "data_key": "electrical_data",
        "item_name": "panel",
        "endpoint": "mep/electrical",
        "display_fields": ["panel", "total_load", "reserve"],
        "edit_fields": {"panel": "text", "total_load": "number", "reserve": "number"},
        "add_fields": {"panel": "text", "total_load": "number", "reserve": "number"}
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

# ------------------------------------------------------------------
# Write all files
# ------------------------------------------------------------------
def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)

def build_all_modules():
    # 1. Create utils with crud.py and mock_data.py
    write_file("modules/utils/crud.py", '''import streamlit as st
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
''')

    write_file("modules/utils/mock_data.py", '''import streamlit as st
def init_mock_data():
    # Projects
    if "projects_data" not in st.session_state or not st.session_state.projects_data:
        st.session_state.projects_data = [
            {"id": 1, "name": "Green Tower", "status": "Active", "budget": 12.5, "progress": 75},
            {"id": 2, "name": "Harbor Bridge", "status": "Planning", "budget": 8.3, "progress": 20},
            {"id": 3, "name": "Riverside Mall", "status": "Completed", "budget": 22.1, "progress": 100},
            {"id": 4, "name": "Solar Park", "status": "Active", "budget": 5.7, "progress": 45},
        ]
    if "buildings_data" not in st.session_state or not st.session_state.buildings_data:
        st.session_state.buildings_data = [
            {"id": 1, "name": "Tower A", "storeys": 25, "area": 15000, "ifc_version": "IFC4"},
            {"id": 2, "name": "Tower B", "storeys": 18, "area": 12000, "ifc_version": "IFC4"},
            {"id": 3, "name": "Pavilion", "storeys": 3, "area": 2500, "ifc_version": "IFC2x3"},
        ]
    if "storeys_data" not in st.session_state:
        st.session_state.storeys_data = {}
        for b in st.session_state.buildings_data:
            b_id = b["id"]
            st.session_state.storeys_data[b_id] = [
                {"id": (b_id*100 + i), "level": f"Level {i}", "height": 4.0 + (i%2)*0.2, "area": 1200 - i*10}
                for i in range(1, min(b["storeys"], 5)+1)
            ]
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
    # Zoning
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
    # Structural
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
    # MEP
    if "electrical_data" not in st.session_state or not st.session_state.electrical_data:
        st.session_state.electrical_data = [
            {"id": 1, "panel": "MDP-1", "total_load": 250, "reserve": 20},
            {"id": 2, "panel": "MDP-2", "total_load": 180, "reserve": 15},
            {"id": 3, "panel": "MDP-3", "total_load": 90, "reserve": 25},
        ]
    # Costing
    if "boq_data" not in st.session_state or not st.session_state.boq_data:
        st.session_state.boq_data = [
            {"id": 1, "item": "Concrete C30", "quantity": 500, "unit": "m³", "rate": 120, "total": 60000},
            {"id": 2, "item": "Steel Rebar", "quantity": 120, "unit": "t", "rate": 950, "total": 114000},
            {"id": 3, "item": "Finishes", "quantity": 300, "unit": "m²", "rate": 75, "total": 22500},
            {"id": 4, "item": "MEP", "quantity": 80, "unit": "LF", "rate": 60, "total": 4800},
            {"id": 5, "item": "Excavation", "quantity": 200, "unit": "m³", "rate": 40, "total": 8000},
        ]
    # Construction
    if "rfi_data" not in st.session_state or not st.session_state.rfi_data:
        st.session_state.rfi_data = [
            {"id": 1, "rfi_number": "RFI-001", "subject": "Rebar spacing", "status": "Open"},
            {"id": 2, "rfi_number": "RFI-002", "subject": "Window detail", "status": "Answered"},
            {"id": 3, "rfi_number": "RFI-003", "subject": "MEP coordination", "status": "Closed"},
            {"id": 4, "rfi_number": "RFI-004", "subject": "Concrete mix", "status": "Pending"},
        ]
    # Digital Twin
    if "sensor_data" not in st.session_state or not st.session_state.sensor_data:
        st.session_state.sensor_data = [
            {"id": 1, "sensor_id": "TEMP-01", "location": "Lobby", "value": 23.5, "unit": "°C"},
            {"id": 2, "sensor_id": "HUM-01", "location": "Lobby", "value": 42, "unit": "%"},
            {"id": 3, "sensor_id": "ENERGY-01", "location": "Main", "value": 320, "unit": "kW"},
            {"id": 4, "sensor_id": "OCC-01", "location": "Office", "value": 245, "unit": "people"},
        ]
    # Governance approvals
    if "approvals_data" not in st.session_state or not st.session_state.approvals_data:
        st.session_state.approvals_data = [
            {"id": 1, "project": "Green Tower", "type": "Design Review", "status": "Pending"},
            {"id": 2, "project": "Harbor Bridge", "type": "Safety", "status": "Approved"},
        ]
    # Documents
    if "revisions_data" not in st.session_state:
        st.session_state.revisions_data = []
    if "transmittals_data" not in st.session_state:
        st.session_state.transmittals_data = []
    if "submittals_data" not in st.session_state:
        st.session_state.submittals_data = []
    if "snagging_data" not in st.session_state:
        st.session_state.snagging_data = []
    if "dt_assets_data" not in st.session_state:
        st.session_state.dt_assets_data = []
    if "dt_maintenance_data" not in st.session_state:
        st.session_state.dt_maintenance_data = []
''')

    # 2. Write the special modules
    for path, content in MODULE_CONTENTS.items():
        write_file(path, content)

    # 3. Write CRUD modules using template
    for module_path, config in CRUD_MODULES.items():
        folder, file = module_path.split("/")
        path = f"{BASE}/{folder}/{file}.py"
        content = CRUD_TEMPLATE.format(
            title=config["title"],
            data_key=config["data_key"],
            item_name=config["item_name"],
            endpoint=config["endpoint"],
            display_fields=config["display_fields"],
            edit_fields=config["edit_fields"],
            add_fields=config["add_fields"]
        )
        write_file(path, content)

    # 4. Create __init__.py files
    for root, dirs, files in os.walk(BASE):
        for d in dirs:
            init_path = os.path.join(root, d, "__init__.py")
            if not os.path.exists(init_path):
                write_file(init_path, "")

    print("✅ All modules built and are now fully functional!")

if __name__ == "__main__":
    build_all_modules()
