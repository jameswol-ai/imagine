"""
IMAGINE
Generative Architecture & Engineering Platform

Main Streamlit application controller.

The application shell is responsible for:
    - Global Streamlit configuration
    - Navigation
    - Module routing
    - Application-level session state

Business logic belongs inside the individual modules.
"""

from __future__ import annotations

import streamlit as st

from architecture.generative_design.ui import (
    render_generative_design,
)


# =====================================================================
# PAGE CONFIGURATION
# =====================================================================

st.set_page_config(
    page_title="IMAGINE",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =====================================================================
# APPLICATION STATE
# =====================================================================

if "active_module" not in st.session_state:
    st.session_state.active_module = "Overview"


# =====================================================================
# NAVIGATION HELPER
# =====================================================================

def navigate_to(module: str) -> None:
    """
    Change the active application module.
    """

    st.session_state.active_module = module


# =====================================================================
# SIDEBAR
# =====================================================================

with st.sidebar:

    # ---------------------------------------------------------------
    # Brand
    # ---------------------------------------------------------------

    st.markdown(
        """
        # 🏗️ IMAGINE

        **Generative Architecture & Engineering**
        """
    )

    st.divider()

    # ---------------------------------------------------------------
    # Overview
    # ---------------------------------------------------------------

    st.markdown("### PLATFORM")

    if st.button(
        "🏠 Overview",
        use_container_width=True,
        key="nav_overview",
    ):
        navigate_to("Overview")

    # ---------------------------------------------------------------
    # Projects
    # ---------------------------------------------------------------

    st.markdown("### PROJECTS")

    if st.button(
        "📁 Projects",
        use_container_width=True,
        key="nav_projects",
    ):
        navigate_to("Projects")

    # ---------------------------------------------------------------
    # Architecture
    # ---------------------------------------------------------------

    st.markdown("### ARCHITECTURE")

    if st.button(
        "📐 Zoning",
        use_container_width=True,
        key="nav_zoning",
    ):
        navigate_to("Zoning")

    if st.button(
        "🗺️ Site Planning",
        use_container_width=True,
        key="nav_site_planning",
    ):
        navigate_to("Site Planning")

    if st.button(
        "🏢 Floor Planning",
        use_container_width=True,
        key="nav_floor_planning",
    ):
        navigate_to("Floor Planning")

    if st.button(
        "🚪 Room Programming",
        use_container_width=True,
        key="nav_room_programming",
    ):
        navigate_to("Room Programming")

    if st.button(
        "✅ Compliance",
        use_container_width=True,
        key="nav_compliance",
    ):
        navigate_to("Compliance")

    if st.button(
        "✨ Generative Design",
        use_container_width=True,
        key="nav_generative_design",
    ):
        navigate_to("Generative Design")

    # ---------------------------------------------------------------
    # Engineering
    # ---------------------------------------------------------------

    st.markdown("### ENGINEERING")

    if st.button(
        "🏗️ Structural",
        use_container_width=True,
        key="nav_structural",
    ):
        navigate_to("Structural")

    if st.button(
        "⚡ MEP",
        use_container_width=True,
        key="nav_mep",
    ):
        navigate_to("MEP")

    # ---------------------------------------------------------------
    # Costing
    # ---------------------------------------------------------------

    st.markdown("### COST MANAGEMENT")

    if st.button(
        "💰 Costing",
        use_container_width=True,
        key="nav_costing",
    ):
        navigate_to("Costing")

    # ---------------------------------------------------------------
    # Construction
    # ---------------------------------------------------------------

    st.markdown("### CONSTRUCTION")

    if st.button(
        "📅 Planning",
        use_container_width=True,
        key="nav_construction_planning",
    ):
        navigate_to("Construction Planning")

    if st.button(
        "📋 RFIs",
        use_container_width=True,
        key="nav_rfis",
    ):
        navigate_to("RFIs")

    if st.button(
        "📄 Submittals",
        use_container_width=True,
        key="nav_submittals",
    ):
        navigate_to("Submittals")

    if st.button(
        "🔧 Variations",
        use_container_width=True,
        key="nav_variations",
    ):
        navigate_to("Variations")

    if st.button(
        "🐛 Snagging",
        use_container_width=True,
        key="nav_snagging",
    ):
        navigate_to("Snagging")

    # ---------------------------------------------------------------
    # Documents
    # ---------------------------------------------------------------

    st.markdown("### DOCUMENTS")

    if st.button(
        "📐 Drawings",
        use_container_width=True,
        key="nav_drawings",
    ):
        navigate_to("Drawings")

    if st.button(
        "📑 Specifications",
        use_container_width=True,
        key="nav_specifications",
    ):
        navigate_to("Specifications")

    if st.button(
        "📝 Contracts",
        use_container_width=True,
        key="nav_contracts",
    ):
        navigate_to("Contracts")

    if st.button(
        "📚 Reports",
        use_container_width=True,
        key="nav_reports",
    ):
        navigate_to("Reports")

    # ---------------------------------------------------------------
    # AI
    # ---------------------------------------------------------------

    st.markdown("### AI")

    if st.button(
        "🤖 IMAGINE Architect",
        use_container_width=True,
        key="nav_ai_architect",
    ):
        navigate_to("AI Architect")

    if st.button(
        "🏗️ IMAGINE Engineer",
        use_container_width=True,
        key="nav_ai_engineer",
    ):
        navigate_to("AI Engineer")

    if st.button(
        "⚡ IMAGINE MEP",
        use_container_width=True,
        key="nav_ai_mep",
    ):
        navigate_to("AI MEP")

    if st.button(
        "💰 IMAGINE QS",
        use_container_width=True,
        key="nav_ai_qs",
    ):
        navigate_to("AI QS")

    if st.button(
        "📋 IMAGINE PM",
        use_container_width=True,
        key="nav_ai_pm",
    ):
        navigate_to("AI PM")

    # ---------------------------------------------------------------
    # Analytics
    # ---------------------------------------------------------------

    st.markdown("### ANALYTICS")

    if st.button(
        "📊 Dashboards",
        use_container_width=True,
        key="nav_dashboards",
    ):
        navigate_to("Dashboards")

    if st.button(
        "📈 KPIs",
        use_container_width=True,
        key="nav_kpis",
    ):
        navigate_to("KPIs")

    if st.button(
        "🏢 Portfolio",
        use_container_width=True,
        key="nav_portfolio",
    ):
        navigate_to("Portfolio")

    if st.button(
        "🔮 Forecasting",
        use_container_width=True,
        key="nav_forecasting",
    ):
        navigate_to("Forecasting")

    # ---------------------------------------------------------------
    # Administration
    # ---------------------------------------------------------------

    st.markdown("### ADMINISTRATION")

    if st.button(
        "⚙️ Administration",
        use_container_width=True,
        key="nav_administration",
    ):
        navigate_to("Administration")


# =====================================================================
# MAIN APPLICATION ROUTER
# =====================================================================

active_module = st.session_state.active_module


# =====================================================================
# OVERVIEW
# =====================================================================

if active_module == "Overview":

    st.title("🏗️ IMAGINE")

    st.subheader(
        "Generative Architecture & Engineering Platform"
    )

    st.markdown(
        """
        Welcome to **IMAGINE**.

        A constraint-driven platform for architectural design,
        structural engineering, MEP, costing, construction and
        project intelligence.
        """
    )

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Projects",
            "—",
        )

    with col2:
        st.metric(
            "Design Runs",
            "—",
        )

    with col3:
        st.metric(
            "Active Projects",
            "—",
        )

    with col4:
        st.metric(
            "Design Candidates",
            "—",
        )

    st.divider()

    st.info(
        "Select a module from the navigation panel to begin."
    )


# =====================================================================
# PROJECTS
# =====================================================================

elif active_module == "Projects":

    st.title("📁 Projects")

    st.info(
        "Project management module is being integrated."
    )


# =====================================================================
# ARCHITECTURE
# =====================================================================

elif active_module == "Zoning":

    st.title("📐 Zoning")

    st.info(
        "Zoning module is being integrated."
    )


elif active_module == "Site Planning":

    st.title("🗺️ Site Planning")

    st.info(
        "Site Planning module is being integrated."
    )


elif active_module == "Floor Planning":

    st.title("🏢 Floor Planning")

    st.info(
        "Floor Planning module is being integrated."
    )


elif active_module == "Room Programming":

    st.title("🚪 Room Programming")

    st.info(
        "Room Programming module is being integrated."
    )


elif active_module == "Compliance":

    st.title("✅ Compliance")

    st.info(
        "Compliance module is being integrated."
    )


# =====================================================================
# GENERATIVE DESIGN
# =====================================================================

elif active_module == "Generative Design":

    render_generative_design()


# =====================================================================
# ENGINEERING
# =====================================================================

elif active_module == "Structural":

    st.title("🏗️ Structural Engineering")

    st.info(
        "Structural engineering module is being integrated."
    )


elif active_module == "MEP":

    st.title("⚡ MEP Engineering")

    st.info(
        "MEP engineering module is being integrated."
    )


# =====================================================================
# COST MANAGEMENT
# =====================================================================

elif active_module == "Costing":

    st.title("💰 Cost Management")

    st.info(
        "Costing module is being integrated."
    )


# =====================================================================
# CONSTRUCTION
# =====================================================================

elif active_module == "Construction Planning":

    st.title("📅 Construction Planning")

    st.info(
        "Construction planning module is being integrated."
    )


elif active_module == "RFIs":

    st.title("📋 Requests for Information")

    st.info(
        "RFI module is being integrated."
    )


elif active_module == "Submittals":

    st.title("📄 Submittals")

    st.info(
        "Submittals module is being integrated."
    )


elif active_module == "Variations":

    st.title("🔧 Variations")

    st.info(
        "Variation management module is being integrated."
    )


elif active_module == "Snagging":

    st.title("🐛 Snagging")

    st.info(
        "Snagging module is being integrated."
    )


# =====================================================================
# DOCUMENTS
# =====================================================================

elif active_module == "Drawings":

    st.title("📐 Drawing Management")

    st.info(
        "Drawing management module is being integrated."
    )


elif active_module == "Specifications":

    st.title("📑 Specifications")

    st.info(
        "Specifications module is being integrated."
    )


elif active_module == "Contracts":

    st.title("📝 Contracts")

    st.info(
        "Contracts module is being integrated."
    )


elif active_module == "Reports":

    st.title("📚 Reports")

    st.info(
        "Reports module is being integrated."
    )


# =====================================================================
# AI
# =====================================================================

elif active_module == "AI Architect":

    st.title("🤖 IMAGINE Architect")

    st.info(
        "AI Architect module is being integrated."
    )


elif active_module == "AI Engineer":

    st.title("🏗️ IMAGINE Engineer")

    st.info(
        "AI Engineer module is being integrated."
    )


elif active_module == "AI MEP":

    st.title("⚡ IMAGINE MEP")

    st.info(
        "AI MEP module is being integrated."
    )


elif active_module == "AI QS":

    st.title("💰 IMAGINE QS")

    st.info(
        "AI Quantity Surveyor module is being integrated."
    )


elif active_module == "AI PM":

    st.title("📋 IMAGINE PM")

    st.info(
        "AI Project Manager module is being integrated."
    )


# =====================================================================
# ANALYTICS
# =====================================================================

elif active_module == "Dashboards":

    st.title("📊 Dashboards")

    st.info(
        "Analytics dashboards are being integrated."
    )


elif active_module == "KPIs":

    st.title("📈 KPIs")

    st.info(
        "KPI module is being integrated."
    )


elif active_module == "Portfolio":

    st.title("🏢 Portfolio")

    st.info(
        "Portfolio analytics are being integrated."
    )


elif active_module == "Forecasting":

    st.title("🔮 Forecasting")

    st.info(
        "Forecasting module is being integrated."
    )


# =====================================================================
# ADMINISTRATION
# =====================================================================

elif active_module == "Administration":

    st.title("⚙️ Administration")

    st.info(
        "Administration module is being integrated."
    )


# =====================================================================
# FALLBACK
# =====================================================================

else:

    st.session_state.active_module = "Overview"

    st.rerun()
