"""
IMAGINE — Integrated AEC & Civil Engineering Platform
Path: streamlit_app.py
App: imagine
"""

import importlib
import streamlit as st
from modules.utils.mock_data import init_mock_data

# ==============================================================================
# 1. PAGE CONFIGURATION & ENTERPRISE STYLING
# ==============================================================================
st.set_page_config(
    page_title="IMAGINE — AEC & Civil Engineering Engine",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* Glassmorphic Sidebar Styling */
    div[data-testid="stSidebar"] {
        background: rgba(20, 24, 36, 0.85);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* Brand Header */
    .brand-header {
        font-size: 1.6rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #FFFFFF;
        margin-bottom: 0px;
    }
    .brand-sub {
        font-size: 0.78rem;
        color: #63B3ED;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-weight: 600;
    }

    /* User Profile Card */
    .user-profile-card {
        background: rgba(255, 255, 255, 0.04);
        padding: 0.65rem 0.85rem;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 1rem;
    }
    .user-profile-card p {
        margin: 0;
        font-size: 0.80rem;
        color: #CBD5E0;
    }
    .user-profile-card strong {
        color: #FFFFFF;
    }

    /* Status Badge */
    .status-badge {
        display: inline-block;
        padding: 0.15rem 0.5rem;
        border-radius: 10px;
        font-size: 0.70rem;
        font-weight: 600;
        background: rgba(72, 187, 120, 0.2);
        color: #68D391;
        border: 1px solid rgba(104, 211, 145, 0.3);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# 2. SESSION STATE INITIALIZATION
# ==============================================================================
init_mock_data()

# Ensure Projects Data key sync
if "projects_data" not in st.session_state:
    st.session_state.projects_data = st.session_state.get("projects", [])

# ==============================================================================
# 3. WORKSPACE MODULE REGISTRY & ROUTING TABLE
# ==============================================================================
NAVIGATION_STRUCTURE = {
    "Dashboard": {
        "Executive Dashboard": ("modules.dashboard.dashboard", "render"),
    },
    "Projects & Planning": {
        "Project Portfolio": ("modules.projects.project_page", "ProjectPage"),
    },
    "Architecture": {
        "Generative Synthesis": ("modules.architecture.synthesis", "render"),
        "Zoning & Planning": ("modules.architecture.zoning", "render"),
        "Room Programming": ("modules.architecture.room_programming", "render"),
    },
    "BIM & Spatial": {
        "Buildings": ("modules.bim.buildings", "render"),
        "Storeys": ("modules.bim.storeys", "render"),
        "Spaces": ("modules.bim.spaces", "render"),
        "IFC Model Export": ("modules.bim.ifc_export", "render"),
    },
    "Structural Engineering": {
        "Eurocodes Design Suite": ("modules.structural.eurocode", "render_eurocode_router"),
        "Beam Design": ("modules.structural.beam_design", "render"),
        "Column Design": ("modules.structural.column_design", "render"),
        "Slab Design": ("modules.structural.slab_design", "render"),
        "Foundation Design": ("modules.structural.foundation_design", "render"),
        "Retaining Walls": ("modules.structural.retaining_walls", "render"),
        "Steel Connections": ("modules.structural.steel_connections", "render"),
    },
    "MEP Engineering": {
        "Systems Analysis": ("modules.mep.analysis", "render"),
        "HVAC Design": ("modules.mep.hvac", "render"),
        "Electrical Distribution": ("modules.mep.electrical", "render"),
        "Plumbing & Drainage": ("modules.mep.plumbing", "render"),
        "Energy Simulation": ("modules.mep.energy_simulation", "render"),
    },
    "Costing & Commercial": {
        "Bill of Quantities (BOQ)": ("modules.costing.boq", "render"),
        "Procurement Manager": ("modules.costing.procurement", "render"),
        "Forex Tracking": ("modules.costing.forex", "render"),
        "Cost Escalation": ("modules.costing.escalation", "render"),
        "Risk Analysis": ("modules.costing.risk_analysis", "render"),
    },
    "Construction & Site": {
        "RFIs": ("modules.construction.rfis", "render"),
        "Submittals": ("modules.construction.submittals", "render"),
        "Site Diary": ("modules.construction.site_diary", "render"),
        "Progress Tracking": ("modules.construction.progress_tracking", "render"),
        "Snagging & Defect List": ("modules.construction.snagging", "render"),
    },
    "Documents & Governance": {
        "Document Register": ("modules.documents.documents", "render"),
        "Revisions Control": ("modules.documents.revisions", "render"),
        "Drawing Register": ("modules.documents.drawing_register", "render"),
        "Specifications": ("modules.documents.specifications", "render"),
        "Transmittals": ("modules.documents.transmittals", "render"),
        "Approvals & Governance": ("modules.governance.approvals", "render"),
    },
    "Digital Twin & Telemetry": {
        "Asset Register": ("modules.digital_twin.assets", "render"),
        "Sensors Grid": ("modules.digital_twin.sensors", "render"),
        "Telemetry Stream": ("modules.digital_twin.telemetry", "render"),
        "Maintenance Schedule": ("modules.digital_twin.maintenance", "render"),
        "Predictive AI": ("modules.digital_twin.predictive_ai", "render"),
    },
    "Analytics & Portfolio": {
        "Portfolio Analytics": ("modules.analytics.portfolio", "render"),
        "Custom Reporting": ("modules.analytics.reporting", "render"),
        "Financial Forecasting": ("modules.analytics.forecasting", "render"),
        "KPI Dashboard": ("modules.analytics.kpis", "render"),
    },
    "AI Co-Pilots": {
        "AI Architect": ("modules.ai.architect", "render"),
        "AI Structural Engineer": ("modules.ai.engineer", "render"),
        "AI MEP Consultant": ("modules.ai.mep", "render"),
        "AI Quantity Surveyor": ("modules.ai.qs", "render"),
        "AI Project Manager": ("modules.ai.project_manager", "render"),
    },
}

# ==============================================================================
# 4. DYNAMIC MODULE RENDER ENGINE
# ==============================================================================
def render_placeholder_view(module_label: str, module_path: str) -> None:
    """Fallback UI rendered when a domain module file is being built."""
    st.subheader(f"🚧 {module_label}")
    st.info(f"The module `{module_path}` is configured in the route engine and ready for code implementation.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Status", "In Pipeline")
    col2.metric("Package Path", module_path.split(".")[1].upper())
    col3.metric("State Connection", "Active (st.session_state)")
    st.divider()


def execute_module_renderer(module_path: str, target_name: str, module_label: str) -> None:
    """Dynamically imports and executes a target module callable or class."""
    try:
        mod = importlib.import_module(module_path)

        if hasattr(mod, target_name):
            target = getattr(mod, target_name)
            # Handle class-based modules with static/classmethod render()
            if isinstance(target, type) and hasattr(target, "render"):
                target.render()
            # Handle standard function renderers
            elif callable(target):
                target()
            else:
                st.error(f"Target `{target_name}` in `{module_path}` is not callable.")
        else:
            render_placeholder_view(module_label, module_path)

    except ModuleNotFoundError:
        render_placeholder_view(module_label, module_path)
    except Exception as err:
        st.error(f"❌ Execution error inside `{module_label}` ({module_path}):")
        st.exception(err)

# ==============================================================================
# 5. MAIN ROUTER CONTROLLER
# ==============================================================================
def main() -> None:
    with st.sidebar:
        st.markdown("<div class='brand-header'>IMAGINE</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='brand-sub'>AEC & Civil Engineering Engine</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class='user-profile-card'>
                <p>User: <strong>admin</strong></p>
                <p>Role: <strong>Principal AEC Lead</strong></p>
                <p><span class='status-badge'>imagine v24.1 Enterprise</span></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Primary Domain Category Router
        domain_category = st.selectbox(
            "Domain Category",
            options=list(NAVIGATION_STRUCTURE.keys()),
            index=1,  # Default to Projects & Planning
        )

        # Sub-Module Router
        sub_modules = NAVIGATION_STRUCTURE[domain_category]
        selected_module_label = st.radio(
            "Select Module",
            options=list(sub_modules.keys()),
            index=0,
        )

        st.divider()

    # Dynamic Execution
    module_path, target_name = sub_modules[selected_module_label]
    execute_module_renderer(module_path, target_name, selected_module_label)


if __name__ == "__main__":
    main()
