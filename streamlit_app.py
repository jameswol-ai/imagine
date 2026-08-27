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
                    st.session_state.role = "Project Manager"  # you can fetch from /users/me later
                    st.rerun()
        st.stop()

check_authentication()

# ---------------------------
# API client functions
# ---------------------------
def api_get(endpoint, params=None):
    """Make authenticated GET request."""
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
# Session state initialisation (using real data)
# ---------------------------
def init_session_state():
    # We'll fetch real data on demand; no need to pre-fill.
    pass

# ---------------------------
# Helper: Convert API list to DataFrame
# ---------------------------
def api_list_to_df(endpoint):
    data = api_get(endpoint)
    if data:
        return pd.DataFrame(data)
    return pd.DataFrame()

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
# Helper for editable tables (sync with API)
# We'll implement a pattern: on edit, call api_put/delete/post.
# For simplicity in this step, we'll still use session_state and then 
# sync with API via a "Save" button or automatic update.
# But to keep it simple now, we'll keep using session_state and later 
# add sync buttons. Let's do a hybrid: fetch on load, edit locally, 
# and provide a "Save" button to persist.
# ---------------------------
def editable_table(data, key, endpoint, columns=None):
    df = pd.DataFrame(data)
    if columns:
        df = df[columns]
    edited = st.data_editor(df, use_container_width=True, num_rows="dynamic", key=key)
    # For now, just return edited; we'll handle saving outside.
    return edited.to_dict('records')

# ---------------------------
# PAGE: DASHBOARD
# ---------------------------
def page_dashboard():
    st.title("📊 Dashboard")
    # Fetch metrics from API (if available)
    # For now, we'll keep static metrics as before.
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Active Projects", "12", "+2")
    col2.metric("Total Budget", "$184M", "+5%")
    col3.metric("Progress (avg)", "68%", "+12%")
    col4.metric("Open RFIs", "7", "-3")

    st.subheader("Project Health")
    df_proj = api_list_to_df("projects")
    if not df_proj.empty:
        fig = px.bar(df_proj, x="name", y="progress", color="status", text="progress")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No project data available.")

    st.subheader("Recent Activity")
    # Placeholder; we can add an audit log endpoint later.
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
    # Load projects from API
    projects = api_get("projects")
    if projects:
        df = pd.DataFrame(projects)
    else:
        df = pd.DataFrame(columns=["id", "name", "status", "budget", "progress"])
    # Use editable table (but saving not yet implemented)
    # We'll implement a simple Save button that calls api_post/put
    # For now, display and allow edits but don't save.
    # To keep it simple, we'll just show.
    st.dataframe(df, use_container_width=True)

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
                    st.rerun()

# ---------------------------
# PAGE: ARCHITECTURE (similar pattern)
# ---------------------------
def page_architecture():
    st.title("📐 Architecture")
    # ... implement using api_get, api_post, etc.
    st.info("Architecture pages will use real API endpoints once the backend is running.")
    # We'll reuse the same pattern: fetch data, display, edit with Save.

# ---------------------------
# PAGE: BIM (similar pattern)
# ---------------------------
def page_bim():
    st.title("🏛️ BIM")
    st.info("BIM pages will use real API endpoints.")

# ---------------------------
# PAGE: STRUCTURAL (similar pattern)
# ---------------------------
def page_structural():
    st.title("🔩 Structural Engineering")
    st.info("Structural pages will use real API endpoints.")

# ---------------------------
# PAGE: MEP (similar pattern)
# ---------------------------
def page_mep():
    st.title("⚡ MEP")
    st.info("MEP pages will use real API endpoints.")

# ---------------------------
# PAGE: COSTING (similar pattern)
# ---------------------------
def page_costing():
    st.title("💰 Cost Estimation")
    st.info("Costing pages will use real API endpoints.")

# ---------------------------
# PAGE: CONSTRUCTION (similar pattern)
# ---------------------------
def page_construction():
    st.title("🚧 Construction Management")
    st.info("Construction pages will use real API endpoints.")

# ---------------------------
# PAGE: REGIONAL (similar pattern)
# ---------------------------
def page_regional():
    st.title("🌍 Regional – East Africa Codes")
    st.info("Regional pages will use real API endpoints.")

# ---------------------------
# PAGE: DIGITAL TWIN (similar pattern)
# ---------------------------
def page_digital_twin():
    st.title("🔄 Digital Twin – Live Monitoring")
    st.info("Digital Twin pages will use real API endpoints.")

# ---------------------------
# PAGE: AI ASSISTANT (similar pattern)
# ---------------------------
def page_ai():
    st.title("🤖 AI Assistant - IMAGINE Architect")
    st.info("AI Assistant will use real endpoints for RAG and prompts.")

# ---------------------------
# PAGE: ANALYTICS (similar pattern)
# ---------------------------
def page_analytics():
    st.title("📈 Analytics & Reporting")
    st.info("Analytics will use real reporting endpoints.")

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