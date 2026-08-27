"""
IMAGINE AEC Engine — Fixed Session State
"""

import importlib
import sys
from pathlib import Path
import streamlit as st

# ----------------------------------------------
# Page Configuration
# ----------------------------------------------
st.set_page_config(
    page_title="IMAGINE — Integrated AEC Engine",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------
# SAFE Session State Initialization
# ----------------------------------------------
def init_session_state():
    """Initialize all required session state keys with defaults."""
    defaults = {
        "projects_data": [
            {"id": 1, "name": "Green Tower", "status": "Active", "budget": 12.5, "progress": 75},
            {"id": 2, "name": "Harbor Bridge", "status": "Planning", "budget": 8.3, "progress": 20},
            {"id": 3, "name": "Riverside Mall", "status": "Completed", "budget": 22.1, "progress": 100},
        ],
        "buildings_data": [
            {"id": 1, "name": "Tower A", "storeys": 25, "area": 15000, "ifc_version": "IFC4"},
            {"id": 2, "name": "Tower B", "storeys": 18, "area": 12000, "ifc_version": "IFC4"},
        ],
        "zoning_data": [],
        "room_program_data": [],
        "beam_data": [],
        "column_data": [],
        "slab_data": [],
        "foundation_data": [],
        "retaining_data": [],
        "connection_data": [],
        "electrical_data": [],
        "boq_data": [],
        "rfi_data": [],
        "sensor_data": [],
        "approvals_data": [],
        "storeys_data": {},
        "spaces_data": {},
        "revisions_data": [],
        "transmittals_data": [],
        "submittals_data": [],
        "snagging_data": [],
        "dt_assets_data": [],
        "dt_maintenance_data": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Call the initializer
init_session_state()

# ----------------------------------------------
# Navigation Catalog
# ----------------------------------------------
MODULE_CATALOG = {
    "📊 Executive Dashboard": {
        "Overview Dashboard": ("modules.dashboard.dashboard", "render"),
    },
    "📂 Project Hub": {
        "Project Directory": ("modules.projects.project_page", "render"),
    },
    "🏛️ Architectural Generative Synthesis": {
        "Generative Layout Solver": ("modules.architecture.synthesis", "render"),
        "Zoning Analysis": ("modules.architecture.zoning", "render"),
        "Site Planning": ("modules.architecture.site_planning", "render"),
        "Floor Planning": ("modules.architecture.floor_planning", "render"),
        "Room Programming": ("modules.architecture.room_programming", "render"),
        "Compliance": ("modules.architecture.compliance", "render"),
    },
    "🏢 BIM & Spatial Management": {
        "Building Registry": ("modules.bim.buildings", "render"),
        "Storeys & Levels": ("modules.bim.storeys", "render"),
        "Spatial Allocations": ("modules.bim.spaces", "render"),
        "IFC OpenBIM Exporter": ("modules.bim.ifc_export", "render"),
    },
    "🧱 Structural Engineering (Eurocodes)": {
        "Eurocode Suite Overview": ("modules.structural.eurocode", "render"),
        "EN 1992 Reinforced Concrete Beams": ("modules.structural.beam_design", "render"),
        "EN 1992 Concrete Column Design": ("modules.structural.column_design", "render"),
        "EN 1992 Floor Slab Design": ("modules.structural.slab_design", "render"),
        "EN 1997 Geotechnical Foundations": ("modules.structural.foundation_design", "render"),
        "Retaining Wall Analysis": ("modules.structural.retaining_walls", "render"),
        "EN 1993 Structural Steel Connections": ("modules.structural.steel_connections", "render"),
    },
    "⚡ MEP & Environmental Services": {
        "Integrated MEP Analysis": ("modules.mep.analysis", "render"),
        "HVAC Thermal Loads": ("modules.mep.hvac", "render"),
        "Electrical Distribution": ("modules.mep.electrical", "render"),
        "Plumbing & Drainage": ("modules.mep.plumbing", "render"),
        "Building Energy Simulation": ("modules.mep.energy_simulation", "render"),
    },
    "💰 Costing & Quantity Surveying": {
        "Bill of Quantities (BOQ)": ("modules.costing.boq", "render"),
        "Procurement Tracker": ("modules.costing.procurement", "render"),
        "Forex Multi-Currency Engine": ("modules.costing.forex", "render"),
        "Cost Escalation Index": ("modules.costing.escalation", "render"),
        "Financial Risk Analysis": ("modules.costing.risk_analysis", "render"),
    },
    "🛡️ Governance & Approvals": {
        "Sign-offs & Approvals": ("modules.governance.approvals", "render"),
    },
    "🏗️ Construction Site Management": {
        "Requests for Information (RFIs)": ("modules.construction.rfis", "render"),
        "Material Submittals": ("modules.construction.submittals", "render"),
        "Digital Site Diary": ("modules.construction.site_diary", "render"),
        "Progress & S-Curves": ("modules.construction.progress_tracking", "render"),
        "Defect & Snagging Management": ("modules.construction.snagging", "render"),
    },
    "📄 Document Control (CDE)": {
        "Document Register": ("modules.documents.documents", "render"),
        "Revision History": ("modules.documents.revisions", "render"),
        "Drawing Schedule": ("modules.documents.drawing_register", "render"),
        "Technical Specifications": ("modules.documents.specifications", "render"),
        "Transmittals Engine": ("modules.documents.transmittals", "render"),
    },
    "📈 Portfolio Analytics": {
        "Portfolio Performance": ("modules.analytics.portfolio", "render"),
        "Executive Reporting": ("modules.analytics.reporting", "render"),
        "Cashflow Forecasting": ("modules.analytics.forecasting", "render"),
        "Project KPIs": ("modules.analytics.kpis", "render"),
    },
    "📡 Digital Twin & Structural Health": {
        "Asset Register": ("modules.digital_twin.assets", "render"),
        "IoT Sensor Network": ("modules.digital_twin.sensors", "render"),
        "Telemetry Stream": ("modules.digital_twin.telemetry", "render"),
        "Predictive Maintenance": ("modules.digital_twin.maintenance", "render"),
        "Predictive Structural AI": ("modules.digital_twin.predictive_ai", "render"),
    },
    "🤖 Copilot AI Assistants": {
        "Architectural Copilot": ("modules.ai.architect", "render"),
        "Structural Copilot": ("modules.ai.engineer", "render"),
        "MEP Engineering Copilot": ("modules.ai.mep", "render"),
        "Quantity Surveyor Copilot": ("modules.ai.qs", "render"),
        "Project Manager Copilot": ("modules.ai.project_manager", "render"),
    },
}

# ----------------------------------------------
# Sidebar Navigation
# ----------------------------------------------
st.sidebar.title("🏗️ IMAGINE Engine")
st.sidebar.caption("Integrated Architecture & Civil Engineering")
st.sidebar.markdown("---")

domain_category = st.sidebar.selectbox("Select Domain", list(MODULE_CATALOG.keys()))
sub_modules = MODULE_CATALOG[domain_category]
selected_submodule = st.sidebar.radio("Select Module", list(sub_modules.keys()))
module_path, target_symbol = sub_modules[selected_submodule]

# Debug: show module path
st.sidebar.caption(f"📍 `{module_path}`")

# ----------------------------------------------
# Module Loader with better error handling
# ----------------------------------------------
def render_module(module_path, target_symbol):
    try:
        imported_module = importlib.import_module(module_path)

        # Try exact target first
        if hasattr(imported_module, target_symbol):
            render_func = getattr(imported_module, target_symbol)
            if callable(render_func):
                render_func()
                return True
            else:
                st.error(f"❌ `{target_symbol}` exists but is not callable.")

        # Try fallback "render" function
        if hasattr(imported_module, "render"):
            render_func = getattr(imported_module, "render")
            if callable(render_func):
                render_func()
                return True

        st.warning(f"⚠️ Module `{module_path}` has no `render()` function.")
        st.caption("Available attributes:")
        st.code([a for a in dir(imported_module) if not a.startswith("_")])
        return False
    except ModuleNotFoundError as e:
        st.info(f"🚧 **{selected_submodule}** is under development.")
        st.caption(f"Module `{module_path}` not found.")
        with st.expander("🔍 Details"):
            st.exception(e)
        return False
    except Exception as e:
        st.error(f"💥 Error loading **{selected_submodule}**")
        with st.expander("🔍 Details"):
            st.exception(e)
        return False

# ----------------------------------------------
# Execute
# ----------------------------------------------
if not render_module(module_path, target_symbol):
    st.info("💡 Module not available yet. Check the path or create the file.")

# ----------------------------------------------
# Footer
# ----------------------------------------------
st.sidebar.markdown("---")
st.sidebar.caption("IMAGINE Enterprise v24.1")