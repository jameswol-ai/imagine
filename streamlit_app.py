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
                    # Optionally fetch user details from /users/me
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
    if "editing_project" not in st.session_state:
        st.session_state.editing_project = None
    if "projects_data" not in st.session_state:
        st.session_state.projects_data = None
    # Add other state variables as needed

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
# PAGE: PROJECTS (full CRUD)
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
# PAGE: ARCHITECTURE (stub)
# ---------------------------
def page_architecture():
    st.title("📐 Architecture")
    st.info("Architecture pages coming soon. (Will integrate with generative_design, zoning, etc.)")

# ---------------------------
# PAGE: BIM (stub)
# ---------------------------
def page_bim():
    st.title("🏛️ BIM")
    st.info("BIM pages coming soon. (Buildings, Storeys, Spaces, Elements, IFC, COBie, Digital Twin)")

# ---------------------------
# PAGE: STRUCTURAL (stub)
# ---------------------------
def page_structural():
    st.title("🔩 Structural Engineering")
    st.info("Structural pages coming soon. (Eurocode, beams, columns, etc.)")

# ---------------------------
# PAGE: MEP (stub)
# ---------------------------
def page_mep():
    st.title("⚡ MEP")
    st.info("MEP pages coming soon. (HVAC, electrical, plumbing)")

# ---------------------------
# PAGE: COSTING (stub)
# ---------------------------
def page_costing():
    st.title("💰 Cost Estimation")
    st.info("Costing pages coming soon. (BOQ, quantity takeoff, etc.)")

# ---------------------------
# PAGE: CONSTRUCTION (stub)
# ---------------------------
def page_construction():
    st.title("🚧 Construction Management")
    st.info("Construction pages coming soon. (RFIs, progress tracking, site diaries)")

# ---------------------------
# PAGE: REGIONAL (stub)
# ---------------------------
def page_regional():
    st.title("🌍 Regional – East Africa Codes")
    st.info("Regional pages coming soon. (Uganda, Kenya, Tanzania, etc.)")

# ---------------------------
# PAGE: DIGITAL TWIN (stub)
# ---------------------------
def page_digital_twin():
    st.title("🔄 Digital Twin – Live Monitoring")
    st.info("Digital Twin pages coming soon. (Sensors, telemetry, predictive AI)")

# ---------------------------
# PAGE: AI ASSISTANT (stub)
# ---------------------------
def page_ai():
    st.title("🤖 AI Assistant - IMAGINE Architect")
    st.info("AI Assistant coming soon. (RAG, prompt library, imagine_architect)")

# ---------------------------
# PAGE: ANALYTICS (stub)
# ---------------------------
def page_analytics():
    st.title("📈 Analytics & Reporting")
    st.info("Analytics pages coming soon. (KPIs, portfolio, forecasting)")

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