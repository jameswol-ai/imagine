"""
IMAGINE AEC Engine — Enhanced UI (with class support)
Path: streamlit_app.py
"""

import importlib
import sys
from pathlib import Path
import streamlit as st

# ----------------------------------------------
# Custom CSS for better UI
# ----------------------------------------------
st.markdown("""
<style>
    .main { padding: 0 1rem; }
    .metric-card {
        background: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .metric-card h3 { color: #1e3c72; font-size: 1.2rem; margin-bottom: 0.3rem; }
    .metric-value { font-size: 2.2rem; font-weight: 700; color: #1e3c72; }
    .metric-change { font-size: 0.9rem; color: #28a745; }
    .sidebar .sidebar-content { background: #f8f9fa; }
    .sidebar h1, .sidebar h2 { color: #1e3c72; }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background: #e9ecef;
        border-radius: 8px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 500;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: #1e3c72;
        color: white;
    }
    .footer {
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #dee2e6;
        text-align: center;
        color: #6c757d;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

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
# Session State Initialization
# ----------------------------------------------
try:
    from modules.utils.mock_data import init_mock_data as init_session_state
    init_session_state()
except Exception as e:
    st.sidebar.warning(f"⚠️ State bootstrapper: {e}")

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
# Module Loader – handles both functions and classes
# ----------------------------------------------
def render_module(module_path, target_symbol):
    try:
        imported_module = importlib.import_module(module_path)

        # 1. Try the exact target (e.g., "render")
        if hasattr(imported_module, target_symbol):
            render_func = getattr(imported_module, target_symbol)
            if callable(render_func):
                render_func()
                return True
            else:
                st.error(f"❌ `{target_symbol}` exists but is not callable.")

        # 2. Look for a class with a .render() method
        for attr_name in dir(imported_module):
            attr = getattr(imported_module, attr_name)
            if isinstance(attr, type) and hasattr(attr, "render"):
                render_method = getattr(attr, "render")
                if callable(render_method):
                    # If it's a classmethod or staticmethod, call it directly
                    try:
                        render_method()
                    except TypeError:
                        # It might need an instance – instantiate and call
                        instance = attr()
                        instance.render()
                    return True

        # 3. Fallback: try a module-level "render" function
        if hasattr(imported_module, "render"):
            render_func = getattr(imported_module, "render")
            if callable(render_func):
                render_func()
                return True

        # 4. No render found
        st.warning(f"⚠️ Module `{module_path}` has no `render()` function or class with `.render()`.")
        st.caption("Available attributes:")
        st.code(dir(imported_module))
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
    st.info("💡 Try creating the module file or check the path.")

# ----------------------------------------------
# Footer
# ----------------------------------------------
st.sidebar.markdown("---")
st.sidebar.caption("IMAGINE Enterprise v24.1")
st.markdown('<div class="footer">IMAGINE — Integrated AEC Engine</div>', unsafe_allow_html=True)