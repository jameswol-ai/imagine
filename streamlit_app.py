"""
IMAGINE — Integrated AEC & Civil Engineering Platform
Path: streamlit_app.py
App: imagine
"""

import importlib
import streamlit as st
from Modules.utils.mock_data import init_mock_data

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
        "Executive Dashboard": ("Modules.dashboard.dashboard", "render"),
    },
    "Projects & Planning": {
        "Project Portfolio": ("Modules.projects.project_page", "ProjectPage"),
    },
    "Architecture": {
        "Generative Synthesis": ("Modules.architecture.synthesis", "render"),
        "Zoning & Planning": ("Modules.architecture.zoning", "render"),
        "Room Programming": ("Modules.architecture.room_programming", "render"),
    },
    "BIM & Spatial": {
        "Buildings": ("Modules.bim.buildings", "render"),
        "Storeys": ("Modules.bim.storeys", "render"),
        "Spaces": ("Modules.bim.spaces", "render"),
        "IFC Model Export": ("Modules.bim.ifc_export", "render"),
    },
    "Structural Engineering": {
        "Eurocodes Design Suite": ("Modules.structural.eurocode", "render_eurocode_router"),
        "Beam Design": ("Modules.structural.beam_design", "render"),
        "Column Design": ("Modules.structural.column_design", "render"),
        "Slab Design": ("Modules.structural.slab_design", "render"),
        "Foundation Design": ("Modules.structural.foundation_design", "render"),
        "Retaining Walls": ("Modules.structural.retaining_walls", "render"),
        "Steel Connections": ("Modules.structural.steel_connections", "render"),
    },
    "MEP Engineering": {
        "Systems Analysis": ("Modules.mep.analysis", "render"),
        "HVAC Design": ("Modules.mep.hvac", "render"),
        "Electrical Distribution": ("Modules.mep.electrical", "render"),
        "Plumbing & Drainage": ("Modules.mep.plumbing", "render"),
        "Energy Simulation": ("Modules.mep.energy_simulation", "render"),
    },
    "Costing & Commercial": {
        "Bill of Quantities (BOQ)": ("Modules.costing.boq", "render"),
        "Procurement Manager": ("Modules.costing.procurement", "render"),
        "Forex Tracking": ("Modules.costing.forex", "render"),
        "Cost Escalation": ("Modules.costing.escalation", "render"),
        "Risk Analysis": ("Modules.costing.risk_analysis", "render"),
    },
    "Construction & Site": {
        "RFIs": ("Modules.construction.rfis", "render"),
        "Submittals": ("Modules.construction.submittals", "render"),
        "Site Diary": ("Modules.construction.site_diary", "render"),
        "Progress Tracking": ("Modules.construction.progress_tracking", "render"),
        "Snagging & Defect List": ("Modules.construction.snagging", "render"),
    },
    "Documents & Governance": {
        "Document Register": ("Modules.documents.documents", "render"),
        "Revisions Control": ("Modules.documents.revisions", "render"),
        "Drawing Register": ("Modules.documents.drawing_register", "render"),
        "Specifications": ("Modules.documents.specifications", "render"),
        "Transmittals": ("Modules.documents.transmittals", "render"),
        "Approvals & Governance": ("Modules.governance.approvals", "render"),
    },
    "Digital Twin & Telemetry": {
        "Asset Register": ("Modules.digital_twin.assets", "render"),
        "Sensors Grid": ("Modules.digital_twin.sensors", "render"),
        "Telemetry Stream": ("Modules.digital_twin.telemetry", "render"),
        "Maintenance Schedule": ("Modules.digital_twin.maintenance", "render"),
        "Predictive AI": ("Modules.digital_twin.predictive_ai", "render"),
    },
    "Analytics & Portfolio": {
        "Portfolio Analytics": ("Modules.analytics.portfolio", "render"),
        "Custom Reporting": ("Modules.analytics.reporting", "render"),
        "Financial Forecasting": ("Modules.analytics.forecasting", "render"),
        "KPI Dashboard": ("Modules.analytics.kpis", "render"),
    },
    "AI Co-Pilots": {
        "AI Architect": ("Modules.ai.architect", "render"),
        "AI Structural Engineer": ("Modules.ai.engineer", "render"),
        "AI MEP Consultant": ("Modules.ai.mep", "render"),
        "AI Quantity Surveyor": ("Modules.ai.qs", "render"),
        "AI Project Manager": ("Modules.ai.project_manager", "render"),
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
