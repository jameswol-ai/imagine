"""
IMAGINE
Generative Architecture & Civil Engine

Main Streamlit application entry point.

Application shell responsibilities:
    - Navigation
    - Centralized module registry
    - Lazy renderer imports
    - Error isolation
    - Module status
    - Domain routing
    - System health diagnostics

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

from dataclasses import dataclass
from datetime import datetime, timezone
from importlib import import_module
from typing import Any, Callable

import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="IMAGINE",
    page_icon="IMAGINE",
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
    """Definition of a navigable IMAGINE module."""

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
class ModuleStatus:
    """Runtime status for one registered module."""

    route: str
    label: str
    status: str = "not_checked"
    error: str | None = None
    renderer: RenderFunction | None = None


MODULE_STATUS: dict[str, ModuleStatus] = {}


# ============================================================
# SAFE IMPORT
# ============================================================


def safe_import_renderer(
    module: ModuleDefinition,
) -> RenderFunction | None:
    """
    Lazily import a module renderer.

    Import failures are isolated to the individual module.
    The application shell remains operational.
    """

    route = module.route

    status = MODULE_STATUS.setdefault(
        route,
        ModuleStatus(
            route=route,
            label=module.label,
        ),
    )

    if not module.renderer_module:
        status.status = (
            "registered"
            if module.implemented
            else "not_implemented"
        )
        status.error = None
        status.renderer = None
        return None

    if not module.renderer_function:
        status.status = "configuration_error"
        status.error = (
            "Renderer module is configured but "
            "renderer_function is missing."
        )
        status.renderer = None
        return None

    try:
        imported_module = import_module(
            module.renderer_module
        )

        renderer = getattr(
            imported_module,
            module.renderer_function,
            None,
        )

        if not callable(renderer):
            status.status = "configuration_error"

            status.error = (
                f"Renderer function "
                f"{module.renderer_function!r} was not found "
                f"in {module.renderer_module!r}."
            )

            status.renderer = None

            return None

        status.status = "available"
        status.error = None
        status.renderer = renderer

        return renderer

    except Exception as exc:

        status.status = "import_failed"
        status.error = (
            f"{type(exc).__name__}: {exc}"
        )
        status.renderer = None

        return None


# ============================================================
# GENERIC MODULE PLACEHOLDER
# ============================================================


def render_module_placeholder(
    module: ModuleDefinition,
) -> None:
    """Render a safe placeholder for unavailable modules."""

    st.title(module.label)

    if module.description:
        st.caption(module.description)

    status = MODULE_STATUS.get(
        module.route
    )

    st.divider()

    if status is None:
        st.info(
            "This module is registered but has not "
            "yet been checked."
        )

        return

    if status.status == "not_implemented":

        st.info(
            "This module is registered in IMAGINE, "
            "but its interactive interface has not "
            "been implemented yet."
        )

        return

    if status.status == "registered":

        st.info(
            "This module is registered, but no "
            "renderer has been connected yet."
        )

        return

    if status.status == "configuration_error":

        st.error(
            "The module renderer configuration is invalid."
        )

        if status.error:
            st.code(
                status.error,
                language="text",
            )

        return

    if status.status == "import_failed":

        st.error(
            f"{module.label} could not be loaded."
        )

        if status.error:
            st.code(
                status.error,
                language="text",
            )

        st.warning(
            "The module failure is isolated. "
            "The rest of IMAGINE remains available."
        )

        return

    st.info(
        "No interactive renderer is currently available."
    )


# ============================================================
# REGISTERED MODULE RENDERER
# ============================================================


def render_registered_module(
    module: ModuleDefinition,
) -> None:
    """
    Resolve and render a module safely.

    The renderer must have a zero-argument interface:

        renderer()
    """

    renderer = safe_import_renderer(
        module
    )

    if renderer is None:

        render_module_placeholder(
            module
        )

        return

    try:

        renderer()

        MODULE_STATUS[
            module.route
        ].status = "healthy"

    except Exception as exc:

        MODULE_STATUS[
            module.route
        ].status = "render_failed"

        MODULE_STATUS[
            module.route
        ].error = (
            f"{type(exc).__name__}: {exc}"
        )

        st.error(
            f"{module.label} encountered a rendering error."
        )

        st.warning(
            "The application shell is still running."
        )

        with st.expander(
            "Complete renderer traceback",
            expanded=True,
        ):

            st.exception(exc)


# ============================================================
# OVERVIEW
# ============================================================


def render_overview() -> None:
    """Render the IMAGINE application overview."""

    st.title("IMAGINE")

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
            str(
                len(
                    [
                        module
                        for module in ALL_MODULES
                        if module.domain
                        not in {
                            "Projects",
                            "Documents",
                        }
                    ]
                )
            ),
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
        "Projects",
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

    domain_descriptions = [
        (
            "Architecture",
            "Planning, zoning, site planning, "
            "floor planning, room programming, "
            "compliance and generative design.",
        ),
        (
            "Structural",
            "Eurocode-based structural engineering "
            "and analysis.",
        ),
        (
            "BIM",
            "Buildings, storeys, spaces, elements, "
            "IFC and COBie.",
        ),
        (
            "MEP",
            "Mechanical, electrical and plumbing "
            "engineering systems.",
        ),
        (
            "Costing",
            "BOQ, quantity takeoff, procurement, "
            "risk and cashflow.",
        ),
        (
            "Construction",
            "Planning, scheduling, RFIs, submittals, "
            "variations and progress.",
        ),
        (
            "Documents",
            "Drawings, specifications, contracts, "
            "reports and archives.",
        ),
        (
            "Digital Twin",
            "Assets, sensors, telemetry, energy "
            "and predictive maintenance.",
        ),
    ]

    columns = st.columns(4)

    for index, (name, description) in enumerate(
        domain_descriptions
    ):

        with columns[index % 4]:

            st.markdown(
                f"### {name}"
            )

            st.caption(
                description
            )


# ============================================================
# SITE PLANNING ADAPTER
# ============================================================


def render_site_planning_registered() -> None:
    """
    Zero-argument Streamlit adapter for Site Planning.

    The Streamlit registry calls:

        renderer()

    Site Planning internally uses:

        Repository
            ->
        Service
            ->
        UI

    The adapter is deliberately lazy so importing the
    Streamlit shell does not import the database layer.
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

        st.warning(
            "The failure is isolated to Site Planning. "
            "The rest of IMAGINE remains available."
        )

        with st.expander(
            "Complete import traceback",
            expanded=True,
        ):

            st.exception(exc)

        return

    try:

        repository = (
            SitePlanningRepository()
        )

        service = (
            SitePlanningService(
                repository
            )
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

            st.exception(exc)


# ============================================================
# GENERATIVE DESIGN ADAPTER
# ============================================================


def render_generative_design_safe() -> None:
    """Zero-argument adapter for Generative Design."""

    st.title(
        "Generative Design"
    )

    try:

        from architecture.generative_design.ui import (
            render_generative_design,
        )

    except Exception as exc:

        st.error(
            "The Generative Design module could not be loaded."
        )

        with st.expander(
            "Complete import traceback",
            expanded=True,
        ):

            st.exception(exc)

        return

    try:

        render_generative_design()

    except Exception as exc:

        st.error(
            "Generative Design could not be rendered."
        )

        with st.expander(
            "Complete renderer traceback",
            expanded=True,
        ):

            st.exception(exc)


# ============================================================
# MODULE DEFINITIONS
# ============================================================


PROJECT_MODULES = [
    ModuleDefinition(
        label="Projects",
        route="projects",
        domain="Projects",
        description="Project lifecycle and project records.",
    ),
    ModuleDefinition(
        label="Approvals",
        route="project_approvals",
        domain="Projects",
        description="Project approvals and authorization workflows.",
    ),
    ModuleDefinition(
        label="Revisions",
        route="project_revisions",
        domain="Projects",
        description="Project revisions and design history.",
    ),
    ModuleDefinition(
        label="Workflows",
        route="project_workflows",
        domain="Projects",
        description="Project workflow orchestration.",
    ),
    ModuleDefinition(
        label="Governance",
        route="project_governance",
        domain="Projects",
        description="Project governance and controls.",
    ),
]


ARCHITECTURE_MODULES = [
    ModuleDefinition(
        label="Zoning",
        route="architecture_zoning",
        domain="Architecture",
        description=(
            "Planning controls, setbacks, coverage "
            "and zoning constraints."
        ),
        renderer_module="architecture.zoning.ui",
        renderer_function="render_zoning",
        implemented=True,
    ),
    ModuleDefinition(
        label="Site Planning",
        route="architecture_site_planning",
        domain="Architecture",
        description=(
            "Site organization and development planning."
        ),
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
        description="Room requirements, areas and adjacencies.",
        renderer_module="architecture.room_programming.ui",
        renderer_function="render_room_programming",
        implemented=True,
    ),
    ModuleDefinition(
        label="Compliance",
        route="architecture_compliance",
        domain="Architecture",
        description="Regulatory and design compliance constraints.",
        renderer_module="architecture.compliance.ui",
        renderer_function="render_compliance",
        implemented=True,
    ),
    ModuleDefinition(
        label="Generative Design",
        route="architecture_generative_design",
        domain="Architecture",
        description=(
            "Constraint-driven design generation "
            "and ranking."
        ),
        implemented=True,
    ),
]


STRUCTURAL_MODULES = [
    ModuleDefinition(
        label="Eurocode EN 1990",
        route="structural_en1990",
        domain="Structural",
        description="Basis of structural design.",
    ),
    ModuleDefinition(
        label="Eurocode EN 1991",
        route="structural_en1991",
        domain="Structural",
        description="Actions on structures.",
    ),
    ModuleDefinition(
        label="Eurocode EN 1992",
        route="structural_en1992",
        domain="Structural",
        description="Design of concrete structures.",
    ),
    ModuleDefinition(
        label="Eurocode EN 1993",
        route="structural_en1993",
        domain="Structural",
        description="Design of steel structures.",
    ),
    ModuleDefinition(
        label="Eurocode EN 1995",
        route="structural_en1995",
        domain="Structural",
        description="Design of timber structures.",
    ),
    ModuleDefinition(
        label="Eurocode EN 1997",
        route="structural_en1997",
        domain="Structural",
        description="Geotechnical design.",
    ),
    ModuleDefinition(
        label="Eurocode EN 1998",
        route="structural_en1998",
        domain="Structural",
        description="Earthquake-resistant design.",
    ),
    ModuleDefinition(
        label="Beam Design",
        route="structural_beams",
        domain="Structural",
        description="Structural beam analysis and design.",
    ),
    ModuleDefinition(
        label="Column Design",
        route="structural_columns",
        domain="Structural",
        description="Structural column analysis and design.",
    ),
    ModuleDefinition(
        label="Slab Design",
        route="structural_slabs",
        domain="Structural",
        description="Structural slab analysis and design.",
    ),
    ModuleDefinition(
        label="Foundation Design",
        route="structural_foundations",
        domain="Structural",
        description="Foundation analysis and design.",
    ),
    ModuleDefinition(
        label="Retaining Walls",
        route="structural_retaining_walls",
        domain="Structural",
        description="Retaining wall analysis and design.",
    ),
    ModuleDefinition(
        label="Steel Connections",
        route="structural_steel_connections",
        domain="Structural",
        description="Steel connection design.",
    ),
    ModuleDefinition(
        label="Finite Element Analysis",
        route="structural_fea",
        domain="Structural",
        description="Finite element analysis workflows.",
    ),
]


BIM_MODULES = [
    ModuleDefinition(
        label="Buildings",
        route="bim_buildings",
        domain="BIM",
        description="BIM building information.",
    ),
    ModuleDefinition(
        label="Storeys",
        route="bim_storeys",
        domain="BIM",
        description="Building storeys and levels.",
    ),
    ModuleDefinition(
        label="Spaces",
        route="bim_spaces",
        domain="BIM",
        description="BIM spaces and spatial entities.",
    ),
    ModuleDefinition(
        label="Elements",
        route="bim_elements",
        domain="BIM",
        description="Building elements and components.",
    ),
    ModuleDefinition(
        label="IFC",
        route="bim_ifc",
        domain="BIM",
        description="Industry Foundation Classes workflows.",
    ),
    ModuleDefinition(
        label="COBie",
        route="bim_cobie",
        domain="BIM",
        description="Construction Operations Building information exchange.",
    ),
    ModuleDefinition(
        label="Digital Twin",
        route="bim_digital_twin",
        domain="BIM",
        description="BIM-connected digital twin.",
    ),
]


MEP_MODULES = [
    ModuleDefinition(
        label="HVAC",
        route="mep_hvac",
        domain="MEP",
        description="Heating, ventilation and air conditioning.",
    ),
    ModuleDefinition(
        label="Ventilation",
        route="mep_ventilation",
        domain="MEP",
        description="Ventilation analysis and design.",
    ),
    ModuleDefinition(
        label="Chilled Water",
        route="mep_chilled_water",
        domain="MEP",
        description="Chilled water system design.",
    ),
    ModuleDefinition(
        label="Energy Simulation",
        route="mep_energy",
        domain="MEP",
        description="Building energy simulation.",
    ),
    ModuleDefinition(
        label="Electrical Load Analysis",
        route="mep_load_analysis",
        domain="MEP",
        description="Electrical load calculations.",
    ),
    ModuleDefinition(
        label="Transformers",
        route="mep_transformers",
        domain="MEP",
        description="Transformer sizing and analysis.",
    ),
    ModuleDefinition(
        label="Generators",
        route="mep_generators",
        domain="MEP",
        description="Generator systems.",
    ),
    ModuleDefinition(
        label="Cable Sizing",
        route="mep_cable_sizing",
        domain="MEP",
        description="Electrical cable sizing.",
    ),
    ModuleDefinition(
        label="Solar PV",
        route="mep_solar_pv",
        domain="MEP",
        description="Solar photovoltaic system design.",
    ),
    ModuleDefinition(
        label="Water Supply",
        route="mep_water_supply",
        domain="MEP",
        description="Water supply system design.",
    ),
    ModuleDefinition(
        label="Drainage",
        route="mep_drainage",
        domain="MEP",
        description="Drainage system design.",
    ),
    ModuleDefinition(
        label="Stormwater",
        route="mep_stormwater",
        domain="MEP",
        description="Stormwater management.",
    ),
    ModuleDefinition(
        label="Sewer Networks",
        route="mep_sewer",
        domain="MEP",
        description="Sewer network design.",
    ),
    ModuleDefinition(
        label="Firefighting",
        route="mep_firefighting",
        domain="MEP",
        description="Firefighting systems.",
    ),
]


COSTING_MODULES = [
    ModuleDefinition(
        label="BOQ",
        route="costing_boq",
        domain="Costing",
        description="Bills of quantities.",
    ),
    ModuleDefinition(
        label="Quantity Takeoff",
        route="costing_quantity_takeoff",
        domain="Costing",
        description="Automated quantity takeoff.",
    ),
    ModuleDefinition(
        label="Procurement",
        route="costing_procurement",
        domain="Costing",
        description="Construction procurement costing.",
    ),
    ModuleDefinition(
        label="Forex",
        route="costing_forex",
        domain="Costing",
        description="Foreign exchange costing.",
    ),
    ModuleDefinition(
        label="Inflation",
        route="costing_inflation",
        domain="Costing",
        description="Construction cost inflation.",
    ),
    ModuleDefinition(
        label="Risk Analysis",
        route="costing_risk",
        domain="Costing",
        description="Cost and project risk analysis.",
    ),
    ModuleDefinition(
        label="Cashflow",
        route="costing_cashflow",
        domain="Costing",
        description="Project cashflow forecasting.",
    ),
]


CONSTRUCTION_MODULES = [
    ModuleDefinition(
        label="Planning",
        route="construction_planning",
        domain="Construction",
    ),
    ModuleDefinition(
        label="Scheduling",
        route="construction_scheduling",
        domain="Construction",
    ),
    ModuleDefinition(
        label="RFIs",
        route="construction_rfis",
        domain="Construction",
    ),
    ModuleDefinition(
        label="Submittals",
        route="construction_submittals",
        domain="Construction",
    ),
    ModuleDefinition(
        label="Variations",
        route="construction_variations",
        domain="Construction",
    ),
    ModuleDefinition(
        label="Snagging",
        route="construction_snagging",
        domain="Construction",
    ),
    ModuleDefinition(
        label="Progress Tracking",
        route="construction_progress",
        domain="Construction",
    ),
    ModuleDefinition(
        label="Site Diaries",
        route="construction_site_diaries",
        domain="Construction",
    ),
]


DOCUMENT_MODULES = [
    ModuleDefinition(
        label="Drawing Management",
        route="documents_drawings",
        domain="Documents",
    ),
    ModuleDefinition(
        label="Specifications",
        route="documents_specifications",
        domain="Documents",
    ),
    ModuleDefinition(
        label="Contracts",
        route="documents_contracts",
        domain="Documents",
    ),
    ModuleDefinition(
        label="Reports",
        route="documents_reports",
        domain="Documents",
    ),
    ModuleDefinition(
        label="Version Control",
        route="documents_versions",
        domain="Documents",
    ),
    ModuleDefinition(
        label="Archives",
        route="documents_archives",
        domain="Documents",
    ),
]


AI_MODULES = [
    ModuleDefinition(
        label="IMAGINE Architect",
        route="ai_architect",
        domain="AI",
    ),
    ModuleDefinition(
        label="IMAGINE Engineer",
        route="ai_engineer",
        domain="AI",
    ),
    ModuleDefinition(
        label="IMAGINE MEP",
        route="ai_mep",
        domain="AI",
    ),
    ModuleDefinition(
        label="IMAGINE QS",
        route="ai_qs",
        domain="AI",
    ),
    ModuleDefinition(
        label="IMAGINE PM",
        route="ai_pm",
        domain="AI",
    ),
    ModuleDefinition(
        label="Vector Store",
        route="ai_vector_store",
        domain="AI",
    ),
    ModuleDefinition(
        label="RAG",
        route="ai_rag",
        domain="AI",
    ),
    ModuleDefinition(
        label="Prompt Library",
        route="ai_prompt_library",
        domain="AI",
    ),
]


ANALYTICS_MODULES = [
    ModuleDefinition(
        label="Dashboards",
        route="analytics_dashboards",
        domain="Analytics",
    ),
    ModuleDefinition(
        label="KPIs",
        route="analytics_kpis",
        domain="Analytics",
    ),
    ModuleDefinition(
        label="Portfolio",
        route="analytics_portfolio",
        domain="Analytics",
    ),
    ModuleDefinition(
        label="Forecasting",
        route="analytics_forecasting",
        domain="Analytics",
    ),
    ModuleDefinition(
        label="Reporting",
        route="analytics_reporting",
        domain="Analytics",
    ),
]


REGIONAL_MODULES = [
    ModuleDefinition(
        label="Uganda",
        route="regional_uganda",
        domain="Regional",
    ),
    ModuleDefinition(
        label="Kenya",
        route="regional_kenya",
        domain="Regional",
    ),
    ModuleDefinition(
        label="Tanzania",
        route="regional_tanzania",
        domain="Regional",
    ),
    ModuleDefinition(
        label="Rwanda",
        route="regional_rwanda",
        domain="Regional",
    ),
    ModuleDefinition(
        label="South Sudan",
        route="regional_south_sudan",
        domain="Regional",
    ),
    ModuleDefinition(
        label="Codes",
        route="regional_codes",
        domain="Regional",
    ),
    ModuleDefinition(
        label="Zoning Laws",
        route="regional_zoning_laws",
        domain="Regional",
    ),
]


INTEGRATION_MODULES = [
    ModuleDefinition(
        label="Microsoft",
        route="integration_microsoft",
        domain="Integrations",
    ),
    ModuleDefinition(
        label="AutoCAD",
        route="integration_autocad",
        domain="Integrations",
    ),
    ModuleDefinition(
        label="Revit",
        route="integration_revit",
        domain="Integrations",
    ),
    ModuleDefinition(
        label="Archicad",
        route="integration_archicad",
        domain="Integrations",
    ),
    ModuleDefinition(
        label="Tekla",
        route="integration_tekla",
        domain="Integrations",
    ),
    ModuleDefinition(
        label="IfcOpenShell",
        route="integration_ifcopenshell",
        domain="Integrations",
    ),
    ModuleDefinition(
        label="ArcGIS",
        route="integration_arcgis",
        domain="Integrations",
    ),
    ModuleDefinition(
        label="Azure",
        route="integration_azure",
        domain="Integrations",
    ),
    ModuleDefinition(
        label="Mapbox",
        route="integration_mapbox",
        domain="Integrations",
    ),
]


DIGITAL_TWIN_MODULES = [
    ModuleDefinition(
        label="Assets",
        route="digital_twin_assets",
        domain="Digital Twin",
    ),
    ModuleDefinition(
        label="Sensors",
        route="digital_twin_sensors",
        domain="Digital Twin",
    ),
    ModuleDefinition(
        label="Telemetry",
        route="digital_twin_telemetry",
        domain="Digital Twin",
    ),
    ModuleDefinition(
        label="Energy",
        route="digital_twin_energy",
        domain="Digital Twin",
    ),
    ModuleDefinition(
        label="Maintenance",
        route="digital_twin_maintenance",
        domain="Digital Twin",
    ),
    ModuleDefinition(
        label="Predictive AI",
        route="digital_twin_predictive_ai",
        domain="Digital Twin",
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
# ROUTE REGISTRY
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
# REGISTRY VALIDATION
# ============================================================


def validate_module_registry() -> None:
    """Validate all application routes."""

    required_routes = {
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
    }

    missing = sorted(
        required_routes
        - set(MODULES_BY_ROUTE)
    )

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
    """
    Run application health diagnostics without allowing
    health-check failures to crash Streamlit.
    """

    st.title("System Health")

    st.caption(
        "IMAGINE application and module diagnostics"
    )

    try:

        from architecture.health import (
            health_summary,
            run_startup_health_check,
        )

    except Exception as exc:

        st.error(
            "The health subsystem could not be imported."
        )

        with st.expander(
            "Complete health import traceback",
            expanded=True,
        ):
            st.exception(exc)

        return

    try:

        results = run_startup_health_check()

    except Exception as exc:

        st.error(
            "The system health check failed."
        )

        with st.expander(
            "Complete health-check traceback",
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
            st.exception(exc)

        return

    all_modules_healthy = all(
        result.status == "ok"
        for result in results
    )

    if all_modules_healthy:

        st.session_state[
            "health_last_successful_at"
        ] = checked_at

    timestamp_col1, timestamp_col2 = (
        st.columns(2)
    )

    with timestamp_col1:

        st.markdown(
            "**Latest Health Check**"
        )

        st.code(
            checked_at.strftime(
                "%Y-%m-%d %H:%M:%S UTC"
            )
        )

    with timestamp_col2:

        st.markdown(
            "**Last Successful Check**"
        )

        last_successful = (
            st.session_state.get(
                "health_last_successful_at"
            )
        )

        st.code(
            (
                last_successful.strftime(
                    "%Y-%m-%d %H:%M:%S UTC"
                )
                if last_successful
                else "No successful check recorded"
            )
        )

    st.divider()

    metric1, metric2, metric3 = (
        st.columns(3)
    )

    with metric1:
        st.metric(
            "Modules Checked",
            summary["total"],
        )

    with metric2:
        st.metric(
            "Healthy",
            summary["healthy"],
        )

    with metric3:
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

    st.subheader(
        "Module Results"
    )

    for result in results:

        if result.status == "ok":

            st.success(
                f"{result.name}"
            )

            if result.path:

                st.caption(
                    f"Loaded from: {result.path}"
                )

        else:

            st.error(
                f"{result.name}"
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
    """
    Resolve and safely render an application route.
    """

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

    special_renderer = (
        SPECIAL_RENDERERS.get(route)
    )

    if special_renderer is not None:

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
# NAVIGATION HELPER
# ============================================================


def navigate(
    route: str,
) -> None:
    """Set the active route and rerun Streamlit."""

    st.session_state[
        "active_route"
    ] = route

    st.rerun()


# ============================================================
# NAVIGATION GROUP
# ============================================================


def render_navigation_group(
    title: str,
    modules: list[ModuleDefinition],
    expanded: bool = False,
) -> None:
    """Render an interactive sidebar navigation group."""

    with st.expander(
        title,
        expanded=expanded,
    ):

        for module in modules:

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

                navigate(
                    module.route
                )


# ============================================================
# SESSION STATE
# ============================================================


if "active_route" not in st.session_state:

    st.session_state[
        "active_route"
    ] = "overview"


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

    # --------------------------------------------------------
    # Overview
    # --------------------------------------------------------

    overview_active = (
        st.session_state.active_route
        == "overview"
    )

    if st.button(
        "Overview",
        key="nav_overview",
        use_container_width=True,
        type=(
            "primary"
            if overview_active
            else "secondary"
        ),
    ):

        navigate(
            "overview"
        )

    # --------------------------------------------------------
    # Domain groups
    # --------------------------------------------------------

    render_navigation_group(
        "PROJECTS",
        PROJECT_MODULES,
    )

    render_navigation_group(
        "ARCHITECTURE",
        ARCHITECTURE_MODULES,
        expanded=True,
    )

    render_navigation_group(
        "STRUCTURAL",
        STRUCTURAL_MODULES,
    )

    render_navigation_group(
        "BIM",
        BIM_MODULES,
    )

    render_navigation_group(
        "MEP",
        MEP_MODULES,
    )

    render_navigation_group(
        "COSTING",
        COSTING_MODULES,
    )

    render_navigation_group(
        "CONSTRUCTION",
        CONSTRUCTION_MODULES,
    )

    render_navigation_group(
        "DOCUMENTS",
        DOCUMENT_MODULES,
    )

    render_navigation_group(
        "AI",
        AI_MODULES,
    )

    render_navigation_group(
        "ANALYTICS",
        ANALYTICS_MODULES,
    )

    render_navigation_group(
        "REGIONAL",
        REGIONAL_MODULES,
    )

    render_navigation_group(
        "INTEGRATIONS",
        INTEGRATION_MODULES,
    )

    render_navigation_group(
        "DIGITAL TWIN",
        DIGITAL_TWIN_MODULES,
    )

    st.divider()

    health_active = (
        st.session_state.active_route
        == "system_health"
    )

    if st.button(
        "System Health",
        key="nav_system_health",
        use_container_width=True,
        type=(
            "primary"
            if health_active
            else "secondary"
        ),
    ):

        navigate(
            "system_health"
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

    st.session_state[
        "active_route"
    ] = active_route


# ============================================================
# ACTIVE MODULE HEADER
# ============================================================


active_module = MODULES_BY_ROUTE.get(
    active_route
)

if active_module is not None:

    if active_route not in {
        "overview",
        "system_health",
    }:

        st.caption(
            f"IMAGINE | {active_module.domain}"
        )


# ============================================================
# RENDER ACTIVE ROUTE
# ============================================================


render_route(
    active_route
)