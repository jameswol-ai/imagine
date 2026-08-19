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

from architecture.health import (
    health_summary,
    run_startup_health_check,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="IMAGINE",
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

    renderer_module and renderer_function identify a standard
    zero-argument UI renderer.

    Special modules can be handled through SPECIAL_RENDERERS.
    """

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
    module_name: str,
    function_name: str,
) -> RenderFunction | None:
    """
    Safely import a renderer.

    Any import failure returns None.

    The application shell must never fail simply because one
    optional domain module has an import problem.
    """

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
# SAFE RENDERER EXECUTION
# ============================================================


def _render_with_error_isolation(
    module: ModuleDefinition,
    renderer: RenderFunction,
) -> None:
    """
    Execute a renderer without allowing its exception to
    terminate the application shell.
    """

    try:

        renderer()

    except Exception as exc:

        st.error(
            f"{module.label} could not be rendered."
        )

        st.warning(
            "The application shell is still running. "
            "Use System Health to inspect module failures."
        )

        with st.expander(
            "Complete renderer traceback",
            expanded=True,
        ):

            st.exception(exc)


# ============================================================
# PLACEHOLDER RENDERER
# ============================================================


def render_module_placeholder(
    module: ModuleDefinition,
) -> None:
    """
    Render a safe placeholder for a registered module that
    does not yet expose a UI renderer.
    """

    st.title(
        module.label
    )

    if module.description:

        st.caption(
            module.description
        )

    st.info(
        f"{module.label} is registered in IMAGINE, "
        "but its interactive interface is not available yet."
    )

    st.divider()

    st.subheader(
        "Module Status"
    )

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
            "Registry",
            "Registered",
        )


# ============================================================
# STANDARD MODULE RENDERER
# ============================================================


def render_registered_module(
    module: ModuleDefinition,
) -> None:
    """
    Resolve and render a standard registered module.

    Import failures and renderer failures are isolated.
    """

    if not module.renderer_module:

        render_module_placeholder(
            module
        )

        return

    if not module.renderer_function:

        render_module_placeholder(
            module
        )

        return

    try:

        renderer = import_module(
            module.renderer_module
        )

    except Exception as exc:

        st.title(
            module.label
        )

        if module.description:

            st.caption(
                module.description
            )

        st.error(
            f"The {module.label} module could not be loaded."
        )

        with st.expander(
            "Complete import traceback",
            expanded=True,
        ):

            st.exception(exc)

        return

    function = getattr(
        renderer,
        module.renderer_function,
        None,
    )

    if not callable(function):

        st.title(
            module.label
        )

        st.error(
            f"{module.renderer_module} does not expose "
            f"{module.renderer_function}()."
        )

        return

    _render_with_error_isolation(
        module,
        function,
    )


# ============================================================
# OVERVIEW
# ============================================================


def render_overview() -> None:
    """
    Render the IMAGINE application overview.
    """

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
            str(
                len(ALL_MODULES)
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
                    min-height:70px;
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
            "BOQ, quantities, procurement and cost analysis.",
        ),
        (
            "Construction",
            "Planning, scheduling and site execution.",
        ),
        (
            "Documents",
            "Drawings, specifications and contracts.",
        ),
        (
            "AI",
            "AI engineering and knowledge systems.",
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

    st.divider()

    st.subheader(
        "System Status"
    )

    status_col1, status_col2 = st.columns(2)

    with status_col1:

        st.success(
            "IMAGINE application shell is running."
        )

    with status_col2:

        st.info(
            "Domain modules are independently isolated."
        )


# ============================================================
# GENERATIVE DESIGN ADAPTER
# ============================================================


def render_generative_design_safe() -> None:
    """
    Zero-argument adapter for Generative Design.
    """

    module = ModuleDefinition(
        label="Generative Design",
        route="architecture_generative_design",
        domain="Architecture",
        description=(
            "Constraint-driven design generation and ranking."
        ),
    )

    try:

        imported_module = import_module(
            "architecture.generative_design.ui"
        )

    except Exception as exc:

        st.title(
            module.label
        )

        st.error(
            "The Generative Design module could not be loaded."
        )

        with st.expander(
            "Complete import traceback",
            expanded=True,
        ):

            st.exception(exc)

        return

    renderer = getattr(
        imported_module,
        "render_generative_design",
        None,
    )

    if not callable(renderer):

        st.title(
            module.label
        )

        st.error(
            "architecture.generative_design.ui does not "
            "expose render_generative_design()."
        )

        return

    _render_with_error_isolation(
        module,
        renderer,
    )


# ============================================================
# SITE PLANNING ADAPTER
# ============================================================


def render_site_planning_registered() -> None:
    """
    Zero-argument Streamlit adapter for Site Planning.

    Streamlit registry contract:

        renderer()

    Site Planning domain contract:

        repository
            |
            v
        service
            |
            v
        UI

    The service itself exposes synchronous adapter methods
    while preserving its existing asynchronous API methods.
    """

    module = ModuleDefinition(
        label="Site Planning",
        route="architecture_site_planning",
        domain="Architecture",
        description=(
            "Site organization and development planning."
        ),
    )

    st.title(
        module.label
    )

    st.caption(
        module.description
    )

    # --------------------------------------------------------
    # Import repository
    # --------------------------------------------------------

    try:

        repository_module = import_module(
            "architecture.site_planning.repository"
        )

        SitePlanningRepository = getattr(
            repository_module,
            "SitePlanningRepository",
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

    # --------------------------------------------------------
    # Import service
    # --------------------------------------------------------

    try:

        service_module = import_module(
            "architecture.site_planning.service"
        )

        SitePlanningService = getattr(
            service_module,
            "SitePlanningService",
        )

    except Exception as exc:

        st.error(
            "The Site Planning service could not be loaded."
        )

        with st.expander(
            "Complete service import traceback",
            expanded=True,
        ):

            st.exception(exc)

        return

    # --------------------------------------------------------
    # Import UI
    # --------------------------------------------------------

    try:

        ui_module = import_module(
            "architecture.site_planning.ui"
        )

        render_site_planning = getattr(
            ui_module,
            "render_site_planning",
        )

    except Exception as exc:

        st.error(
            "The Site Planning UI could not be loaded."
        )

        with st.expander(
            "Complete UI import traceback",
            expanded=True,
        ):

            st.exception(exc)

        return

    # --------------------------------------------------------
    # Validate imported symbols
    # --------------------------------------------------------

    if not callable(
        SitePlanningRepository
    ):

        st.error(
            "SitePlanningRepository is not callable."
        )

        return

    if not callable(
        SitePlanningService
    ):

        st.error(
            "SitePlanningService is not callable."
        )

        return

    if not callable(
        render_site_planning
    ):

        st.error(
            "render_site_planning is not callable."
        )

        return

    # --------------------------------------------------------
    # Construct repository
    # --------------------------------------------------------

    try:

        repository = (
            SitePlanningRepository()
        )

    except Exception as exc:

        st.error(
            "Site Planning repository could not be created."
        )

        with st.expander(
            "Complete repository traceback",
            expanded=True,
        ):

            st.exception(exc)

        return

    # --------------------------------------------------------
    # Construct service
    # --------------------------------------------------------

    try:

        service = SitePlanningService(
            repository
        )

    except Exception as exc:

        st.error(
            "Site Planning service could not be created."
        )

        with st.expander(
            "Complete service traceback",
            expanded=True,
        ):

            st.exception(exc)

        return

    # --------------------------------------------------------
    # Render UI
    # --------------------------------------------------------

    try:

        render_site_planning(
            service
        )

    except Exception as exc:

        st.error(
            "Site Planning could not be rendered."
        )

        with st.expander(
            "Complete Site Planning renderer traceback",
            expanded=True,
        ):

            st.exception(exc)


# ============================================================
# PROJECT MODULES
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


# ============================================================
# ARCHITECTURE MODULES
# ============================================================


ARCHITECTURE_MODULES = [

    ModuleDefinition(
        label="Zoning",
        route="architecture_zoning",
        domain="Architecture",
        description=(
            "Planning controls, setbacks, coverage and zoning constraints."
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
        description=(
            "Room requirements, areas and adjacencies."
        ),
        renderer_module="architecture.room_programming.ui",
        renderer_function="render_room_programming",
        implemented=True,
    ),

    ModuleDefinition(
        label="Compliance",
        route="architecture_compliance",
        domain="Architecture",
        description=(
            "Regulatory and design compliance constraints."
        ),
        renderer_module="architecture.compliance.ui",
        renderer_function="render_compliance",
        implemented=True,
    ),

    ModuleDefinition(
        label="Generative Design",
        route="architecture_generative_design",
        domain="Architecture",
        description=(
            "Constraint-driven design generation and ranking."
        ),
        implemented=True,
    ),
]


# ============================================================
# STRUCTURAL MODULES
# ============================================================


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


# ============================================================
# BIM MODULES
# ============================================================


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
        description=(
            "Construction Operations Building information exchange."
        ),
    ),

    ModuleDefinition(
        label="BIM Digital Twin",
        route="bim_digital_twin",
        domain="BIM",
        description="BIM-connected digital twin.",
    ),
]


# ============================================================
# MEP MODULES
# ============================================================


MEP_MODULES = [

    ModuleDefinition(
        label="HVAC",
        route="mep_hvac",
        domain="MEP",
        description=(
            "Heating, ventilation and air conditioning."
        ),
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


# ============================================================
# COSTING MODULES
# ============================================================


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


# ============================================================
# CONSTRUCTION MODULES
# ============================================================


CONSTRUCTION_MODULES = [

    ModuleDefinition(
        label="Planning",
        route="construction_planning",
        domain="Construction",
        description="Construction planning.",
    ),

    ModuleDefinition(
        label="Scheduling",
        route="construction_scheduling",
        domain="Construction",
        description="Construction scheduling.",
    ),

    ModuleDefinition(
        label="RFIs",
        route="construction_rfis",
        domain="Construction",
        description="Requests for information.",
    ),

    ModuleDefinition(
        label="Submittals",
        route="construction_submittals",
        domain="Construction",
        description="Construction submittals.",
    ),

    ModuleDefinition(
        label="Variations",
        route="construction_variations",
        domain="Construction",
        description="Contract and construction variations.",
    ),

    ModuleDefinition(
        label="Snagging",
        route="construction_snagging",
        domain="Construction",
        description="Snagging and defect tracking.",
    ),

    ModuleDefinition(
        label="Progress Tracking",
        route="construction_progress",
        domain="Construction",
        description="Construction progress tracking.",
    ),

    ModuleDefinition(
        label="Site Diaries",
        route="construction_site_diaries",
        domain="Construction",
        description="Construction site diaries.",
    ),
]


# ============================================================
# DOCUMENT MODULES
# ============================================================


DOCUMENT_MODULES = [

    ModuleDefinition(
        label="Drawing Management",
        route="documents_drawings",
        domain="Documents",
        description="Drawing management.",
    ),

    ModuleDefinition(
        label="Specifications",
        route="documents_specifications",
        domain="Documents",
        description="Technical specifications.",
    ),

    ModuleDefinition(
        label="Contracts",
        route="documents_contracts",
        domain="Documents",
        description="Project contracts.",
    ),

    ModuleDefinition(
        label="Reports",
        route="documents_reports",
        domain="Documents",
        description="Project reports.",
    ),

    ModuleDefinition(
        label="Version Control",
        route="documents_versions",
        domain="Documents",
        description="Document version control.",
    ),

    ModuleDefinition(
        label="Archives",
        route="documents_archives",
        domain="Documents",
        description="Project document archives.",
    ),
]


# ============================================================
# AI MODULES
# ============================================================


AI_MODULES = [

    ModuleDefinition(
        label="IMAGINE Architect",
        route="ai_architect",
        domain="AI",
        description="AI-assisted architectural design.",
    ),

    ModuleDefinition(
        label="IMAGINE Engineer",
        route="ai_engineer",
        domain="AI",
        description="AI-assisted engineering.",
    ),

    ModuleDefinition(
        label="IMAGINE MEP",
        route="ai_mep",
        domain="AI",
        description="AI-assisted MEP engineering.",
    ),

    ModuleDefinition(
        label="IMAGINE QS",
        route="ai_qs",
        domain="AI",
        description="AI-assisted quantity surveying.",
    ),

    ModuleDefinition(
        label="IMAGINE PM",
        route="ai_pm",
        domain="AI",
        description="AI-assisted project management.",
    ),

    ModuleDefinition(
        label="Vector Store",
        route="ai_vector_store",
        domain="AI",
        description="AI vector storage.",
    ),

    ModuleDefinition(
        label="RAG",
        route="ai_rag",
        domain="AI",
        description="Retrieval augmented generation.",
    ),

    ModuleDefinition(
        label="Prompt Library",
        route="ai_prompt_library",
        domain="AI",
        description="Reusable engineering prompts.",
    ),
]


# ============================================================
# ANALYTICS MODULES
# ============================================================


ANALYTICS_MODULES = [

    ModuleDefinition(
        label="Dashboards",
        route="analytics_dashboards",
        domain="Analytics",
        description="Analytics dashboards.",
    ),

    ModuleDefinition(
        label="KPIs",
        route="analytics_kpis",
        domain="Analytics",
        description="Engineering KPIs.",
    ),

    ModuleDefinition(
        label="Portfolio",
        route="analytics_portfolio",
        domain="Analytics",
        description="Project portfolio analytics.",
    ),

    ModuleDefinition(
        label="Forecasting",
        route="analytics_forecasting",
        domain="Analytics",
        description="Engineering and project forecasting.",
    ),

    ModuleDefinition(
        label="Reporting",
        route="analytics_reporting",
        domain="Analytics",
        description="Analytics reporting.",
    ),
]


# ============================================================
# REGIONAL MODULES
# ============================================================


REGIONAL_MODULES = [

    ModuleDefinition(
        label="Uganda",
        route="regional_uganda",
        domain="Regional",
        description="Uganda engineering and regulatory context.",
    ),

    ModuleDefinition(
        label="Kenya",
        route="regional_kenya",
        domain="Regional",
        description="Kenya engineering and regulatory context.",
    ),

    ModuleDefinition(
        label="Tanzania",
        route="regional_tanzania",
        domain="Regional",
        description="Tanzania engineering and regulatory context.",
    ),

    ModuleDefinition(
        label="Rwanda",
        route="regional_rwanda",
        domain="Regional",
        description="Rwanda engineering and regulatory context.",
    ),

    ModuleDefinition(
        label="South Sudan",
        route="regional_south_sudan",
        domain="Regional",
        description="South Sudan engineering and regulatory context.",
    ),

    ModuleDefinition(
        label="Codes",
        route="regional_codes",
        domain="Regional",
        description="Regional engineering codes.",
    ),

    ModuleDefinition(
        label="Zoning Laws",
        route="regional_zoning_laws",
        domain="Regional",
        description="Regional zoning legislation.",
    ),
]


# ============================================================
# INTEGRATION MODULES
# ============================================================


INTEGRATION_MODULES = [

    ModuleDefinition(
        label="Microsoft",
        route="integration_microsoft",
        domain="Integrations",
        description="Microsoft integrations.",
    ),

    ModuleDefinition(
        label="AutoCAD",
        route="integration_autocad",
        domain="Integrations",
        description="AutoCAD integration.",
    ),

    ModuleDefinition(
        label="Revit",
        route="integration_revit",
        domain="Integrations",
        description="Autodesk Revit integration.",
    ),

    ModuleDefinition(
        label="Archicad",
        route="integration_archicad",
        domain="Integrations",
        description="Graphisoft Archicad integration.",
    ),

    ModuleDefinition(
        label="Tekla",
        route="integration_tekla",
        domain="Integrations",
        description="Tekla integration.",
    ),

    ModuleDefinition(
        label="IfcOpenShell",
        route="integration_ifcopenshell",
        domain="Integrations",
        description="IFC processing integration.",
    ),

    ModuleDefinition(
        label="ArcGIS",
        route="integration_arcgis",
        domain="Integrations",
        description="GIS integration.",
    ),

    ModuleDefinition(
        label="Azure",
        route="integration_azure",
        domain="Integrations",
        description="Microsoft Azure integration.",
    ),

    ModuleDefinition(
        label="Mapbox",
        route="integration_mapbox",
        domain="Integrations",
        description="Mapbox mapping integration.",
    ),
]


# ============================================================
# DIGITAL TWIN MODULES
# ============================================================


DIGITAL_TWIN_MODULES = [

    ModuleDefinition(
        label="Assets",
        route="digital_twin_assets",
        domain="Digital Twin",
        description="Digital twin assets.",
    ),

    ModuleDefinition(
        label="Sensors",
        route="digital_twin_sensors",
        domain="Digital Twin",
        description="Digital twin sensors.",
    ),

    ModuleDefinition(
        label="Telemetry",
        route="digital_twin_telemetry",
        domain="Digital Twin",
        description="Digital twin telemetry.",
    ),

    ModuleDefinition(
        label="Energy",
        route="digital_twin_energy",
        domain="Digital Twin",
        description="Digital twin energy monitoring.",
    ),

    ModuleDefinition(
        label="Maintenance",
        route="digital_twin_maintenance",
        domain="Digital Twin",
        description="Digital twin maintenance.",
    ),

    ModuleDefinition(
        label="Predictive AI",
        route="digital_twin_predictive_ai",
        domain="Digital Twin",
        description="Predictive digital twin analytics.",
    ),
]


# ============================================================
# ALL MODULES
# ============================================================


ALL_MODULES: list[
    ModuleDefinition
] = [

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
    """
    Validate the centralized application registry.
    """

    routes = list(
        MODULES_BY_ROUTE.keys()
    )

    if len(routes) != len(set(routes)):

        raise RuntimeError(
            "Duplicate module routes detected."
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
        "structural_columns",
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
    """
    Render application and dependency health diagnostics.
    """

    st.title(
        "System Health"
    )

    st.caption(
        "IMAGINE application and module diagnostics"
    )

    # --------------------------------------------------------
    # Startup health check
    # --------------------------------------------------------

    try:

        results = run_startup_health_check()

    except Exception as exc:

        st.error(
            "The system health check itself failed."
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

    all_modules_healthy = (
        bool(results)
        and all(
            result.status == "ok"
            for result in results
        )
    )

    if all_modules_healthy:

        st.session_state[
            "health_last_successful_at"
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
            "Complete summary traceback",
            expanded=True,
        ):

            st.exception(exc)

        return

    # --------------------------------------------------------
    # Timestamps
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            "**Latest Health Check**"
        )

        last_checked = st.session_state.get(
            "health_last_checked_at"
        )

        if last_checked:

            st.code(
                last_checked.strftime(
                    "%Y-%m-%d %H:%M:%S UTC"
                )
            )

        else:

            st.code(
                "No health check recorded"
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

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    metric1, metric2, metric3 = st.columns(3)

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

    # --------------------------------------------------------
    # Module results
    # --------------------------------------------------------

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
                    expanded=False,
                ):

                    st.code(
                        result.traceback_text,
                        language="text",
                    )

            if result.path:

                st.caption(
                    f"Loaded from: {result.path}"
                )

    st.divider()

    # --------------------------------------------------------
    # Manual refresh
    # --------------------------------------------------------

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
    Resolve and render an IMAGINE route.

    No domain renderer is allowed to terminate the application
    shell.
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

    special_renderer = SPECIAL_RENDERERS.get(
        route
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
# SESSION STATE
# ============================================================


if "active_route" not in st.session_state:

    st.session_state.active_route = (
        "overview"
    )


# ============================================================
# NAVIGATION BUTTON
# ============================================================


def navigation_button(
    module: ModuleDefinition,
) -> None:
    """
    Render one interactive navigation button.
    """

    is_active = (
        st.session_state.active_route
        == module.route
    )

    if st.button(
        module.label,
        key=f"nav_{module.route}",
        use_container_width=True,
        type=(
            "primary"
            if is_active
            else "secondary"
        ),
    ):

        st.session_state.active_route = (
            module.route
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

    # --------------------------------------------------------
    # Overview
    # --------------------------------------------------------

    navigation_button(
        MODULES_BY_ROUTE["overview"]
    )

    # --------------------------------------------------------
    # Projects
    # --------------------------------------------------------

    with st.expander(
        "PROJECTS",
        expanded=False,
    ):

        for module in PROJECT_MODULES:

            navigation_button(
                module
            )

    # --------------------------------------------------------
    # Architecture
    # --------------------------------------------------------

    with st.expander(
        "ARCHITECTURE",
        expanded=True,
    ):

        for module in ARCHITECTURE_MODULES:

            navigation_button(
                module
            )

    # --------------------------------------------------------
    # Structural
    # --------------------------------------------------------

    with st.expander(
        "STRUCTURAL",
        expanded=False,
    ):

        for module in STRUCTURAL_MODULES:

            navigation_button(
                module
            )

    # --------------------------------------------------------
    # BIM
    # --------------------------------------------------------

    with st.expander(
        "BIM",
        expanded=False,
    ):

        for module in BIM_MODULES:

            navigation_button(
                module
            )

    # --------------------------------------------------------
    # MEP
    # --------------------------------------------------------

    with st.expander(
        "MEP",
        expanded=False,
    ):

        for module in MEP_MODULES:

            navigation_button(
                module
            )

    # --------------------------------------------------------
    # Costing
    # --------------------------------------------------------

    with st.expander(
        "COSTING",
        expanded=False,
    ):

        for module in COSTING_MODULES:

            navigation_button(
                module
            )

    # --------------------------------------------------------
    # Construction
    # --------------------------------------------------------

    with st.expander(
        "CONSTRUCTION",
        expanded=False,
    ):

        for module in CONSTRUCTION_MODULES:

            navigation_button(
                module
            )

    # --------------------------------------------------------
    # Documents
    # --------------------------------------------------------

    with st.expander(
        "DOCUMENTS",
        expanded=False,
    ):

        for module in DOCUMENT_MODULES:

            navigation_button(
                module
            )

    # --------------------------------------------------------
    # AI
    # --------------------------------------------------------

    with st.expander(
        "AI",
        expanded=False,
    ):

        for module in AI_MODULES:

            navigation_button(
                module
            )

    # --------------------------------------------------------
    # Analytics
    # --------------------------------------------------------

    with st.expander(
        "ANALYTICS",
        expanded=False,
    ):

        for module in ANALYTICS_MODULES:

            navigation_button(
                module
            )

    # --------------------------------------------------------
    # Regional
    # --------------------------------------------------------

    with st.expander(
        "REGIONAL",
        expanded=False,
    ):

        for module in REGIONAL_MODULES:

            navigation_button(
                module
            )

    # --------------------------------------------------------
    # Integrations
    # --------------------------------------------------------

    with st.expander(
        "INTEGRATIONS",
        expanded=False,
    ):

        for module in INTEGRATION_MODULES:

            navigation_button(
                module
            )

    # --------------------------------------------------------
    # Digital Twin
    # --------------------------------------------------------

    with st.expander(
        "DIGITAL TWIN",
        expanded=False,
    ):

        for module in DIGITAL_TWIN_MODULES:

            navigation_button(
                module
            )

    st.divider()

    navigation_button(
        MODULES_BY_ROUTE["system_health"]
    )

    st.divider()

    st.caption(
        "IMAGINE | Generative Architecture"
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
# ACTIVE MODULE INFORMATION
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