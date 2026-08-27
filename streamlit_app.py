"""
IMAGINE AEC Engine — Unified Harness
Path: streamlit_app.py
"""

import importlib
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
# Session State Initialization
# ----------------------------------------------
try:
    from modules.utils.mock_data import init_session_state
    init_session_state()
except Exception as e:
    st.sidebar.warning(f"⚠️ State bootstrapper failed: {e}")

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
    "🏛️ Architecture": {
        "Generative Layout Solver": ("modules.architecture.synthesis", "render"),
        "Zoning Analysis": ("modules.architecture.zoning", "render"),
        "Room Programming": ("modules.architecture.room_programming", "render"),
    },
    "🏢 BIM": {
        "Building Registry": ("modules.bim.buildings", "render"),
        "Storeys & Levels": ("modules.bim.storeys", "render"),
        "Spatial Allocations": ("modules.bim.spaces", "render"),
        "IFC Exporter": ("modules.bim.ifc_export", "render"),
    },
    "🧱 Structural": {
        "Eurocode Overview": ("modules.structural.eurocode", "render"),
        "Beam Design": ("modules.structural.beam_design", "render"),
        "Column Design": ("modules.structural.column_design", "render"),
        "Slab Design": ("modules.structural.slab_design", "render"),
        "Foundation Design": ("modules.structural.foundation_design", "render"),
        "Retaining Walls": ("modules.structural.retaining_walls", "render"),
        "Steel Connections": ("modules.structural.steel_connections", "render"),
    },
    "⚡ MEP": {
        "Analysis": ("modules.mep.analysis", "render"),
        "HVAC": ("modules.mep.hvac", "render"),
        "Electrical": ("modules.mep.electrical", "render"),
        "Plumbing": ("modules.mep.plumbing", "render"),
        "Energy Simulation": ("modules.mep.energy_simulation", "render"),
    },
    "💰 Costing": {
        "BoQ": ("modules.costing.boq", "render"),
        "Procurement": ("modules.costing.procurement", "render"),
        "Forex": ("modules.costing.forex", "render"),
        "Escalation": ("modules.costing.escalation", "render"),
        "Risk Analysis": ("modules.costing.risk_analysis", "render"),
    },
    "🛡️ Governance": {
        "Approvals": ("modules.governance.approvals", "render"),
    },
    "🏗️ Construction": {
        "RFIs": ("modules.construction.rfis", "render"),
        "Submittals": ("modules.construction.submittals", "render"),
        "Site Diary": ("modules.construction.site_diary", "render"),
        "Progress Tracking": ("modules.construction.progress_tracking", "render"),
        "Snagging": ("modules.construction.snagging", "render"),
    },
    "📄 Documents": {
        "Documents": ("modules.documents.documents", "render"),
        "Revisions": ("modules.documents.revisions", "render"),
        "Drawing Register": ("modules.documents.drawing_register", "render"),
        "Specifications": ("modules.documents.specifications", "render"),
        "Transmittals": ("modules.documents.transmittals", "render"),
    },
    "📈 Analytics": {
        "Portfolio": ("modules.analytics.portfolio", "render"),
        "Reporting": ("modules.analytics.reporting", "render"),
        "Forecasting": ("modules.analytics.forecasting", "render"),
        "KPIs": ("modules.analytics.kpis", "render"),
    },
    "📡 Digital Twin": {
        "Assets": ("modules.digital_twin.assets", "render"),
        "Sensors": ("modules.digital_twin.sensors", "render"),
        "Telemetry": ("modules.digital_twin.telemetry", "render"),
        "Maintenance": ("modules.digital_twin.maintenance", "render"),
        "Predictive AI": ("modules.digital_twin.predictive_ai", "render"),
    },
    "🤖 AI Copilots": {
        "Architect": ("modules.ai.architect", "render"),
        "Engineer": ("modules.ai.engineer", "render"),
        "MEP": ("modules.ai.mep", "render"),
        "QS": ("modules.ai.qs", "render"),
        "Project Manager": ("modules.ai.project_manager", "render"),
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

st.sidebar.caption(f"📍 `{module_path}`")

# ----------------------------------------------
# Module Loader (robust)
# ----------------------------------------------
def render_module(module_path, target_symbol):
    try:
        imported_module = importlib.import_module(module_path)

        # 1. Exact target
        if hasattr(imported_module, target_symbol):
            render_func = getattr(imported_module, target_symbol)
            if callable(render_func):
                render_func()
                return True

        # 2. Class with .render()
        for attr_name in dir(imported_module):
            attr = getattr(imported_module, attr_name)
            if isinstance(attr, type) and hasattr(attr, "render"):
                try:
                    instance = attr()
                    instance.render()
                except Exception:
                    # fallback to classmethod/staticmethod
                    getattr(attr, "render")()
                return True

        # 3. Module-level render
        if hasattr(imported_module, "render"):
            render_func = getattr(imported_module, "render")
            if callable(render_func):
                render_func()
                return True

        # 4. Fallback stub
        st.warning(f"⚠️ Module `{module_path}` has no `render()`.")
        st.write("ℹ️ Create a `render()` function or class with `.render()` in this module.")
        return False

    except ModuleNotFoundError:
        st.info(f"🚧 **{selected_submodule}** is under development.")
        return False
    except Exception as e:
        st.error(f"💥 Error loading **{selected_submodule}**")
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
