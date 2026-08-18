# streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime, timedelta
import json

# ---------------------------
# Page configuration
# ---------------------------
st.set_page_config(
    page_title="IMAGINE Platform",
    page_icon="🏗️",
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
                # Replace with real API call
                if username and password:
                    st.session_state.authenticated = True
                    st.session_state.user = username
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        st.stop()

check_authentication()

# ---------------------------
# API Client (mocked)
# ---------------------------
API_BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8000/api/v1")

def api_get(endpoint):
    # For demo, return mock data
    # In production: requests.get(f"{API_BASE_URL}/{endpoint}", headers={"Authorization": f"Bearer {st.session_state.get('token')}"})
    # We'll use mock data for demonstration
    if endpoint == "projects":
        return pd.DataFrame({
            "ID": [1, 2, 3],
            "Name": ["Green Tower", "Harbor Bridge", "Riverside Mall"],
            "Status": ["Active", "Planning", "Completed"],
            "Budget (M USD)": [12.5, 8.3, 22.1],
            "Progress %": [75, 20, 100],
        })
    elif endpoint == "bim/buildings":
        return pd.DataFrame({
            "Building": ["Tower A", "Tower B", "Pavilion"],
            "Storeys": [25, 18, 3],
            "Area (m²)": [15000, 12000, 2500],
            "IFC Version": ["IFC4", "IFC4", "IFC2x3"],
        })
    elif endpoint == "structural/beams":
        return pd.DataFrame({
            "Beam ID": ["B-101", "B-102", "B-201"],
            "Span (m)": [6.5, 8.2, 5.0],
            "Load (kN/m)": [45, 60, 30],
            "Status": ["OK", "Overstressed", "OK"],
        })
    elif endpoint == "costing/boq":
        return pd.DataFrame({
            "Item": ["Concrete", "Steel", "Finishes"],
            "Quantity": [500, 120, 300],
            "Unit": ["m³", "t", "m²"],
            "Rate (USD)": [120, 950, 75],
            "Total (USD)": [60000, 114000, 22500],
        })
    elif endpoint == "construction/progress":
        dates = pd.date_range(start="2026-01-01", end="2026-08-19", freq="W")
        return pd.DataFrame({
            "Date": dates,
            "Planned": [10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100],
            "Actual": [8, 12, 18, 22, 28, 32, 38, 42, 48, 52, 58, 63, 68, 72, 78, 82, 88, 92, 96],
        })
    else:
        return pd.DataFrame()

# ---------------------------
# Navigation
# ---------------------------
st.sidebar.title("🏗️ IMAGINE")
st.sidebar.markdown(f"Welcome, **{st.session_state.user}**")
if st.sidebar.button("Sign Out"):
    st.session_state.authenticated = False
    st.rerun()

page = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard",
        "📁 Projects",
        "🏛️ BIM",
        "🔩 Structural",
        "⚡ MEP",
        "💰 Costing",
        "🚧 Construction",
        "🤖 AI Assistant",
        "📈 Analytics",
    ],
)

# ---------------------------
# Page Content
# ---------------------------

# ---------- DASHBOARD ----------
def page_dashboard():
    st.title("📊 Dashboard")
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

# ---------- PROJECTS ----------
def page_projects():
    st.title("📁 Projects")
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
    # Mock Gantt – just a placeholder
    st.bar_chart(df.set_index("Name")["Progress %"])

# ---------- BIM ----------
def page_bim():
    st.title("🏛️ BIM")
    tab1, tab2, tab3 = st.tabs(["Buildings", "Storeys", "IFC Viewer"])

    with tab1:
        df = api_get("bim/buildings")
        st.dataframe(df, use_container_width=True)

    with tab2:
        st.write("Storey details for selected building")
        building = st.selectbox("Select Building", ["Tower A", "Tower B"])
        storeys = pd.DataFrame({
            "Level": [f"Level {i}" for i in range(1, 6)],
            "Height (m)": [4.2, 3.8, 3.8, 3.8, 4.0],
            "Area (m²)": [1200, 1150, 1150, 1150, 1200],
        })
        st.dataframe(storeys)

    with tab3:
        st.info("IFC Viewer (integrate with xeokit or Three.js)")
        st.file_uploader("Upload IFC file", type=["ifc"])

# ---------- STRUCTURAL ----------
def page_structural():
    st.title("🔩 Structural Engineering")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Eurocode Modules")
        codes = ["EN 1990", "EN 1991", "EN 1992 (Concrete)", "EN 1993 (Steel)", "EN 1995 (Timber)", "EN 1997 (Geotech)", "EN 1998 (Seismic)"]
        for code in codes:
            st.checkbox(code, value=True)
    with col2:
        st.subheader("Beam Analysis")
        df = api_get("structural/beams")
        st.dataframe(df)

    st.subheader("Finite Element Mesh")
    st.image("https://via.placeholder.com/800x300?text=FEA+Mesh+Visualization", use_column_width=True)

# ---------- MEP ----------
def page_mep():
    st.title("⚡ MEP")
    tabs = st.tabs(["Mechanical (HVAC)", "Electrical", "Plumbing"])

    with tabs[0]:
        st.subheader("HVAC Load Summary")
        data = pd.DataFrame({
            "Zone": ["Office", "Atrium", "Core"],
            "Cooling (kW)": [150, 80, 30],
            "Heating (kW)": [100, 60, 20],
        })
        st.bar_chart(data.set_index("Zone"))

    with tabs[1]:
        st.subheader("Electrical Load Analysis")
        loads = pd.DataFrame({
            "Panel": ["MDP-1", "MDP-2", "MDP-3"],
            "Total Load (kVA)": [250, 180, 90],
            "Reserve (%)": [20, 15, 25],
        })
        st.dataframe(loads)

    with tabs[2]:
        st.subheader("Water Supply Network")
        st.write("Piping isometric view placeholder")
        st.line_chart(pd.DataFrame({"Flow (L/s)": [2.5, 3.2, 2.8, 4.1]}))

# ---------- COSTING ----------
def page_costing():
    st.title("💰 Cost Estimation")
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

# ---------- CONSTRUCTION ----------
def page_construction():
    st.title("🚧 Construction Management")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Progress vs Planned")
        df = api_get("construction/progress")
        st.line_chart(df.set_index("Date"))

    with col2:
        st.subheader("RFI & Submittals")
        rfi = pd.DataFrame({
            "RFI #": ["RFI-001", "RFI-002", "RFI-003"],
            "Subject": ["Rebar spacing", "Window detail", "MEP coordination"],
            "Status": ["Open", "Answered", "Closed"],
        })
        st.dataframe(rfi)

    st.subheader("Site Diary (latest)")
    diary = """2026-08-19: Completed foundation pour for Block A. 
    Weather: sunny, 28°C. 12 workers on site. Equipment: 2 mixers.
    Safety: no incidents.
    """
    st.text_area("Today's Log", diary, height=150)

# ---------- AI ASSISTANT ----------
def page_ai():
    st.title("🤖 AI Assistant - IMAGINE Architect")
    st.caption("Ask questions about your project, design, or compliance.")

    prompt = st.text_area("Your query:", "Suggest a column size for a 10-storey building in seismic zone 3.")
    if st.button("Ask AI"):
        with st.spinner("Consulting IMAGINE's knowledge base..."):
            # Mock response
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

# ---------- ANALYTICS ----------
def page_analytics():
    st.title("📈 Analytics & Reporting")
    st.subheader("Portfolio KPIs")
    kpi_data = pd.DataFrame({
        "Project": ["Green Tower", "Harbor Bridge", "Riverside Mall"],
        "Budget Variance (%)": [-5, 3, 0],
        "Schedule Variance (days)": [12, -8, 5],
        "Safety Index": [0.95, 0.88, 0.92],
    })
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
if page == "📊 Dashboard":
    page_dashboard()
elif page == "📁 Projects":
    page_projects()
elif page == "🏛️ BIM":
    page_bim()
elif page == "🔩 Structural":
    page_structural()
elif page == "⚡ MEP":
    page_mep()
elif page == "💰 Costing":
    page_costing()
elif page == "🚧 Construction":
    page_construction()
elif page == "🤖 AI Assistant":
    page_ai()
elif page == "📈 Analytics":
    page_analytics()

# ---------------------------
# Footer
# ---------------------------
st.sidebar.markdown("---")
st.sidebar.caption("IMAGINE Platform v0.1 | © 2026")