"""
IMAGINE AEC Engine — Production Streamlit Cloud Entry Point
Path: streamlit_app.py
App: imagine
"""

import importlib
import sys
from pathlib import Path
import streamlit as st

# Force add root directory to system path for Linux environments
ROOT_DIR = Path(__file__).parent.resolve()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Page Configuration
st.set_page_config(
    page_title="IMAGINE — Integrated AEC Engine",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Session State
try:
    from modules.utils.mock_data import init_session_state
    init_session_state()
except Exception as e:
    st.sidebar.warning(f"State Bootstrapper Warning: {e}")

# Navigation Catalog Mapping: Category -> { Display Name: (module_path, class_or_fn_name) }
MODULE_CATALOG = {
    "📊 Executive Dashboard": {
        "Overview Dashboard": ("modules.dashboard.dashboard", "render"),
    },
    "📂 Project Hub": {
        "Project Directory": ("modules.projects.project_page", "ProjectPage"),
    },
    "🏛️ Architectural Generative Synthesis": {
        "Generative Layout Solver": ("modules.architecture.synthesis_page", "ArchitectureSynthesisPage"),
        "Zoning Analysis": ("modules.architecture.zoning", "render"),
        "Room Programming": ("modules.architecture.room_programming", "render"),
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

# Sidebar UI Controls
st.sidebar.title("🏗️ IMAGINE Engine")
st.sidebar.caption("Integrated Architecture & Civil Engineering")

domain_category = st.sidebar.selectbox("Select Domain", list(MODULE_CATALOG.keys()))
sub_modules = MODULE_CATALOG[domain_category]
selected_submodule = st.sidebar.radio("Select Module", list(sub_modules.keys()))

# Dynamic Safe Loader Engine
module_path, target_symbol = sub_modules[selected_submodule]

try:
    # Dynamically import module at runtime
    imported_module = importlib.import_module(module_path)

    # Check if target symbol is a function or class
    if hasattr(imported_module, target_symbol):
        symbol = getattr(imported_module, target_symbol)

        # If it's a class with a .render() classmethod
        if isinstance(symbol, type) and hasattr(symbol, "render"):
            symbol.render()
        # If it's a standard render function
        elif callable(symbol):
            symbol()
        else:
            st.error(f"Symbol `{target_symbol}` in `{module_path}` is not callable.")
    elif hasattr(imported_module, "render"):
        # Fallback to module-level render() function
        imported_module.render()
    else:
        st.warning(
            f"Module `{module_path}` loaded successfully, but does not expose a `render()` function or `{target_symbol}` class."
        )

except ModuleNotFoundError as e:
    st.info(f"🚧 **{selected_submodule}** is under active development.")
    st.caption(f"Module path `{module_path}` was not found in the current branch.")
    with st.expander("Technical Traceback"):
        st.exception(e)

except Exception as e:
    st.error(f"⚠️ Error executing **{selected_submodule}** (`{module_path}`)")
    st.exception(e)
