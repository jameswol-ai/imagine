"""
IMAGINE v24 Enterprise

Application Entry Point
"""

import streamlit as st

from modules.dashboard.dashboard import DashboardPage
from modules.projects.project_page import ProjectPage

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="IMAGINE Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# Authentication
# --------------------------------------------------

if "authenticated" not in st.session_state:
    st.session_state.authenticated = True
    st.session_state.user = "Demo User"
    st.session_state.role = "Admin"

# --------------------------------------------------
# Session Initialization
# --------------------------------------------------

if "projects_data" not in st.session_state:
    st.session_state.projects_data = []

if "buildings_data" not in st.session_state:
    st.session_state.buildings_data = []

if "approvals_data" not in st.session_state:
    st.session_state.approvals_data = []

# --------------------------------------------------
# Sidebar
# --------------------------------------------------

st.sidebar.title("🏗️ IMAGINE")

st.sidebar.write(
    f"User: {st.session_state.user}"
)

st.sidebar.write(
    f"Role: {st.session_state.role}"
)

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
        "Governance",
        "Construction",
        "Documents",
        "Analytics",
        "Digital Twin",
        "AI Assistant"
    ]
)

# --------------------------------------------------
# Routing
# --------------------------------------------------

if page == "Dashboard":

    DashboardPage.render(
        st.session_state.projects_data
    )

elif page == "Projects":

    ProjectPage.render()

elif page == "Architecture":

    st.title("📐 Architecture")

elif page == "BIM":

    st.title("🏛️ BIM")

elif page == "Structural":

    st.title("🔩 Structural")

elif page == "MEP":

    st.title("⚡ MEP")

elif page == "Costing":

    st.title("💰 Costing")

elif page == "Governance":

    st.title("🔒 Governance")

elif page == "Construction":

    st.title("🚧 Construction")

elif page == "Documents":

    st.title("📄 Documents")

elif page == "Analytics":

    st.title("📈 Analytics")

elif page == "Digital Twin":

    st.title("🔄 Digital Twin")

elif page == "AI Assistant":

    st.title("🤖 AI Assistant")

# --------------------------------------------------
# Footer
# --------------------------------------------------

st.sidebar.markdown("---")
st.sidebar.caption(
    "IMAGINE Enterprise v24.1"
)
