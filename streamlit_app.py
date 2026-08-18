# streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import random

# ---------------------------
# Page configuration
# ---------------------------
st.set_page_config(
    page_title="IMAGINE Platform",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------
# Load custom CSS (embedded fallback)
# ---------------------------
def load_css():
    # Try to load external style.css, but fall back to embedded styles
    try:
        with open("style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        # Embedded CSS (teal & orange theme)
        st.markdown("""
        <style>
        .metric-card {
            background: white;
            padding: 1.2rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            text-align: center;
            border-left: 5px solid #00695C;
        }
        .metric-value {
            font-size: 2.2rem;
            font-weight: 700;
            color: #00695C;
        }
        .metric-change {
            font-size: 0.9rem;
        }
        .stButton button {
            background: linear-gradient(135deg, #00695C, #00897B);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1.2rem;
            transition: all 0.2s;
        }
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,105,92,0.3);
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            background: #f0f4f8;
            border-radius: 12px;
            padding: 4px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 8px 20px;
            font-weight: 500;
            color: #1a2a3a;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: #00695C;
            color: white;
        }
        h1, h2, h3 {
            color: #004d40;
            font-weight: 600;
        }
        .sidebar .sidebar-content {
            background: #004d40;
        }
        </style>
        """, unsafe_allow_html=True)

load_css()

# ---------------------------
# Authentication (mock)
# ---------------------------
def check_authentication():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        with st.sidebar:
            st.subheader("🔐 Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Sign In"):
                if username and password:
                    st.session_state.authenticated = True
                    st.session_state.user = username
                    st.session_state.role = "Project Manager"
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        st.stop()

check_authentication()

# ---------------------------
# Session state initialisation
# ---------------------------
def init_session_state():
    # Projects
    if "projects_data" not in st.session_state:
        st.session_state.projects_data = [
            {"ID": 1, "Name": "Green Tower", "Status": "Active", "Budget (M USD)": 12.5, "Progress %": 75},
            {"ID": 2, "Name": "Harbor Bridge", "Status": "Planning", "Budget (M USD)": 8.3, "Progress %": 20},
            {"ID": 3, "Name": "Riverside Mall", "Status": "Completed", "Budget (M USD)": 22.1, "Progress %": 100},
            {"ID": 4, "Name": "Solar Park", "Status": "Active", "Budget (M USD)": 5.7, "Progress %": 45},
        ]
    # BIM
    if "bim_buildings" not in st.session_state:
        st.session_state.bim_buildings = [
            {"Building": "Tower A", "Storeys": 25, "Area (m²)": 15000, "IFC Version": "IFC4"},
            {"Building": "Tower B", "Storeys": 18, "Area (m²)": 12000, "IFC Version": "IFC4"},
            {"Building": "Pavilion", "Storeys": 3, "Area (m²)": 2500, "IFC Version": "IFC2x3"},
        ]
    if "bim_storeys" not in st.session_state:
        st.session_state.bim_storeys = {
            "Tower A": [{"Level": f"Level {i}", "Height (m)": 4.0 + (i%2)*0.2, "Area (m²)": 1200 - i*10} for i in range(1, 6)],
            "Tower B": [{"Level": f"Level {i}", "Height (m)": 3.8, "Area (m²)": 1150 - i*10} for i in range(1, 5)],
            "Pavilion": [{"Level": f"Level {i}", "Height (m)": 3.5, "Area (m²)": 2500} for i in range(1, 4)],
        }
    if "bim_spaces" not in st.session_state:
        st.session_state.bim_spaces = [
            {"Space": "Office 101", "Area (m²)": 45, "Height (m)": 3.2, "Type": "Workspace"},
            {"Space": "Conference", "Area (m²)": 30, "Height (m)": 3.5, "Type": "Meeting"},
            {"Space": "Lobby", "Area (m²)": 80, "Height (m)": 5.0, "Type": "Public"},
            {"Space": "Cafeteria", "Area (m²)": 60, "Height (m)": 3.0, "Type": "Amenity"},
        ]
    if "bim_elements" not in st.session_state:
        st.session_state.bim_elements = [
            {"Element": "Wall", "Material": "Concrete", "Quantity": 120, "Unit": "m²"},
            {"Element": "Slab", "Material": "Concrete", "Quantity": 80, "Unit": "m²"},
            {"Element": "Column", "Material": "Steel", "Quantity": 45, "Unit": "each"},
            {"Element": "Beam", "Material": "Steel", "Quantity": 30, "Unit": "each"},
        ]
    if "bim_cobie" not in st.session_state:
        st.session_state.bim_cobie = [
            {"Asset": "Chiller", "Serial": "CH-001", "Manufacturer": "Trane", "Warranty (years)": 5},
            {"Asset": "Pump", "Serial": "PM-002", "Manufacturer": "Grundfos", "Warranty (years)": 3},
            {"Asset": "AHU", "Serial": "AH-003", "Manufacturer": "Carrier", "Warranty (years)": 4},
            {"Asset": "Boiler", "Serial": "BL-004", "Manufacturer": "Viessmann", "Warranty (years)": 6},
        ]
    # Architecture
    if "zoning_data" not in st.session_state:
        st.session_state.zoning_data = [
            {"Zone": "Residential", "Max Height (m)": 15, "Coverage (%)": 50, "Setback (m)": 3},
            {"Zone": "Commercial", "Max Height (m)": 30, "Coverage (%)": 60, "Setback (m)": 5},
            {"Zone": "Mixed-Use", "Max Height (m)": 45, "Coverage (%)": 70, "Setback (m)": 4},
        ]
    if "room_program" not in st.session_state:
        st.session_state.room_program = [
            {"Room": "Office", "Area (m²)": 20, "Quantity": 10, "Adjacency": ""},
            {"Room": "Conference", "Area (m²)": 40, "Quantity": 2, "Adjacency": "Lobby"},
            {"Room": "Lobby", "Area (m²)": 60, "Quantity": 1, "Adjacency": "Lobby"},
            {"Room": "Restroom", "Area (m²)": 10, "Quantity": 4, "Adjacency": "Corridor"},
        ]
    # Structural
    if "structural_beams" not in st.session_state:
        st.session_state.structural_beams = [
            {"Beam ID": "B-101", "Span (m)": 6.5, "Load (kN/m)": 45, "Status": "OK"},
            {"Beam ID": "B-102", "Span (m)": 8.2, "Load (kN/m)": 60, "Status": "Overstressed"},
            {"Beam ID": "B-201", "Span (m)": 5.0, "Load (kN/m)": 30, "Status": "OK"},
            {"Beam ID": "B-202", "Span (m)": 7.0, "Load (kN/m)": 50, "Status": "OK"},
        ]
    if "structural_columns" not in st.session_state:
        st.session_state.structural_columns = [
            {"Column ID": "C-1", "Axial Load (kN)": 1200, "Section": "400x400", "Reinf. Ratio (%)": 1.5},
            {"Column ID": "C-2", "Axial Load (kN)": 800, "Section": "300x300", "Reinf. Ratio (%)": 1.2},
            {"Column ID": "C-3", "Axial Load (kN)": 1500, "Section": "500x500", "Reinf. Ratio (%)": 2.0},
            {"Column ID": "C-4", "Axial Load (kN)": 950, "Section": "350x350", "Reinf. Ratio (%)": 1.3},
        ]
    if "structural_slabs" not in st.session_state:
        st.session_state.structural_slabs = [
            {"Slab ID": "S1", "Thickness (mm)": 200, "Span (m)": 6, "Load (kN/m²)": 5},
            {"Slab ID": "S2", "Thickness (mm)": 150, "Span (m)": 4, "Load (kN/m²)": 4},
            {"Slab ID": "S3", "Thickness (mm)": 250, "Span (m)": 7, "Load (kN/m²)": 6},
            {"Slab ID": "S4", "Thickness (mm)": 180, "Span (m)": 5, "Load (kN/m²)": 4.5},
        ]
    if "structural_foundations" not in st.session_state:
        st.session_state.structural_foundations = [
            {"Foundation": "Pad", "Capacity (kN)": 800, "Depth (m)": 1.5, "Type": "Isolated"},
            {"Foundation": "Strip", "Capacity (kN)": 500, "Depth (m)": 1.0, "Type": "Continuous"},
            {"Foundation": "Pile", "Capacity (kN)": 1200, "Depth (m)": 12, "Type": "Driven"},
            {"Foundation": "Raft", "Capacity (kN)": 1500, "Depth (m)": 0.8, "Type": "Mat"},
        ]
    if "structural_retaining" not in st.session_state:
        st.session_state.structural_retaining = [
            {"Wall": "RW-1", "Height (m)": 4.5, "Thickness (m)": 0.3, "Stability": "OK"},
            {"Wall": "RW-2", "Height (m)": 6.0, "Thickness (m)": 0.4, "Stability": "OK"},
            {"Wall": "RW-3", "Height (m)": 3.2, "Thickness (m)": 0.25, "Stability": "Warning"},
        ]
    if "structural_connections" not in st.session_state:
        st.session_state.structural_connections = [
            {"Connection": "Moment", "Bolts": "M20", "Capacity (kN)": 200},
            {"Connection": "Shear", "Bolts": "M16", "Capacity (kN)": 120},
            {"Connection": "Base Plate", "Bolts": "M24", "Capacity (kN)": 350},
            {"Connection": "Brace", "Bolts": "M22", "Capacity (kN)": 180},
        ]
    # MEP
    if "mep_hvac" not in st.session_state:
        st.session_state.mep_hvac = {
            "Cooling (kW)": {"Office": 150, "Atrium": 80, "Core": 30},
            "Heating (kW)": {"Office": 100, "Atrium": 60, "Core": 20},
        }
    if "mep_electrical" not in st.session_state:
        st.session_state.mep_electrical = [
            {"Panel": "MDP-1", "Total Load (kVA)": 250, "Reserve (%)": 20},
            {"Panel": "MDP-2", "Total Load (kVA)": 180, "Reserve (%)": 15},
            {"Panel": "MDP-3", "Total Load (kVA)": 90, "Reserve (%)": 25},
        ]
    # Costing
    if "costing_boq" not in st.session_state:
        st.session_state.costing_boq = [
            {"Item": "Concrete C30", "Quantity": 500, "Unit": "m³", "Rate (USD)": 120, "Total (USD)": 60000},
            {"Item": "Steel Rebar", "Quantity": 120, "Unit": "t", "Rate (USD)": 950, "Total (USD)": 114000},
            {"Item": "Finishes", "Quantity": 300, "Unit": "m²", "Rate (USD)": 75, "Total (USD)": 22500},
            {"Item": "MEP", "Quantity": 80, "Unit": "LF", "Rate (USD)": 60, "Total (USD)": 4800},
            {"Item": "Excavation", "Quantity": 200, "Unit": "m³", "Rate (USD)": 40, "Total (USD)": 8000},
        ]
    # Construction
    if "construction_rfis" not in st.session_state:
        st.session_state.construction_rfis = [
            {"RFI #": "RFI-001", "Subject": "Rebar spacing", "Status": "Open"},
            {"RFI #": "RFI-002", "Subject": "Window detail", "Status": "Answered"},
            {"RFI #": "RFI-003", "Subject": "MEP coordination", "Status": "Closed"},
            {"RFI #": "RFI-004", "Subject": "Concrete mix", "Status": "Pending"},
        ]
    # Regional
    if "regional_codes" not in st.session_state:
        st.session_state.regional_codes = {
            "Uganda": {"Code": "UNBC 2020", "Seismic Zone": "Zone 3", "Wind Speed": "35 m/s"},
            "Kenya": {"Code": "KBC 2015", "Seismic Zone": "Zone 2", "Wind Speed": "30 m/s"},
            "Tanzania": {"Code": "TBS 2018", "Seismic Zone": "Zone 2", "Wind Speed": "28 m/s"},
            "Rwanda": {"Code": "RBC 2019", "Seismic Zone": "Zone 3", "Wind Speed": "32 m/s"},
            "South Sudan": {"Code": "SSBC 2021", "Seismic Zone": "Zone 1", "Wind Speed": "25 m/s"},
        }
    # Digital Twin
    if "dt_sensors" not in st.session_state:
        st.session_state.dt_sensors = [
            {"Sensor ID": "TEMP-01", "Location": "Lobby", "Value": 23.5, "Unit": "°C"},
            {"Sensor ID": "HUM-01", "Location": "Lobby", "Value": 42, "Unit": "%"},
            {"Sensor ID": "ENERGY-01", "Location": "Main", "Value": 320, "Unit": "kW"},
            {"Sensor ID": "OCC-01", "Location": "Office", "Value": 245, "Unit": "people"},
        ]

init_session_state()

# ---------------------------
# Navigation Sidebar
# ---------------------------
st.sidebar.title("🏗️ IMAGINE")
st.sidebar.markdown(f"Welcome, **{st.session_state.user}**")
st.sidebar.markdown(f"Role: `{st.session_state.role}`")
if st.sidebar.button("Sign Out"):
    st.session_state.authenticated = False
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
# Helper function for editable tables
# ---------------------------
def editable_table(data, key, columns=None):
    df = pd.DataFrame(data)
    if columns:
        df = df[columns]
    edited = st.data_editor(df, use_container_width=True, num_rows="dynamic", key=key)
    return edited.to_dict('records')

# ---------------------------
# PAGE: DASHBOARD
# ---------------------------
def page_dashboard():
    st.title("📊 Dashboard")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card"><h4>Active Projects</h4><div class="metric-value">12</div><div class="metric-change" style="color:#FF6F00;">↑ 2</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><h4>Total Budget</h4><div class="metric-value">$184M</div><div class="metric-change" style="color:#FF6F00;">↑ 5%</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><h4>Progress (avg)</h4><div class="metric-value">68%</div><div class="metric-change" style="color:#FF6F00;">↑ 12%</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card"><h4>Open RFIs</h4><div class="metric-value">7</div><div class="metric-change" style="color:#d32f2f;">↓ 3</div></div>', unsafe_allow_html=True)

    st.subheader("Project Health")
    df_proj = pd.DataFrame(st.session_state.projects_data)
    fig = px.bar(df_proj, x="Name", y="Progress %", color="Status", text="Progress %")
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Recent Activity")
    activity = pd.DataFrame({
        "Time": [datetime.now() - timedelta(hours=i) for i in range(5)],
        "User": ["Alice", "Bob", "Charlie", "Alice", "Dave"],
        "Action": ["Updated BOQ", "Submitted RFI", "Approved revision", "Added drawing", "Closed snag"],
    })
    st.dataframe(activity, use_container_width=True)

# ---------------------------
# PAGE: PROJECTS
# ---------------------------
def page_projects():
    st.title("📁 Projects")
    st.session_state.projects_data = editable_table(st.session_state.projects_data, "projects_editor")

    with st.expander("➕ Add New Project"):
        with st.form("new_project_form"):
            name = st.text_input("Project Name")
            status = st.selectbox("Status", ["Planning", "Active", "On Hold", "Completed"])
            budget = st.number_input("Budget (M USD)", min_value=0.0, step=0.1)
            progress = st.slider("Progress %", 0, 100, 0)
            if st.form_submit_button("Create"):
                new_id = max([p["ID"] for p in st.session_state.projects_data]) + 1 if st.session_state.projects_data else 1
                st.session_state.projects_data.append({
                    "ID": new_id,
                    "Name": name,
                    "Status": status,
                    "Budget (M USD)": budget,
                    "Progress %": progress,
                })
                st.success("Project added!")
                st.rerun()

# ---------------------------
# PAGE: ARCHITECTURE
# ---------------------------
def page_architecture():
    st.title("📐 Architecture")
    tabs = ["Generative Design", "Zoning", "Site Planning", "Floor Planning", "Room Programming", "Compliance"]
    tab_objects = st.tabs(tabs)

    with tab_objects[0]:
        st.subheader("Generative Design Options")
        col1, col2 = st.columns(2)
        with col1:
            iterations = st.slider("Iterations", 10, 100, 50)
            objective = st.selectbox("Objective", ["Maximize area", "Minimize energy", "Balance"])
        with col2:
            population = st.slider("Population", 20, 200, 100)
            seed = st.number_input("Seed", value=42)
        if st.button("Run Generative Design"):
            with st.spinner("Generating..."):
                options = pd.DataFrame({
                    "Option": ["A", "B", "C"],
                    "Area (m²)": [12500, 11800, 13200],
                    "Energy (kWh/m²)": [45, 42, 48],
                    "Score": [0.85, 0.82, 0.90],
                })
                st.dataframe(options)
                st.bar_chart(options.set_index("Option")["Score"])

    with tab_objects[1]:
        st.subheader("Zoning & Land Use")
        st.session_state.zoning_data = editable_table(st.session_state.zoning_data, "zoning_editor")

    with tab_objects[2]:
        st.subheader("Site Planning")
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("Site Area (m²)", value=5000)
            st.slider("Slope (%)", 0, 20, 5)
        with col2:
            st.selectbox("Soil Type", ["Clay", "Sand", "Rock"])
            st.selectbox("Orientation", ["North", "South", "East", "West"])
        st.text("Site layout placeholder")

    with tab_objects[3]:
        st.subheader("Floor Planning")
        st.selectbox("Building Type", ["Office", "Residential", "Hospital", "School"])
        st.slider("Number of floors", 1, 20, 5)
        if st.button("Generate Floor Plan"):
            st.success("Floor plan generated")
            st.text("Floor plan image placeholder")

    with tab_objects[4]:
        st.subheader("Room Programming")
        st.session_state.room_program = editable_table(st.session_state.room_program, "room_editor")

    with tab_objects[5]:
        st.subheader("Compliance Checking")
        st.selectbox("Select Code", ["Uganda National Building Code", "Kenya Building Code", "Tanzania Building Standards"])
        st.file_uploader("Upload floor plan (DXF/PDF)", type=["dxf", "pdf"])
        if st.button("Run Compliance Check"):
            results = pd.DataFrame({
                "Rule": ["Fire escape distance", "Parking ratio", "Daylight factor"],
                "Required": ["< 30m", "1:100 m²", "> 2%"],
                "Actual": ["25m", "1:120 m²", "2.5%"],
                "Status": ["Pass", "Warning", "Pass"],
            })
            st.dataframe(results, use_container_width=True)

# ---------------------------
# PAGE: BIM
# ---------------------------
def page_bim():
    st.title("🏛️ BIM")
    tabs = ["Buildings", "Storeys", "Spaces", "Elements", "IFC Viewer", "COBie", "Digital Twin"]
    tab_objects = st.tabs(tabs)

    with tab_objects[0]:
        st.session_state.bim_buildings = editable_table(st.session_state.bim_buildings, "bim_buildings_editor")

    with tab_objects[1]:
        building_names = [b["Building"] for b in st.session_state.bim_buildings]
        if building_names:
            selected = st.selectbox("Select Building", building_names)
            if selected:
                if selected not in st.session_state.bim_storeys:
                    st.session_state.bim_storeys[selected] = [
                        {"Level": f"Level {i}", "Height (m)": 4.0, "Area (m²)": 1000} for i in range(1, 4)
                    ]
                storeys = st.session_state.bim_storeys[selected]
                edited = editable_table(storeys, f"storeys_{selected}")
                st.session_state.bim_storeys[selected] = edited

    with tab_objects[2]:
        st.session_state.bim_spaces = editable_table(st.session_state.bim_spaces, "bim_spaces_editor")

    with tab_objects[3]:
        st.session_state.bim_elements = editable_table(st.session_state.bim_elements, "bim_elements_editor")

    with tab_objects[4]:
        st.info("IFC Viewer (integrate with xeokit or Three.js)")
        st.file_uploader("Upload IFC file", type=["ifc"])
        st.caption("Supports IFC4, IFC2x3")

    with tab_objects[5]:
        st.session_state.bim_cobie = editable_table(st.session_state.bim_cobie, "bim_cobie_editor")
        st.download_button("Export COBie (Excel)", data="", file_name="cobie_export.xlsx")

    with tab_objects[6]:
        st.subheader("Digital Twin – Live Data")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Occupancy", "245 people", "+12")
            st.metric("Energy (kW)", "320", "-8%")
        with col2:
            st.metric("Temperature", "23.5°C", "+0.5")
            st.metric("Humidity", "42%", "-3%")
        now = datetime.now()
        start_time = now - timedelta(hours=23)
        times = [start_time + timedelta(hours=i) for i in range(24)]
        energy_vals = [310 - i*5 for i in range(24)]
        df_energy = pd.DataFrame({"Time": times, "Energy": energy_vals})
        st.line_chart(df_energy.set_index("Time"))

# ---------------------------
# PAGE: STRUCTURAL
# ---------------------------
def page_structural():
    st.title("🔩 Structural Engineering")
    tabs = ["Eurocode", "Beam Design", "Column Design", "Slab Design", "Foundation Design", "Retaining Walls", "Steel Connections", "FEA"]
    tab_objects = st.tabs(tabs)

    with tab_objects[0]:
        st.subheader("Eurocode Modules")
        codes = {
            "EN 1990 (Basis)": True,
            "EN 1991 (Actions)": True,
            "EN 1992 (Concrete)": True,
            "EN 1993 (Steel)": True,
            "EN 1995 (Timber)": True,
            "EN 1997 (Geotech)": True,
            "EN 1998 (Seismic)": True,
        }
        cols = st.columns(4)
        for i, (code, default) in enumerate(codes.items()):
            cols[i % 4].checkbox(code, value=default)
        st.subheader("Load Combinations")
        st.dataframe(pd.DataFrame({
            "Combination": ["ULS 1", "ULS 2", "SLS 1"],
            "G (dead)": [1.35, 1.0, 1.0],
            "Q (live)": [1.5, 1.5, 0.7],
            "Wind": [0, 0.6, 0.3],
        }))

    with tab_objects[1]:
        st.session_state.structural_beams = editable_table(st.session_state.structural_beams, "beams_editor")
        with st.expander("New Beam Design"):
            with st.form("beam_form"):
                st.text_input("Beam ID")
                st.number_input("Span (m)", min_value=1.0)
                st.number_input("Load (kN/m)", min_value=0.0)
                st.selectbox("Material", ["Concrete C30/37", "Steel S355"])
                st.form_submit_button("Design")

    with tab_objects[2]:
        st.session_state.structural_columns = editable_table(st.session_state.structural_columns, "columns_editor")

    with tab_objects[3]:
        st.session_state.structural_slabs = editable_table(st.session_state.structural_slabs, "slabs_editor")
        st.text("Slab reinforcement layout placeholder")

    with tab_objects[4]:
        st.session_state.structural_foundations = editable_table(st.session_state.structural_foundations, "foundations_editor")

    with tab_objects[5]:
        st.session_state.structural_retaining = editable_table(st.session_state.structural_retaining, "retaining_editor")
        st.text("Retaining wall section placeholder")

    with tab_objects[6]:
        st.session_state.structural_connections = editable_table(st.session_state.structural_connections, "connections_editor")
        st.info("Design according to EN 1993-1-8")

    with tab_objects[7]:
        st.subheader("Finite Element Analysis")
        st.selectbox("Analysis Type", ["Linear Static", "Nonlinear", "Modal", "Pushover"])
        if st.button("Run Analysis"):
            with st.spinner("Solving..."):
                st.success("Analysis complete")
                st.text("FEA displacement contour placeholder")

# ---------------------------
# PAGE: MEP
# ---------------------------
def page_mep():
    st.title("⚡ MEP")
    tabs = ["Mechanical (HVAC)", "Electrical", "Plumbing"]
    tab_objects = st.tabs(tabs)

    with tab_objects[0]:
        st.subheader("HVAC Load Summary")
        hvac = st.session_state.mep_hvac
        df_hvac = pd.DataFrame(hvac)
        st.bar_chart(df_hvac)
        st.subheader("Ventilation & Chilled Water")
        st.write("Placeholder for duct sizing and pump schedules")

    with tab_objects[1]:
        st.subheader("Electrical Load Analysis")
        st.session_state.mep_electrical = editable_table(st.session_state.mep_electrical, "electrical_editor")
        st.subheader("Solar PV Sizing")
        st.slider("Peak Power (kWp)", 0, 500, 150)

    with tab_objects[2]:
        st.subheader("Water Supply Network")
        st.line_chart(pd.DataFrame({"Flow (L/s)": [2.5, 3.2, 2.8, 4.1]}))
        st.subheader("Drainage & Stormwater")
        st.write("Placeholder for pipe routing and catch basins")

# ---------------------------
# PAGE: COSTING
# ---------------------------
def page_costing():
    st.title("💰 Cost Estimation")
    st.session_state.costing_boq = editable_table(st.session_state.costing_boq, "boq_editor")
    total = sum(item["Total (USD)"] for item in st.session_state.costing_boq)
    st.metric("Total Estimated Cost", f"${total:,.0f}")

    st.subheader("Cost Breakdown")
    df_boq = pd.DataFrame(st.session_state.costing_boq)
    fig = px.pie(df_boq, values="Total (USD)", names="Item")
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Forex & Inflation"):
        st.write("Exchange rates: USD/UGX 3700, USD/KES 130")
        st.slider("Inflation factor", 0.0, 0.15, 0.05)

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
        st.session_state.construction_rfis = editable_table(st.session_state.construction_rfis, "rfi_editor")

    st.subheader("Site Diary (latest)")
    diary = """2026-08-19: Completed foundation pour for Block A. 
    Weather: sunny, 28°C. 12 workers on site. Equipment: 2 mixers.
    Safety: no incidents.
    """
    st.text_area("Today's Log", diary, height=150)
    st.subheader("Snagging & Variations")
    st.write("Placeholder for snag list and variation orders")

# ---------------------------
# PAGE: REGIONAL
# ---------------------------
def page_regional():
    st.title("🌍 Regional – East Africa Codes")
    st.subheader("Building Codes by Country")
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
    st.session_state.dt_sensors = editable_table(st.session_state.dt_sensors, "dt_sensors_editor")

    st.subheader("Historical Energy Consumption")
    now = datetime.now()
    start_time = now - timedelta(days=7)
    times = [start_time + timedelta(hours=i) for i in range(168)]
    energy_vals = [300 + 50 * (i % 24) / 24 for i in range(168)]
    df_energy_hist = pd.DataFrame({"Time": times, "Energy (kW)": energy_vals})
    st.line_chart(df_energy_hist.set_index("Time"))

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