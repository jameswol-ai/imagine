"""
IMAGINE AEC Engine
Integrated Architecture, Engineering & Construction Platform

Main Streamlit application shell.

Responsibilities:
- Application configuration
- Safe session-state initialization
- Complete sidebar navigation
- Lazy module loading
- Renderer dispatch
- Isolated module failures
- System health view

The application shell deliberately does not eagerly import database,
service, schema, or model modules. This prevents one broken module from
preventing the rest of IMAGINE from starting.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Callable

import streamlit as st


# ============================================================
# APPLICATION PATH
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="IMAGINE | Integrated AEC Engine",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

def init_session_state() -> None:
    """
    Initialize application-level session state.

    Module-specific state remains owned by the individual module.
    """

    defaults = {
        "imagine_initialized": True,
        "active_domain": "Overview",
        "active_module": "Overview",

        "projects_data": [
            {
                "id": 1,
                "name": "Green Tower",
                "status": "Active",
                "budget": 12.5,
                "progress": 75,
            },
            {
                "id": 2,
                "name": "Harbor Bridge",
                "status": "Planning",
                "budget": 8.3,
                "progress": 20,
            },
            {
                "id": 3,
                "name": "Riverside Mall",
                "status": "Completed",
                "budget": 22.1,
                "progress": 100,
            },
        ],

        "buildings_data": [
            {
                "id": 1,
                "name": "Tower A",
                "storeys": 25,
                "area": 15000,
                "ifc_version": "IFC4",
            },
            {
                "id": 2,
                "name": "Tower B",
                "storeys": 18,
                "area": 12000,
                "ifc_version": "IFC4",
            },
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


init_session_state()


# ============================================================
# NAVIGATION CATALOG
# ============================================================

# Each entry is:
#
#     "Display Name": ("python.module.path", "renderer_function")
#
# Renderers are imported only after the user selects them.

NAVIGATION = {
    "Overview": {
        "Overview": (
            "modules.dashboard.dashboard",
            "render",
        ),
    },

    # --------------------------------------------------------
    # PROJECTS
    # --------------------------------------------------------

    "PROJECTS": {
        "Projects": (
            "projects.projects.ui",
            "render_projects",
        ),
        "Approvals": (
            "projects.approvals.ui",
            "render_approvals",
        ),
        "Revisions": (
            "projects.revisions.ui",
            "render_revisions",
        ),
        "Workflows": (
            "projects.workflows.ui",
            "render_workflows",
        ),
        "Governance": (
            "projects.governance.ui",
            "render_governance",
        ),
    },

    # --------------------------------------------------------
    # ARCHITECTURE
    # --------------------------------------------------------

    "ARCHITECTURE": {
        "Architecture Workspace": (
            "architecture.ui",
            "render_architecture",
        ),
        "Zoning": (
            "architecture.zoning.ui",
            "render_zoning",
        ),
        "Site Planning": (
            "architecture.site_planning.ui",
            "render_site_planning",
        ),
        "Floor Planning": (
            "architecture.floor_planning.ui",
            "render_floor_planning",
        ),
        "Room Programming": (
            "architecture.room_programming.ui",
            "render_room_programming",
        ),
        "Compliance": (
            "architecture.compliance.ui",
            "render_compliance",
        ),
        "Generative Design": (
            "architecture.generative_design.ui",
            "render_generative_design",
        ),
    },

    # --------------------------------------------------------
    # BIM
    # --------------------------------------------------------

    "BIM": {
        "Buildings": (
            "modules.bim.buildings",
            "render",
        ),
        "Storeys": (
            "modules.bim.storeys",
            "render",
        ),
        "Spaces": (
            "modules.bim.spaces",
            "render",
        ),
        "IFC OpenBIM": (
            "modules.bim.ifc_export",
            "render",
        ),
    },

    # --------------------------------------------------------
    # STRUCTURAL
    # --------------------------------------------------------

    "STRUCTURAL": {
        "Eurocode Suite": (
            "modules.structural.eurocode",
            "render",
        ),
        "Beam Design": (
            "modules.structural.beam_design",
            "render",
        ),
        "Column Design": (
            "modules.structural.column_design",
            "render",
        ),
        "Slab Design": (
            "modules.structural.slab_design",
            "render",
        ),
        "Foundation Design": (
            "modules.structural.foundation_design",
            "render",
        ),
        "Retaining Walls": (
            "modules.structural.retaining_walls",
            "render",
        ),
        "Steel Connections": (
            "modules.structural.steel_connections",
            "render",
        ),
    },

    # --------------------------------------------------------
    # MEP
    # --------------------------------------------------------

    "MEP": {
        "Integrated MEP Analysis": (
            "modules.mep.analysis",
            "render",
        ),
        "HVAC": (
            "modules.mep.hvac",
            "render",
        ),
        "Ventilation": (
            "modules.mep.analysis",
            "render",
        ),
        "Chilled Water": (
            "modules.mep.analysis",
            "render",
        ),
        "Energy Simulation": (
            "modules.mep.energy_simulation",
            "render",
        ),
        "Electrical": (
            "modules.mep.electrical",
            "render",
        ),
        "Plumbing": (
            "modules.mep.plumbing",
            "render",
        ),
    },

    # --------------------------------------------------------
    # COSTING
    # --------------------------------------------------------

    "COSTING": {
        "BOQ": (
            "modules.costing.boq",
            "render",
        ),
        "Procurement": (
            "modules.costing.procurement",
            "render",
        ),
        "Forex": (
            "modules.costing.forex",
            "render",
        ),
        "Cost Escalation": (
            "modules.costing.escalation",
            "render",
        ),
        "Risk Analysis": (
            "modules.costing.risk_analysis",
            "render",
        ),
    },

    # --------------------------------------------------------
    # CONSTRUCTION
    # --------------------------------------------------------

    "CONSTRUCTION": {
        "Planning": (
            "modules.construction.progress_tracking",
            "render",
        ),
        "Scheduling": (
            "modules.construction.progress_tracking",
            "render",
        ),
        "RFIs": (
            "modules.construction.rfis",
            "render",
        ),
        "Submittals": (
            "modules.construction.submittals",
            "render",
        ),
        "Variations": (
            "modules.construction.submittals",
            "render",
        ),
        "Snagging": (
            "modules.construction.snagging",
            "render",
        ),
        "Progress Tracking": (
            "modules.construction.progress_tracking",
            "render",
        ),
        "Site Diaries": (
            "modules.construction.site_diary",
            "render",
        ),
    },

    # --------------------------------------------------------
    # DOCUMENTS
    # --------------------------------------------------------

    "DOCUMENTS": {
        "Document Register": (
            "modules.documents.documents",
            "render",
        ),
        "Drawing Management": (
            "modules.documents.drawing_register",
            "render",
        ),
        "Specifications": (
            "modules.documents.specifications",
            "render",
        ),
        "Contracts": (
            "modules.documents.documents",
            "render",
        ),
        "Revision History": (
            "modules.documents.revisions",
            "render",
        ),
        "Transmittals": (
            "modules.documents.transmittals",
            "render",
        ),
    },

    # --------------------------------------------------------
    # AI
    # --------------------------------------------------------

    "AI": {
        "IMAGINE Architect": (
            "modules.ai.architect",
            "render",
        ),
        "IMAGINE Engineer": (
            "modules.ai.engineer",
            "render",
        ),
        "IMAGINE MEP": (
            "modules.ai.mep",
            "render",
        ),
        "IMAGINE QS": (
            "modules.ai.qs",
            "render",
        ),
        "IMAGINE PM": (
            "modules.ai.project_manager",
            "render",
        ),
    },

    # --------------------------------------------------------
    # ANALYTICS
    # --------------------------------------------------------

    "ANALYTICS": {
        "Dashboards": (
            "modules.dashboard.dashboard",
            "render",
        ),
        "Portfolio": (
            "modules.analytics.portfolio",
            "render",
        ),
        "Forecasting": (
            "modules.analytics.forecasting",
            "render",
        ),
        "Reporting": (
            "modules.analytics.reporting",
            "render",
        ),
        "KPIs": (
            "modules.analytics.kpis",
            "render",
        ),
    },

    # --------------------------------------------------------
    # DIGITAL TWIN
    # --------------------------------------------------------

    "DIGITAL TWIN": {
        "Assets": (
            "modules.digital_twin.assets",
            "render",
        ),
        "Sensors": (
            "modules.digital_twin.sensors",
            "render",
        ),
        "Telemetry": (
            "modules.digital_twin.telemetry",
            "render",
        ),
        "Maintenance": (
            "modules.digital_twin.maintenance",
            "render",
        ),
        "Predictive AI": (
            "modules.digital_twin.predictive_ai",
            "render",
        ),
    },

    # --------------------------------------------------------
    # GOVERNANCE
    # --------------------------------------------------------

    "GOVERNANCE": {
        "Approvals": (
            "modules.governance.approvals",
            "render",
        ),
    },

    # --------------------------------------------------------
    # REGIONAL
    # --------------------------------------------------------

    "REGIONAL": {
        "Uganda": (
            None,
            None,
        ),
        "Kenya": (
            None,
            None,
        ),
        "Tanzania": (
            None,
            None,
        ),
        "Rwanda": (
            None,
            None,
        ),
        "South Sudan": (
            None,
            None,
        ),
        "Codes": (
            None,
            None,
        ),
        "Zoning Laws": (
            None,
            None,
        ),
    },

    # --------------------------------------------------------
    # INTEGRATIONS
    # --------------------------------------------------------

    "INTEGRATIONS": {
        "Microsoft": (
            None,
            None,
        ),
        "AutoCAD": (
            None,
            None,
        ),
        "Revit": (
            None,
            None,
        ),
        "Archicad": (
            None,
            None,
        ),
        "Tekla": (
            None,
            None,
        ),
        "IfcOpenShell": (
            None,
            None,
        ),
        "ArcGIS": (
            None,
            None,
        ),
        "Azure": (
            None,
            None,
        ),
        "Mapbox": (
            None,
            None,
        ),
    },
}


# ============================================================
# SYSTEM HEALTH
# ============================================================

def render_system_health() -> None:
    """
    Render the existing IMAGINE health checks without allowing
    an individual health-check import to crash the application.
    """

    st.title("System Health")
    st.caption(
        "Application dependency and module health diagnostics."
    )

    try:
        from architecture.health import (
            check_module,
            health_summary,
        )
    except Exception as exc:
        st.error(
            "System health module could not be loaded."
        )

        with st.expander(
            "Complete health-module error",
            expanded=True,
        ):
            st.exception(exc)

        return

    modules = [
        "projects.projects.ui",
        "projects.approvals.ui",
        "projects.revisions.ui",
        "projects.workflows.ui",
        "projects.governance.ui",
        "architecture.ui",
        "architecture.zoning.ui",
        "architecture.site_planning.ui",
        "architecture.floor_planning.ui",
        "architecture.room_programming.ui",
        "architecture.compliance.ui",
        "architecture.generative_design.ui",
    ]

    results = [
        check_module(module_name)
        for module_name in modules
    ]

    summary = health_summary(results)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Modules Checked",
        summary["total"],
    )

    col2.metric(
        "Healthy",
        summary["healthy"],
    )

    col3.metric(
        "Failed",
        summary["failed"],
    )

    col4.metric(
        "Overall Status",
        summary["status"].upper(),
    )

    st.divider()

    for result in results:

        if result.status == "ok":
            st.success(
                f"{result.name} — OK"
            )

        else:
            st.error(
                f"{result.name} — FAILED"
            )

            if result.error:

                with st.expander(
                    f"Error details: {result.name}"
                ):
                    st.code(
                        result.error
                    )

                    if result.traceback_text:
                        st.code(
                            result.traceback_text
                        )


# ============================================================
# PLACEHOLDER
# ============================================================

def render_placeholder(
    domain: str,
    module_name: str,
) -> None:
    """
    Render a clean placeholder for navigation entries whose
    backend/UI implementation does not yet exist.
    """

    st.title(module_name)

    st.caption(
        f"{domain} module"
    )

    st.info(
        f"{module_name} is registered in IMAGINE, "
        "but its interactive Streamlit renderer is not "
        "implemented yet."
    )

    st.markdown(
        """
        ### Module Status

        The navigation entry is intentionally preserved so the
        IMAGINE information architecture remains complete.

        The renderer can be connected later without changing
        the sidebar structure.
        """
    )


# ============================================================
# MODULE LOADER
# ============================================================

def load_renderer(
    module_path: str | None,
    target_symbol: str | None,
) -> Callable[[], object] | None:
    """
    Lazily import and resolve a renderer.

    Returns None when the module or renderer cannot be loaded.
    """

    if not module_path or not target_symbol:
        return None

    try:
        module = importlib.import_module(
            module_path
        )
    except ModuleNotFoundError:
        raise
    except Exception:
        raise

    renderer = getattr(
        module,
        target_symbol,
        None,
    )

    if renderer is None:
        renderer = getattr(
            module,
            "render",
            None,
        )

    if renderer is None:
        raise AttributeError(
            f"Module '{module_path}' does not expose "
            f"'{target_symbol}' or 'render'."
        )

    if not callable(renderer):
        raise TypeError(
            f"Renderer '{target_symbol}' in "
            f"'{module_path}' is not callable."
        )

    return renderer


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar() -> tuple[str, str]:
    """
    Build the complete IMAGINE sidebar and return the selected
    domain and module.
    """

    with st.sidebar:

        st.title("IMAGINE")

        st.caption(
            "Integrated Architecture, Engineering & "
            "Construction Engine"
        )

        st.divider()

        domains = list(
            NAVIGATION.keys()
        )

        current_domain = st.session_state.get(
            "active_domain",
            "Overview",
        )

        if current_domain not in domains:
            current_domain = "Overview"

        domain = st.selectbox(
            "Domain",
            domains,
            index=domains.index(
                current_domain
            ),
            key="imagine_domain_selector",
        )

        modules = list(
            NAVIGATION[domain].keys()
        )

        current_module = st.session_state.get(
            "active_module",
            modules[0],
        )

        if current_module not in modules:
            current_module = modules[0]

        module = st.radio(
            "Module",
            modules,
            index=modules.index(
                current_module
            ),
            key="imagine_module_selector",
        )

        st.session_state.active_domain = domain
        st.session_state.active_module = module

        st.divider()

        st.caption(
            f"Domain: {domain}"
        )

        entry = NAVIGATION[domain][module]

        module_path, target_symbol = entry

        if module_path:
            st.caption(
                f"`{module_path}.{target_symbol}`"
            )
        else:
            st.caption(
                "Renderer pending"
            )

        st.divider()

        st.caption(
            "IMAGINE AEC Engine"
        )

        st.caption(
            "Enterprise Architecture & Civil Engineering "
            "Platform"
        )

    return domain, module


# ============================================================
# RENDER SELECTED MODULE
# ============================================================

def render_selected_module(
    domain: str,
    module_name: str,
) -> None:
    """
    Render the selected navigation target.
    """

    module_path, target_symbol = (
        NAVIGATION[domain][module_name]
    )

    # --------------------------------------------------------
    # Placeholder entries
    # --------------------------------------------------------

    if not module_path:
        render_placeholder(
            domain,
            module_name,
        )
        return

    # --------------------------------------------------------
    # Actual renderer
    # --------------------------------------------------------

    try:

        renderer = load_renderer(
            module_path,
            target_symbol,
        )

        if renderer is None:
            render_placeholder(
                domain,
                module_name,
            )
            return

        renderer()

    except ModuleNotFoundError as exc:

        st.warning(
            f"{module_name} is not currently available."
        )

        with st.expander(
            "Module import details"
        ):
            st.code(
                f"Module: {module_path}\n"
                f"Renderer: {target_symbol}"
            )
            st.exception(exc)

    except AttributeError as exc:

        st.error(
            f"{module_name} does not expose its expected renderer."
        )

        with st.expander(
            "Renderer details",
            expanded=True,
        ):
            st.code(
                "Expected:\n"
                f"{module_path}.{target_symbol}"
            )
            st.exception(exc)

    except Exception as exc:

        st.error(
            f"{module_name} encountered a runtime error."
        )

        with st.expander(
            "Complete module error",
            expanded=True,
        ):
            st.exception(exc)


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    """
    Main IMAGINE application entry point.
    """

    domain, module_name = render_sidebar()

    # --------------------------------------------------------
    # Overview
    # --------------------------------------------------------

    if domain == "Overview":

        st.title(
            "IMAGINE"
        )

        st.subheader(
            "Generative Architecture & Civil Engine"
        )

        st.caption(
            "Integrated AEC workspace for architecture, "
            "structural engineering, BIM, MEP, costing, "
            "construction, documents, analytics and AI."
        )

        st.divider()

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Projects",
            len(
                st.session_state.get(
                    "projects_data",
                    [],
                )
            ),
        )

        col2.metric(
            "Buildings",
            len(
                st.session_state.get(
                    "buildings_data",
                    [],
                )
            ),
        )

        col3.metric(
            "Active Design",
            "Architecture",
        )

        col4.metric(
            "System",
            "Online",
        )

        st.divider()

        st.markdown(
            "### IMAGINE Workspace"
        )

        left, right = st.columns(2)

        with left:

            st.markdown(
                """
                **PROJECTS**

                Manage projects, approvals, revisions,
                workflows and governance.

                **ARCHITECTURE**

                Develop zoning, site planning, floor planning,
                room programming, compliance and generative design.
                """
            )

        with right:

            st.markdown(
                """
                **ENGINEERING**

                Coordinate structural, BIM and MEP workflows.

                **DELIVERY**

                Connect costing, construction, documents,
                analytics, AI and digital-twin capabilities.
                """
            )

        return

    # --------------------------------------------------------
    # System Health
    # --------------------------------------------------------

    if (
        domain == "GOVERNANCE"
        and module_name == "System Health"
    ):
        render_system_health()
        return

    # --------------------------------------------------------
    # Selected module
    # --------------------------------------------------------

    render_selected_module(
        domain,
        module_name,
    )


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()