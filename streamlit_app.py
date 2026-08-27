"""
IMAGINE Platform — Main Entry Point & Router
Path: streamlit_app.py
App: imagine
"""

import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="IMAGINE — Integrated AEC Engine",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Session State Keys for CRUD operations
def init_session_state():
    defaults = {
        "projects": [],
        "structural_calcs": [],
        "boq_items": [],
        "rfis": [],
        "digital_twin_sensors": [],
        "architecture_layouts": [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session_state()

# Navigation Sidebar
st.sidebar.title("🏗️ IMAGINE AEC Engine")
st.sidebar.caption("Integrated Architecture & Civil Engineering Platform")

route = st.sidebar.radio(
    "Navigation Modules",
    [
        "📊 Dashboard",
        "📂 Projects",
        "🏛️ Architecture Synthesis",
        "🧱 Structural (Eurocodes)",
    ],
)

# Route Dispatcher
try:
    if route == "📊 Dashboard":
        from modules.dashboard import dashboard
        dashboard.render()

    elif route == "📂 Projects":
        from modules.projects.project_page import ProjectPage
        ProjectPage.render()

    elif route == "🏛️ Architecture Synthesis":
        from modules.architecture.synthesis_page import ArchitectureSynthesisPage
        ArchitectureSynthesisPage.render()

    elif route == "🧱 Structural (Eurocodes)":
        from modules.structural import eurocode
        eurocode.render()

except Exception as e:
    st.error(f"⚠️ Failed to load module `{route}`")
    st.exception(e)
