"""
IMAGINE
Generative Architecture & Civil Engine

Main Streamlit application entry point.

Application shell responsibilities:
    - Navigation
    - Module registry
    - Safe renderer loading
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

import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib import import_module
from typing import Any, Callable


# ============================================================
# APP MODULE SHADOWING PROTECTION
# ============================================================
#
# The database layer imports:
#
#     from app.settings import settings
#
# Streamlit can occasionally cause a top-level `app` module
# to be resolved before the repository's `app/` package.
#
# We remove only an already-loaded NON-PACKAGE `app` module.
# A real `app` package is left untouched.
#
# This keeps the Streamlit shell from modifying the database,
# service, or model contracts.
# ============================================================

_loaded_app = sys.modules.get("app")

if (
    _loaded_app is not None
    and not hasattr(_loaded_app, "__path__")
):
    del sys.modules["app"]


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

except Exception:
    health_summary = None
    run_startup_health_check = None
    HEALTH_AVAILABLE = False


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
    Defines a navigable IMAGINE module.

    A module may have an implemented renderer or may remain
    registered while its UI is still under development.
    """

    label: str
    route: str
    domain: str

    icon: str = ""

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
    """
    Safely import a zero-argument renderer.

    Import failures are isolated from the application shell.
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
# GENERIC MODULE PLACEHOLDER
# ============================================================


def render_module_placeholder(
    module: ModuleDefinition,
) -> None:
    """
    Render a safe placeholder for a registered module that
    does not currently expose a Streamlit renderer.
    """

    title = module.label

    if module.icon:
        title = f"{module.icon} {module.label}"

    st.title(title)

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
            "UI",
            "Not implemented",
        )

    with col3:
        st.metric(
            "Registry",
            "Registered",
        )


# ============================================================
# REGISTERED MODULE RENDERER
# ============================================================


def render_registered_module(
    module: ModuleDefinition,
) -> None:
    """
    Render a registered module.

    Implemented modules use their own zero-argument renderer.

    Missing renderers receive a safe placeholder.

    Import and runtime errors are isolated so that one broken
    module cannot destroy the entire Streamlit application.
    """

    if not module.renderer_module:
        render_module_placeholder(module)
        return

    if not module.renderer_function:
        render_module_placeholder(module)
        return

    try:
        renderer = import_module(
            module.renderer_module
        )

    except Exception as exc:

        title = module.label

        if module.icon:
            title = f"{module.icon} {module.label}"

        st.title(title)

        st.error(
            f"{module.label} could not be loaded."
        )

        with st.expander(
            "Complete import traceback",
            expanded=True,
        ):
            st.exception(exc)

        return

    try:
        render_function = getattr(
            renderer,
            module.renderer_function,
            None,
        )

    except Exception as exc:

        st.error(
            f"{module.label} renderer could not be resolved."
        )

        with st.expander(
            "Complete renderer lookup traceback",
            expanded=True,
        ):
            st.exception(exc)

        return

    if not callable(render_function):

        st.error(
            f"{module.label} does not expose the expected "
            f"renderer `{module.renderer_function}()`."
        )

        return

    try:
        render_function()

    except Exception as exc:

        st.error(
            f"{module.label} could not be rendered."
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
            str(len(ALL_MODULES)),
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
            "BOQ, quantity takeoff and cost analysis.",
        ),
        (
            "Construction",
            "Planning, scheduling and site management.",
        ),
        (
            "Documents",
            "Drawings, specifications and project records.",
        ),
        (
            "AI",
            "Engineering intelligence and retrieval.",
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

        if HEALTH_AVAILABLE:
            st.info(
                "System Health diagnostics are available."
            )
        else:
            st.warning(
                "System Health diagnostics are unavailable."
            )


# ============================================================
# GENERATIVE DESIGN
# ============================================================


def render_generative_design_safe() -> None:
    """
    Safe adapter for Generative Design.

    The domain UI remains responsible for its own logic.
    """

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
            "Generative Design encountered an error."
        )

        with st.expander(
            "Complete renderer traceback",
            expanded=True,
        ):
            st.exception(exc)


# ============================================================
# SITE PLANNING
# ============================================================


def render_site_planning_registered() -> None:
    """
    Zero-argument Streamlit adapter for Site Planning.

    The Site Planning domain follows:

        Repository
            |
        Service
            |
          UI

    The adapter constructs the synchronous service once and
    passes that service to the UI renderer.
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
            st.exception(exc)

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
            st.exception(exc)


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
# ARCHITECTURE MODULES
# ============================================================


ARCHITECTURE_MODULES = [

    ModuleDefinition(
        label="Zoning",
        icon="Zoning",
        route="architecture_zoning",
        domain="Architecture",
        description="Planning controls, setbacks, coverage and zoning constraints.",
        renderer_module="architecture.zoning.ui",
        renderer_function="render_zoning",
        implemented=True,
    ),

    ModuleDefinition(
        label="Site Planning",
        icon="Site Planning",
        route="architecture_site_planning",
        domain="Architecture",
        description="Site organization and development planning.",
        implemented=True,
    ),

    ModuleDefinition(
        label="Floor Planning",
        icon="Floor Planning",
        route="architecture_floor_planning",
        domain="Architecture",
        description="Floor layouts and spatial planning.",
        renderer_module="architecture.floor_planning.ui",
        renderer_function="render_floor_planning",
        implemented=True,
    ),

    ModuleDefinition(
        label="Room Programming",
        icon="Room Programming",
        route="architecture_room_programming",
        domain="Architecture",
        description="Room requirements, areas and adjacencies.",
        renderer_module="architecture.room_programming.ui",
        renderer_function="render_room_programming",
        implemented=True,
    ),

    ModuleDefinition(
        label="Compliance",
        icon="Compliance",
        route="architecture_compliance",
        domain="Architecture",
        description="Regulatory and design compliance constraints.",
        renderer_module="architecture.compliance.ui",
        renderer_function="render_compliance",
        implemented=True,
    ),

    ModuleDefinition(
        label="Generative Design",
        icon="Generative Design",
        route="architecture_generative_design",
        domain="Architecture",
        description="Constraint-driven design generation and ranking.",
        implemented=True,
    ),
]


# ============================================================
# STRUCTURAL MODULES
# ============================================================


STRUCTURAL_MODULES = [

    ModuleDefinition(
        label="Eurocode EN 1990",
        icon="EN 1990",
        route="structural_en1990",
        domain="Structural",
        description="Basis of structural design.",
    ),

    ModuleDefinition(
        label="Eurocode EN 1991",
        icon="EN 1991",
        route="structural_en1991",
        domain="Structural",
        description="Actions on structures.",
    ),

    ModuleDefinition(
        label="Eurocode EN 1992",
        icon="EN 1992",
        route="structural_en1992",
        domain="Structural",
        description="Design of concrete structures.",
    ),

    ModuleDefinition(
        label="Eurocode EN 1993",
        icon="EN 1993",
        route="structural_en1993",
        domain="Structural",
        description="Design of steel structures.",
    ),

    ModuleDefinition(
        label="Eurocode EN 1995",
        icon="EN 1995",
        route="structural_en1995",
        domain="Structural",
        description="Design of timber structures.",
    ),

    ModuleDefinition(
        label="Eurocode EN 1997",
        icon="EN 1997",
        route="structural_en1997",
        domain="Structural",
        description="Geotechnical design.",
    ),

    ModuleDefinition(
        label="Eurocode EN 1998",
        icon="EN 1998",
        route="structural_en1998",
        domain="Structural",
        description="Earthquake-resistant design.",
    ),

    ModuleDefinition(
        label="Beam Design",
        icon="Beam Design",
        route="structural_beams",
        domain="Structural",
        description="Structural beam analysis and design.",
    ),

    ModuleDefinition(
        label="Column Design",
        icon="Column Design",
        route="structural_columns",
        domain="Structural",
        description="Structural column analysis and design.",
    ),

    ModuleDefinition(
        label="Slab Design",
        icon="Slab Design",
        route="structural_slabs",
        domain="Structural",
        description="Structural slab analysis and design.",
    ),

    ModuleDefinition(
        label="Foundation Design",
        icon="Foundation Design",
        route="structural_foundations",
        domain="Structural",
        description="Foundation analysis and design.",
    ),

    ModuleDefinition(
        label="Retaining Walls",
        icon="Retaining Walls",
        route="structural_retaining_walls",
        domain="Structural",
        description="Retaining wall analysis and design.",
    ),

    ModuleDefinition(
        label="Steel Connections",
        icon="Steel Connections",
        route="structural_steel_connections",
        domain="Structural",
        description="Steel connection design.",
    ),

    ModuleDefinition(
        label="Finite Element Analysis",
        icon="Finite Element Analysis",
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
        icon="Buildings",
        route="bim_buildings",
        domain="BIM",
        description="BIM building information.",
    ),

    ModuleDefinition(
        label="Storeys",
        icon="Storeys",
        route="bim_storeys",
        domain="BIM",
        description="Building storeys and levels.",
    ),

    ModuleDefinition(
        label="Spaces",
        icon="Spaces",
        route="bim_spaces",
        domain="BIM",
        description="BIM spaces and spatial entities.",
    ),

    ModuleDefinition(
        label="Elements",
        icon="Elements",
        route="bim_elements",
        domain="BIM",
        description="Building elements and components.",
    ),

    ModuleDefinition(
        label="IFC",
        icon="IFC",
        route="bim_ifc",
        domain="BIM",
        description="Industry Foundation Classes workflows.",
    ),

    ModuleDefinition(
        label="COBie",
        icon="COBie",
        route="bim_cobie",
        domain="BIM",
        description="Construction Operations Building information exchange.",
    ),

    ModuleDefinition(
        label="BIM Digital Twin",
        icon="BIM Digital Twin",
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
        icon="HVAC",
        route="mep_hvac",
        domain="MEP",
        description="Heating, ventilation and air conditioning.",
    ),

    ModuleDefinition(
        label="Ventilation",
        icon="Ventilation",
        route="mep_ventilation",
        domain="MEP",
        description="Ventilation analysis and design.",
    ),

    ModuleDefinition(
        label="Chilled Water",
        icon="Chilled Water",
        route="mep_chilled_water",
        domain="MEP",
        description="Chilled water system design.",
    ),

    ModuleDefinition(
        label="Energy Simulation",
        icon="Energy",
        route="mep_energy",
        domain="MEP",
        description="Building energy simulation.",
    ),

    ModuleDefinition(
        label="Electrical Load Analysis",
        icon="Load Analysis",
        route="mep_load_analysis",
        domain="MEP",
        description="Electrical load calculations.",
    ),

    ModuleDefinition(
        label="Transformers",
        icon="Transformers",
        route="mep_transformers",
        domain="MEP",
        description="Transformer sizing and analysis.",
    ),

    ModuleDefinition(
        label="Generators",
        icon="Generators",
        route="mep_generators",
        domain="MEP",
        description="Generator systems.",
    ),

    ModuleDefinition(
        label="Cable Sizing",
        icon="Cable Sizing",
        route="mep_cable_sizing",
        domain="MEP",
        description="Electrical cable sizing.",
    ),

    ModuleDefinition(
        label="Solar PV",
        icon="Solar PV",
        route="mep_solar_pv",
        domain="MEP",
        description="Solar photovoltaic system design.",
    ),

    ModuleDefinition(
        label="Water Supply",
        icon="Water Supply",
        route="mep_water_supply",
        domain="MEP",
        description="Water supply system design.",
    ),

    ModuleDefinition(
        label="Drainage",
        icon="Drainage",
        route="mep_drainage",
        domain="MEP",
        description="Drainage system design.",
    ),

    ModuleDefinition(
        label="Stormwater",
        icon="Stormwater",
        route="mep_stormwater",
        domain="MEP",
        description="Stormwater management.",
    ),

    ModuleDefinition(
        label="Sewer Networks",
        icon="Sewer",
        route="mep_sewer",
        domain="MEP",
        description="Sewer network design.",
    ),

    ModuleDefinition(
        label="Firefighting",
        icon="Firefighting",
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
        icon="BOQ",
        route="costing_boq",
        domain="Costing",
        description="Bills of quantities.",
    ),

    ModuleDefinition(
        label="Quantity Takeoff",
        icon="Quantity Takeoff",
        route="costing_quantity_takeoff",
        domain="Costing",
        description="Automated quantity takeoff.",
    ),

    ModuleDefinition(
        label="Procurement",
        icon="Procurement",
        route="costing_procurement",
        domain="Costing",
        description="Construction procurement costing.",
    ),

    ModuleDefinition(
        label="Forex",
        icon="Forex",
        route="costing_forex",
        domain="Costing",
        description="Foreign exchange costing.",
    ),

    ModuleDefinition(
        label="Inflation",
        icon="Inflation",
        route="costing_inflation",
        domain="Costing",
        description="Construction cost inflation.",
    ),

    ModuleDefinition(
        label="Risk Analysis",
        icon="Risk Analysis",
        route="costing_risk",
        domain="Costing",
        description="Cost and project risk analysis.",
    ),

    ModuleDefinition(
        label="Cashflow",
        icon="Cashflow",
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
        icon="Planning",
        route="construction_planning",
        domain="Construction",
    ),

    ModuleDefinition(
        label="Scheduling",
        icon="Scheduling",
        route="construction_scheduling",
        domain="Construction",
    ),

    ModuleDefinition(
        label="RFIs",
        icon="RFIs",
        route="construction_rfis",
        domain="Construction",
    ),

    ModuleDefinition(
        label="Submittals",
        icon="Submittals",
        route="construction_submittals",
        domain="Construction",
    ),

    ModuleDefinition(
        label="Variations",
        icon="Variations",
        route="construction_variations",
        domain="Construction",
    ),

    ModuleDefinition(
        label="Snagging",
        icon="Snagging",
        route="construction_snagging",
        domain="Construction",
    ),

    ModuleDefinition(
        label="Progress Tracking",
        icon="Progress Tracking",
        route="construction_progress",
        domain="Construction",
    ),

    ModuleDefinition(
        label="Site Diaries",
        icon="Site Diaries",
        route="construction_site_diaries",
        domain="Construction",
    ),
]


# ============================================================
# DOCUMENT MODULES
# ============================================================


DOCUMENT_MODULES = [

    ModuleDefinition(
        label="Drawing Management",
        icon="Drawing Management",
        route="documents_drawings",
        domain="Documents",
    ),

    ModuleDefinition(
        label="Specifications",
        icon="Specifications",
        route="documents_specifications",
        domain="Documents",
    ),

    ModuleDefinition(
        label="Contracts",
        icon="Contracts",
        route="documents_contracts",
        domain="Documents",
    ),

    ModuleDefinition(
        label="Reports",
        icon="Reports",
        route="documents_reports",
        domain="Documents",
    ),

    ModuleDefinition(
        label="Version Control",
        icon="Version Control",
        route="documents_versions",
        domain="Documents",
    ),

    ModuleDefinition(
        label="Archives",
        icon="Archives",
        route="documents_archives",
        domain="Documents",
    ),
]


# ============================================================
# AI MODULES
# ============================================================


AI_MODULES = [

    ModuleDefinition(
        label="IMAGINE Architect",
        icon="IMAGINE Architect",
        route="ai_architect",
        domain="AI",
    ),

    ModuleDefinition(
        label="IMAGINE Engineer",
        icon="IMAGINE Engineer",
        route="ai_engineer",
        domain="AI",
    ),

    ModuleDefinition(
        label="IMAGINE MEP",
        icon="IMAGINE MEP",
        route="ai_mep",
        domain="AI",
    ),

    ModuleDefinition(
        label="IMAGINE QS",
        icon="IMAGINE QS",
        route="ai_qs",
        domain="AI",
    ),

    ModuleDefinition(
        label="IMAGINE PM",
        icon="IMAGINE PM",
        route="ai_pm",
        domain="AI",
    ),

    ModuleDefinition(
        label="Vector Store",
        icon="Vector Store",
        route="ai_vector_store",
        domain="AI",
    ),

    ModuleDefinition(
        label="RAG",
        icon="RAG",
        route="ai_rag",
        domain="AI",
    ),

    ModuleDefinition(
        label="Prompt Library",
        icon="Prompt Library",
        route="ai_prompt_library",
        domain="AI",
    ),
]


# ============================================================
# ANALYTICS MODULES
# ============================================================


ANALYTICS_MODULES = [

    ModuleDefinition(
        label="Dashboards",
        icon="Dashboards",
        route="analytics_dashboards",
        domain="Analytics",
    ),

    ModuleDefinition(
        label="KPIs",
        icon="KPIs",
        route="analytics_kpis",
        domain="Analytics",
    ),

    ModuleDefinition(
        label="Portfolio",
        icon="Portfolio",
        route="analytics_portfolio",
        domain="Analytics",
    ),

    ModuleDefinition(
        label="Forecasting",
        icon="Forecasting",
        route="analytics_forecasting",
        domain="Analytics",
    ),

    ModuleDefinition(
        label="Reporting",
        icon="Reporting",
        route="analytics_reporting",
        domain="Analytics",
    ),
]


# ============================================================
# REGIONAL MODULES
# ============================================================


REGIONAL_MODULES = [

    ModuleDefinition(
        label="Uganda",
        icon="Uganda",
        route="regional_uganda",
        domain="Regional",
    ),

    ModuleDefinition(
        label="Kenya",
        icon="Kenya",
        route="regional_kenya",
        domain="Regional",
    ),

    ModuleDefinition(
        label="Tanzania",
        icon="Tanzania",
        route="regional_tanzania",
        domain="Regional",
    ),

    ModuleDefinition(
        label="Rwanda",
        icon="Rwanda",
        route="regional_rwanda",
        domain="Regional",
    ),

    ModuleDefinition(
        label="South Sudan",
        icon="South Sudan",
        route="regional_south_sudan",
        domain="Regional",
    ),

    ModuleDefinition(
        label="Codes",
        icon="Codes",
        route="regional_codes",
        domain="Regional",
    ),

    ModuleDefinition(
        label="Zoning Laws",
        icon="Zoning Laws",
        route="regional_zoning_laws",
        domain="Regional",
    ),
]


# ============================================================
# INTEGRATION MODULES
# ============================================================


INTEGRATION_MODULES = [

    ModuleDefinition(
        label="Microsoft",
        icon="Microsoft",
        route="integration_microsoft",
        domain="Integrations",
    ),

    ModuleDefinition(
        label="AutoCAD",
        icon="AutoCAD",
        route="integration_autocad",
        domain="Integrations",
    ),

    ModuleDefinition(
        label="Revit",
        icon="Revit",
        route="integration_revit",
        domain="Integrations",
    ),

    ModuleDefinition(
        label="Archicad",
        icon="Archicad",
        route="integration_archicad",
        domain="Integrations",
    ),

    ModuleDefinition(
        label="Tekla",
        icon="Tekla",
        route="integration_tekla",
        domain="Integrations",
    ),

    ModuleDefinition(
        label="IfcOpenShell",
        icon="IfcOpenShell",
        route="integration_ifcopenshell",
        domain="Integrations",
    ),

    ModuleDefinition(
        label="ArcGIS",
        icon="ArcGIS",
        route="integration_arcgis",
        domain="Integrations",
    ),

    ModuleDefinition(
        label="Azure",
        icon="Azure",
        route="integration_azure",
        domain="Integrations",
    ),

    ModuleDefinition(
        label="Mapbox",
        icon="Mapbox",
        route="integration_mapbox",
        domain="Integrations",
    ),
]


# ============================================================
# DIGITAL TWIN MODULES
# ============================================================


DIGITAL_TWIN_MODULES = [

    ModuleDefinition(
        label="Assets",
        icon="Assets",
        route="digital_twin_assets",
        domain="Digital Twin",
    ),

    ModuleDefinition(
        label="Sensors",
        icon="Sensors",
        route="digital_twin_sensors",
        domain="Digital Twin",
    ),

    ModuleDefinition(
        label="Telemetry",
        icon="Telemetry",
        route="digital_twin_telemetry",
        domain="Digital Twin",
    ),

    ModuleDefinition(
        label="Energy",
        icon="Energy",
        route="digital_twin_energy",
        domain="Digital Twin",
    ),

    ModuleDefinition(
        label="Maintenance",
        icon="Maintenance",
        route="digital_twin_maintenance",
        domain="Digital Twin",
    ),

    ModuleDefinition(
        label="Predictive AI",
        icon="Predictive AI",
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
# MODULE ROUTE REGISTRY
# ============================================================


MODULES_BY_ROUTE: dict[
    str,
    ModuleDefinition,
] = {

    "overview": ModuleDefinition(
        label="Overview",
        icon="Overview",
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
        icon="System Health",
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
    Validate the IMAGINE application route registry.
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

        "projects",
        "project_approvals",
        "project_revisions",
        "project_workflows",
        "project_governance",

        "architecture_zoning",
        "architecture_site_planning",
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
    """
    Render application health and dependency diagnostics.
    """

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

        st.info(
            "The application shell remains operational, "
            "but health diagnostics are unavailable."
        )

        return

    try:

        results = run_startup_health_check()

    except Exception as exc:

        st.error(
            "System Health could not execute the startup checks."
        )

        with st.expander(
            "Complete health traceback",
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

    all_modules_healthy = all(
        result.status == "ok"
        for result in results
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
            "System Health returned invalid diagnostic data."
        )

        with st.expander(
            "Complete summary traceback",
            expanded=True,
        ):
            st.exception(exc)

        return

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

    if summary.get("status") == "healthy":

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

    if st.button(
        "Run Health Check Again",
        key="health_rerun",
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
    Resolve and render an application route.
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
                "Complete adapter traceback",
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
# NAVIGATION HELPER
# ============================================================


def _navigate(
    route: str,
) -> None:
    """
    Set the active application route.
    """

    st.session_state.active_route = route


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
    # OVERVIEW
    # --------------------------------------------------------

    if st.button(
        "Overview",
        key="nav_overview",
        use_container_width=True,
        type=(
            "primary"
            if st.session_state.active_route
            == "overview"
            else "secondary"
        ),
    ):

        _navigate(
            "overview"
        )

        st.rerun()

    # ========================================================
    # PROJECTS
    # ========================================================

    with st.expander(
        "PROJECTS",
        expanded=True,
    ):

        for module in PROJECT_MODULES:

            if st.button(
                module.label,
                key=f"nav_{module.route}",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.active_route
                    == module.route
                    else "secondary"
                ),
            ):

                _navigate(
                    module.route
                )

                st.rerun()

    # ========================================================
    # ARCHITECTURE
    # ========================================================

    with st.expander(
        "ARCHITECTURE",
        expanded=False,
    ):

        for module in ARCHITECTURE_MODULES:

            if st.button(
                module.label,
                key=f"nav_{module.route}",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.active_route
                    == module.route
                    else "secondary"
                ),
            ):

                _navigate(
                    module.route
                )

                st.rerun()

    # ========================================================
    # STRUCTURAL
    # ========================================================

    with st.expander(
        "STRUCTURAL",
        expanded=False,
    ):

        for module in STRUCTURAL_MODULES:

            if st.button(
                module.label,
                key=f"nav_{module.route}",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.active_route
                    == module.route
                    else "secondary"
                ),
            ):

                _navigate(
                    module.route
                )

                st.rerun()

    # ========================================================
    # BIM
    # ========================================================

    with st.expander(
        "BIM",
        expanded=False,
    ):

        for module in BIM_MODULES:

            if st.button(
                module.label,
                key=f"nav_{module.route}",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.active_route
                    == module.route
                    else "secondary"
                ),
            ):

                _navigate(
                    module.route
                )

                st.rerun()

    # ========================================================
    # MEP
    # ========================================================

    with st.expander(
        "MEP",
        expanded=False,
    ):

        for module in MEP_MODULES:

            if st.button(
                module.label,
                key=f"nav_{module.route}",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.active_route
                    == module.route
                    else "secondary"
                ),
            ):

                _navigate(
                    module.route
                )

                st.rerun()

    # ========================================================
    # COSTING
    # ========================================================

    with st.expander(
        "COSTING",
        expanded=False,
    ):

        for module in COSTING_MODULES:

            if st.button(
                module.label,
                key=f"nav_{module.route}",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.active_route
                    == module.route
                    else "secondary"
                ),
            ):

                _navigate(
                    module.route
                )

                st.rerun()

    # ========================================================
    # CONSTRUCTION
    # ========================================================

    with st.expander(
        "CONSTRUCTION",
        expanded=False,
    ):

        for module in CONSTRUCTION_MODULES:

            if st.button(
                module.label,
                key=f"nav_{module.route}",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.active_route
                    == module.route
                    else "secondary"
                ),
            ):

                _navigate(
                    module.route
                )

                st.rerun()

    # ========================================================
    # DOCUMENTS
    # ========================================================

    with st.expander(
        "DOCUMENTS",
        expanded=False,
    ):

        for module in DOCUMENT_MODULES:

            if st.button(
                module.label,
                key=f"nav_{module.route}",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.active_route
                    == module.route
                    else "secondary"
                ),
            ):

                _navigate(
                    module.route
                )

                st.rerun()

    # ========================================================
    # AI
    # ========================================================

    with st.expander(
        "AI",
        expanded=False,
    ):

        for module in AI_MODULES:

            if st.button(
                module.label,
                key=f"nav_{module.route}",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.active_route
                    == module.route
                    else "secondary"
                ),
            ):

                _navigate(
                    module.route
                )

                st.rerun()

    # ========================================================
    # ANALYTICS
    # ========================================================

    with st.expander(
        "ANALYTICS",
        expanded=False,
    ):

        for module in ANALYTICS_MODULES:

            if st.button(
                module.label,
                key=f"nav_{module.route}",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.active_route
                    == module.route
                    else "secondary"
                ),
            ):

                _navigate(
                    module.route
                )

                st.rerun()

    # ========================================================
    # REGIONAL
    # ========================================================

    with st.expander(
        "REGIONAL",
        expanded=False,
    ):

        for module in REGIONAL_MODULES:

            if st.button(
                module.label,
                key=f"nav_{module.route}",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.active_route
                    == module.route
                    else "secondary"
                ),
            ):

                _navigate(
                    module.route
                )

                st.rerun()

    # ========================================================
    # INTEGRATIONS
    # ========================================================

    with st.expander(
        "INTEGRATIONS",
        expanded=False,
    ):

        for module in INTEGRATION_MODULES:

            if st.button(
                module.label,
                key=f"nav_{module.route}",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.active_route
                    == module.route
                    else "secondary"
                ),
            ):

                _navigate(
                    module.route
                )

                st.rerun()

    # ========================================================
    # DIGITAL TWIN
    # ========================================================

    with st.expander(
        "DIGITAL TWIN",
        expanded=False,
    ):

        for module in DIGITAL_TWIN_MODULES:

            if st.button(
                module.label,
                key=f"nav_{module.route}",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.active_route
                    == module.route
                    else "secondary"
                ),
            ):

                _navigate(
                    module.route
                )

                st.rerun()

    st.divider()

    # ========================================================
    # SYSTEM HEALTH
    # ========================================================

    if st.button(
        "System Health",
        key="nav_system_health",
        use_container_width=True,
        type=(
            "primary"
            if st.session_state.active_route
            == "system_health"
            else "secondary"
        ),
    ):

        _navigate(
            "system_health"
        )

        st.rerun()

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
# RENDER ACTIVE MODULE
# ============================================================


render_route(
    active_route
)