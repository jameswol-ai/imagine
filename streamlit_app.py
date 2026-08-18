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
# Authentication (mock)
# ---------------------------
def check_authentication():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        with st.sidebar:
            st.subheader("Login")
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
# Mock API Client
# ---------------------------
def api_get(endpoint):
    if endpoint == "projects":
        return pd.DataFrame({
            "ID": [1, 2, 3, 4],
            "Name": ["Green Tower", "Harbor Bridge", "Riverside Mall", "Solar Park"],
            "Status": ["Active", "Planning", "Completed", "Active"],
            "Budget (M USD)": [12.5, 8.3, 22.1, 5.7],
            "Progress %": [75, 20, 100, 45],
        })
    elif endpoint == "bim/buildings":
        return pd.DataFrame({
            "Building": ["Tower A", "Tower B", "Pavilion"],
            "Storeys": [25, 18, 3],
            "Area (m²)": [15000, 12000, 2500],
            "IFC Version": ["IFC4", "IFC4", "IFC2x3"],
        })
    elif endpoint == "bim/spaces":
        return pd.DataFrame({
            "Space": ["Office 101", "Conference", "Lobby", "Cafeteria"],
            "Area (m²)": [45, 30, 80, 60],
            "Height (m)": [3.2, 3.5, 5.0, 3.0],
            "Type": ["Workspace", "Meeting", "Public", "Amenity"],
        })
    elif endpoint == "bim/elements":
        return pd.DataFrame({
            "Element": ["Wall", "Slab", "Column", "Beam"],
            "Material": ["Concrete", "Concrete", "Steel", "Steel"],
            "Quantity": [120, 80, 45, 30],
            "Unit": ["m²", "m²", "each", "each"],
        })
    elif endpoint == "bim/cobie":
        return pd.DataFrame({
            "Asset": ["Chiller", "Pump", "AHU", "Boiler"],
            "Serial": ["CH-001", "PM-002", "AH-003", "BL-004"],
            "Manufacturer": ["Trane", "Grundfos", "Carrier", "Viessmann"],
            "Warranty (years)": [5, 3, 4, 6],
        })
    elif endpoint == "structural/beams":
        return pd.DataFrame({
            "Beam ID": ["B-101", "B-102", "B-201", "B-202"],
            "Span (m)": [6.5, 8.2, 5.0, 7.0],
            "Load (kN/m)": [45, 60, 30, 50],
            "Status": ["OK", "Overstressed", "OK", "OK"],
        })
    elif endpoint == "structural/columns":
        return pd.DataFrame({
            "Column ID": ["C-1", "C-2", "C-3", "C-4"],
            "Axial Load (kN)": [1200, 800, 1500, 950],
            "Section": ["400x400", "300x300", "500x500", "350x350"],
            "Reinf. Ratio (%)": [1.5, 1.2, 2.0, 1.3],
        })
    elif endpoint == "structural/slabs":
        return pd.DataFrame({
            "Slab ID": ["S1", "S2", "S3", "S4"],
            "Thickness (mm)": [200, 150, 250, 180],
            "Span (m)": [6, 4, 7, 5],
            "Load (kN/m²)": [5, 4, 6, 4.5],
        })
    elif endpoint == "structural/foundations":
        return pd.DataFrame({
            "Foundation": ["Pad", "Strip", "Pile", "Raft"],
            "Capacity (kN)": [800, 500, 1200, 1500],
            "Depth (m)": [1.5, 1.0, 12, 0.8],
            "Type": ["Isolated", "Continuous", "Driven", "Mat"],
        })
    elif endpoint == "structural/retaining_walls":
        return pd.DataFrame({
            "Wall": ["RW-1", "RW-2", "RW-3"],
            "Height (m)": [4.5, 6.0, 3.2],
            "Thickness (m)": [0.3, 0.4, 0.25],
            "Stability": ["OK", "OK", "Warning"],
        })
    elif endpoint == "structural/steel_connections":
        return pd.DataFrame({
            "Connection": ["Moment", "Shear", "Base Plate", "Brace"],
            "Bolts": ["M20", "M16", "M24", "M22"],
            "Capacity (kN)": [200, 120, 350, 180],
        })
    elif endpoint == "costing/boq":
        return pd.DataFrame({
            "Item": ["Concrete C30", "Steel Rebar", "Finishes", "MEP", "Excavation"],
            "Quantity": [500, 120, 300, 80, 200],
            "Unit": ["m³", "t", "m²", "LF", "m³"],
            "Rate (USD)": [120, 950, 75, 60, 40],
            "Total (USD)": [60000, 114000, 22500, 4800, 8000],
        })
    elif endpoint == "construction/progress":
        dates = pd.date_range(start="2026-01-01", end="2026-08-19", freq="W")
        planned = list(range(10, 110, 5))[:len(dates)]
        actual = [p - random.randint(0, 8) for p in planned]
        return pd.DataFrame({"Date": dates, "Planned": planned, "Actual": actual})
    elif endpoint == "analytics/kpis":
        return pd.DataFrame({
            "Project": ["Green Tower", "Harbor Bridge", "Riverside Mall", "Solar Park"],
            "Budget Variance (%)": [-5, 3, 0, -2],
            "Schedule Variance (days)": [12, -8, 5, -3],
            "Safety Index": [0.95, 0.88, 0.92, 0.97],
        })
    else:
        return pd.DataFrame()

# ---------------------------
# Navigation Sidebar
# ---------------------------
st.sidebar.title("IMAGINE")
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
        "AI Assistant",
        "Analytics",
    ],
)

# ---------------------------
# Helper for rendering tabs
# ---------------------------
def render_tabs(tab_list, content_dict):
    tabs = st.tabs(tab_list)
    for tab, func in zip(tabs, [content_dict[t] for t in tab_list]):
        with tab:
            func()

# ---------------------------
# PAGE: DASHBOARD
# ---------------------------
def page_dashboard():
    st.title("Dashboard")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Active Projects", "12", "+2")
    col2.metric("Total Budget", "$184M", "+5%")
    col3.metric("Progress (avg)", "68%", "+12%")
    col4.metric("Open RFIs", "7", "-3")

    st.subheader("Project Health")
    df_proj = api_get("projects")
    fig = px.bar(df_proj, x="Name", y="Progress %", color="Status", text="Progress %")
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
    st.title("Projects")
    df = api_get("projects")
    st.dataframe(df, use_container_width=True)

    with st.expander("Create New Project"):
        with st.form("new_project"):
            st.text_input("Project Name")
            st.selectbox("Status", ["Planning", "Active", "On Hold", "Completed"])
            st.number_input("Budget (M USD)", min_value=0.0, step=0.1)
            st.text_area("Description")
            st.form_submit_button("Create")

    st.subheader("Project Timeline")
    st.bar_chart(df.set_index("Name")["Progress %"])

# ---------------------------
# PAGE: ARCHITECTURE
# ---------------------------
def page_architecture():
    st.title("Architecture")

    def tab_generative():
        st.subheader("Generative Design Options")
        col1, col2 = st.columns(2)
        with col1:
            st.slider("Iterations", 10, 100, 50)
            st.selectbox("Objective", ["Maximize area", "Minimize energy", "Balance"])
        with col2:
            st.slider("Population", 20, 200, 100)
            st.number_input("Seed", value=42)
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

    def tab_zoning():
        st.subheader("Zoning & Land Use")
        st.text("Zoning map placeholder")
        zoning_data = pd.DataFrame({
            "Zone": ["Residential", "Commercial", "Mixed-Use"],
            "Max Height (m)": [15, 30, 45],
            "Coverage (%)": [50, 60, 70],
            "Setback (m)": [3, 5, 4],
        })
        st.dataframe(zoning_data)

    def tab_site():
        st.subheader("Site Planning")
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("Site Area (m²)", value=5000)
            st.slider("Slope (%)", 0, 20, 5)
        with col2:
            st.selectbox("Soil Type", ["Clay", "Sand", "Rock"])
            st.selectbox("Orientation", ["North", "South", "East", "West"])
        st.text("Site layout placeholder")

    def tab_floor():
        st.subheader("Floor Planning")
        building_type = st.selectbox("Building Type", ["Office", "Residential", "Hospital", "School"])
        floors = st.slider("Number of floors", 1, 20, 5)
        if st.button("Generate Floor Plan"):
            st.success("Floor plan generated")
            st.text("Floor plan image placeholder")

    def tab_room():
        st.subheader("Room Programming")
        rooms = pd.DataFrame({
            "Room": ["Office", "Conference", "Lobby", "Restroom"],
            "Area (m²)": [20, 40, 60, 10],
            "Quantity": [10, 2, 1, 4],
            "Adjacency": ["", "Lobby", "Lobby", "Corridor"],
        })
        st.data_editor(rooms, use_container_width=True)

    def tab_compliance():
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
            st.dataframe(results, use_container_width=True)

    render_tabs(
        ["Generative Design", "Zoning", "Site Planning", "Floor Planning", "Room Programming", "Compliance"],
        {
            "Generative Design": tab_generative,
            "Zoning": tab_zoning,
            "Site Planning": tab_site,
            "Floor Planning": tab_floor,
            "Room Programming": tab_room,
            "Compliance": tab_compliance,
        }
    )

# ---------------------------
# PAGE: BIM
# ---------------------------
def page_bim():
    st.title("BIM")

    def tab_buildings():
        df = api_get("bim/buildings")
        st.dataframe(df, use_container_width=True)

    def tab_storeys():
        building = st.selectbox("Select Building", ["Tower A", "Tower B"])
        storeys = pd.DataFrame({
            "Level": [f"Level {i}" for i in range(1, 6)],
            "Height (m)": [4.2, 3.8, 3.8, 3.8, 4.0],
            "Area (m²)": [1200, 1150, 1150, 1150, 1200],
        })
        st.dataframe(storeys)

    def tab_spaces():
        spaces = api_get("bim/spaces")
        st.dataframe(spaces, use_container_width=True)
        st.text("Space heatmap placeholder")

    def tab_elements():
        elements = api_get("bim/elements")
        st.dataframe(elements, use_container_width=True)

    def tab_ifc():
        st.info("IFC Viewer (integrate with xeokit or Three.js)")
        st.file_uploader("Upload IFC file", type=["ifc"])
        st.caption("Supports IFC4, IFC2x3")

    def tab_cobie():
        cobie = api_get("bim/cobie")
        st.dataframe(cobie, use_container_width=True)
        st.download_button("Export COBie (Excel)", data="", file_name="cobie_export.xlsx")

    def tab_digital_twin():
        st.subheader("Digital Twin – Live Data")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Occupancy", "245 people", "+12")
            st.metric("Energy (kW)", "320", "-8%")
        with col2:
            st.metric("Temperature", "23.5°C", "+0.5")
            st.metric("Humidity", "42%", "-3%")
        # Fixed the date_range error: use freq="1H" and ensure correct start
        st.line_chart(pd.DataFrame({
            "Time": pd.date_range(start=datetime.now() - timedelta(hours=23), periods=24, freq="1H"),
            "Energy": [310, 305, 300, 295, 290, 285, 280, 275, 270, 265, 260, 255, 250, 245, 240, 235, 230, 225, 220, 215, 210, 205, 200, 195],
        }).set_index("Time"))

    render_tabs(
        ["Buildings", "Storeys", "Spaces", "Elements", "IFC Viewer", "COBie", "Digital Twin"],
        {
            "Buildings": tab_buildings,
            "Storeys": tab_storeys,
            "Spaces": tab_spaces,
            "Elements": tab_elements,
            "IFC Viewer": tab_ifc,
            "COBie": tab_cobie,
            "Digital Twin": tab_digital_twin,
        }
    )

# ---------------------------
# PAGE: STRUCTURAL
# ---------------------------
def page_structural():
    st.title("Structural Engineering")

    def tab_eurocode():
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

    def tab_beams():
        df = api_get("structural/beams")
        st.dataframe(df, use_container_width=True)
        with st.expander("New Beam Design"):
            with st.form("beam_form"):
                st.text_input("Beam ID")
                st.number_input("Span (m)", min_value=1.0)
                st.number_input("Load (kN/m)", min_value=0.0)
                st.selectbox("Material", ["Concrete C30/37", "Steel S355"])
                st.form_submit_button("Design")

    def tab_columns():
        df = api_get("structural/columns")
        st.dataframe(df, use_container_width=True)

    def tab_slabs():
        df = api_get("structural/slabs")
        st.dataframe(df, use_container_width=True)
        st.text("Slab reinforcement layout placeholder")

    def tab_foundations():
        df = api_get("structural/foundations")
        st.dataframe(df, use_container_width=True)

    def tab_retaining():
        df = api_get("structural/retaining_walls")
        st.dataframe(df, use_column_width=True)
        st.text("Retaining wall section placeholder")

    def tab_steel():
        df = api_get("structural/steel_connections")
        st.dataframe(df, use_column_width=True)
        st.info("Design according to EN 1993-1-8")

    def tab_fea():
        st.subheader("Finite Element Analysis")
        analysis_type = st.selectbox("Analysis Type", ["Linear Static", "Nonlinear", "Modal", "Pushover"])
        if st.button("Run Analysis"):
            with st.spinner("Solving..."):
                st.success("Analysis complete")
                st.text("FEA displacement contour placeholder")

    render_tabs(
        ["Eurocode", "Beam Design", "Column Design", "Slab Design", "Foundation Design", "Retaining Walls", "Steel Connections", "FEA"],
        {
            "Eurocode": tab_eurocode,
            "Beam Design": tab_beams,
            "Column Design": tab_columns,
            "Slab Design": tab_slabs,
            "Foundation Design": tab_foundations,
            "Retaining Walls": tab_retaining,
            "Steel Connections": tab_steel,
            "FEA": tab_fea,
        }
    )

# ---------------------------
# PAGE: MEP
# ---------------------------
def page_mep():
    st.title("MEP")

    def tab_mechanical():
        st.subheader("HVAC Load Summary")
        data = pd.DataFrame({
            "Zone": ["Office", "Atrium", "Core"],
            "Cooling (kW)": [150, 80, 30],
            "Heating (kW)": [100, 60, 20],
        })
        st.bar_chart(data.set_index("Zone"))
        st.subheader("Ventilation & Chilled Water")
        st.write("Placeholder for duct sizing and pump schedules")

    def tab_electrical():
        st.subheader("Electrical Load Analysis")
        loads = pd.DataFrame({
            "Panel": ["MDP-1", "MDP-2", "MDP-3"],
            "Total Load (kVA)": [250, 180, 90],
            "Reserve (%)": [20, 15, 25],
        })
        st.dataframe(loads)
        st.subheader("Solar PV Sizing")
        st.slider("Peak Power (kWp)", 0, 500, 150)

    def tab_plumbing():
        st.subheader("Water Supply Network")
        st.line_chart(pd.DataFrame({"Flow (L/s)": [2.5, 3.2, 2.8, 4.1]}))
        st.subheader("Drainage & Stormwater")
        st.write("Placeholder for pipe routing and catch basins")

    render_tabs(
        ["Mechanical (HVAC)", "Electrical", "Plumbing"],
        {
            "Mechanical (HVAC)": tab_mechanical,
            "Electrical": tab_electrical,
            "Plumbing": tab_plumbing,
        }
    )

# ---------------------------
# PAGE: COSTING
# ---------------------------
def page_costing():
    st.title("Cost Estimation")
    df = api_get("costing/boq")
    st.dataframe(df, use_container_width=True)
    total = df["Total (USD)"].sum()
    st.metric("Total Estimated Cost", f"${total:,.0f}")

    st.subheader("Cost Breakdown")
    fig = px.pie(df, values="Total (USD)", names="Item")
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Forex & Inflation"):
        st.write("Exchange rates: USD/UGX 3700, USD/KES 130")
        st.slider("Inflation factor", 0.0, 0.15, 0.05)

# ---------------------------
# PAGE: CONSTRUCTION
# ---------------------------
def page_construction():
    st.title("Construction Management")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Progress vs Planned")
        df = api_get("construction/progress")
        st.line_chart(df.set_index("Date"))
    with col2:
        st.subheader("RFI & Submittals")
        rfi = pd.DataFrame({
            "RFI #": ["RFI-001", "RFI-002", "RFI-003", "RFI-004"],
            "Subject": ["Rebar spacing", "Window detail", "MEP coordination", "Concrete mix"],
            "Status": ["Open", "Answered", "Closed", "Pending"],
        })
        st.dataframe(rfi)
    st.subheader("Site Diary (latest)")
    diary = """2026-08-19: Completed foundation pour for Block A. 
    Weather: sunny, 28°C. 12 workers on site. Equipment: 2 mixers.
    Safety: no incidents.
    """
    st.text_area("Today's Log", diary, height=150)
    st.subheader("Snagging & Variations")
    st.write("Placeholder for snag list and variation orders")

# ---------------------------
# PAGE: AI ASSISTANT
# ---------------------------
def page_ai():
    st.title("AI Assistant - IMAGINE Architect")
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
    st.title("Analytics & Reporting")
    st.subheader("Portfolio KPIs")
    kpi_data = api_get("analytics/kpis")
    st.dataframe(kpi_data)

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
elif page == "AI Assistant":
    page_ai()
elif page == "Analytics":
    page_analytics()

# ---------------------------
# Footer
# ---------------------------
st.sidebar.markdown("---")
st.sidebar.caption("IMAGINE Platform v0.1 | 2026")