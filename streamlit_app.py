"""
IMAGINE
Generative Architecture & Civil Engine

Main Streamlit application entry point.

Application shell responsibilities:
    - Navigation
    - Centralized module registry
    - Safe renderer loading
    - Error isolation
    - Module status
    - Domain routing
    - System health

Domain logic remains inside:
    architecture/
    structural/
    bim/
    mep/
    costing/
    construction/
    documents/
    ai/
    analytics/
    regional/
    integrations/
    digital_twin/
    projects/
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib import import_module
from typing import Any, Callable

import streamlit as st


# ============================================================
# APP PACKAGE SHADOWING PROTECTION
# ============================================================

def _protect_app_package() -> None:
    """
    Prevent a root-level app.py module from shadowing the
    app/ package.

    This is intentionally performed by the Streamlit shell
    instead of modifying the database layer.
    """

    loaded_app = sys.modules.get("app")

    if loaded_app is None:
        return

    app_path = getattr(loaded_app, "__file__", None)

    if not app_path:
        return

    if app_path.endswith("/app.py") or app_path.endswith("\\app.py"):
        sys.modules.pop("app", None)


_protect_app_package()


# ============================================================
# OPTIONAL HEALTH IMPORT
# ============================================================

try:
    from architecture.health import (
        health_summary,
        run_startup_health_check,
    )
except Exception:

    health_summary = None
    run_startup_health_check = None


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="IMAGINE",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# TYPES
# ============================================================

RenderFunction = Callable[[], Any]


# ============================================================
# MODULE DEFINITION
# ============================================================

@dataclass(frozen=True)
class ModuleDefinition:
    label: str
    route: str
    domain: str
    description: str = ""

    renderer_module: str | None = None
    renderer_function: str | None = None

    implemented: bool = False


# ============================================================
# SAFE IMPORT
# ============================================================

def _safe_import(
    module_name: str | None,
    function_name: str | None,
) -> RenderFunction | None:

    if not module_name:
        return None

    if not function_name:
        return None

    try:
        module = import_module(module_name)

        renderer = getattr(
            module,
            function_name,
            None,
        )

        if callable(renderer):
            return renderer

    except Exception:
        return None

    return None


# ============================================================
# PLACEHOLDER
# ============================================================

def render_module_placeholder(
    module: ModuleDefinition,
) -> None:

    st.title(module.label)

    if module.description:
        st.caption(module.description)

    st.info(
        f"{module.label} is registered in IMAGINE, "
        "but a Streamlit renderer has not yet been implemented."
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Domain",
            module.domain,
        )

    with col2:
        st.metric(
            "Renderer",
            "Not available",
        )

    with col3:
        st.metric(
            "Registration",
            "Connected",
        )

    st.divider()

    st.subheader("Domain Integration")

    st.write(
        "The navigation route is connected to the IMAGINE "
        "application shell. The domain implementation remains "
        "inside its own package."
    )

    if module.renderer_module:
        st.code(
            f"{module.renderer_module}.{module.renderer_function}"
        )

    else:
        st.code(
            f"{module.domain} domain package"
        )


# ============================================================
# REGISTERED MODULE RENDERER
# ============================================================

def render_registered_module(
    module: ModuleDefinition,
) -> None:

    if (
        module.renderer_module
        and module.renderer_function
    ):

        try:

            renderer = _safe_import(
                module.renderer_module,
                module.renderer_function,
            )

        except Exception as exc:

            st.error(
                f"{module.label} could not be imported."
            )

            with st.expander(
                "Import traceback",
                expanded=True,
            ):
                st.exception(exc)

            return

        if renderer is not None:

            try:

                renderer()

            except Exception as exc:

                st.error(
                    f"{module.label} could not be rendered."
                )

                with st.expander(
                    "Renderer traceback",
                    expanded=True,
                ):
                    st.exception(exc)

            return

    render_module_placeholder(module)


# ============================================================
# OVERVIEW
# ============================================================

def render_overview() -> None:

    st.title("IMAGINE")

    st.caption(
        "Generative Architecture & Civil Engine"
    )

    st.markdown(
        """
        ## Engineering Platform

        IMAGINE connects project management, architecture,
        structural engineering, BIM, MEP, costing, construction,
        documents, AI, analytics, regional requirements,
        integrations and digital twins.
        """
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Projects", "0")

    with col2:
        st.metric("Design Runs", "0")

    with col3:
        st.metric("Engineering Modules", "0")

    with col4:
        st.metric("BIM Assets", "0")

    st.divider()

    st.subheader("Engineering Pipeline")

    pipeline = [
        "Projects",
        "Architecture",
        "Structural",
        "BIM",
        "MEP",
        "Costing",
        "Construction",
        "Digital Twin",
    ]

    columns = st.columns(len(pipeline))

    for column, step in zip(columns, pipeline):

        with column:

            st.markdown(
                f"""
                <div style="
                    border:1px solid rgba(128,128,128,.25);
                    border-radius:12px;
                    padding:16px;
                    text-align:center;
                    min-height:80px;
                ">
                    <strong>{step}</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()

    st.subheader("System Status")

    c1, c2 = st.columns(2)

    with c1:
        st.success(
            "IMAGINE application shell is running."
        )

    with c2:
        st.info(
            "Domain modules are isolated from the navigation shell."
        )


# ============================================================
# PROJECT MODULES
# ============================================================

PROJECT_MODULES = [

    ModuleDefinition(
        label="Projects",
        icon="Projects",
        route="projects",
        domain="Projects",
        description="Project lifecycle and project records.",
        renderer_module="projects.projects.ui",
        renderer_function="render_projects",
        implemented=True,
    ),

    ModuleDefinition(
        label="Approvals",
        icon="Approvals",
        route="project_approvals",
        domain="Projects",
        description="Project approvals and authorization workflows.",
        renderer_module="projects.approvals.ui",
        renderer_function="render_approvals",
        implemented=True,
    ),

    ModuleDefinition(
        label="Revisions",
        icon="Revisions",
        route="project_revisions",
        domain="Projects",
        description="Project revisions and design history.",
        renderer_module="projects.revisions.ui",
        renderer_function="render_revisions",
        implemented=True,
    ),

    ModuleDefinition(
        label="Workflows",
        icon="Workflows",
        route="project_workflows",
        domain="Projects",
        description="Project workflow orchestration.",
        renderer_module="projects.workflows.ui",
        renderer_function="render_workflows",
        implemented=True,
    ),

    ModuleDefinition(
        label="Governance",
        icon="Governance",
        route="project_governance",
        domain="Projects",
        description="Project governance and controls.",
        renderer_module="projects.governance.ui",
        renderer_function="render_governance",
        implemented=True,
    ),
]


# ============================================================
# ARCHITECTURE
# ============================================================

def render_generative_design_safe() -> None:

    try:

        module = import_module(
            "architecture.generative_design.ui"
        )

        renderer = getattr(
            module,
            "render_generative_design",
        )

        renderer()

    except Exception as exc:

        st.error(
            "The Generative Design module could not be loaded."
        )

        with st.expander(
            "Complete import or renderer traceback",
            expanded=True,
        ):
            st.exception(exc)


def render_site_planning_registered() -> None:

    try:

        from architecture.site_planning.ui import (
            render_site_planning,
        )

    except Exception as exc:

        st.error(
            "The Site Planning module could not be loaded."
        )

        with st.expander(
            "Complete import traceback",
            expanded=True,
        ):
            st.exception(exc)

        return

    try:

        render_site_planning()

    except Exception as exc:

        st.error(
            "Site Planning could not be rendered."
        )

        with st.expander(
            "Complete renderer traceback",
            expanded=True,
        ):
            st.exception(exc)


ARCHITECTURE_MODULES = [

    ModuleDefinition(
        label="Zoning",
        route="architecture_zoning",
        domain="Architecture",
        description="Planning controls and zoning constraints.",
        renderer_module="architecture.zoning.ui",
        renderer_function="render_zoning",
        implemented=True,
    ),

    ModuleDefinition(
        label="Site Planning",
        route="architecture_site_planning",
        domain="Architecture",
        description="Site organization and development planning.",
        implemented=True,
    ),

    ModuleDefinition(
        label="Floor Planning",
        route="architecture_floor_planning",
        domain="Architecture",
        description="Floor layouts and spatial planning.",
        renderer_module="architecture.floor_planning.ui",
        renderer_function="render_floor_planning",
        implemented=True,
    ),

    ModuleDefinition(
        label="Room Programming",
        route="architecture_room_programming",
        domain="Architecture",
        description="Room requirements and spatial programming.",
        renderer_module="architecture.room_programming.ui",
        renderer_function="render_room_programming",
        implemented=True,
    ),

    ModuleDefinition(
        label="Compliance",
        route="architecture_compliance",
        domain="Architecture",
        description="Regulatory and design compliance.",
        renderer_module="architecture.compliance.ui",
        renderer_function="render_compliance",
        implemented=True,
    ),

    ModuleDefinition(
        label="Generative Design",
        route="architecture_generative_design",
        domain="Architecture",
        description="Constraint-driven design generation.",
        implemented=True,
    ),
]


# ============================================================
# OTHER DOMAINS
# ============================================================

STRUCTURAL_MODULES = [
    "Eurocode EN 1990",
    "Eurocode EN 1991",
    "Eurocode EN 1992",
    "Eurocode EN 1993",
    "Eurocode EN 1995",
    "Eurocode EN 1997",
    "Eurocode EN 1998",
    "Beam Design",
    "Column Design",
    "Slab Design",
    "Foundation Design",
    "Retaining Walls",
    "Steel Connections",
    "Finite Element Analysis",
]

BIM_MODULES = [
    "Buildings",
    "Storeys",
    "Spaces",
    "Elements",
    "IFC",
    "COBie",
    "BIM Digital Twin",
]

MEP_MODULES = [
    "HVAC",
    "Ventilation",
    "Chilled Water",
    "Energy Simulation",
    "Electrical Load Analysis",
    "Transformers",
    "Generators",
    "Cable Sizing",
    "Solar PV",
    "Water Supply",
    "Drainage",
    "Stormwater",
    "Sewer Networks",
    "Firefighting",
]

COSTING_MODULES = [
    "BOQ",
    "Quantity Takeoff",
    "Procurement",
    "Forex",
    "Inflation",
    "Risk Analysis",
    "Cashflow",
]

CONSTRUCTION_MODULES = [
    "Planning",
    "Scheduling",
    "RFIs",
    "Submittals",
    "Variations",
    "Snagging",
    "Progress Tracking",
    "Site Diaries",
]

DOCUMENT_MODULES = [
    "Drawing Management",
    "Specifications",
    "Contracts",
    "Reports",
    "Version Control",
    "Archives",
]

AI_MODULES = [
    "IMAGINE Architect",
    "IMAGINE Engineer",
    "IMAGINE MEP",
    "IMAGINE QS",
    "IMAGINE PM",
    "Vector Store",
    "RAG",
    "Prompt Library",
]

ANALYTICS_MODULES = [
    "Dashboards",
    "KPIs",
    "Portfolio",
    "Forecasting",
    "Reporting",
]

REGIONAL_MODULES = [
    "Uganda",
    "Kenya",
    "Tanzania",
    "Rwanda",
    "South Sudan",
    "Codes",
    "Zoning Laws",
]

INTEGRATION_MODULES = [
    "Microsoft",
    "AutoCAD",
    "Revit",
    "Archicad",
    "Tekla",
    "IfcOpenShell",
    "ArcGIS",
    "Azure",
    "Mapbox",
]

DIGITAL_TWIN_MODULES = [
    "Assets",
    "Sensors",
    "Telemetry",
    "Energy",
    "Maintenance",
    "Predictive AI",
]


# ============================================================
# SIMPLE DOMAIN MODULE DEFINITIONS
# ============================================================

def _simple_modules(
    labels: list[str],
    domain: str,
    prefix: str,
) -> list[ModuleDefinition]:

    modules = []

    for label in labels:

        route_name = (
            label.lower()
            .replace(" ", "_")
            .replace("-", "_")
        )

        modules.append(
            ModuleDefinition(
                label=label,
                route=f"{prefix}_{route_name}",
                domain=domain,
                description=f"{label} {domain.lower()} module.",
            )
        )

    return modules


STRUCTURAL_DEFINITIONS = _simple_modules(
    STRUCTURAL_MODULES,
    "Structural",
    "structural",
)

BIM_DEFINITIONS = _simple_modules(
    BIM_MODULES,
    "BIM",
    "bim",
)

MEP_DEFINITIONS = _simple_modules(
    MEP_MODULES,
    "MEP",
    "mep",
)

COSTING_DEFINITIONS = _simple_modules(
    COSTING_MODULES,
    "Costing",
    "costing",
)

CONSTRUCTION_DEFINITIONS = _simple_modules(
    CONSTRUCTION_MODULES,
    "Construction",
    "construction",
)

DOCUMENT_DEFINITIONS = _simple_modules(
    DOCUMENT_MODULES,
    "Documents",
    "documents",
)

AI_DEFINITIONS = _simple_modules(
    AI_MODULES,
    "AI",
    "ai",
)

ANALYTICS_DEFINITIONS = _simple_modules(
    ANALYTICS_MODULES,
    "Analytics",
    "analytics",
)

REGIONAL_DEFINITIONS = _simple_modules(
    REGIONAL_MODULES,
    "Regional",
    "regional",
)

INTEGRATION_DEFINITIONS = _simple_modules(
    INTEGRATION_MODULES,
    "Integrations",
    "integration",
)

DIGITAL_TWIN_DEFINITIONS = _simple_modules(
    DIGITAL_TWIN_MODULES,
    "Digital Twin",
    "digital_twin",
)


# ============================================================
# ALL MODULES
# ============================================================

ALL_MODULES = [

    *PROJECT_MODULES,

    *ARCHITECTURE_MODULES,

    *STRUCTURAL_DEFINITIONS,

    *BIM_DEFINITIONS,

    *MEP_DEFINITIONS,

    *COSTING_DEFINITIONS,

    *CONSTRUCTION_DEFINITIONS,

    *DOCUMENT_DEFINITIONS,

    *AI_DEFINITIONS,

    *ANALYTICS_DEFINITIONS,

    *REGIONAL_DEFINITIONS,

    *INTEGRATION_DEFINITIONS,

    *DIGITAL_TWIN_DEFINITIONS,
]


# ============================================================
# ROUTE REGISTRY
# ============================================================

MODULES_BY_ROUTE: dict[str, ModuleDefinition] = {

    "overview": ModuleDefinition(
        label="Overview",
        route="overview",
        domain="Core",
        description="IMAGINE engineering overview.",
        implemented=True,
    ),

    **{
        module.route: module
        for module in ALL_MODULES
    },

    "system_health": ModuleDefinition(
        label="System Health",
        route="system_health",
        domain="Core",
        description="Application and module diagnostics.",
        implemented=True,
    ),
}


# ============================================================
# SPECIAL RENDERERS
# ============================================================

SPECIAL_RENDERERS: dict[str, RenderFunction] = {

    "architecture_site_planning":
        render_site_planning_registered,

    "architecture_generative_design":
        render_generative_design_safe,
}


# ============================================================
# SYSTEM HEALTH
# ============================================================

def render_system_health() -> None:

    st.title("System Health")

    st.caption(
        "IMAGINE application and module diagnostics."
    )

    if run_startup_health_check is None:

        st.warning(
            "The IMAGINE health subsystem could not be imported."
        )

        return

    try:

        results = run_startup_health_check()

    except Exception as exc:

        st.error(
            "System Health could not run."
        )

        with st.expander(
            "Health-check traceback",
            expanded=True,
        ):
            st.exception(exc)

        return

    checked_at = datetime.now(
        timezone.utc
    )

    st.session_state[
        "health_last_checked_at"
    ] = checked_at

    healthy = all(
        result.status == "ok"
        for result in results
    )

    if healthy:

        st.session_state[
            "health_last_successful_at"
        ] = checked_at

    if health_summary is not None:

        summary = health_summary(
            results
        )

    else:

        total = len(results)

        healthy_count = sum(
            result.status == "ok"
            for result in results
        )

        summary = {
            "total": total,
            "healthy": healthy_count,
            "failed": total - healthy_count,
            "status": (
                "healthy"
                if healthy_count == total
                else "degraded"
            ),
        }

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Modules Checked",
            summary["total"],
        )

    with col2:
        st.metric(
            "Healthy",
            summary["healthy"],
        )

    with col3:
        st.metric(
            "Failed",
            summary["failed"],
        )

    if summary["status"] == "healthy":

        st.success(
            "All checked modules imported successfully."
        )

    else:

        st.warning(
            "IMAGINE is running in degraded mode."
        )

    st.divider()

    for result in results:

        if result.status == "ok":

            st.success(
                result.name
            )

        else:

            st.error(
                result.name
            )

            if result.error:

                st.code(
                    result.error,
                    language="text",
                )

            if result.traceback_text:

                with st.expander(
                    "Complete traceback",
                    expanded=True,
                ):

                    st.code(
                        result.traceback_text,
                        language="text",
                    )

    if st.button(
        "Run Health Check Again",
        use_container_width=True,
    ):

        st.rerun()


# ============================================================
# ROUTE RENDERING
# ============================================================

def render_route(
    route: str,
) -> None:

    if route == "overview":

        render_overview()
        return

    if route == "system_health":

        render_system_health()
        return

    module = MODULES_BY_ROUTE.get(
        route
    )

    if module is None:

        st.error(
            f"Unknown IMAGINE route: {route}"
        )

        return

    special_renderer = SPECIAL_RENDERERS.get(
        route
    )

    if special_renderer:

        try:

            special_renderer()

        except Exception as exc:

            st.error(
                f"{module.label} could not be rendered."
            )

            with st.expander(
                "Complete renderer traceback",
                expanded=True,
            ):
                st.exception(exc)

        return

    render_registered_module(
        module
    )


# ============================================================
# NAVIGATION
# ============================================================

def _navigation_button(
    module: ModuleDefinition,
) -> None:

    active = (
        st.session_state.active_route
        == module.route
    )

    if st.button(
        module.label,
        key=f"nav_{module.route}",
        use_container_width=True,
        type=(
            "primary"
            if active
            else "secondary"
        ),
    ):

        st.session_state.active_route = (
            module.route
        )

        st.rerun()


def _navigation_group(
    title: str,
    modules: list[ModuleDefinition],
    expanded: bool = False,
) -> None:

    with st.expander(
        title,
        expanded=expanded,
    ):

        for module in modules:

            _navigation_button(
                module
            )


# ============================================================
# SESSION STATE
# ============================================================

if "active_route" not in st.session_state:

    st.session_state.active_route = (
        "overview"
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        # IMAGINE

        **Generative Architecture & Civil Engine**
        """
    )

    st.divider()

    st.caption("NAVIGATION")

    _navigation_button(
        MODULES_BY_ROUTE["overview"]
    )

    _navigation_group(
        "PROJECTS",
        PROJECT_MODULES,
        expanded=False,
    )

    _navigation_group(
        "ARCHITECTURE",
        ARCHITECTURE_MODULES,
        expanded=True,
    )

    _navigation_group(
        "STRUCTURAL",
        STRUCTURAL_DEFINITIONS,
    )

    _navigation_group(
        "BIM",
        BIM_DEFINITIONS,
    )

    _navigation_group(
        "MEP",
        MEP_DEFINITIONS,
    )

    _navigation_group(
        "COSTING",
        COSTING_DEFINITIONS,
    )

    _navigation_group(
        "CONSTRUCTION",
        CONSTRUCTION_DEFINITIONS,
    )

    _navigation_group(
        "DOCUMENTS",
        DOCUMENT_DEFINITIONS,
    )

    _navigation_group(
        "AI",
        AI_DEFINITIONS,
    )

    _navigation_group(
        "ANALYTICS",
        ANALYTICS_DEFINITIONS,
    )

    _navigation_group(
        "REGIONAL",
        REGIONAL_DEFINITIONS,
    )

    _navigation_group(
        "INTEGRATIONS",
        INTEGRATION_DEFINITIONS,
    )

    _navigation_group(
        "DIGITAL TWIN",
        DIGITAL_TWIN_DEFINITIONS,
    )

    st.divider()

    _navigation_button(
        MODULES_BY_ROUTE["system_health"]
    )


# ============================================================
# ROUTE VALIDATION
# ============================================================

active_route = st.session_state.get(
    "active_route",
    "overview",
)

if active_route not in MODULES_BY_ROUTE:

    active_route = "overview"

    st.session_state.active_route = (
        active_route
    )


# ============================================================
# ACTIVE MODULE
# ============================================================

active_module = MODULES_BY_ROUTE.get(
    active_route
)

if active_module is not None:

    if active_route not in (
        "overview",
        "system_health",
    ):

        st.caption(
            f"IMAGINE | {active_module.domain}"
        )


# ============================================================
# RENDER
# ============================================================

render_route(
    active_route
)