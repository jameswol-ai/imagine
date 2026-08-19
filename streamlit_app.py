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

from pathlib import Path
import sys


# Ensure the IMAGINE repository root is first on sys.path.
# This prevents an unrelated module named "app" from shadowing
# the repository's app/ package.
PROJECT_ROOT = Path(__file__).resolve().parent

if str(PROJECT_ROOT) in sys.path:
    sys.path.remove(str(PROJECT_ROOT))

sys.path.insert(0, str(PROJECT_ROOT))

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
# PLACEHOLDER
# ============================================================


def render_module_placeholder(
    module: ModuleDefinition,
) -> None:
    """
    Render a safe placeholder for a module whose UI has not
    yet been implemented.
    """

    st.title(module.label)

    if module.description:
        st.caption(module.description)

    st.info(
        f"{module.label} is registered in IMAGINE, "
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

    st.divider()

    st.subheader("Module Architecture")

    st.markdown(
        f"""
        This module belongs to the **{module.domain}** domain.

        The application shell is already connected to this
        route. Its domain logic should remain inside the
        corresponding repository folder.

        When the module receives a Streamlit renderer, register
        its `ui.py` module and renderer function in the module
        definition.
        """
    )


# ============================================================
# REGISTERED MODULE RENDERER
# ============================================================


def render_registered_module(
    module: ModuleDefinition,
) -> None:
    """
    Resolve and render a registered module.

    Modules with a valid renderer are loaded lazily.

    Modules without a renderer receive a safe placeholder.
    """

    if (
        module.renderer_module
        and module.renderer_function
    ):
        renderer = _safe_import(
            module.renderer_module,
            module.renderer_function,
        )

        if renderer is not None:
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
                    st.exception(exc)

            return

    render_module_placeholder(module)


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

    domain_columns = st.columns(4)

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
    ]

    for column, domain in zip(
        domain_columns,
        domains,
    ):
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
            "IMAGINE application is running."
        )

    with status_col2:
        st.info(
            "Domain modules are independently connected."
        )


# ============================================================
# GENERATIVE DESIGN
# ============================================================


def render_generative_design_safe() -> None:
    """
    Safe adapter for Generative Design.
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

    Application-shell contract:

        render_site_planning_registered()

    Domain UI contract:

        render_site_planning(service)

    Dependency flow:

        Streamlit
            ↓
        Repository
            ↓
        Service
            ↓
        Site Planning UI
    """

    st.title(
        "Site Planning"
    )

    try:

        from database.connection import (
            SessionLocal,
        )

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

    db = SessionLocal()

    try:

        repository = SitePlanningRepository(
            db
        )

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

    finally:

        db.close()


# ============================================================
# PROJECT MODULES
# ============================================================


PROJECT_MODULES = [
    ModuleDefinition(
        label="Projects",
        route="projects",
        domain="Projects",
        description="Project lifecycle and project records.",
        renderer_module="projects.projects.ui",
        renderer_function="render_projects",
        implemented=False,
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
        renderer_module="structural.beam_design.ui",
        renderer_function="render_beam_design",
    ),
    ModuleDefinition(
        label="Column Design",
        route="structural_columns",
        domain="Structural",
        description="Structural column analysis and design.",
        renderer_module="structural.column_design.ui",
        renderer_function="render_column_design",
    ),
    ModuleDefinition(
        label="Slab Design",
        route="structural_slabs",
        domain="Structural",
        description="Structural slab analysis and design.",
        renderer_module="structural.slab_design.ui",
        renderer_function="render_slab_design",
    ),
    ModuleDefinition(
        label="Foundation Design",
        route="structural_foundations",
        domain="Structural",
        description="Foundation analysis and design.",
        renderer_module="structural.foundation_design.ui",
        renderer_function="render_foundation_design",
    ),
    ModuleDefinition(
        label="Retaining Walls",
        route="structural_retaining_walls",
        domain="Structural",
        description="Retaining wall analysis and design.",
        renderer_module="structural.retaining_walls.ui",
        renderer_function="render_retaining_walls",
    ),
    ModuleDefinition(
        label="Steel Connections",
        route="structural_steel_connections",
        domain="Structural",
        description="Steel connection design.",
        renderer_module="structural.steel_connections.ui",
        renderer_function="render_steel_connections",
    ),
    ModuleDefinition(
        label="Finite Element Analysis",
        route="structural_fea",
        domain="Structural",
        description="Finite element analysis workflows.",
        renderer_module="structural.finite_element_analysis.ui",
        renderer_function="render_finite_element_analysis",
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
        renderer_module="bim.buildings.ui",
        renderer_function="render_buildings",
    ),
    ModuleDefinition(
        label="Storeys",
        route="bim_storeys",
        domain="BIM",
        description="Building storeys and levels.",
        renderer_module="bim.storeys.ui",
        renderer_function="render_storeys",
    ),
    ModuleDefinition(
        label="Spaces",
        route="bim_spaces",
        domain="BIM",
        description="BIM spaces and spatial entities.",
        renderer_module="bim.spaces.ui",
        renderer_function="render_spaces",
    ),
    ModuleDefinition(
        label="Elements",
        route="bim_elements",
        domain="BIM",
        description="Building elements and components.",
        renderer_module="bim.elements.ui",
        renderer_function="render_elements",
    ),
    ModuleDefinition(
        label="IFC",
        route="bim_ifc",
        domain="BIM",
        description="Industry Foundation Classes workflows.",
        renderer_module="bim.ifc.ui",
        renderer_function="render_ifc",
    ),
    ModuleDefinition(
        label="COBie",
        route="bim_cobie",
        domain="BIM",
        description="Construction Operations Building information exchange.",
        renderer_module="bim.cobie.ui",
        renderer_function="render_cobie",
    ),
    ModuleDefinition(
        label="BIM Digital Twin",
        route="bim_digital_twin",
        domain="BIM",
        description="BIM-connected digital twin.",
        renderer_module="bim.digital_twin.ui",
        renderer_function="render_digital_twin",
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
        description="Heating, ventilation and air conditioning.",
        renderer_module="mep.mechanical.hvac.ui",
        renderer_function="render_hvac",
    ),
    ModuleDefinition(
        label="Ventilation",
        route="mep_ventilation",
        domain="MEP",
        description="Ventilation analysis and design.",
        renderer_module="mep.mechanical.ventilation.ui",
        renderer_function="render_ventilation",
    ),
    ModuleDefinition(
        label="Chilled Water",
        route="mep_chilled_water",
        domain="MEP",
        description="Chilled water system design.",
        renderer_module="mep.mechanical.chilled_water.ui",
        renderer_function="render_chilled_water",
    ),
    ModuleDefinition(
        label="Energy Simulation",
        route="mep_energy",
        domain="MEP",
        description="Building energy simulation.",
        renderer_module="mep.mechanical.energy_simulation.ui",
        renderer_function="render_energy_simulation",
    ),
    ModuleDefinition(
        label="Electrical Load Analysis",
        route="mep_load_analysis",
        domain="MEP",
        description="Electrical load calculations.",
        renderer_module="mep.electrical.load_analysis.ui",
        renderer_function="render_load_analysis",
    ),
    ModuleDefinition(
        label="Transformers",
        route="mep_transformers",
        domain="MEP",
        description="Transformer sizing and analysis.",
        renderer_module="mep.electrical.transformers.ui",
        renderer_function="render_transformers",
    ),
    ModuleDefinition(
        label="Generators",
        route="mep_generators",
        domain="MEP",
        description="Generator systems.",
        renderer_module="mep.electrical.generators.ui",
        renderer_function="render_generators",
    ),
    ModuleDefinition(
        label="Cable Sizing",
        route="mep_cable_sizing",
        domain="MEP",
        description="Electrical cable sizing.",
        renderer_module="mep.electrical.cable_sizing.ui",
        renderer_function="render_cable_sizing",
    ),
    ModuleDefinition(
        label="Solar PV",
        route="mep_solar_pv",
        domain="MEP",
        description="Solar photovoltaic system design.",
        renderer_module="mep.electrical.solar_pv.ui",
        renderer_function="render_solar_pv",
    ),
    ModuleDefinition(
        label="Water Supply",
        route="mep_water_supply",
        domain="MEP",
        description="Water supply system design.",
        renderer_module="mep.plumbing.water_supply.ui",
        renderer_function="render_water_supply",
    ),
    ModuleDefinition(
        label="Drainage",
        route="mep_drainage",
        domain="MEP",
        description="Drainage system design.",
        renderer_module="mep.plumbing.drainage.ui",
        renderer_function="render_drainage",
    ),
    ModuleDefinition(
        label="Stormwater",
        route="mep_stormwater",
        domain="MEP",
        description="Stormwater management.",
        renderer_module="mep.plumbing.stormwater.ui",
        renderer_function="render_stormwater",
    ),
    ModuleDefinition(
        label="Sewer Networks",
        route="mep_sewer",
        domain="MEP",
        description="Sewer network design.",
        renderer_module="mep.plumbing.sewer_networks.ui",
        renderer_function="render_sewer_networks",
    ),
    ModuleDefinition(
        label="Firefighting",
        route="mep_firefighting",
        domain="MEP",
        description="Firefighting systems.",
        renderer_module="mep.plumbing.firefighting.ui",
        renderer_function="render_firefighting",
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
        renderer_module="costing.boq.ui",
        renderer_function="render_boq",
    ),
    ModuleDefinition(
        label="Quantity Takeoff",
        route="costing_quantity_takeoff",
        domain="Costing",
        description="Automated quantity takeoff.",
        renderer_module="costing.quantity_takeoff.ui",
        renderer_function="render_quantity_takeoff",
    ),
    ModuleDefinition(
        label="Procurement",
        route="costing_procurement",
        domain="Costing",
        description="Construction procurement costing.",
        renderer_module="costing.procurement.ui",
        renderer_function="render_procurement",
    ),
    ModuleDefinition(
        label="Forex",
        route="costing_forex",
        domain="Costing",
        description="Foreign exchange costing.",
        renderer_module="costing.forex.ui",
        renderer_function="render_forex",
    ),
    ModuleDefinition(
        label="Inflation",
        route="costing_inflation",
        domain="Costing",
        description="Construction cost inflation.",
        renderer_module="costing.inflation.ui",
        renderer_function="render_inflation",
    ),
    ModuleDefinition(
        label="Risk Analysis",
        route="costing_risk",
        domain="Costing",
        description="Cost and project risk analysis.",
        renderer_module="costing.risk_analysis.ui",
        renderer_function="render_risk_analysis",
    ),
    ModuleDefinition(
        label="Cashflow",
        route="costing_cashflow",
        domain="Costing",
        description="Project cashflow forecasting.",
        renderer_module="costing.cashflow.ui",
        renderer_function="render_cashflow",
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
        renderer_module="construction.planning.ui",
        renderer_function="render_planning",
    ),
    ModuleDefinition(
        label="Scheduling",
        route="construction_scheduling",
        domain="Construction",
        renderer_module="construction.scheduling.ui",
        renderer_function="render_scheduling",
    ),
    ModuleDefinition(
        label="RFIs",
        route="construction_rfis",
        domain="Construction",
        renderer_module="construction.rfis.ui",
        renderer_function="render_rfis",
    ),
    ModuleDefinition(
        label="Submittals",
        route="construction_submittals",
        domain="Construction",
        renderer_module="construction.submittals.ui",
        renderer_function="render_submittals",
    ),
    ModuleDefinition(
        label="Variations",
        route="construction_variations",
        domain="Construction",
        renderer_module="construction.variations.ui",
        renderer_function="render_variations",
    ),
    ModuleDefinition(
        label="Snagging",
        route="construction_snagging",
        domain="Construction",
        renderer_module="construction.snagging.ui",
        renderer_function="render_snagging",
    ),
    ModuleDefinition(
        label="Progress Tracking",
        route="construction_progress",
        domain="Construction",
        renderer_module="construction.progress_tracking.ui",
        renderer_function="render_progress_tracking",
    ),
    ModuleDefinition(
        label="Site Diaries",
        route="construction_site_diaries",
        domain="Construction",
        renderer_module="construction.site_diaries.ui",
        renderer_function="render_site_diaries",
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
        renderer_module="documents.drawing_management.ui",
        renderer_function="render_drawing_management",
    ),
    ModuleDefinition(
        label="Specifications",
        route="documents_specifications",
        domain="Documents",
        renderer_module="documents.specifications.ui",
        renderer_function="render_specifications",
    ),
    ModuleDefinition(
        label="Contracts",
        route="documents_contracts",
        domain="Documents",
        renderer_module="documents.contracts.ui",
        renderer_function="render_contracts",
    ),
    ModuleDefinition(
        label="Reports",
        route="documents_reports",
        domain="Documents",
        renderer_module="documents.reports.ui",
        renderer_function="render_reports",
    ),
    ModuleDefinition(
        label="Version Control",
        route="documents_versions",
        domain="Documents",
        renderer_module="documents.version_control.ui",
        renderer_function="render_version_control",
    ),
    ModuleDefinition(
        label="Archives",
        route="documents_archives",
        domain="Documents",
        renderer_module="documents.archives.ui",
        renderer_function="render_archives",
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
        renderer_module="ai.imagine_architect.ui",
        renderer_function="render_imagine_architect",
    ),
    ModuleDefinition(
        label="IMAGINE Engineer",
        route="ai_engineer",
        domain="AI",
        renderer_module="ai.imagine_engineer.ui",
        renderer_function="render_imagine_engineer",
    ),
    ModuleDefinition(
        label="IMAGINE MEP",
        route="ai_mep",
        domain="AI",
        renderer_module="ai.imagine_mep.ui",
        renderer_function="render_imagine_mep",
    ),
    ModuleDefinition(
        label="IMAGINE QS",
        route="ai_qs",
        domain="AI",
        renderer_module="ai.imagine_qs.ui",
        renderer_function="render_imagine_qs",
    ),
    ModuleDefinition(
        label="IMAGINE PM",
        route="ai_pm",
        domain="AI",
        renderer_module="ai.imagine_pm.ui",
        renderer_function="render_imagine_pm",
    ),
    ModuleDefinition(
        label="Vector Store",
        route="ai_vector_store",
        domain="AI",
        renderer_module="ai.vector_store.ui",
        renderer_function="render_vector_store",
    ),
    ModuleDefinition(
        label="RAG",
        route="ai_rag",
        domain="AI",
        renderer_module="ai.rag.ui",
        renderer_function="render_rag",
    ),
    ModuleDefinition(
        label="Prompt Library",
        route="ai_prompt_library",
        domain="AI",
        renderer_module="ai.prompt_library.ui",
        renderer_function="render_prompt_library",
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
        renderer_module="analytics.dashboards.ui",
        renderer_function="render_dashboards",
    ),
    ModuleDefinition(
        label="KPIs",
        route="analytics_kpis",
        domain="Analytics",
        renderer_module="analytics.kpis.ui",
        renderer_function="render_kpis",
    ),
    ModuleDefinition(
        label="Portfolio",
        route="analytics_portfolio",
        domain="Analytics",
        renderer_module="analytics.portfolio.ui",
        renderer_function="render_portfolio",
    ),
    ModuleDefinition(
        label="Forecasting",
        route="analytics_forecasting",
        domain="Analytics",
        renderer_module="analytics.forecasting.ui",
        renderer_function="render_forecasting",
    ),
    ModuleDefinition(
        label="Reporting",
        route="analytics_reporting",
        domain="Analytics",
        renderer_module="analytics.reporting.ui",
        renderer_function="render_reporting",
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
        renderer_module="regional.uganda.ui",
        renderer_function="render_uganda",
    ),
    ModuleDefinition(
        label="Kenya",
        route="regional_kenya",
        domain="Regional",
        renderer_module="regional.kenya.ui",
        renderer_function="render_kenya",
    ),
    ModuleDefinition(
        label="Tanzania",
        route="regional_tanzania",
        domain="Regional",
        renderer_module="regional.tanzania.ui",
        renderer_function="render_tanzania",
    ),
    ModuleDefinition(
        label="Rwanda",
        route="regional_rwanda",
        domain="Regional",
        renderer_module="regional.rwanda.ui",
        renderer_function="render_rwanda",
    ),
    ModuleDefinition(
        label="South Sudan",
        route="regional_south_sudan",
        domain="Regional",
        renderer_module="regional.south_sudan.ui",
        renderer_function="render_south_sudan",
    ),
    ModuleDefinition(
        label="Codes",
        route="regional_codes",
        domain="Regional",
        renderer_module="regional.codes.ui",
        renderer_function="render_codes",
    ),
    ModuleDefinition(
        label="Zoning Laws",
        route="regional_zoning_laws",
        domain="Regional",
        renderer_module="regional.zoning_laws.ui",
        renderer_function="render_zoning_laws",
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
        renderer_module="integrations.microsoft.ui",
        renderer_function="render_microsoft",
    ),
    ModuleDefinition(
        label="AutoCAD",
        route="integration_autocad",
        domain="Integrations",
        renderer_module="integrations.autocad.ui",
        renderer_function="render_autocad",
    ),
    ModuleDefinition(
        label="Revit",
        route="integration_revit",
        domain="Integrations",
        renderer_module="integrations.revit.ui",
        renderer_function="render_revit",
    ),
    ModuleDefinition(
        label="Archicad",
        route="integration_archicad",
        domain="Integrations",
        renderer_module="integrations.archicad.ui",
        renderer_function="render_archicad",
    ),
    ModuleDefinition(
        label="Tekla",
        route="integration_tekla",
        domain="Integrations",
        renderer_module="integrations.tekla.ui",
        renderer_function="render_tekla",
    ),
    ModuleDefinition(
        label="IfcOpenShell",
        route="integration_ifcopenshell",
        domain="Integrations",
        renderer_module="integrations.ifcopenshell.ui",
        renderer_function="render_ifcopenshell",
    ),
    ModuleDefinition(
        label="ArcGIS",
        route="integration_arcgis",
        domain="Integrations",
        renderer_module="integrations.arcgis.ui",
        renderer_function="render_arcgis",
    ),
    ModuleDefinition(
        label="Azure",
        route="integration_azure",
        domain="Integrations",
        renderer_module="integrations.azure.ui",
        renderer_function="render_azure",
    ),
    ModuleDefinition(
        label="Mapbox",
        route="integration_mapbox",
        domain="Integrations",
        renderer_module="integrations.mapbox.ui",
        renderer_function="render_mapbox",
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
        renderer_module="digital_twin.assets.ui",
        renderer_function="render_assets",
    ),
    ModuleDefinition(
        label="Sensors",
        route="digital_twin_sensors",
        domain="Digital Twin",
        renderer_module="digital_twin.sensors.ui",
        renderer_function="render_sensors",
    ),
    ModuleDefinition(
        label="Telemetry",
        route="digital_twin_telemetry",
        domain="Digital Twin",
        renderer_module="digital_twin.telemetry.ui",
        renderer_function="render_telemetry",
    ),
    ModuleDefinition(
        label="Energy",
        route="digital_twin_energy",
        domain="Digital Twin",
        renderer_module="digital_twin.energy.ui",
        renderer_function="render_energy",
    ),
    ModuleDefinition(
        label="Maintenance",
        route="digital_twin_maintenance",
        domain="Digital Twin",
        renderer_module="digital_twin.maintenance.ui",
        renderer_function="render_maintenance",
    ),
    ModuleDefinition(
        label="Predictive AI",
        route="digital_twin_predictive_ai",
        domain="Digital Twin",
        renderer_module="digital_twin.predictive_ai.ui",
        renderer_function="render_predictive_ai",
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
    Validate the application route registry.
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

    try:
        results = run_startup_health_check()

    except Exception as exc:
        st.error(
            "The system health check could not be executed."
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

    all_modules_healthy = all(
        result.status == "ok"
        for result in results
    )

    if all_modules_healthy:
        st.session_state[
            "health_last_successful_at"
        ] = checked_at

    summary = health_summary(
        results
    )

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

            if result.path:
                st.caption(
                    f"Loaded from: {result.path}"
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
        special_renderer()
        return

    render_registered_module(
        module
    )


# ============================================================
# NAVIGATION HELPER
# ============================================================


def navigate_to(
    route: str,
) -> None:
    """
    Store the active route.
    """

    if route not in MODULES_BY_ROUTE:
        return

    st.session_state.active_route = route


# ============================================================
# SIDEBAR DOMAIN NAVIGATION
# ============================================================


def render_navigation_group(
    title: str,
    modules: list[ModuleDefinition],
    expanded: bool = False,
) -> None:
    """
    Render one interactive navigation group.
    """

    with st.expander(
        title,
        expanded=expanded,
    ):
        for module in modules:

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
                navigate_to(
                    module.route
                )

                st.rerun()


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

    st.caption(
        "NAVIGATION"
    )

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
        navigate_to(
            "overview"
        )

        st.rerun()

    render_navigation_group(
        "PROJECTS",
        PROJECT_MODULES,
        expanded=False,
    )

    render_navigation_group(
        "ARCHITECTURE",
        ARCHITECTURE_MODULES,
        expanded=True,
    )

    render_navigation_group(
        "STRUCTURAL",
        STRUCTURAL_MODULES,
        expanded=False,
    )

    render_navigation_group(
        "BIM",
        BIM_MODULES,
        expanded=False,
    )

    render_navigation_group(
        "MEP",
        MEP_MODULES,
        expanded=False,
    )

    render_navigation_group(
        "COSTING",
        COSTING_MODULES,
        expanded=False,
    )

    render_navigation_group(
        "CONSTRUCTION",
        CONSTRUCTION_MODULES,
        expanded=False,
    )

    render_navigation_group(
        "DOCUMENTS",
        DOCUMENT_MODULES,
        expanded=False,
    )

    render_navigation_group(
        "AI",
        AI_MODULES,
        expanded=False,
    )

    render_navigation_group(
        "ANALYTICS",
        ANALYTICS_MODULES,
        expanded=False,
    )

    render_navigation_group(
        "REGIONAL",
        REGIONAL_MODULES,
        expanded=False,
    )

    render_navigation_group(
        "INTEGRATIONS",
        INTEGRATION_MODULES,
        expanded=False,
    )

    render_navigation_group(
        "DIGITAL TWIN",
        DIGITAL_TWIN_MODULES,
        expanded=False,
    )

    st.divider()

    system_health_active = (
        st.session_state.active_route
        == "system_health"
    )

    if st.button(
        "System Health",
        key="nav_system_health",
        use_container_width=True,
        type=(
            "primary"
            if system_health_active
            else "secondary"
        ),
    ):
        navigate_to(
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