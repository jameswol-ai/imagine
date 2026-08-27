"""
IMAGINE AEC Engine
Integrated Architecture, Engineering & Construction Platform

Main Streamlit application shell.

Responsibilities:
- Application configuration
- Session-state initialization
- Enterprise sidebar navigation
- Interactive domain and module navigation
- Quick navigation
- Lazy module loading
- Renderer dispatch
- Isolated module failures
- System health diagnostics
- Responsive application layout

The application shell deliberately avoids eager imports of database,
service, schema, and model modules. Individual modules are loaded only
when selected from the navigation.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Callable

import streamlit as st


# =============================================================================
# APPLICATION PATH
# =============================================================================

ROOT_DIR = Path(__file__).resolve().parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="IMAGINE | Integrated AEC Engine",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# APPLICATION CSS
# =============================================================================

def inject_styles() -> None:
    st.markdown(
        """
        <style>
        /* =============================================================
           GLOBAL
        ============================================================= */

        .stApp {
            background: #f5f7fa;
        }

        .block-container {
            max-width: 1550px;
            padding-top: 1.6rem;
            padding-bottom: 3rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }

        /* =============================================================
           SIDEBAR
        ============================================================= */

        section[data-testid="stSidebar"] {
            width: 320px !important;
            background: #ffffff;
            border-right: 1px solid #dfe4ea;
        }

        section[data-testid="stSidebar"] > div {
            padding-top: 1rem;
        }

        section[data-testid="stSidebar"] .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .imagine-sidebar-brand {
            padding: 0.4rem 0.25rem 0.9rem 0.25rem;
        }

        .imagine-sidebar-brand-title {
            font-size: 1.55rem;
            font-weight: 800;
            letter-spacing: -0.035em;
            color: #162033;
        }

        .imagine-sidebar-brand-subtitle {
            margin-top: 0.3rem;
            color: #687386;
            font-size: 0.76rem;
            line-height: 1.45;
        }

        .imagine-sidebar-label {
            margin-top: 0.8rem;
            margin-bottom: 0.35rem;
            color: #697587;
            font-size: 0.68rem;
            font-weight: 750;
            letter-spacing: 0.09em;
            text-transform: uppercase;
        }

        .imagine-sidebar-status {
            margin-top: 1rem;
            padding: 0.8rem;
            border: 1px solid #dfe4ea;
            border-radius: 9px;
            background: #f8fafc;
        }

        .imagine-sidebar-status-title {
            color: #687386;
            font-size: 0.68rem;
            font-weight: 750;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .imagine-sidebar-status-value {
            margin-top: 0.25rem;
            color: #172033;
            font-size: 0.84rem;
            font-weight: 700;
        }

        /* =============================================================
           MAIN HEADER
        ============================================================= */

        .imagine-header {
            margin-bottom: 1.2rem;
        }

        .imagine-header-title {
            margin: 0;
            color: #172033;
            font-size: 2.15rem;
            line-height: 1.1;
            font-weight: 800;
            letter-spacing: -0.04em;
        }

        .imagine-header-subtitle {
            margin-top: 0.4rem;
            color: #687386;
            font-size: 0.92rem;
            line-height: 1.45;
        }

        .imagine-breadcrumb {
            display: inline-block;
            margin-top: 0.85rem;
            padding: 0.38rem 0.7rem;
            border: 1px solid #dfe4ea;
            border-radius: 7px;
            background: #eef2f6;
            color: #566276;
            font-size: 0.75rem;
        }

        /* =============================================================
           KPI CARDS
        ============================================================= */

        .imagine-card {
            min-height: 118px;
            padding: 1.05rem;
            border: 1px solid #dfe4ea;
            border-radius: 10px;
            background: #ffffff;
        }

        .imagine-card-title {
            color: #687386;
            font-size: 0.7rem;
            font-weight: 750;
            letter-spacing: 0.07em;
            text-transform: uppercase;
        }

        .imagine-card-value {
            margin-top: 0.45rem;
            color: #172033;
            font-size: 1.65rem;
            font-weight: 800;
            letter-spacing: -0.025em;
        }

        .imagine-card-description {
            margin-top: 0.25rem;
            color: #7b8798;
            font-size: 0.75rem;
        }

        /* =============================================================
           MODULE PANEL
        ============================================================= */

        .imagine-module-panel {
            margin-bottom: 1rem;
            padding: 1.25rem 1.35rem;
            border: 1px solid #dfe4ea;
            border-radius: 10px;
            background: #ffffff;
        }

        .imagine-module-title {
            color: #172033;
            font-size: 1.3rem;
            font-weight: 760;
            letter-spacing: -0.02em;
        }

        .imagine-module-description {
            margin-top: 0.35rem;
            color: #687386;
            font-size: 0.86rem;
            line-height: 1.5;
        }

        /* =============================================================
           NAVIGATION
        ============================================================= */

        div.stButton > button {
            min-height: 2.35rem;
            border-radius: 7px;
            font-weight: 650;
        }

        div[data-testid="stRadio"] label {
            font-size: 0.82rem;
        }

        /* =============================================================
           EXPANDERS
        ============================================================= */

        div[data-testid="stExpander"] {
            border-color: #dfe4ea;
            border-radius: 8px;
        }

        /* =============================================================
           FOOTER
        ============================================================= */

        .imagine-footer {
            margin-top: 3rem;
            padding-top: 1rem;
            border-top: 1px solid #dfe4ea;
            color: #8791a0;
            font-size: 0.72rem;
        }

        /* =============================================================
           DARK MODE
        ============================================================= */

        @media (prefers-color-scheme: dark) {

            .stApp {
                background: #0d131b;
            }

            section[data-testid="stSidebar"] {
                background: #111821;
                border-right-color: #293441;
            }

            .imagine-sidebar-brand-title,
            .imagine-header-title,
            .imagine-card-value,
            .imagine-module-title,
            .imagine-sidebar-status-value {
                color: #f1f4f8;
            }

            .imagine-sidebar-brand-subtitle,
            .imagine-header-subtitle,
            .imagine-module-description,
            .imagine-card-description {
                color: #a5afbd;
            }

            .imagine-sidebar-status {
                background: #151d27;
                border-color: #2b3745;
            }

            .imagine-sidebar-status-title,
            .imagine-card-title {
                color: #a5afbd;
            }

            .imagine-breadcrumb {
                background: #1a2330;
                border-color: #2b3745;
                color: #b8c1ce;
            }

            .imagine-card,
            .imagine-module-panel {
                background: #141b24;
                border-color: #2b3745;
            }

            .imagine-footer {
                border-top-color: #2b3745;
                color: #7e8998;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# SESSION STATE
# =============================================================================

def init_session_state() -> None:
    """Initialize application-wide session state."""

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


# =============================================================================
# NAVIGATION CATALOG
# =============================================================================

NAVIGATION: dict[str, dict[str, tuple[str | None, str | None]]] = {

    "Overview": {
        "Overview": (
            "__builtin_overview__",
            "render_overview",
        ),
        "System Health": (
            "__builtin_health__",
            "render_system_health",
        ),
    },

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

    "ARCHITECTURE": {
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

    "STRUCTURAL": {
        "Eurocode Suite": (
            "modules.structural.eurocode",
            "render",
        ),
        "EN 1990": (None, None),
        "EN 1991": (None, None),
        "EN 1992": (None, None),
        "EN 1993": (None, None),
        "EN 1995": (None, None),
        "EN 1997": (None, None),
        "EN 1998": (None, None),
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
        "Finite Element Analysis": (None, None),
    },

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
        "Elements": (None, None),
        "IFC": (
            "modules.bim.ifc_export",
            "render",
        ),
        "COBie": (None, None),
        "BIM Digital Twin": (None, None),
    },

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
        "Electrical Load Analysis": (
            "modules.mep.electrical",
            "render",
        ),
        "Transformers": (None, None),
        "Generators": (None, None),
        "Cable Sizing": (None, None),
        "Solar PV": (None, None),
        "Water Supply": (
            "modules.mep.plumbing",
            "render",
        ),
        "Drainage": (
            "modules.mep.plumbing",
            "render",
        ),
        "Stormwater": (None, None),
        "Sewer Networks": (None, None),
        "Firefighting": (None, None),
    },

    "COSTING": {
        "BOQ": (
            "modules.costing.boq",
            "render",
        ),
        "Quantity Takeoff": (
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
        "Inflation / Escalation": (
            "modules.costing.escalation",
            "render",
        ),
        "Risk Analysis": (
            "modules.costing.risk_analysis",
            "render",
        ),
        "Cashflow": (None, None),
    },

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

    "DOCUMENTS": {
        "Drawing Management": (
            "modules.documents.drawing_register",
            "render",
        ),
        "Document Register": (
            "modules.documents.documents",
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
        "Reports": (None, None),
        "Revision History": (
            "modules.documents.revisions",
            "render",
        ),
        "Transmittals": (
            "modules.documents.transmittals",
            "render",
        ),
        "Archives": (None, None),
    },

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
        "Vector Store": (None, None),
        "RAG": (None, None),
        "Prompt Library": (None, None),
    },

    "ANALYTICS": {
        "Dashboards": (
            "modules.dashboard.dashboard",
            "render",
        ),
        "KPIs": (
            "modules.analytics.kpis",
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
    },

    "REGIONAL": {
        "Uganda": (None, None),
        "Kenya": (None, None),
        "Tanzania": (None, None),
        "Rwanda": (None, None),
        "South Sudan": (None, None),
        "Codes": (None, None),
        "Zoning Laws": (None, None),
    },

    "INTEGRATIONS": {
        "Microsoft": (None, None),
        "AutoCAD": (None, None),
        "Revit": (None, None),
        "Archicad": (None, None),
        "Tekla": (None, None),
        "IfcOpenShell": (None, None),
        "ArcGIS": (None, None),
        "Azure": (None, None),
        "Mapbox": (None, None),
    },

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
        "Energy": (None, None),
        "Maintenance": (
            "modules.digital_twin.maintenance",
            "render",
        ),
        "Predictive AI": (
            "modules.digital_twin.predictive_ai",
            "render",
        ),
    },

    "GOVERNANCE": {
        "Approvals": (
            "modules.governance.approvals",
            "render",
        ),
        "System Health": (
            "__builtin_health__",
            "render_system_health",
        ),
    },
}


# =============================================================================
# DOMAIN DESCRIPTIONS
# =============================================================================

DOMAIN_DESCRIPTIONS = {
    "Overview": (
        "Enterprise workspace, portfolio summary and system diagnostics."
    ),
    "PROJECTS": (
        "Project lifecycle, approvals, revisions, workflows and governance."
    ),
    "ARCHITECTURE": (
        "Zoning, site planning, floor planning, room programming, "
        "compliance and generative design."
    ),
    "STRUCTURAL": (
        "Structural engineering workflows and Eurocode design."
    ),
    "BIM": (
        "Buildings, storeys, spaces, elements and OpenBIM."
    ),
    "MEP": (
        "Mechanical, electrical and plumbing engineering."
    ),
    "COSTING": (
        "BOQ, quantity takeoff, procurement and financial analysis."
    ),
    "CONSTRUCTION": (
        "Planning, scheduling, RFIs, submittals and site management."
    ),
    "DOCUMENTS": (
        "Drawing, document, specification, contract and revision control."
    ),
    "AI": (
        "Architecture, engineering, MEP, QS and project management AI."
    ),
    "ANALYTICS": (
        "Portfolio analytics, KPIs, forecasting and reporting."
    ),
    "REGIONAL": (
        "Regional codes, regulations and zoning requirements."
    ),
    "INTEGRATIONS": (
        "AEC software, GIS, cloud and interoperability integrations."
    ),
    "DIGITAL TWIN": (
        "Assets, sensors, telemetry, maintenance and predictive AI."
    ),
    "GOVERNANCE": (
        "Enterprise governance, approvals and system controls."
    ),
}


# =============================================================================
# NAVIGATION HELPERS
# =============================================================================

def set_navigation(domain: str, module: str) -> None:
    """Persist navigation state."""

    if domain not in NAVIGATION:
        return

    if module not in NAVIGATION[domain]:
        return

    st.session_state.active_domain = domain
    st.session_state.active_module = module


def navigation_callback(domain: str, module: str) -> None:
    """Callback used by interactive navigation controls."""

    set_navigation(domain, module)


# =============================================================================
# BUILT-IN OVERVIEW
# =============================================================================

def render_overview() -> None:
    """Render the main IMAGINE overview."""

    st.markdown(
        """
        <div class="imagine-header">
            <div class="imagine-header-title">
                IMAGINE
            </div>
            <div class="imagine-header-subtitle">
                Integrated Architecture, Engineering & Construction Engine
            </div>
            <div class="imagine-breadcrumb">
                Overview / Enterprise Workspace
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    projects = st.session_state.get("projects_data", [])
    buildings = st.session_state.get("buildings_data", [])

    active_projects = sum(
        1
        for project in projects
        if str(project.get("status", "")).lower() == "active"
    )

    completed_projects = sum(
        1
        for project in projects
        if str(project.get("status", "")).lower() == "completed"
    )

    if projects:
        average_progress = sum(
            float(project.get("progress", 0) or 0)
            for project in projects
        ) / len(projects)
    else:
        average_progress = 0.0

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""
            <div class="imagine-card">
                <div class="imagine-card-title">Projects</div>
                <div class="imagine-card-value">{len(projects)}</div>
                <div class="imagine-card-description">
                    Registered projects
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
            <div class="imagine-card">
                <div class="imagine-card-title">Active Projects</div>
                <div class="imagine-card-value">{active_projects}</div>
                <div class="imagine-card-description">
                    Currently active
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f"""
            <div class="imagine-card">
                <div class="imagine-card-title">Buildings</div>
                <div class="imagine-card-value">{len(buildings)}</div>
                <div class="imagine-card-description">
                    BIM building records
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown(
            f"""
            <div class="imagine-card">
                <div class="imagine-card-title">Average Progress</div>
                <div class="imagine-card-value">
                    {average_progress:.0f}%
                </div>
                <div class="imagine-card-description">
                    Across registered projects
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    left, right = st.columns([1.25, 1])

    with left:

        st.markdown(
            """
            <div class="imagine-module-panel">
                <div class="imagine-module-title">
                    Enterprise Workspace
                </div>
                <div class="imagine-module-description">
                    Use the navigation panel to move between project
                    management, architecture, structural engineering,
                    BIM, MEP, costing, construction, documents,
                    analytics, AI, regional services, integrations
                    and digital twin capabilities.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### Project Portfolio")

        if projects:
            for project in projects:
                name = project.get("name", "Unnamed Project")
                status = project.get("status", "Unknown")
                progress = project.get("progress", 0)

                st.write(
                    f"**{name}**  \n"
                    f"Status: {status} | Progress: {progress}%"
                )
        else:
            st.info("No project records are currently available.")

    with right:

        st.markdown("### Workspace Domains")

        for domain, description in DOMAIN_DESCRIPTIONS.items():

            st.markdown(
                f"**{domain}**  \n"
                f"{description}"
            )


# =============================================================================
# SYSTEM HEALTH
# =============================================================================

def render_system_health() -> None:
    """Render module import diagnostics."""

    st.markdown(
        """
        <div class="imagine-header">
            <div class="imagine-header-title">
                System Health
            </div>
            <div class="imagine-header-subtitle">
                IMAGINE module availability and import diagnostics
            </div>
            <div class="imagine-breadcrumb">
                Overview / System Health
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    health_modules = [
        (
            "Projects",
            "projects.projects.ui",
            "render_projects",
        ),
        (
            "Approvals",
            "projects.approvals.ui",
            "render_approvals",
        ),
        (
            "Revisions",
            "projects.revisions.ui",
            "render_revisions",
        ),
        (
            "Workflows",
            "projects.workflows.ui",
            "render_workflows",
        ),
        (
            "Governance",
            "projects.governance.ui",
            "render_governance",
        ),
        (
            "Zoning",
            "architecture.zoning.ui",
            "render_zoning",
        ),
        (
            "Site Planning",
            "architecture.site_planning.ui",
            "render_site_planning",
        ),
        (
            "Floor Planning",
            "architecture.floor_planning.ui",
            "render_floor_planning",
        ),
        (
            "Room Programming",
            "architecture.room_programming.ui",
            "render_room_programming",
        ),
        (
            "Compliance",
            "architecture.compliance.ui",
            "render_compliance",
        ),
        (
            "Generative Design",
            "architecture.generative_design.ui",
            "render_generative_design",
        ),
    ]

    results: list[dict[str, object]] = []

    for label, module_path, renderer_name in health_modules:

        try:
            module = importlib.import_module(module_path)

            renderer = getattr(
                module,
                renderer_name,
                None,
            )

            if renderer is None:
                renderer = getattr(
                    module,
                    "render",
                    None,
                )

            if not callable(renderer):
                raise TypeError(
                    f"Expected renderer '{renderer_name}' "
                    f"was not found."
                )

            results.append(
                {
                    "label": label,
                    "module": module_path,
                    "status": "Healthy",
                    "error": "",
                }
            )

        except Exception as exc:

            results.append(
                {
                    "label": label,
                    "module": module_path,
                    "status": "Failed",
                    "error": (
                        f"{type(exc).__name__}: {exc}"
                    ),
                }
            )

    healthy = sum(
        result["status"] == "Healthy"
        for result in results
    )

    failed = len(results) - healthy

    a, b, c = st.columns(3)

    with a:
        st.metric(
            "Modules Checked",
            len(results),
        )

    with b:
        st.metric(
            "Healthy",
            healthy,
        )

    with c:
        st.metric(
            "Failed",
            failed,
        )

    st.divider()

    for result in results:

        if result["status"] == "Healthy":

            st.success(
                f"{result['label']} — renderer available"
            )

        else:

            st.error(
                f"{result['label']} — renderer unavailable"
            )

            with st.expander(
                f"Diagnostic details: {result['label']}"
            ):
                st.code(
                    f"Module: {result['module']}\n"
                    f"Error: {result['error']}"
                )


# =============================================================================
# PLACEHOLDER
# =============================================================================

def render_placeholder(
    domain: str,
    module_name: str,
) -> None:
    """Render a controlled placeholder for future modules."""

    st.markdown(
        f"""
        <div class="imagine-header">
            <div class="imagine-header-title">
                {module_name}
            </div>
            <div class="imagine-header-subtitle">
                {domain}
            </div>
            <div class="imagine-breadcrumb">
                {domain} / {module_name}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="imagine-module-panel">
            <div class="imagine-module-title">
                Module Registered
            </div>
            <div class="imagine-module-description">
                This module is registered in the IMAGINE navigation
                system, but its dedicated Streamlit renderer has not
                yet been connected.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# RENDERER LOADER
# =============================================================================

def load_renderer(
    module_path: str,
    target_symbol: str,
) -> Callable[[], object]:
    """
    Lazily import a module and return its renderer.

    The configured renderer is checked first. The conventional
    render() function is then used as a fallback.
    """

    module = importlib.import_module(module_path)

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


# =============================================================================
# SIDEBAR NAVIGATION
# =============================================================================

def render_sidebar() -> tuple[str, str]:
    """
    Build the complete interactive sidebar.

    Navigation state is persisted in session_state so Streamlit reruns
    do not unexpectedly reset the selected module.
    """

    with st.sidebar:

        st.markdown(
            """
            <div class="imagine-sidebar-brand">
                <div class="imagine-sidebar-brand-title">
                    IMAGINE
                </div>
                <div class="imagine-sidebar-brand-subtitle">
                    Integrated Architecture, Engineering &
                    Construction Engine
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        st.markdown(
            '<div class="imagine-sidebar-label">Domain</div>',
            unsafe_allow_html=True,
        )

        domains = list(NAVIGATION)

        current_domain = st.session_state.get(
            "active_domain",
            "Overview",
        )

        if current_domain not in domains:
            current_domain = "Overview"

        domain_index = domains.index(current_domain)

        domain = st.selectbox(
            "Domain",
            options=domains,
            index=domain_index,
            key="imagine_domain_selector",
            label_visibility="collapsed",
        )

        if domain != st.session_state.active_domain:

            module_names = list(NAVIGATION[domain])

            set_navigation(
                domain,
                module_names[0],
            )

            st.rerun()

        st.caption(
            DOMAIN_DESCRIPTIONS.get(
                domain,
                "IMAGINE enterprise module domain.",
            )
        )

        st.markdown(
            '<div class="imagine-sidebar-label">Module</div>',
            unsafe_allow_html=True,
        )

        module_names = list(
            NAVIGATION[domain]
        )

        current_module = st.session_state.get(
            "active_module",
            module_names[0],
        )

        if current_module not in module_names:
            current_module = module_names[0]

        module = st.radio(
            "Module",
            options=module_names,
            index=module_names.index(current_module),
            key=f"imagine_module_selector_{domain}",
            label_visibility="collapsed",
        )

        set_navigation(
            domain,
            module,
        )

        st.divider()

        st.markdown(
            '<div class="imagine-sidebar-label">Quick Navigation</div>',
            unsafe_allow_html=True,
        )

        quick_targets = [
            ("Overview", "Overview"),
            ("Projects", "PROJECTS"),
            ("Architecture", "ARCHITECTURE"),
            ("Structural", "STRUCTURAL"),
            ("BIM", "BIM"),
            ("MEP", "MEP"),
            ("Costing", "COSTING"),
            ("Construction", "CONSTRUCTION"),
            ("Documents", "DOCUMENTS"),
            ("AI", "AI"),
            ("Analytics", "ANALYTICS"),
            ("Digital Twin", "DIGITAL TWIN"),
        ]

        for label, target_domain in quick_targets:

            if target_domain not in NAVIGATION:
                continue

            first_module = next(
                iter(NAVIGATION[target_domain])
            )

            selected = (
                st.session_state.active_domain
                == target_domain
            )

            button_label = (
                f"Current: {label}"
                if selected
                else label
            )

            if st.button(
                button_label,
                key=f"quick_nav_{target_domain}",
                use_container_width=True,
                disabled=selected,
            ):
                set_navigation(
                    target_domain,
                    first_module,
                )
                st.rerun()

        st.divider()

        module_path, target_symbol = NAVIGATION[
            domain
        ][module]

        if module_path is None:

            navigation_status = "Registered module"
            renderer_reference = "Renderer pending"

        elif module_path.startswith(
            "__builtin_"
        ):

            navigation_status = "Built-in view"

            renderer_reference = (
                target_symbol
                or "Built-in renderer"
            )

        else:

            navigation_status = "Connected module"

            renderer_reference = (
                f"{module_path}.{target_symbol}"
            )

        st.markdown(
            f"""
            <div class="imagine-sidebar-status">
                <div class="imagine-sidebar-status-title">
                    Navigation Status
                </div>
                <div class="imagine-sidebar-status-value">
                    {navigation_status}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption(renderer_reference)

        st.divider()

        st.caption(
            "IMAGINE AEC Engine"
        )

        st.caption(
            "Enterprise Architecture & Civil Engineering Platform"
        )

    return domain, module


# =============================================================================
# MAIN CONTENT HEADER
# =============================================================================

def render_navigation_header(
    domain: str,
    module_name: str,
) -> None:
    """Render a consistent header above external modules."""

    if domain == "Overview":
        return

    st.markdown(
        f"""
        <div class="imagine-header">
            <div class="imagine-header-title">
                {module_name}
            </div>
            <div class="imagine-header-subtitle">
                IMAGINE {domain.title()} Workspace
            </div>
            <div class="imagine-breadcrumb">
                {domain} / {module_name}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# MAIN MODULE DISPATCH
# =============================================================================

def render_selected_module(
    domain: str,
    module_name: str,
) -> None:
    """Dispatch the selected navigation item."""

    module_path, target_symbol = NAVIGATION[
        domain
    ][module_name]

    # -------------------------------------------------------------------------
    # Built-in overview
    # -------------------------------------------------------------------------

    if module_path == "__builtin_overview__":

        render_overview()
        return

    # -------------------------------------------------------------------------
    # Built-in health
    # -------------------------------------------------------------------------

    if module_path == "__builtin_health__":

        render_system_health()
        return

    # -------------------------------------------------------------------------
    # Registered but not implemented
    # -------------------------------------------------------------------------

    if (
        module_path is None
        or target_symbol is None
    ):

        render_placeholder(
            domain,
            module_name,
        )
        return

    # -------------------------------------------------------------------------
    # External renderer
    # -------------------------------------------------------------------------

    render_navigation_header(
        domain,
        module_name,
    )

    try:

        renderer = load_renderer(
            module_path,
            target_symbol,
        )

        renderer()

    except ModuleNotFoundError as exc:

        st.warning(
            f"{module_name} is not currently available."
        )

        with st.expander(
            "Module import details",
            expanded=True,
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
                f"Expected: "
                f"{module_path}.{target_symbol}"
            )

            st.exception(exc)

    except ImportError as exc:

        st.error(
            f"{module_name} could not be imported."
        )

        with st.expander(
            "Import error",
            expanded=True,
        ):

            st.code(
                f"Module: {module_path}\n"
                f"Renderer: {target_symbol}"
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

            st.code(
                f"Domain: {domain}\n"
                f"Module: {module_name}\n"
                f"Python module: {module_path}\n"
                f"Renderer: {target_symbol}"
            )

            st.exception(exc)


# =============================================================================
# FOOTER
# =============================================================================

def render_footer() -> None:

    st.markdown(
        """
        <div class="imagine-footer">
            IMAGINE AEC Engine |
            Integrated Architecture, Engineering & Construction Platform
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:
    """
    Main Streamlit application entry point.

    The sidebar is explicitly constructed here so navigation remains
    part of the application shell on every rerun.
    """

    inject_styles()

    init_session_state()

    domain, module_name = render_sidebar()

    render_selected_module(
        domain,
        module_name,
    )

    render_footer()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()