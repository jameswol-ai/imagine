"""
IMAGINE
Generative Architecture & Civil Engine

Main Streamlit application entry point.

Application shell responsibilities:
    - Navigation
    - Centralized module registry
    - Safe renderer loading
    - Module status
    - Domain routing
    - System health
    - Import isolation

Domain logic belongs inside:
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
"""

from __future__ import annotations

import importlib
import importlib.util
import sys
import traceback
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType
from typing import Any, Callable


# ============================================================
# APP PACKAGE COMPATIBILITY
# ============================================================

def _bootstrap_app_package() -> None:
    """
    Prevent a repository-level app.py from shadowing the
    app/ package.

    The database layer may legitimately import:

        from app.settings import settings

    If Python resolves a root-level app.py first, that import
    fails with:

        ModuleNotFoundError:
        No module named 'app.settings'; 'app' is not a package

    This compatibility layer makes the real app/ directory
    available as the app package without modifying the existing
    database models or API contracts.
    """

    project_root = Path(__file__).resolve().parent
    app_directory = project_root / "app"

    if not app_directory.is_dir():
        return

    existing = sys.modules.get("app")

    if existing is not None:
        existing_path = getattr(existing, "__path__", None)

        if existing_path:
            return

        # A module named "app" exists but is not a package.
        # Remove it so the real package can be loaded.
        sys.modules.pop("app", None)

    app_init = app_directory / "__init__.py"

    if app_init.exists():
        spec = importlib.util.spec_from_file_location(
            "app",
            app_init,
            submodule_search_locations=[str(app_directory)],
        )
    else:
        spec = importlib.util.spec_from_loader(
            "app",
            loader=None,
            is_package=True,
        )

        if spec is not None:
            spec.submodule_search_locations = [
                str(app_directory)
            ]

    if spec is None:
        return

    module = importlib.util.module_from_spec(spec)

    module.__path__ = [str(app_directory)]
    module.__package__ = "app"

    sys.modules["app"] = module

    if spec.loader is not None:
        try:
            spec.loader.exec_module(module)
        except Exception:
            # Do not allow the compatibility layer to crash the
            # Streamlit application. Individual module imports
            # will expose their own detailed traceback.
            sys.modules.pop("app", None)


_bootstrap_app_package()


# ============================================================
# STREAMLIT
# ============================================================

import streamlit as st


# ============================================================
# OPTIONAL HEALTH IMPORT
# ============================================================

try:
    from architecture.health import (
        health_summary,
        run_startup_health_check,
    )

    HEALTH_AVAILABLE = True
    HEALTH_IMPORT_ERROR: Exception | None = None

except Exception as exc:
    HEALTH_AVAILABLE = False
    HEALTH_IMPORT_ERROR = exc

    def health_summary(
        results: list[Any],
    ) -> dict[str, Any]:
        total = len(results)
        healthy = sum(
            1
            for result in results
            if getattr(result, "status", None) == "ok"
        )

        return {
            "total": total,
            "healthy": healthy,
            "failed": total - healthy,
            "status": (
                "healthy"
                if total == healthy
                else "degraded"
            ),
        }

    def run_startup_health_check() -> list[Any]:
        return []


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="IMAGINE",
    page_icon="I",
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
    """
    Definition of a navigable IMAGINE module.
    """

    label: str
    route: str
    domain: str
    description: str = ""

    renderer_module: str | None = None
    renderer_function: str | None = None

    implemented: bool = False


# ============================================================
# IMPORT STATUS
# ============================================================

@dataclass
class ImportStatus:
    """
    Runtime status for a module renderer.
    """

    route: str
    label: str
    status: str
    renderer: RenderFunction | None = None
    error: str | None = None
    traceback_text: str | None = None


IMPORT_STATUS: dict[str, ImportStatus] = {}


# ============================================================
# SAFE IMPORT
# ============================================================

def _safe_import(
    module_name: str | None,
    function_name: str | None,
    *,
    route: str = "",
    label: str = "",
) -> RenderFunction | None:
    """
    Safely import a renderer.

    Import failures are captured instead of crashing the
    application shell.
    """

    if not module_name:
        IMPORT_STATUS[route] = ImportStatus(
            route=route,
            label=label,
            status="not_implemented",
        )

        return None

    if not function_name:
        IMPORT_STATUS[route] = ImportStatus(
            route=route,
            label=label,
            status="not_implemented",
        )

        return None

    try:
        module = importlib.import_module(
            module_name
        )

        renderer = getattr(
            module,
            function_name,
            None,
        )

        if not callable(renderer):

            error = (
                f"Renderer '{function_name}' was not found "
                f"in module '{module_name}'."
            )

            IMPORT_STATUS[route] = ImportStatus(
                route=route,
                label=label,
                status="failed",
                error=error,
            )

            return None

        IMPORT_STATUS[route] = ImportStatus(
            route=route,
            label=label,
            status="ok",
            renderer=renderer,
        )

        return renderer

    except Exception as exc:

        IMPORT_STATUS[route] = ImportStatus(
            route=route,
            label=label,
            status="failed",
            error=str(exc),
            traceback_text=traceback.format_exc(),
        )

        return None


# ============================================================
# PLACEHOLDER
# ============================================================

def render_module_placeholder(
    module: ModuleDefinition,
) -> None:
    """
    Render a safe placeholder for an unavailable module.
    """

    st.title(
        module.label
    )

    if module.description:
        st.caption(
            module.description
        )

    status = IMPORT_STATUS.get(
        module.route
    )

    if status and status.status == "failed":

        st.error(
            f"{module.label} could not be loaded."
        )

        if status.error:

            st.code(
                status.error,
                language="text",
            )

        if status.traceback_text:

            with st.expander(
                "Complete import traceback",
                expanded=True,
            ):

                st.code(
                    status.traceback_text,
                    language="text",
                )

        return

    st.info(
        f"{module.label} is registered in IMAGINE "
        "but its interactive interface is not available yet."
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
            "UI",
            "Not implemented",
        )

    with col3:
        st.metric(
            "Status",
            "Registered",
        )


# ============================================================
# REGISTERED MODULE RENDERER
# ============================================================

def render_registered_module(
    module: ModuleDefinition,
) -> None:
    """
    Load and render a module while isolating import and
    renderer failures.
    """

    if not module.renderer_module:
        render_module_placeholder(module)
        return

    if not module.renderer_function:
        render_module_placeholder(module)
        return

    renderer = _safe_import(
        module.renderer_module,
        module.renderer_function,
        route=module.route,
        label=module.label,
    )

    if renderer is None:
        render_module_placeholder(module)
        return

    try:

        renderer()

    except Exception as exc:

        st.error(
            f"{module.label} could not be rendered."
        )

        with st.expander(
            "Complete renderer traceback",
            expanded=True,
        ):

            st.code(
                traceback.format_exc(),
                language="text",
            )


# ============================================================
# OVERVIEW
# ============================================================

def render_overview() -> None:

    st.title(
        "IMAGINE"
    )

    st.caption(
        "Generative Architecture & Civil Engine"
    )

    st.markdown(
        """
        ## Project Overview

        IMAGINE connects architecture, structural engineering,
        BIM, MEP, costing, construction, documents, AI,
        analytics, regional regulations, integrations and
        digital twins into one engineering platform.
        """
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Projects",
            "0",
        )

    with col2:
        st.metric(
            "Design Runs",
            "0",
        )

    with col3:
        st.metric(
            "Engineering Modules",
            "0",
        )

    with col4:
        st.metric(
            "BIM Assets",
            "0",
        )

    st.divider()

    st.subheader(
        "IMAGINE Engineering Pipeline"
    )

    pipeline = [
        "Project",
        "Architecture",
        "Structural",
        "MEP",
        "BIM",
        "Costing",
        "Construction",
        "Digital Twin",
    ]

    columns = st.columns(
        len(pipeline)
    )

    for column, step in zip(
        columns,
        pipeline,
    ):

        with column:

            st.markdown(
                f"""
                <div style="
                    border:1px solid rgba(128,128,128,.25);
                    border-radius:12px;
                    padding:14px;
                    text-align:center;
                    min-height:80px;
                ">
                    <strong>{step}</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()

    st.subheader(
        "Engineering Domains"
    )

    domains = [
        (
            "Architecture",
            "Planning, compliance and generative design.",
        ),
        (
            "Structural",
            "Eurocode-based structural engineering.",
        ),
        (
            "BIM",
            "Buildings, spaces, elements and IFC.",
        ),
        (
            "MEP",
            "Mechanical, electrical and plumbing systems.",
        ),
        (
            "Costing",
            "BOQ, quantity takeoff and project costs.",
        ),
        (
            "Construction",
            "Planning, scheduling and site management.",
        ),
        (
            "Documents",
            "Drawings, specifications and contracts.",
        ),
        (
            "AI",
            "Engineering intelligence and RAG.",
        ),
    ]

    domain_columns = st.columns(4)

    for index, domain in enumerate(domains):

        column = domain_columns[
            index % 4
        ]

        with column:

            title, description = domain

            st.markdown(
                f"""
                ### {title}

                {description}
                """
            )


# ============================================================
# GENERATIVE DESIGN
# ============================================================

def render_generative_design_safe() -> None:

    st.title(
        "Generative Design"
    )

    try:

        module = importlib.import_module(
            "architecture.generative_design.ui"
        )

        renderer = getattr(
            module,
            "render_generative_design",
            None,
        )

        if not callable(renderer):
            raise AttributeError(
                "render_generative_design was not found."
            )

    except Exception as exc:

        st.error(
            "The Generative Design module could not be loaded."
        )

        with st.expander(
            "Complete import traceback",
            expanded=True,
        ):

            st.code(
                traceback.format_exc(),
                language="text",
            )

        return

    try:

        renderer()

    except Exception:

        st.error(
            "Generative Design encountered an error."
        )

        with st.expander(
            "Complete renderer traceback",
            expanded=True,
        ):

            st.code(
                traceback.format_exc(),
                language="text",
            )


# ============================================================
# SITE PLANNING
# ============================================================

def render_site_planning_registered() -> None:
    """
    Zero-argument Streamlit adapter.

    Existing domain contract:

        render_site_planning(service)

    Application-shell contract:

        renderer()

    The adapter creates the repository and service and then
    passes the synchronous service to the UI.

    Existing asynchronous service methods remain untouched.
    """

    st.title(
        "Site Planning"
    )

    try:

        from architecture.site_planning.repository import (
            SitePlanningRepository,
        )

        from architecture.site_planning.service import (
            SitePlanningService,
        )

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

            st.code(
                traceback.format_exc(),
                language="text",
            )

        return

    try:

        repository = SitePlanningRepository()

        service = SitePlanningService(
            repository
        )

        render_site_planning(
            service
        )

    except Exception as exc:

        st.error(
            "Site Planning could not be rendered."
        )

        with st.expander(
            "Complete renderer traceback",
            expanded=True,
        ):

            st.code(
                traceback.format_exc(),
                language="text",
            )


# ============================================================
# MODULE DEFINITIONS
# ============================================================

def module(
    label: str,
    route: str,
    domain: str,
    description: str = "",
    renderer_module: str | None = None,
    renderer_function: str | None = None,
) -> ModuleDefinition:

    return ModuleDefinition(
        label=label,
        route=route,
        domain=domain,
        description=description,
        renderer_module=renderer_module,
        renderer_function=renderer_function,
        implemented=(
            renderer_module is not None
            and renderer_function is not None
        ),
    )


# ============================================================
# PROJECTS
# ============================================================

PROJECT_MODULES = [

    module(
        "Projects",
        "projects",
        "Projects",
        "Project lifecycle and project records.",
    ),

    module(
        "Approvals",
        "project_approvals",
        "Projects",
        "Project approvals and authorization workflows.",
    ),

    module(
        "Revisions",
        "project_revisions",
        "Projects",
        "Project revisions and design history.",
    ),

    module(
        "Workflows",
        "project_workflows",
        "Projects",
        "Project workflow orchestration.",
    ),

    module(
        "Governance",
        "project_governance",
        "Projects",
        "Project governance and controls.",
    ),
]


# ============================================================
# ARCHITECTURE
# ============================================================

ARCHITECTURE_MODULES = [

    module(
        "Zoning",
        "architecture_zoning",
        "Architecture",
        "Planning controls, setbacks, coverage and zoning constraints.",
        "architecture.zoning.ui",
        "render_zoning",
    ),

    module(
        "Site Planning",
        "architecture_site_planning",
        "Architecture",
        "Site organization and development planning.",
    ),

    module(
        "Floor Planning",
        "architecture_floor_planning",
        "Architecture",
        "Floor layouts and spatial planning.",
        "architecture.floor_planning.ui",
        "render_floor_planning",
    ),

    module(
        "Room Programming",
        "architecture_room_programming",
        "Architecture",
        "Room requirements, areas and adjacencies.",
        "architecture.room_programming.ui",
        "render_room_programming",
    ),

    module(
        "Compliance",
        "architecture_compliance",
        "Architecture",
        "Regulatory and design compliance constraints.",
        "architecture.compliance.ui",
        "render_compliance",
    ),

    module(
        "Generative Design",
        "architecture_generative_design",
        "Architecture",
        "Constraint-driven design generation and ranking.",
    ),
]


# ============================================================
# STRUCTURAL
# ============================================================

STRUCTURAL_MODULES = [

    module(
        "Eurocode EN 1990",
        "structural_en1990",
        "Structural",
        "Basis of structural design.",
    ),

    module(
        "Eurocode EN 1991",
        "structural_en1991",
        "Structural",
        "Actions on structures.",
    ),

    module(
        "Eurocode EN 1992",
        "structural_en1992",
        "Structural",
        "Design of concrete structures.",
    ),

    module(
        "Eurocode EN 1993",
        "structural_en1993",
        "Structural",
        "Design of steel structures.",
    ),

    module(
        "Eurocode EN 1995",
        "structural_en1995",
        "Structural",
        "Design of timber structures.",
    ),

    module(
        "Eurocode EN 1997",
        "structural_en1997",
        "Structural",
        "Geotechnical design.",
    ),

    module(
        "Eurocode EN 1998",
        "structural_en1998",
        "Structural",
        "Earthquake-resistant design.",
    ),

    module(
        "Beam Design",
        "structural_beams",
        "Structural",
        "Structural beam analysis and design.",
    ),

    module(
        "Column Design",
        "structural_columns",
        "Structural",
        "Structural column analysis and design.",
    ),

    module(
        "Slab Design",
        "structural_slabs",
        "Structural",
        "Structural slab analysis and design.",
    ),

    module(
        "Foundation Design",
        "structural_foundations",
        "Structural",
        "Foundation analysis and design.",
    ),

    module(
        "Retaining Walls",
        "structural_retaining_walls",
        "Structural",
        "Retaining wall analysis and design.",
    ),

    module(
        "Steel Connections",
        "structural_steel_connections",
        "Structural",
        "Steel connection design.",
    ),

    module(
        "Finite Element Analysis",
        "structural_fea",
        "Structural",
        "Finite element analysis workflows.",
    ),
]


# ============================================================
# BIM
# ============================================================

BIM_MODULES = [

    module(
        "Buildings",
        "bim_buildings",
        "BIM",
        "BIM building information.",
    ),

    module(
        "Storeys",
        "bim_storeys",
        "BIM",
        "Building storeys and levels.",
    ),

    module(
        "Spaces",
        "bim_spaces",
        "BIM",
        "BIM spaces and spatial entities.",
    ),

    module(
        "Elements",
        "bim_elements",
        "BIM",
        "Building elements and components.",
    ),

    module(
        "IFC",
        "bim_ifc",
        "BIM",
        "Industry Foundation Classes workflows.",
    ),

    module(
        "COBie",
        "bim_cobie",
        "BIM",
        "Construction Operations Building information exchange.",
    ),

    module(
        "BIM Digital Twin",
        "bim_digital_twin",
        "BIM",
        "BIM-connected digital twin.",
    ),
]


# ============================================================
# MEP
# ============================================================

MEP_MODULES = [

    module(
        "HVAC",
        "mep_hvac",
        "MEP",
        "Heating, ventilation and air conditioning.",
    ),

    module(
        "Ventilation",
        "mep_ventilation",
        "MEP",
        "Ventilation analysis and design.",
    ),

    module(
        "Chilled Water",
        "mep_chilled_water",
        "MEP",
        "Chilled water system design.",
    ),

    module(
        "Energy Simulation",
        "mep_energy",
        "MEP",
        "Building energy simulation.",
    ),

    module(
        "Electrical Load Analysis",
        "mep_load_analysis",
        "MEP",
        "Electrical load calculations.",
    ),

    module(
        "Transformers",
        "mep_transformers",
        "MEP",
        "Transformer sizing and analysis.",
    ),

    module(
        "Generators",
        "mep_generators",
        "MEP",
        "Generator systems.",
    ),

    module(
        "Cable Sizing",
        "mep_cable_sizing",
        "MEP",
        "Electrical cable sizing.",
    ),

    module(
        "Solar PV",
        "mep_solar_pv",
        "MEP",
        "Solar photovoltaic system design.",
    ),

    module(
        "Water Supply",
        "mep_water_supply",
        "MEP",
        "Water supply system design.",
    ),

    module(
        "Drainage",
        "mep_drainage",
        "MEP",
        "Drainage system design.",
    ),

    module(
        "Stormwater",
        "mep_stormwater",
        "MEP",
        "Stormwater management.",
    ),

    module(
        "Sewer Networks",
        "mep_sewer",
        "MEP",
        "Sewer network design.",
    ),

    module(
        "Firefighting",
        "mep_firefighting",
        "MEP",
        "Firefighting systems.",
    ),
]


# ============================================================
# COSTING
# ============================================================

COSTING_MODULES = [

    module(
        "BOQ",
        "costing_boq",
        "Costing",
        "Bills of quantities.",
    ),

    module(
        "Quantity Takeoff",
        "costing_quantity_takeoff",
        "Costing",
        "Automated quantity takeoff.",
    ),

    module(
        "Procurement",
        "costing_procurement",
        "Costing",
        "Construction procurement costing.",
    ),

    module(
        "Forex",
        "costing_forex",
        "Costing",
        "Foreign exchange costing.",
    ),

    module(
        "Inflation",
        "costing_inflation",
        "Costing",
        "Construction cost inflation.",
    ),

    module(
        "Risk Analysis",
        "costing_risk",
        "Costing",
        "Cost and project risk analysis.",
    ),

    module(
        "Cashflow",
        "costing_cashflow",
        "Costing",
        "Project cashflow forecasting.",
    ),
]


# ============================================================
# CONSTRUCTION
# ============================================================

CONSTRUCTION_MODULES = [

    module(
        "Planning",
        "construction_planning",
        "Construction",
    ),

    module(
        "Scheduling",
        "construction_scheduling",
        "Construction",
    ),

    module(
        "RFIs",
        "construction_rfis",
        "Construction",
    ),

    module(
        "Submittals",
        "construction_submittals",
        "Construction",
    ),

    module(
        "Variations",
        "construction_variations",
        "Construction",
    ),

    module(
        "Snagging",
        "construction_snagging",
        "Construction",
    ),

    module(
        "Progress Tracking",
        "construction_progress",
        "Construction",
    ),

    module(
        "Site Diaries",
        "construction_site_diaries",
        "Construction",
    ),
]


# ============================================================
# DOCUMENTS
# ============================================================

DOCUMENT_MODULES = [

    module(
        "Drawing Management",
        "documents_drawings",
        "Documents",
    ),

    module(
        "Specifications",
        "documents_specifications",
        "Documents",
    ),

    module(
        "Contracts",
        "documents_contracts",
        "Documents",
    ),

    module(
        "Reports",
        "documents_reports",
        "Documents",
    ),

    module(
        "Version Control",
        "documents_versions",
        "Documents",
    ),

    module(
        "Archives",
        "documents_archives",
        "Documents",
    ),
]


# ============================================================
# AI
# ============================================================

AI_MODULES = [

    module(
        "IMAGINE Architect",
        "ai_architect",
        "AI",
    ),

    module(
        "IMAGINE Engineer",
        "ai_engineer",
        "AI",
    ),

    module(
        "IMAGINE MEP",
        "ai_mep",
        "AI",
    ),

    module(
        "IMAGINE QS",
        "ai_qs",
        "AI",
    ),

    module(
        "IMAGINE PM",
        "ai_pm",
        "AI",
    ),

    module(
        "Vector Store",
        "ai_vector_store",
        "AI",
    ),

    module(
        "RAG",
        "ai_rag",
        "AI",
    ),

    module(
        "Prompt Library",
        "ai_prompt_library",
        "AI",
    ),
]


# ============================================================
# ANALYTICS
# ============================================================

ANALYTICS_MODULES = [

    module(
        "Dashboards",
        "analytics_dashboards",
        "Analytics",
    ),

    module(
        "KPIs",
        "analytics_kpis",
        "Analytics",
    ),

    module(
        "Portfolio",
        "analytics_portfolio",
        "Analytics",
    ),

    module(
        "Forecasting",
        "analytics_forecasting",
        "Analytics",
    ),

    module(
        "Reporting",
        "analytics_reporting",
        "Analytics",
    ),
]


# ============================================================
# REGIONAL
# ============================================================

REGIONAL_MODULES = [

    module(
        "Uganda",
        "regional_uganda",
        "Regional",
    ),

    module(
        "Kenya",
        "regional_kenya",
        "Regional",
    ),

    module(
        "Tanzania",
        "regional_tanzania",
        "Regional",
    ),

    module(
        "Rwanda",
        "regional_rwanda",
        "Regional",
    ),

    module(
        "South Sudan",
        "regional_south_sudan",
        "Regional",
    ),

    module(
        "Codes",
        "regional_codes",
        "Regional",
    ),

    module(
        "Zoning Laws",
        "regional_zoning_laws",
        "Regional",
    ),
]


# ============================================================
# INTEGRATIONS
# ============================================================

INTEGRATION_MODULES = [

    module(
        "Microsoft",
        "integration_microsoft",
        "Integrations",
    ),

    module(
        "AutoCAD",
        "integration_autocad",
        "Integrations",
    ),

    module(
        "Revit",
        "integration_revit",
        "Integrations",
    ),

    module(
        "Archicad",
        "integration_archicad",
        "Integrations",
    ),

    module(
        "Tekla",
        "integration_tekla",
        "Integrations",
    ),

    module(
        "IfcOpenShell",
        "integration_ifcopenshell",
        "Integrations",
    ),

    module(
        "ArcGIS",
        "integration_arcgis",
        "Integrations",
    ),

    module(
        "Azure",
        "integration_azure",
        "Integrations",
    ),

    module(
        "Mapbox",
        "integration_mapbox",
        "Integrations",
    ),
]


# ============================================================
# DIGITAL TWIN
# ============================================================

DIGITAL_TWIN_MODULES = [

    module(
        "Assets",
        "digital_twin_assets",
        "Digital Twin",
    ),

    module(
        "Sensors",
        "digital_twin_sensors",
        "Digital Twin",
    ),

    module(
        "Telemetry",
        "digital_twin_telemetry",
        "Digital Twin",
    ),

    module(
        "Energy",
        "digital_twin_energy",
        "Digital Twin",
    ),

    module(
        "Maintenance",
        "digital_twin_maintenance",
        "Digital Twin",
    ),

    module(
        "Predictive AI",
        "digital_twin_predictive_ai",
        "Digital Twin",
    ),
]


# ============================================================
# ALL MODULES
# ============================================================

ALL_MODULES: list[ModuleDefinition] = [

    *PROJECT_MODULES,
    *ARCHITECTURE_MODULES,
    *STRUCTURAL_MODULES,
    *BIM_MODULES,
    *MEP_MODULES,
    *COSTING_MODULES,
    *CONSTRUCTION_MODULES,
    *DOCUMENT_MODULES,
    *AI_MODULES,
    *ANALYTICS_MODULES,
    *REGIONAL_MODULES,
    *INTEGRATION_MODULES,
    *DIGITAL_TWIN_MODULES,
]


# ============================================================
# SPECIAL RENDERERS
# ============================================================

SPECIAL_RENDERERS: dict[
    str,
    RenderFunction,
] = {
    "architecture_site_planning":
        render_site_planning_registered,

    "architecture_generative_design":
        render_generative_design_safe,
}


# ============================================================
# CENTRAL ROUTE REGISTRY
# ============================================================

MODULES_BY_ROUTE: dict[
    str,
    ModuleDefinition,
] = {

    "overview": ModuleDefinition(
        label="Overview",
        route="overview",
        domain="Core",
        description="IMAGINE engineering overview.",
        implemented=True,
    ),

    **{
        item.route: item
        for item in ALL_MODULES
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
# REGISTRY VALIDATION
# ============================================================

def validate_module_registry() -> None:

    routes = list(
        MODULES_BY_ROUTE.keys()
    )

    duplicates = {
        route
        for route in routes
        if routes.count(route) > 1
    }

    if duplicates:

        raise RuntimeError(
            "Duplicate module routes detected: "
            + ", ".join(
                sorted(duplicates)
            )
        )

    required_routes = (
        "overview",
        "architecture_zoning",
        "architecture_site_planning",
        "architecture_floor_planning",
        "architecture_room_programming",
        "architecture_compliance",
        "architecture_generative_design",
        "structural_beams",
        "bim_buildings",
        "mep_hvac",
        "costing_boq",
        "construction_planning",
        "documents_drawings",
        "ai_architect",
        "analytics_dashboards",
        "regional_uganda",
        "integration_revit",
        "digital_twin_assets",
        "system_health",
    )

    missing = [
        route
        for route in required_routes
        if route not in MODULES_BY_ROUTE
    ]

    if missing:

        raise RuntimeError(
            "Required module routes are missing: "
            + ", ".join(missing)
        )


validate_module_registry()


# ============================================================
# SYSTEM HEALTH
# ============================================================

def render_system_health() -> None:

    st.title(
        "System Health"
    )

    st.caption(
        "IMAGINE application and module diagnostics"
    )

    if not HEALTH_AVAILABLE:

        st.error(
            "The IMAGINE health subsystem could not be imported."
        )

        if HEALTH_IMPORT_ERROR:

            with st.expander(
                "Complete health import traceback",
                expanded=True,
            ):

                st.code(
                    "".join(
                        traceback.format_exception(
                            type(HEALTH_IMPORT_ERROR),
                            HEALTH_IMPORT_ERROR,
                            HEALTH_IMPORT_ERROR.__traceback__,
                        )
                    ),
                    language="text",
                )

        return

    try:

        results = run_startup_health_check()

    except Exception as exc:

        st.error(
            "The startup health check failed."
        )

        with st.expander(
            "Complete health-check traceback",
            expanded=True,
        ):

            st.code(
                traceback.format_exc(),
                language="text",
            )

        return

    checked_at = datetime.now(
        timezone.utc
    )

    st.session_state[
        "health_last_checked_at"
    ] = checked_at

    try:

        summary = health_summary(
            results
        )

    except Exception as exc:

        st.error(
            "The health summary could not be generated."
        )

        with st.expander(
            "Complete health-summary traceback",
            expanded=True,
        ):

            st.code(
                traceback.format_exc(),
                language="text",
            )

        return

    all_modules_healthy = all(
        getattr(
            result,
            "status",
            None,
        ) == "ok"
        for result in results
    )

    if all_modules_healthy:

        st.session_state[
            "health_last_successful_at"
        ] = checked_at

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            "**Latest Health Check**"
        )

        st.code(
            checked_at.strftime(
                "%Y-%m-%d %H:%M:%S UTC"
            )
        )

    with col2:

        st.markdown(
            "**Last Successful Check**"
        )

        last_successful = st.session_state.get(
            "health_last_successful_at"
        )

        if last_successful:

            st.code(
                last_successful.strftime(
                    "%Y-%m-%d %H:%M:%S UTC"
                )
            )

        else:

            st.code(
                "No successful check recorded"
            )

    st.divider()

    metric1, metric2, metric3 = st.columns(3)

    with metric1:

        st.metric(
            "Modules Checked",
            summary.get(
                "total",
                0,
            ),
        )

    with metric2:

        st.metric(
            "Healthy",
            summary.get(
                "healthy",
                0,
            ),
        )

    with metric3:

        st.metric(
            "Failed",
            summary.get(
                "failed",
                0,
            ),
        )

    if summary.get(
        "status"
    ) == "healthy":

        st.success(
            "All checked modules imported successfully."
        )

    else:

        st.warning(
            "IMAGINE is running in degraded mode."
        )

    st.divider()

    st.subheader(
        "Module Results"
    )

    for result in results:

        name = getattr(
            result,
            "name",
            "Unknown module",
        )

        status = getattr(
            result,
            "status",
            "unknown",
        )

        path = getattr(
            result,
            "path",
            None,
        )

        error = getattr(
            result,
            "error",
            None,
        )

        traceback_text = getattr(
            result,
            "traceback_text",
            None,
        )

        if status == "ok":

            st.success(
                f"{name}"
            )

            if path:

                st.caption(
                    f"Loaded from: {path}"
                )

        else:

            st.error(
                f"{name}"
            )

            if error:

                st.code(
                    error,
                    language="text",
                )

            if traceback_text:

                with st.expander(
                    "Complete traceback",
                    expanded=True,
                ):

                    st.code(
                        traceback_text,
                        language="text",
                    )

            if path:

                st.caption(
                    f"Loaded from: {path}"
                )

    st.divider()

    st.subheader(
        "Application Shell Import Status"
    )

    for route, status in IMPORT_STATUS.items():

        if status.status == "ok":

            st.success(
                f"{status.label}: loaded"
            )

        elif status.status == "failed":

            st.error(
                f"{status.label}: import failed"
            )

        else:

            st.info(
                f"{status.label}: registered"
            )

    st.divider()

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

    module_definition = MODULES_BY_ROUTE.get(
        route
    )

    if module_definition is None:

        st.error(
            f"Unknown IMAGINE route: {route}"
        )

        return

    special_renderer = SPECIAL_RENDERERS.get(
        route
    )

    if special_renderer is not None:

        try:

            special_renderer()

        except Exception:

            st.error(
                f"{module_definition.label} could not be rendered."
            )

            with st.expander(
                "Complete renderer traceback",
                expanded=True,
            ):

                st.code(
                    traceback.format_exc(),
                    language="text",
                )

        return

    render_registered_module(
        module_definition
    )


# ============================================================
# SESSION STATE
# ============================================================

if "active_route" not in st.session_state:

    st.session_state.active_route = (
        "overview"
    )


# ============================================================
# NAVIGATION HELPER
# ============================================================

def navigation_button(
    item: ModuleDefinition,
) -> None:

    is_active = (
        st.session_state.active_route
        == item.route
    )

    if st.button(
        item.label,
        key=f"nav_{item.route}",
        use_container_width=True,
        type=(
            "primary"
            if is_active
            else "secondary"
        ),
    ):

        st.session_state.active_route = (
            item.route
        )

        st.rerun()


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

    st.caption(
        "NAVIGATION"
    )

    navigation_button(
        MODULES_BY_ROUTE["overview"]
    )

    st.divider()

    navigation_groups = [

        (
            "PROJECTS",
            PROJECT_MODULES,
        ),

        (
            "ARCHITECTURE",
            ARCHITECTURE_MODULES,
        ),

        (
            "STRUCTURAL",
            STRUCTURAL_MODULES,
        ),

        (
            "BIM",
            BIM_MODULES,
        ),

        (
            "MEP",
            MEP_MODULES,
        ),

        (
            "COSTING",
            COSTING_MODULES,
        ),

        (
            "CONSTRUCTION",
            CONSTRUCTION_MODULES,
        ),

        (
            "DOCUMENTS",
            DOCUMENT_MODULES,
        ),

        (
            "AI",
            AI_MODULES,
        ),

        (
            "ANALYTICS",
            ANALYTICS_MODULES,
        ),

        (
            "REGIONAL",
            REGIONAL_MODULES,
        ),

        (
            "INTEGRATIONS",
            INTEGRATION_MODULES,
        ),

        (
            "DIGITAL TWIN",
            DIGITAL_TWIN_MODULES,
        ),
    ]

    for group_name, modules in navigation_groups:

        with st.expander(
            group_name,
            expanded=(
                group_name
                == "ARCHITECTURE"
            ),
        ):

            for item in modules:

                navigation_button(
                    item
                )

    st.divider()

    navigation_button(
        MODULES_BY_ROUTE["system_health"]
    )

    st.divider()

    st.caption(
        "IMAGINE | Generative Architecture & Civil Engine"
    )


# ============================================================
# ROUTE RESOLUTION
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
# ACTIVE MODULE HEADER
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
# RENDER ACTIVE ROUTE
# ============================================================

render_route(
    active_route
)