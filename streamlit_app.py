"""
streamlit_app.py
----------------
IMAGINE - Generative Architecture & Civil Engine
Resilient Streamlit Application Shell & Centralized Renderer Registry.

This shell handles:
    - Application layout & global glassmorphism CSS
    - Module registry for Architecture, Structural Analysis, Projects, BIM, MEP, Costing, AI, & System
    - Dynamic safe module loading & runtime error isolation
    - Projects ORM model registration
    - Comprehensive system health diagnostics
"""

from __future__ import annotations

import importlib
import inspect
import sys
import traceback
from dataclasses import dataclass, field
from typing import Any, Callable

import streamlit as st


# ============================================================================
# APPLICATION CONFIGURATION
# ============================================================================

APP_NAME = "IMAGINE"
APP_SUBTITLE = "Generative Architecture & Civil Engine"
APP_VERSION = "1.0.0 Alpha"


st.set_page_config(
    page_title=f"{APP_NAME} | Generative Architecture & Civil Engine",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================================
# GLOBAL STYLES
# ============================================================================

st.markdown(
    """
    <style>
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        header { visibility: hidden; }

        .block-container {
            padding-top: 1rem;
            padding-bottom: 2rem;
        }

        [data-testid="stSidebar"] {
            border-right: 1px solid rgba(128, 128, 128, 0.18);
        }

        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1rem;
        }

        .imagine-brand {
            font-size: 1.45rem;
            font-weight: 800;
            line-height: 1.2;
            letter-spacing: 0.02em;
        }

        .imagine-subtitle {
            color: #777;
            font-size: 0.78rem;
            line-height: 1.35;
            margin-top: 0.2rem;
        }

        .imagine-section {
            color: #777;
            font-size: 0.68rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            margin-top: 1rem;
            margin-bottom: 0.3rem;
        }

        .imagine-user-panel {
            border: 1px solid rgba(128, 128, 128, 0.18);
            border-radius: 10px;
            padding: 0.75rem;
            margin-top: 0.5rem;
        }

        .imagine-user-name {
            font-weight: 700;
            font-size: 0.9rem;
        }

        .imagine-user-role {
            color: #777;
            font-size: 0.75rem;
        }

        .imagine-page-label {
            color: #777;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: -0.35rem;
        }

        .imagine-status-ready {
            color: #16803c;
            font-weight: 700;
        }

        .imagine-status-error {
            color: #c62828;
            font-weight: 700;
        }

        .imagine-status-warning {
            color: #a86500;
            font-weight: 700;
        }

        .imagine-kpi {
            border: 1px solid rgba(128, 128, 128, 0.18);
            border-radius: 12px;
            padding: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================================
# TYPES & DATACLASSES
# ============================================================================

Renderer = Callable[[], Any]


@dataclass
class ModuleDefinition:
    key: str
    label: str
    icon: str
    section: str
    description: str

    renderer_path: str | None = None
    renderer_name: str = ""
    implemented: bool = False

    renderer: Renderer | None = field(default=None, repr=False)
    import_error: BaseException | None = field(default=None, repr=False)
    traceback_text: str = field(default="", repr=False)
    loaded: bool = False


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if "imagine_selected_module" not in st.session_state:
    st.session_state.imagine_selected_module = "overview"

if "imagine_renderer_errors" not in st.session_state:
    st.session_state.imagine_renderer_errors = {}

if "imagine_module_status" not in st.session_state:
    st.session_state.imagine_module_status = {}

if "imagine_user" not in st.session_state:
    st.session_state.imagine_user = "admin"

if "imagine_role" not in st.session_state:
    st.session_state.imagine_role = "Administrator"


# ============================================================================
# SAFE IMPORTS & RENDERER RESOLUTION
# ============================================================================

def _safe_import(module_path: str) -> tuple[Any | None, BaseException | None, str]:
    """Import a module safely without raising unhandled exceptions to the main thread."""
    try:
        module = importlib.import_module(module_path)
        return module, None, ""
    except BaseException as exc:
        return None, exc, traceback.format_exc()


def _resolve_renderer(
    module_path: str,
    renderer_name: str,
) -> tuple[Renderer | None, BaseException | None, str]:
    """Import a module and resolve its zero-argument Streamlit renderer adapter."""
    module, import_error, import_traceback = _safe_import(module_path)

    if import_error is not None:
        return None, import_error, import_traceback

    try:
        renderer = getattr(module, renderer_name)
    except AttributeError:
        return (
            None,
            RuntimeError(f"{module_path} does not expose {renderer_name}()."),
            traceback.format_exc(),
        )

    if not callable(renderer):
        return None, TypeError(f"{module_path}.{renderer_name} is not callable."), ""

    try:
        signature = inspect.signature(renderer)
        required = [
            p for p in signature.parameters.values()
            if p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
            and p.default is inspect.Parameter.empty
        ]

        if required:
            names = ", ".join(p.name for p in required)
            return (
                None,
                TypeError(
                    f"{module_path}.{renderer_name} requires arguments ({names}). "
                    "IMAGINE renderers must expose a zero-argument adapter."
                ),
                "",
            )
    except (TypeError, ValueError):
        pass

    return renderer, None, ""


# ============================================================================
# PROJECT MODEL REGISTRATION
# ============================================================================

def _register_project_models() -> tuple[bool, BaseException | None, str]:
    """Register SQLAlchemy ORM models prior to query execution."""
    try:
        importlib.import_module("database.models.organization")
        importlib.import_module("database.models.user")
        importlib.import_module("projects.approvals.models")
        importlib.import_module("projects.revisions.models")
        importlib.import_module("projects.projects.models")
        return True, None, ""
    except BaseException as exc:
        return False, exc, traceback.format_exc()


(_PROJECT_MODELS_OK, _PROJECT_MODELS_ERROR, _PROJECT_MODELS_TRACEBACK) = _register_project_models()


# ============================================================================
# CENTRALIZED MODULE REGISTRY
# ============================================================================

MODULES: list[ModuleDefinition] = [
    # ------------------------------------------------------------------------
    # MAIN
    # ------------------------------------------------------------------------
    ModuleDefinition(
        key="overview",
        label="Overview",
        icon="🏠",
        section="MAIN",
        description="IMAGINE business ecosystem and application hub.",
        implemented=True,
    ),

    # ------------------------------------------------------------------------
    # ARCHITECTURE
    # ------------------------------------------------------------------------
    ModuleDefinition(
        key="architecture",
        label="Architecture Suite",
        icon="🏛️",
        section="ARCHITECTURE",
        description="Generative architecture workspace and layout generator.",
        renderer_path="architecture.ui",
        renderer_name="render_architecture",
        implemented=True,
    ),
    ModuleDefinition(
        key="site_planning",
        label="Site Planning",
        icon="📐",
        section="ARCHITECTURE",
        description="Site planning, topography, and setback analysis.",
        renderer_path="architecture.site_planning.ui",
        renderer_name="render_site_planning",
        implemented=True,
    ),
    ModuleDefinition(
        key="zoning",
        label="Zoning",
        icon="🗺️",
        section="ARCHITECTURE",
        description="Land-use classification and FAR compliance.",
        renderer_path="architecture.zoning.ui",
        renderer_name="render_zoning",
        implemented=True,
    ),
    ModuleDefinition(
        key="floor_planning",
        label="Floor Planning",
        icon="🏢",
        section="ARCHITECTURE",
        description="Generative floor plans and spatial topology.",
        renderer_path="architecture.floor_planning.ui",
        renderer_name="render_floor_planning",
        implemented=True,
    ),
    ModuleDefinition(
        key="room_programming",
        label="Room Programming",
        icon="🚪",
        section="ARCHITECTURE",
        description="Room scheduling, area metrics, and spatial adjacency.",
        renderer_path="architecture.room_programming.ui",
        renderer_name="render_room_programming",
        implemented=True,
    ),
    ModuleDefinition(
        key="compliance",
        label="Compliance",
        icon="✅",
        section="ARCHITECTURE",
        description="Building code, fire safety, and accessibility verification.",
        renderer_path="architecture.compliance.ui",
        renderer_name="render_compliance",
        implemented=True,
    ),
    ModuleDefinition(
        key="generative_design",
        label="Generative Design",
        icon="✨",
        section="ARCHITECTURE",
        description="AI multi-objective architectural optimization.",
        renderer_path="architecture.generative_design.ui",
        renderer_name="render_generative_design",
        implemented=True,
    ),

    # ------------------------------------------------------------------------
    # STRUCTURAL ANALYSIS AI
    # ------------------------------------------------------------------------
    ModuleDefinition(
        key="fea",
        label="FEA Structural Analysis",
        icon="🕸️",
        section="STRUCTURAL ANALYSIS",
        description="2D/3D frame FEA solver, stiffness matrix, and internal action diagrams.",
        renderer_path="structure.fea.ui",
        renderer_name="render_fea",
        implemented=True,
    ),
    ModuleDefinition(
        key="concrete_design",
        label="Concrete Design",
        icon="🧱",
        section="STRUCTURAL ANALYSIS",
        description="Reinforced concrete member sizing, flexure/shear, and rebar detailing.",
        renderer_path="structure.concrete_design.ui",
        renderer_name="render_concrete_design",
        implemented=True,
    ),
    ModuleDefinition(
        key="steel_design",
        label="Steel Design",
        icon="⚙️",
        section="STRUCTURAL ANALYSIS",
        description="Structural steel sizing, section classification, LTB, and AISC/EC3 checks.",
        renderer_path="structure.steel_design.ui",
        renderer_name="render_steel_design",
        implemented=True,
    ),
    ModuleDefinition(
        key="foundation_design",
        label="Foundation Design",
        icon="⚓",
        section="STRUCTURAL ANALYSIS",
        description="Geotechnical bearing capacity, pad footings, piles, and punching shear.",
        renderer_path="structure.foundation_design.ui",
        renderer_name="render_foundation_design",
        implemented=True,
    ),
    ModuleDefinition(
        key="load_calculations",
        label="Load Calculations",
        icon="🏋️",
        section="STRUCTURAL ANALYSIS",
        description="Gravity dead/live, wind pressure gradient, and ELF seismic base shear.",
        renderer_path="structure.load_calculations.ui",
        renderer_name="render_load_calculations",
        implemented=True,
    ),

    # ------------------------------------------------------------------------
    # PROJECTS
    # ------------------------------------------------------------------------
    ModuleDefinition(
        key="projects",
        label="Projects",
        icon="📁",
        section="PROJECTS",
        description="Project portfolio, records, and active metadata.",
        renderer_path="projects.projects.ui",
        renderer_name="render_projects",
        implemented=True,
    ),
    ModuleDefinition(
        key="approvals",
        label="Approvals",
        icon="✔️",
        section="PROJECTS",
        description="Multi-tier sign-off workflows and design approvals.",
        renderer_path="projects.approvals.ui",
        renderer_name="render_approvals",
        implemented=True,
    ),
    ModuleDefinition(
        key="revisions",
        label="Revisions",
        icon="🔄",
        section="PROJECTS",
        description="Version control, delta tracking, and design revisions.",
        renderer_path="projects.revisions.ui",
        renderer_name="render_revisions",
        implemented=True,
    ),
    ModuleDefinition(
        key="workflows",
        label="Workflows",
        icon="🔀",
        section="PROJECTS",
        description="Automated stage-gate project workflows.",
        renderer_path="projects.workflows.ui",
        renderer_name="render_workflows",
        implemented=True,
    ),
    ModuleDefinition(
        key="governance",
        label="Governance",
        icon="⚖️",
        section="PROJECTS",
        description="Audit logging, legal compliance, and quality control.",
        renderer_path="projects.governance.ui",
        renderer_name="render_governance",
        implemented=True,
    ),

    # ------------------------------------------------------------------------
    # BIM & DIGITAL TWIN
    # ------------------------------------------------------------------------
    ModuleDefinition(
        key="bim_elements",
        label="BIM & IFC Model",
        icon="🧊",
        section="BIM & TWIN",
        description="IFC4 schema parsing, spatial hierarchy, and COBie export.",
        implemented=False,
    ),
    ModuleDefinition(
        key="digital_twin",
        label="Digital Twin",
        icon="📡",
        section="BIM & TWIN",
        description="IoT sensor telemetry, structural health, and predictive AI.",
        implemented=False,
    ),

    # ------------------------------------------------------------------------
    # MEP ENGINEERING
    # ------------------------------------------------------------------------
    ModuleDefinition(
        key="hvac",
        label="HVAC & Mechanical",
        icon="❄️",
        section="MEP",
        description="Cooling/heating load, air handling, and energy simulation.",
        implemented=False,
    ),
    ModuleDefinition(
        key="electrical",
        label="Electrical Systems",
        icon="⚡",
        section="MEP",
        description="Cable sizing, distribution boards, transformers, and Solar PV.",
        implemented=False,
    ),
    ModuleDefinition(
        key="plumbing",
        label="Plumbing & Drainage",
        icon="🚰",
        section="MEP",
        description="Water supply, stormwater networks, and firefighting systems.",
        implemented=False,
    ),

    # ------------------------------------------------------------------------
    # COSTING & QUANTITY SURVEYING
    # ------------------------------------------------------------------------
    ModuleDefinition(
        key="boq_takeoff",
        label="Quantity Takeoff & BOQ",
        icon="💰",
        section="COSTING",
        description="Automatic material quantity takeoff, BOQ rates, and cashflow risk.",
        implemented=False,
    ),

    # ------------------------------------------------------------------------
    # IMAGINE AI AGENTS
    # ------------------------------------------------------------------------
    ModuleDefinition(
        key="imagine_ai",
        label="IMAGINE Copilots",
        icon="🤖",
        section="AI SUITE",
        description="Specialized AI agents for Architect, Structural Engineer, MEP, & QS.",
        implemented=False,
    ),

    # ------------------------------------------------------------------------
    # SYSTEM Diagnostics
    # ------------------------------------------------------------------------
    ModuleDefinition(
        key="system_health",
        label="System Health",
        icon="🩺",
        section="SYSTEM",
        description="IMAGINE diagnostics, runtime performance, and renderer state.",
        implemented=True,
    ),
]


MODULE_REGISTRY: dict[str, ModuleDefinition] = {
    module.key: module for module in MODULES
}


# ============================================================================
# RENDERER LOADING
# ============================================================================

def _load_module_renderer(module: ModuleDefinition) -> None:
    """Resolve module renderers lazily/on startup safely."""
    if not module.implemented:
        module.loaded = False
        return

    if not module.renderer_path:
        module.loaded = True
        st.session_state.imagine_module_status[module.key] = {
            "loaded": True,
            "implemented": True,
            "error": None,
        }
        return

    renderer, error, error_traceback = _resolve_renderer(
        module.renderer_path,
        module.renderer_name,
    )

    module.renderer = renderer
    module.import_error = error
    module.traceback_text = error_traceback
    module.loaded = renderer is not None

    st.session_state.imagine_module_status[module.key] = {
        "loaded": module.loaded,
        "implemented": module.implemented,
        "error": error,
    }

    if error is not None:
        st.session_state.imagine_renderer_errors[module.key] = {
            "error": error,
            "traceback": error_traceback,
        }


def _load_all_renderers() -> None:
    for module in MODULES:
        _load_module_renderer(module)


_load_all_renderers()


# ============================================================================
# NAVIGATION HELPERS
# ============================================================================

def _select_module(key: str) -> None:
    st.session_state.imagine_selected_module = key


def _module_button_label(module: ModuleDefinition) -> str:
    label = f"{module.icon} {module.label}"
    if module.renderer_path and not module.loaded:
        label += " ⚠️"
    return label


def _render_navigation_section(section: str) -> None:
    section_modules = [m for m in MODULES if m.section == section]
    if not section_modules:
        return

    st.markdown(f'<div class="imagine-section">{section}</div>', unsafe_allow_html=True)

    for module in section_modules:
        selected = st.session_state.imagine_selected_module == module.key

        if st.button(
            _module_button_label(module),
            key=f"imagine_nav_{module.key}",
            use_container_width=True,
            type="primary" if selected else "secondary",
        ):
            _select_module(module.key)
            st.rerun()


# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

def _render_sidebar() -> None:
    """Full IMAGINE navigation panel with categorised sections."""
    with st.sidebar:
        st.markdown(
            f"""
            <div class="imagine-brand">
                🏗️ {APP_NAME}
            </div>
            <div class="imagine-subtitle">
                {APP_SUBTITLE}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        _render_navigation_section("MAIN")
        _render_navigation_section("ARCHITECTURE")
        _render_navigation_section("STRUCTURAL ANALYSIS")
        _render_navigation_section("PROJECTS")
        _render_navigation_section("BIM & TWIN")
        _render_navigation_section("MEP")
        _render_navigation_section("COSTING")
        _render_navigation_section("AI SUITE")
        _render_navigation_section("SYSTEM")

        st.divider()

        st.markdown('<div class="imagine-section">USER PANEL</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="imagine-user-panel">
                <div class="imagine-user-name">
                    👤 {st.session_state.imagine_user}
                </div>
                <div class="imagine-user-role">
                    Role: {st.session_state.imagine_role}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")

        if st.button("🚪 Logout", key="imagine_logout", use_container_width=True):
            st.session_state.imagine_user = "admin"
            st.session_state.imagine_role = "Administrator"
            st.session_state.imagine_selected_module = "overview"
            st.rerun()

        st.caption(f"{APP_NAME} {APP_VERSION}")


# ============================================================================
# PAGE HEADER & CORE VIEWS
# ============================================================================

def _render_page_header(title: str, description: str = "") -> None:
    st.markdown('<div class="imagine-page-label">IMAGINE | Generative Architecture & Civil Engine</div>', unsafe_allow_html=True)
    st.title(title)
    if description:
        st.caption(description)


def _render_overview() -> None:
    _render_page_header("Overview", "Unified Multi-Disciplinary Generative Engine Dashboard")

    total = len(MODULES)
    implemented = sum(1 for m in MODULES if m.implemented)
    loaded = sum(1 for m in MODULES if m.implemented and (m.loaded or m.key in {"overview", "system_health"}))
    failed = sum(1 for m in MODULES if m.renderer_path and not m.loaded)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Registered Modules", total)
    col2.metric("Implemented", implemented)
    col3.metric("Ready to Run", loaded)
    col4.metric("Import Errors", failed)

    st.markdown("### Structural & Architectural AI Capabilities")
    
    a1, a2, a3 = st.columns(3)
    with a1:
        st.markdown("#### 🏛️ Architecture AI")
        st.write("• Generative Floor Planning")
        st.write("• Room Programming & Zoning")
        st.write("• Building Code Compliance")
        st.write("• Multi-Objective Optimization")

    with a2:
        st.markdown("#### 🏗️ Structural Analysis AI")
        st.write("• 2D/3D Stiffness FEA Engine")
        st.write("• RC Concrete & Bar Detailing")
        st.write("• Structural Steel (AISC / EC3)")
        st.write("• Foundation & Geotechnical")

    with a3:
        st.markdown("#### 📁 Governance & Workflow")
        st.write("• Project Lifecycle Management")
        st.write("• Sign-Off Approvals & Audit")
        st.write("• Version Revision Control")
        st.write("• ORM Database Integration")

    st.divider()

    if failed == 0:
        st.success("All registered active renderers are loaded and operational.")
    else:
        st.warning(f"{failed} module renderer(s) could not be loaded. Check System Health for details.")


def _render_system_health() -> None:
    _render_page_header("System Health", "IMAGINE application, runtime diagnostics, and module status.")

    st.subheader("Runtime Environment")
    columns = st.columns(4)
    columns[0].metric("Python", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    columns[1].metric("Streamlit", getattr(st, "__version__", "unknown"))
    columns[2].metric("Application", APP_VERSION)
    columns[3].metric("Total Modules", len(MODULES))

    st.subheader("Database Model Registry")
    if _PROJECT_MODELS_OK:
        st.success("Projects ORM registration: READY")
    else:
        st.error("Projects ORM registration: FAILED")
        if _PROJECT_MODELS_ERROR is not None:
            st.exception(_PROJECT_MODELS_ERROR)
        if _PROJECT_MODELS_TRACEBACK:
            with st.expander("Complete ORM Traceback"):
                st.code(_PROJECT_MODELS_TRACEBACK, language="text")

    st.subheader("Module Diagnostics Matrix")
    rows = []
    for module in MODULES:
        if module.key in {"overview", "system_health"}:
            status = "READY"
        elif not module.implemented:
            status = "NOT IMPLEMENTED"
        elif module.loaded:
            status = "READY"
        else:
            status = "ERROR"

        renderer = f"{module.renderer_path}:{module.renderer_name}" if module.renderer_path else "Built-in"
        rows.append({
            "Module": module.label,
            "Section": module.section,
            "Status": status,
            "Renderer Adapter": renderer,
        })

    st.dataframe(rows, use_container_width=True, hide_index=True)


def _render_unavailable(module: ModuleDefinition) -> None:
    _render_page_header(module.label, module.description)
    st.error(f"{module.label} could not be loaded due to an import exception.")
    if module.import_error is not None:
        with st.expander("Import Exception & Stacktrace", expanded=True):
            st.exception(module.import_error)
            if module.traceback_text:
                st.code(module.traceback_text, language="text")


def _render_unimplemented(module: ModuleDefinition) -> None:
    _render_page_header(module.label, module.description)
    st.info(f"{module.label} is registered in the architecture schema, but its Streamlit UI renderer has not yet been implemented.")


def _render_module(module: ModuleDefinition) -> None:
    if not module.implemented:
        _render_unimplemented(module)
        return

    if module.renderer is None:
        _render_unavailable(module)
        return

    try:
        module.renderer()
    except Exception as exc:
        st.error(f"{module.label} encountered a runtime exception during rendering.")
        with st.expander("Runtime Traceback", expanded=True):
            st.exception(exc)
            st.code(traceback.format_exc(), language="text")


# ============================================================================
# ROUTING & ENTRY POINT
# ============================================================================

def _render_current_module() -> None:
    selected = st.session_state.imagine_selected_module
    module = MODULE_REGISTRY.get(selected)

    if module is None:
        module = MODULE_REGISTRY["overview"]
        st.session_state.imagine_selected_module = "overview"

    if module.key == "overview":
        _render_overview()
        return

    if module.key == "system_health":
        _render_system_health()
        return

    _render_module(module)


def main() -> None:
    """Zero-argument Streamlit application entry point."""
    _render_sidebar()
    _render_current_module()


if __name__ == "__main__":
    main()
