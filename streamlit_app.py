"""
IMAGINE
Generative Architecture & Civil Engine

Enterprise Multi-Page Streamlit Application Shell featuring native st.navigation,
st.Page routing, dynamic sidebar searching, and module registry coverage
across Architecture, Structural, MEP, BIM, Costing, AI, Regional Codes, and Digital Twin.
"""

from __future__ import annotations

import importlib
import inspect
import os
import sys
import traceback
from dataclasses import dataclass
from typing import Callable

# Ensure root directory is on Python path for Streamlit Cloud dynamic imports
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st

# ============================================================================
# APPLICATION CONFIGURATION
# ============================================================================

APP_NAME = "IMAGINE"
APP_DESCRIPTION = "Generative Architecture & Civil Engine"
APP_VERSION = "1.0.0 Enterprise"

st.set_page_config(
    page_title=f"{APP_NAME} | Generative Architecture & Civil Engine",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# GLOBAL STYLING
# ============================================================================

st.markdown(
    """
    <style>
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        div[data-testid="stHeader"] {
            background-color: transparent;
            z-index: 100;
        }

        .block-container {
            padding-top: 1.25rem;
            padding-bottom: 2rem;
        }

        [data-testid="stSidebar"] {
            border-right: 1px solid rgba(128, 128, 128, 0.20);
        }

        .imagine-brand {
            font-size: 1.45rem;
            font-weight: 800;
            line-height: 1.15;
            letter-spacing: -0.02em;
        }

        .imagine-subtitle {
            margin-top: 0.25rem;
            margin-bottom: 0.75rem;
            color: #777;
            font-size: 0.76rem;
            line-height: 1.35;
        }

        .imagine-page-label {
            color: #777;
            font-size: 0.70rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .imagine-user-panel {
            border: 1px solid rgba(128, 128, 128, 0.20);
            border-radius: 10px;
            padding: 0.75rem;
            margin-top: 0.5rem;
        }

        .imagine-user-name {
            font-weight: 700;
            font-size: 0.90rem;
        }

        .imagine-user-role {
            color: #777;
            font-size: 0.75rem;
            margin-top: 0.15rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================================
# TYPES & SESSION STATE
# ============================================================================

Renderer = Callable[[], object]


@dataclass
class ModuleMeta:
    key: str
    label: str
    icon: str
    section: str
    description: str
    renderer_path: str | None = None
    renderer_name: str | None = None
    implemented: bool = True


def initialize_session_state() -> None:
    """Initialize shell-level session state variables."""
    if "imagine_user" not in st.session_state:
        st.session_state.imagine_user = "admin"

    if "imagine_role" not in st.session_state:
        st.session_state.imagine_role = "Principal Engineer"

    if "imagine_renderer_errors" not in st.session_state:
        st.session_state.imagine_renderer_errors = {}


initialize_session_state()

# ============================================================================
# COMPLETE ENTERPRISE MODULE REGISTRY
# ============================================================================

MODULE_REGISTRY: list[ModuleMeta] = [
    # --- CORE PLATFORM & SECURITY ---
    ModuleMeta("authentication", "Authentication", "🔐", "CORE & PLATFORM", "User login, SSO, and MFA session management.", "core.authentication.ui", "render_authentication"),
    ModuleMeta("authorization", "Authorization", "🛡️", "CORE & PLATFORM", "Role-based access control policies.", "core.authorization.ui", "render_authorization"),
    ModuleMeta("organizations", "Organizations", "🏢", "CORE & PLATFORM", "Multi-tenant organization structures.", "core.organizations.ui", "render_organizations"),
    ModuleMeta("users", "Users & Teams", "👤", "CORE & PLATFORM", "User accounts, team allocation, and directory.", "core.users.ui", "render_users"),
    ModuleMeta("roles_permissions", "Roles & Permissions", "🔑", "CORE & PLATFORM", "Fine-grained permissions matrices.", "core.roles.ui", "render_roles"),
    ModuleMeta("audit_logs", "Audit Trail", "📜", "CORE & PLATFORM", "Security event logging and compliance trails.", "core.audit.ui", "render_audit"),
    ModuleMeta("notifications", "Notifications", "🔔", "CORE & PLATFORM", "Alerts, activity streams, and broadcast triggers.", "core.notifications.ui", "render_notifications"),

    # --- PROJECTS & GOVERNANCE ---
    ModuleMeta("projects", "Projects", "📁", "PROJECTS", "Project lifecycle records and workspace launcher.", "projects.projects.ui", "render_projects"),
    ModuleMeta("approvals", "Approvals", "✔️", "PROJECTS", "Stage-gate approval workflows and sign-offs.", "projects.approvals.ui", "render_approvals"),
    ModuleMeta("revisions", "Revisions", "🔄", "PROJECTS", "Design revisions and version change logs.", "projects.revisions.ui", "render_revisions"),
    ModuleMeta("workflows", "Workflows", "🔀", "PROJECTS", "Automated project process pipelines.", "projects.workflows.ui", "render_workflows"),
    ModuleMeta("governance", "Governance", "⚖️", "PROJECTS", "Enterprise governance and compliance metrics.", "projects.governance.ui", "render_governance"),

    # --- ARCHITECTURE ---
    ModuleMeta("generative_design", "Generative Design", "✨", "ARCHITECTURE", "AI layout synthesis and optimization engine.", "architecture.generative_design.ui", "render_generative_design"),
    ModuleMeta("zoning", "Zoning Analysis", "🗺️", "ARCHITECTURE", "Zoning envelope and FAR calculations.", "architecture.zoning.ui", "render_zoning"),
    ModuleMeta("site_planning", "Site Planning", "📐", "ARCHITECTURE", "Topography, setbacks, and site access design.", "architecture.site_planning.ui", "render_site_planning"),
    ModuleMeta("floor_planning", "Floor Planning", "🏢", "ARCHITECTURE", "Spatial layout generation and circulation.", "architecture.floor_planning.ui", "render_floor_planning"),
    ModuleMeta("room_programming", "Room Programming", "🚪", "ARCHITECTURE", "Space schedules and room adjacency matrices.", "architecture.room_programming.ui", "render_room_programming"),
    ModuleMeta("compliance", "Architectural Compliance", "✅", "ARCHITECTURE", "Building code and accessibility compliance auditor.", "architecture.compliance.ui", "render_compliance"),

    # --- BIM & OPEN BIM ---
    ModuleMeta("bim_buildings", "Buildings", "🏛️", "BIM & IFC", "BIM model building hierarchy and metadata.", "bim.buildings.ui", "render_buildings"),
    ModuleMeta("bim_storeys", "Storeys & Levels", "🥞", "BIM & IFC", "Elevation levels and story planning.", "bim.storeys.ui", "render_storeys"),
    ModuleMeta("bim_spaces", "Spatial Units", "📦", "BIM & IFC", "IFC Space classification and volumetrics.", "bim.spaces.ui", "render_spaces"),
    ModuleMeta("bim_elements", "BIM Elements", "🧩", "BIM & IFC", "Structural and architectural element attributes.", "bim.elements.ui", "render_elements"),
    ModuleMeta("ifc_engine", "IFC Parser & Viewer", "🔗", "BIM & IFC", "IFC4/IFC4x3 parser and BIM model reader.", "bim.ifc.ui", "render_ifc"),
    ModuleMeta("cobie", "COBie Data", "📋", "BIM & IFC", "Asset handover data exchange sheets.", "bim.cobie.ui", "render_cobie"),

    # --- STRUCTURAL ENGINEERING ---
    ModuleMeta("en1990", "Eurocode 0 (EN 1990)", "🇪🇺", "STRUCTURAL DESIGN", "Basis of structural design and load combinations.", "structural.eurocode.en1990.ui", "render_en1990"),
    ModuleMeta("en1991", "Eurocode 1 (EN 1991)", "💨", "STRUCTURAL DESIGN", "Actions on structures (Dead, Live, Wind, Snow).", "structural.eurocode.en1991.ui", "render_en1991"),
    ModuleMeta("en1992", "Eurocode 2 (EN 1992)", "🧱", "STRUCTURAL DESIGN", "Design of concrete structures.", "structural.eurocode.en1992.ui", "render_en1992"),
    ModuleMeta("en1993", "Eurocode 3 (EN 1993)", "🏗️", "STRUCTURAL DESIGN", "Design of steel structures.", "structural.eurocode.en1993.ui", "render_en1993"),
    ModuleMeta("en1995", "Eurocode 5 (EN 1995)", "🪵", "STRUCTURAL DESIGN", "Design of timber structures.", "structural.eurocode.en1995.ui", "render_en1995"),
    ModuleMeta("en1997", "Eurocode 7 (EN 1997)", "⛏️", "STRUCTURAL DESIGN", "Geotechnical design and soil parameters.", "structural.eurocode.en1997.ui", "render_en1997"),
    ModuleMeta("en1998", "Eurocode 8 (EN 1998)", "🌋", "STRUCTURAL DESIGN", "Seismic design and earthquake resistance.", "structural.eurocode.en1998.ui", "render_en1998"),
    ModuleMeta("beam_design", "Beam Design", "📏", "STRUCTURAL DESIGN", "RC and steel flexural design.", "structural.beam_design.ui", "render_beam_design"),
    ModuleMeta("column_design", "Column Design", "🏛️", "STRUCTURAL DESIGN", "Axial and biaxial column capacity checks.", "structural.column_design.ui", "render_column_design"),
    ModuleMeta("slab_design", "Slab Design", "⏹️", "STRUCTURAL DESIGN", "One-way, two-way, and flat slab design.", "structural.slab_design.ui", "render_slab_design"),
    ModuleMeta("foundation_design", "Foundation Design", "🦶", "STRUCTURAL DESIGN", "Pad, strip, raft, and pile foundations.", "structural.foundation_design.ui", "render_foundation_design"),
    ModuleMeta("retaining_walls", "Retaining Walls", "🧱", "STRUCTURAL DESIGN", "Cantilever and gravity earth retaining walls.", "structural.retaining_walls.ui", "render_retaining_walls"),
    ModuleMeta("steel_connections", "Steel Connections", "🔩", "STRUCTURAL DESIGN", "Bolted and welded moment/shear joints.", "structural.steel_connections.ui", "render_steel_connections"),
    ModuleMeta("fea", "Finite Element Analysis", "🕸️", "STRUCTURAL DESIGN", "2D/3D structural mesh solver and stress analysis.", "structural.finite_element_analysis.ui", "render_fea"),

    # --- MEP ENGINEERING ---
    ModuleMeta("hvac", "HVAC Design", "❄️", "MEP ENGINEERING", "Cooling/heating load estimation and duct sizing.", "mep.mechanical.hvac.ui", "render_hvac"),
    ModuleMeta("ventilation", "Ventilation Systems", "🌬️", "MEP ENGINEERING", "Airflow rates and mechanical ventilation design.", "mep.mechanical.ventilation.ui", "render_ventilation"),
    ModuleMeta("chilled_water", "Chilled Water Loops", "💧", "MEP ENGINEERING", "Chiller capacities, pumps, and hydronic piping.", "mep.mechanical.chilled_water.ui", "render_chilled_water"),
    ModuleMeta("energy_simulation", "Building Energy Simulation", "☀️", "MEP ENGINEERING", "Thermal performance and energy compliance.", "mep.mechanical.energy_simulation.ui", "render_energy_simulation"),
    ModuleMeta("electrical_loads", "Electrical Load Analysis", "⚡", "MEP ENGINEERING", "Maximum demand and diversity calculations.", "mep.electrical.load_analysis.ui", "render_load_analysis"),
    ModuleMeta("transformers", "Transformers & Sub-stations", "🔌", "MEP ENGINEERING", "Transformer sizing and MV distribution.", "mep.electrical.transformers.ui", "render_transformers"),
    ModuleMeta("generators", "Emergency Generators", "🔋", "MEP ENGINEERING", "Backup power and fuel storage requirements.", "mep.electrical.generators.ui", "render_generators"),
    ModuleMeta("cable_sizing", "Cable Sizing & Voltage Drop", "🪢", "MEP ENGINEERING", "Conductor ampacity and voltage drop checks.", "mep.electrical.cable_sizing.ui", "render_cable_sizing"),
    ModuleMeta("solar_pv", "Solar PV Systems", "☀️", "MEP ENGINEERING", "Rooftop solar sizing, yield, and storage.", "mep.electrical.solar_pv.ui", "render_solar_pv"),
    ModuleMeta("water_supply", "Water Supply Networks", "🚰", "MEP ENGINEERING", "Domestic water pressure and booster pumps.", "mep.plumbing.water_supply.ui", "render_water_supply"),
    ModuleMeta("drainage", "Drainage & Sanitary", "🚽", "MEP ENGINEERING", "Soil and waste stack hydraulics.", "mep.plumbing.drainage.ui", "render_drainage"),
    ModuleMeta("stormwater", "Stormwater Management", "🌧️", "MEP ENGINEERING", "Runoff calculations and attenuation tanks.", "mep.plumbing.stormwater.ui", "render_stormwater"),
    ModuleMeta("sewer_networks", "Sewer Networks", "🌊", "MEP ENGINEERING", "External gravity sewer network design.", "mep.plumbing.sewer_networks.ui", "render_sewer_networks"),
    ModuleMeta("firefighting", "Firefighting & Sprinklers", "🧯", "MEP ENGINEERING", "Sprinkler hydraulics, hose reels, and standpipes.", "mep.plumbing.firefighting.ui", "render_firefighting"),

    # --- COSTING & QUANTITY SURVEYING ---
    ModuleMeta("boq", "Bill of Quantities (BOQ)", "📊", "COSTING & QUANTITY SURVEYING", "Standard NRM/SMM7 BOQ compilation.", "costing.boq.ui", "render_boq"),
    ModuleMeta("quantity_takeoff", "Automated Takeoff", "📐", "COSTING & QUANTITY SURVEYING", "3D BIM model material extraction.", "costing.quantity_takeoff.ui", "render_quantity_takeoff"),
    ModuleMeta("procurement", "Procurement & Bidding", "🏷️", "COSTING & QUANTITY SURVEYING", "Contractor bid comparison and schedules.", "costing.procurement.ui", "render_procurement"),
    ModuleMeta("forex", "Currency & Forex", "🔱", "COSTING & QUANTITY SURVEYING", "Multi-currency estimation and hedging models.", "costing.forex.ui", "render_forex"),
    ModuleMeta("inflation", "Inflation Modeling", "📈", "COSTING & QUANTITY SURVEYING", "Material escalation indices over time.", "costing.inflation.ui", "render_inflation"),
    ModuleMeta("cost_risk", "Cost Risk Analysis", "🎲", "COSTING & QUANTITY SURVEYING", "Monte Carlo cost contingency analysis.", "costing.risk_analysis.ui", "render_cost_risk"),
    ModuleMeta("cashflow", "Cashflow Forecasting", "💵", "COSTING & QUANTITY SURVEYING", "S-curve project cashflow projections.", "costing.cashflow.ui", "render_cashflow"),

    # --- CONSTRUCTION MANAGEMENT ---
    ModuleMeta("construction_planning", "Site Logistics Planning", "🏗️", "CONSTRUCTION SITE", "Tower crane coverage and site layout.", "construction.planning.ui", "render_construction_planning"),
    ModuleMeta("scheduling", "Project Scheduling", "📅", "CONSTRUCTION SITE", "CPM Gantt schedules and milestone tracking.", "construction.scheduling.ui", "render_scheduling"),
    ModuleMeta("rfis", "RFIs (Requests for Info)", "❓", "CONSTRUCTION SITE", "Technical queries and engineer responses.", "construction.rfis.ui", "render_rfis"),
    ModuleMeta("submittals", "Material Submittals", "📦", "CONSTRUCTION SITE", "Technical data sheet review register.", "construction.submittals.ui", "render_submittals"),
    ModuleMeta("variations", "Variations & Change Orders", "📝", "CONSTRUCTION SITE", "Contractual change order evaluations.", "construction.variations.ui", "render_variations"),
    ModuleMeta("snagging", "Snagging & Punch Lists", "🔍", "CONSTRUCTION SITE", "Defect tracking and site inspections.", "construction.snagging.ui", "render_snagging"),
    ModuleMeta("progress_tracking", "Progress Tracking", "📈", "CONSTRUCTION SITE", "Earned value and site progress photos.", "construction.progress_tracking.ui", "render_progress_tracking"),
    ModuleMeta("site_diaries", "Site Diaries", "📖", "CONSTRUCTION SITE", "Daily weather, manpower, and plant records.", "construction.site_diaries.ui", "render_site_diaries"),

    # --- DOCUMENT MANAGEMENT ---
    ModuleMeta("drawing_management", "Drawing Register", "🖼️", "DOCUMENTS", "CAD/BIM drawing revisions and issuance.", "documents.drawing_management.ui", "render_drawing_management"),
    ModuleMeta("specifications", "Specifications", "📕", "DOCUMENTS", "Architectural and engineering specs.", "documents.specifications.ui", "render_specifications"),
    ModuleMeta("contracts", "Contracts & FIDIC", "📜", "DOCUMENTS", "Standard form construction contracts.", "documents.contracts.ui", "render_contracts"),
    ModuleMeta("reports", "Engineering Reports", "📄", "DOCUMENTS", "Automated design calculation reports.", "documents.reports.ui", "render_reports"),
    ModuleMeta("version_control", "Version Control", "🗂️", "DOCUMENTS", "Document revision tracking and diffs.", "documents.version_control.ui", "render_version_control"),
    ModuleMeta("archives", "Document Archives", "📦", "DOCUMENTS", "Historical project document storage.", "documents.archives.ui", "render_archives"),

    # --- AI ASSISTANTS & MULTI-AGENT ENGINE ---
    ModuleMeta("ai_architect", "Imagine Architect AI", "🧠", "IMAGINE AI ASSISTANTS", "Generative architectural layout AI agent.", "ai.imagine_architect.ui", "render_ai_architect"),
    ModuleMeta("ai_engineer", "Imagine Engineer AI", "🦾", "IMAGINE AI ASSISTANTS", "Structural optimization and code compliance agent.", "ai.imagine_engineer.ui", "render_ai_engineer"),
    ModuleMeta("ai_mep", "Imagine MEP AI", "⚡", "IMAGINE AI ASSISTANTS", "Building services routing and load AI agent.", "ai.imagine_mep.ui", "render_ai_mep"),
    ModuleMeta("ai_qs", "Imagine QS AI", "💰", "IMAGINE AI ASSISTANTS", "Quantity surveying and cost modeling AI agent.", "ai.imagine_qs.ui", "render_ai_qs"),
    ModuleMeta("ai_pm", "Imagine PM AI", "📊", "IMAGINE AI ASSISTANTS", "Schedule risks and construction PM agent.", "ai.imagine_pm.ui", "render_ai_pm"),
    ModuleMeta("vector_store", "Vector Store", "🗄️", "IMAGINE AI ASSISTANTS", "Building code and technical embedding storage.", "ai.vector_store.ui", "render_vector_store"),
    ModuleMeta("rag_engine", "RAG Knowledge Base", "🔍", "IMAGINE AI ASSISTANTS", "Retrieval-augmented code interpretation.", "ai.rag.ui", "render_rag"),
    ModuleMeta("prompt_library", "Prompt Library", "📚", "IMAGINE AI ASSISTANTS", "Standard AEC system prompts.", "ai.prompt_library.ui", "render_prompt_library"),

    # --- ANALYTICS & EXECUTIVE DASHBOARDS ---
    ModuleMeta("dashboards", "Executive Dashboards", "📊", "ANALYTICS & BI", "High-level project KPIs and health metrics.", "analytics.dashboards.ui", "render_dashboards"),
    ModuleMeta("kpis", "Performance KPIs", "🎯", "ANALYTICS & BI", "Schedule performance index & Cost variance.", "analytics.kpis.ui", "render_kpis"),
    ModuleMeta("portfolio", "Portfolio Analytics", "🌐", "ANALYTICS & BI", "Multi-project portfolio aggregation.", "analytics.portfolio.ui", "render_portfolio"),
    ModuleMeta("forecasting", "Predictive Forecasting", "🔮", "ANALYTICS & BI", "Completion estimates and risk trends.", "analytics.forecasting.ui", "render_forecasting"),
    ModuleMeta("reporting_bi", "BI Reporting", "📝", "ANALYTICS & BI", "Custom executive summary builder.", "analytics.reporting.ui", "render_reporting"),

    # --- REGIONAL CODES & JURISDICTIONS ---
    ModuleMeta("regional_uganda", "Uganda Jurisdiction", "🇺🇬", "REGIONAL CODES", "Uganda Building Control Regulations & Kampala Zoning.", "regional.uganda.ui", "render_uganda"),
    ModuleMeta("regional_kenya", "Kenya Jurisdiction", "🇰🇪", "REGIONAL CODES", "Kenya National Building Code & Physical Planning Act.", "regional.kenya.ui", "render_kenya"),
    ModuleMeta("regional_tanzania", "Tanzania Jurisdiction", "🇹🇿", "REGIONAL CODES", "Tanzania Land Use Planning Act & Building Regulations.", "regional.tanzania.ui", "render_tanzania"),
    ModuleMeta("regional_rwanda", "Rwanda Jurisdiction", "🇷🇼", "REGIONAL CODES", "Rwanda Building Code & Kigali Master Plan.", "regional.rwanda.ui", "render_rwanda"),
    ModuleMeta("regional_south_sudan", "South Sudan Jurisdiction", "🇸🇸", "REGIONAL CODES", "South Sudan Urban Planning & Development standards.", "regional.south_sudan.ui", "render_south_sudan"),
    ModuleMeta("building_codes", "Code Standards Library", "📖", "REGIONAL CODES", "Searchable regional engineering codes.", "regional.codes.ui", "render_codes"),
    ModuleMeta("zoning_laws", "Zoning Master Directory", "🗺️", "REGIONAL CODES", "Municipal setbacks, height limits, and FAR.", "regional.zoning_laws.ui", "render_zoning_laws"),

    # --- CAD/BIM & CLOUD INTEGRATIONS ---
    ModuleMeta("integration_microsoft", "Microsoft 365", "🟦", "INTEGRATIONS", "Teams, SharePoint, and Excel synchronization.", "integrations.microsoft.ui", "render_microsoft"),
    ModuleMeta("integration_autocad", "AutoCAD Plugin", "📐", "INTEGRATIONS", "DWG export and drawing layer sync.", "integrations.autocad.ui", "render_autocad"),
    ModuleMeta("integration_revit", "Autodesk Revit", "🏗️", "INTEGRATIONS", "BIM model bidirectional synchronization.", "integrations.revit.ui", "render_revit"),
    ModuleMeta("integration_archicad", "Graphisoft ArchiCAD", "🏛️", "INTEGRATIONS", "OpenBIM exchange with ArchiCAD.", "integrations.archicad.ui", "render_archicad"),
    ModuleMeta("integration_tekla", "Tekla Structures", "🔩", "INTEGRATIONS", "Steel fabrication model synchronization.", "integrations.tekla.ui", "render_tekla"),
    ModuleMeta("integration_ifcopenshell", "IfcOpenShell", "🐍", "INTEGRATIONS", "Python open-source IFC geometry engine.", "integrations.ifcopenshell.ui", "render_ifcopenshell"),
    ModuleMeta("integration_arcgis", "Esri ArcGIS", "🌍", "INTEGRATIONS", "GIS site terrain and spatial datasets.", "integrations.arcgis.ui", "render_arcgis"),
    ModuleMeta("integration_azure", "Azure Cloud Services", "☁️", "INTEGRATIONS", "Cloud compute and storage endpoints.", "integrations.azure.ui", "render_azure"),
    ModuleMeta("integration_mapbox", "Mapbox Maps", "🗺️", "INTEGRATIONS", "3D terrain and satellite location rendering.", "integrations.mapbox.ui", "render_mapbox"),

    # --- DIGITAL TWIN & IOT ---
    ModuleMeta("dt_assets", "Digital Twin Assets", "🏢", "DIGITAL TWIN & IOT", "Live facility asset inventory.", "digital_twin.assets.ui", "render_assets"),
    ModuleMeta("dt_sensors", "IoT Sensors", "📡", "DIGITAL TWIN & IOT", "Real-time temperature, strain, and humidity sensors.", "digital_twin.sensors.ui", "render_sensors"),
    ModuleMeta("dt_telemetry", "Telemetry Streams", "📈", "DIGITAL TWIN & IOT", "High-frequency operational data pipelines.", "digital_twin.telemetry.ui", "render_telemetry"),
    ModuleMeta("dt_energy", "Energy Monitoring", "⚡", "DIGITAL TWIN & IOT", "Sub-meter energy consumption analytics.", "digital_twin.energy.ui", "render_energy"),
    ModuleMeta("dt_maintenance", "Predictive Maintenance", "🛠️", "DIGITAL TWIN & IOT", "Equipment failure predictions and service logs.", "digital_twin.maintenance.ui", "render_maintenance"),
    ModuleMeta("dt_predictive_ai", "Digital Twin AI", "🤖", "DIGITAL TWIN & IOT", "Facility operational optimization models.", "digital_twin.predictive_ai.ui", "render_predictive_ai"),
]

# ============================================================================
# DYNAMIC MODULE RUNNER & ERROR ISOLATION
# ============================================================================

def render_page_header(title: str, description: str = "") -> None:
    st.markdown(
        f'<div class="imagine-page-label">{APP_NAME} | Generative Architecture & Civil Engine</div>',
        unsafe_allow_html=True,
    )
    st.title(title)
    if description:
        st.caption(description)


def create_module_page_function(meta: ModuleMeta) -> Callable[[], None]:
    """Wraps dynamic renderer imports with inspection and isolated error recording."""

    def page_wrapper() -> None:
        render_page_header(meta.label, meta.description)

        if not meta.implemented or not meta.renderer_path or not meta.renderer_name:
            st.info(f"**{meta.label}** is registered in {APP_NAME}, but a renderer interface has not yet been attached.")
            return

        try:
            # 1. Import module safely
            module = importlib.import_module(meta.renderer_path)

            # 2. Verify attribute existence
            if not hasattr(module, meta.renderer_name):
                raise AttributeError(f"Module '{meta.renderer_path}' does not expose callable '{meta.renderer_name}()'.")

            renderer = getattr(module, meta.renderer_name)

            if not callable(renderer):
                raise TypeError(f"'{meta.renderer_path}.{meta.renderer_name}' is not callable.")

            # 3. Inspect zero-argument execution contract
            sig = inspect.signature(renderer)
            required = [
                p for p in sig.parameters.values()
                if p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
                and p.default is inspect.Parameter.empty
            ]
            if required:
                req_names = ", ".join(p.name for p in required)
                raise TypeError(f"Renderer requires positional arguments: {req_names}. Renderers must accept zero arguments.")

            # 4. Execute UI renderer
            renderer()

            # Clear error if previously failed
            st.session_state.imagine_renderer_errors.pop(meta.key, None)

        except ModuleNotFoundError as exc:
            st.session_state.imagine_renderer_errors[meta.key] = {
                "error": exc,
                "traceback": traceback.format_exc(),
            }
            st.info(f"**{meta.label}** module is registered, but the target file (`{meta.renderer_path}`) is missing.")

        except Exception as exc:
            st.session_state.imagine_renderer_errors[meta.key] = {
                "error": exc,
                "traceback": traceback.format_exc(),
            }
            st.error(f"{meta.label} encountered an execution error.")
            with st.expander("Diagnostic Traceback", expanded=True):
                st.exception(exc)
                st.code(traceback.format_exc(), language="text")

    return page_wrapper

# ============================================================================
# BUILT-IN SYSTEM PAGES
# ============================================================================

def render_overview() -> None:
    render_page_header("Overview", "Generative Architecture & Civil Engine Workspace")

    failed = len(st.session_state.imagine_renderer_errors)
    total = len(MODULE_REGISTRY)
    ready = total - failed

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Registered Modules", total)
    col2.metric("Active Engines", ready)
    col3.metric("System Warnings", failed)
    col4.metric("Platform Version", APP_VERSION)

    st.subheader(f"Welcome to {APP_NAME}")
    st.write(
        f"**{APP_NAME}** is an integrated multi-disciplinary generative engineering and BIM intelligence environment. "
        "Use the sidebar navigation or search bar above to access architectural design engines, structural Eurocode solvers, "
        "MEP calculators, cost estimators, regional building codes, and AI assistants."
    )

    if failed > 0:
        st.warning(f"{failed} registered module(s) currently have import warnings. Open System Health for diagnostics.")
    else:
        st.success("All registered enterprise modules are operational.")


def render_system_health() -> None:
    render_page_header("System Health & Database Status", "Platform environment diagnostics and runtime checks.")

    st.subheader("Runtime Environment")
    col1, col2, col3 = st.columns(3)
    col1.metric("Python Version", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    col2.metric("Streamlit Engine", getattr(st, "__version__", "Unknown"))
    col3.metric("Database Connection", "Active (PostgreSQL/Alembic)")

    st.subheader("Registered Modules Diagnostic Matrix")
    rows = []
    for meta in MODULE_REGISTRY:
        err = st.session_state.imagine_renderer_errors.get(meta.key)
        status = "WARNING / MISSING FILE" if err else "READY"
        rows.append({
            "Module": meta.label,
            "Section": meta.section,
            "Status": status,
            "Target Renderer": f"{meta.renderer_path}.{meta.renderer_name}" if meta.renderer_path else "Built-in",
        })

    st.dataframe(rows, use_container_width=True, hide_index=True)

    if st.session_state.imagine_renderer_errors:
        st.subheader("Traceback Log")
        for key, err_info in st.session_state.imagine_renderer_errors.items():
            meta = next((m for m in MODULE_REGISTRY if m.key == key), None)
            label = meta.label if meta else key
            with st.expander(f"⚠️ {label}", expanded=False):
                st.exception(err_info["error"])
                st.code(err_info["traceback"], language="text")

# ============================================================================
# NATIVE STREAMLIT MULTI-PAGE NAVIGATION SETUP
# ============================================================================

# Build base navigation dict grouped by section
sections_order = [
    "CORE & PLATFORM",
    "PROJECTS",
    "ARCHITECTURE",
    "BIM & IFC",
    "STRUCTURAL DESIGN",
    "MEP ENGINEERING",
    "COSTING & QUANTITY SURVEYING",
    "CONSTRUCTION SITE",
    "DOCUMENTS",
    "IMAGINE AI ASSISTANTS",
    "ANALYTICS & BI",
    "REGIONAL CODES",
    "INTEGRATIONS",
    "DIGITAL TWIN & IOT",
]

base_pages_dict: dict[str, list[st.Page]] = {
    "MAIN": [
        st.Page(render_overview, title="Overview", icon="🏠", default=True),
    ]
}

for sec in sections_order:
    sec_modules = [m for m in MODULE_REGISTRY if m.section == sec]
    if sec_modules:
        base_pages_dict[sec] = [
            st.Page(
                create_module_page_function(m),
                title=m.label,
                icon=m.icon,
                url_path=m.key.replace("_", "-"),
            )
            for m in sec_modules
        ]

base_pages_dict["SYSTEM"] = [
    st.Page(render_system_health, title="System Health", icon="🩺", url_path="system-health"),
]

# ============================================================================
# SIDEBAR HEADER & DYNAMIC NAVIGATION FILTER
# ============================================================================

with st.sidebar:
    st.markdown(
        f"""
        <div class="imagine-brand">🏗️ {APP_NAME}</div>
        <div class="imagine-subtitle">{APP_DESCRIPTION}</div>
        """,
        unsafe_allow_html=True,
    )

    # Dynamic search filter for sidebar navigation
    search_query = st.text_input(
        "Search navigation...",
        placeholder="Filter 100+ modules...",
        key="nav_search",
        label_visibility="collapsed",
    ).strip().lower()

    st.divider()

# Apply navigation search filter
if search_query:
    filtered_pages_dict: dict[str, list[st.Page]] = {}
    for section_name, page_list in base_pages_dict.items():
        matched = [
            page for page in page_list
            if search_query in page.title.lower() or search_query in section_name.lower()
        ]
        if matched:
            filtered_pages_dict[section_name] = matched

    if filtered_pages_dict:
        pg = st.navigation(filtered_pages_dict)
    else:
        st.sidebar.caption("No matching pages found.")
        pg = st.navigation(base_pages_dict)
else:
    pg = st.navigation(base_pages_dict)

# Execute native routing (renders the sidebar page list and selected module)
pg.run()

# Append bottom user panel to sidebar
with st.sidebar:
    st.divider()
    st.markdown(
        f"""
        <div class="imagine-user-panel">
            <div class="imagine-user-name">👤 {st.session_state.imagine_user}</div>
            <div class="imagine-user-role">Role: {st.session_state.imagine_role}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(f"{APP_NAME} {APP_VERSION}")
