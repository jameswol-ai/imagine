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
# Authentication - SKIPPED (auto-login)
# ---------------------------
def check_authentication():
    # Always set authenticated to True with a default user
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = True
        st.session_state.token = "dummy-token"  # not used if you don't call API
        st.session_state.user = "Demo User"
        st.session_state.role = "Admin"

check_authentication()

# ---------------------------
# API client functions (will try real calls, but fallback to mock if needed)
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
# Navigation Sidebar (no login/logout)
# ---------------------------
st.sidebar.title("🏗️ IMAGINE")
st.sidebar.markdown(f"Welcome, **{st.session_state.user}**")
st.sidebar.markdown(f"Role: `{st.session_state.role}`")
# Removed Sign Out button

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
                    if api_delete(f"{endpoint}/{item[id_field]}"):
                        st.success(f"{item_name.capitalize()} deleted!")
                        st.session_state[f"{item_name}_data"] = api_get(endpoint)
                        st.rerun()
                    else:
                        st.error("Delete failed.")

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
# PAGE: PROJECTS (kept as is)
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
    # ... (rest of projects page unchanged)

# ---------------------------
# PAGE: ARCHITECTURE
# ---------------------------
def page_architecture():
    st.title("📐 Architecture")
    # ... (keep as in previous version, using crud_table)

# ---------------------------
# PAGE: BIM
# ---------------------------
def page_bim():
    st.title("🏛️ BIM")
    # ... (keep as in previous version)

# ---------------------------
# PAGE: STRUCTURAL
# ---------------------------
def page_structural():
    st.title("🔩 Structural Engineering")
    # ... (keep as in previous version)

# ---------------------------
# PAGE: MEP
# ---------------------------
def page_mep():
    st.title("⚡ MEP")
    # ... (keep as in previous version)

# ---------------------------
# PAGE: COSTING
# ---------------------------
def page_costing():
    st.title("💰 Cost Estimation")
    # ... (keep as in previous version)

# ---------------------------
# PAGE: CONSTRUCTION
# ---------------------------
def page_construction():
    st.title("🚧 Construction Management")
    # ... (keep as in previous version)

# ---------------------------
# PAGE: REGIONAL
# ---------------------------
def page_regional():
    st.title("🌍 Regional – East Africa Codes")
    # ... (keep as in previous version)

# ---------------------------
# PAGE: DIGITAL TWIN
# ---------------------------
def page_digital_twin():
    st.title("🔄 Digital Twin – Live Monitoring")
    # ... (keep as in previous version)

# ---------------------------
# PAGE: AI ASSISTANT
# ---------------------------
def page_ai():
    st.title("🤖 AI Assistant - IMAGINE Architect")
    # ... (keep as in previous version)

# ---------------------------
# PAGE: ANALYTICS
# ---------------------------
def page_analytics():
    st.title("📈 Analytics & Reporting")
    # ... (keep as in previous version)

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