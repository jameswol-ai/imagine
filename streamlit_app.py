"""
streamlit_app.py
----------------
studiohome - Generative Architecture & Civil Engine
Sidebar-free layout with top navigation header & centralized module registry.
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

APP_NAME = "studiohome"
APP_SUBTITLE = "Generative Architecture & Civil Engine"
APP_VERSION = "1.0.0 Alpha"

st.set_page_config(
    page_title=f"{APP_NAME} | {APP_SUBTITLE}",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================================
# GLOBAL STYLES & SIDEBAR REMOVAL
# ============================================================================

st.markdown(
    """
    <style>
        /* Completely remove standard sidebar */
        [data-testid="stSidebar"] { display: none !important; }
        #MainMenu, footer, header { visibility: hidden; }

        .block-container {
            padding-top: 1rem;
            padding-bottom: 2rem;
            max-width: 96%;
        }

        /* Top Navigation Glass Container */
        .studio-navbar {
            border: 1px solid rgba(128, 128, 128, 0.18);
            border-radius: 12px;
            padding: 1rem 1.5rem;
            margin-bottom: 1.25rem;
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(8px);
        }

        .studio-brand {
            font-size: 1.6rem;
            font-weight: 800;
            letter-spacing: 0.03em;
            line-height: 1.1;
        }

        .studio-subtitle {
            color: #888;
            font-size: 0.8rem;
            margin-top: 0.15rem;
        }

        .studio-user-badge {
            text-align: right;
            font-size: 0.85rem;
            color: #aaa;
        }

        .studio-user-name {
            font-weight: 700;
            color: #fff;
        }

        .studio-page-label {
            color: #777;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.25rem;
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

if "selected_section" not in st.session_state:
    st.session_state.selected_section = "MAIN"

if "selected_module" not in st.session_state:
    st.session_state.selected_module = "overview"

if "user_name" not in st.session_state:
    st.session_state.user_name = "admin"

if "user_role" not in st.session_state:
    st.session_state.user_role = "Administrator"


# ============================================================================
# SAFE IMPORTS & RENDERER RESOLUTION
# ============================================================================

def _safe_import(module_path: str) -> tuple[Any | None, BaseException | None, str]:
    try:
        module = importlib.import_module(module_path)
        return module, None, ""
    except BaseException as exc:
        return None, exc, traceback.format_exc()


def _resolve_renderer(
    module_path: str,
    renderer_name: str,
) -> tuple[Renderer | None, BaseException | None, str]:
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
                    f"{APP_NAME} renderers must expose a zero-argument adapter."
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
# MODULE REGISTRY
# ============================================================================

MODULES: list[ModuleDefinition] = [
    # MAIN
    ModuleDefinition(
        key="overview",
        label="Overview",
        icon="🏠",
        section="MAIN",
        description=f"{APP_NAME} ecosystem dashboard and engine core.",
        implemented=True,
    ),

    # ARCHITECTURE
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

    # STRUCTURAL ANALYSIS
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

    # PROJECTS
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

    # BIM & DIGITAL TWIN
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

    # MEP
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

    # COSTING
    ModuleDefinition(
        key="boq_takeoff",
        label="Quantity Takeoff & BOQ",
        icon="💰",
        section="COSTING",
        description="Automatic material quantity takeoff, BOQ rates, and cashflow risk.",
        implemented=False,
    ),

    # AI SUITE
    ModuleDefinition(
        key="imagine_ai",
        label=f"{APP_NAME} Copilots",
        icon="🤖",
        section="AI SUITE",
        description="Specialized AI agents for Architect, Structural Engineer, MEP, & QS.",
        implemented=False,
    ),

    # SYSTEM
    ModuleDefinition(
        key="system_health",
        label="System Health",
        icon="🩺",
        section="SYSTEM",
        description=f"{APP_NAME} diagnostics, runtime performance, and renderer state.",
        implemented=True,
    ),
]

MODULE_REGISTRY: dict[str, ModuleDefinition] = {
    module.key: module for module in MODULES
}

SECTIONS = ["MAIN", "ARCHITECTURE", "STRUCTURAL ANALYSIS", "PROJECTS", "BIM & TWIN", "MEP", "COSTING", "AI SUITE", "SYSTEM"]


# ============================================================================
# RENDERER INITIALIZATION
# ============================================================================

def _load_module_renderer(module: ModuleDefinition) -> None:
    if not module.implemented or not module.renderer_path:
        module.loaded = module.implemented and module.renderer_path is None
        return

    renderer, error, error_traceback = _resolve_renderer(
        module.renderer_path,
        module.renderer_name,
    )

    module.renderer = renderer
    module.import_error = error
    module.traceback_text = error_traceback
    module.loaded = renderer is not None


for m in MODULES:
    _load_module_renderer(m)


# ============================================================================
# TOP NAVIGATION HEADER (NO SIDEBAR)
# ============================================================================

def _render_top_navigation() -> None:
    # Brand & User Bar
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(
            f"""
            <div class="studio-brand">🏠 {APP_NAME}</div>
            <div class="studio-subtitle">{APP_SUBTITLE}</div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="studio-user-badge">
                <span class="studio-user-name">👤 {st.session_state.user_name}</span> ({st.session_state.user_role})
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # Section Tabs Across Top
    selected_sec = st.radio(
        label="Navigation Sections",
        options=SECTIONS,
        index=SECTIONS.index(st.session_state.selected_section),
        horizontal=True,
        label_visibility="collapsed",
        key="top_section_radio",
    )

    if selected_sec != st.session_state.selected_section:
        st.session_state.selected_section = selected_sec
        # Pick first module in newly selected section
        sec_mods = [m for m in MODULES if m.section == selected_sec]
        if sec_mods:
            st.session_state.selected_module = sec_mods[0].key
        st.rerun()

    # Sub-module Selector Pills
    section_modules = [m for m in MODULES if m.section == st.session_state.selected_section]
    if section_modules:
        cols = st.columns(len(section_modules))
        for idx, mod in enumerate(section_modules):
            is_active = st.session_state.selected_module == mod.key
            btn_label = f"{mod.icon} {mod.label}"
            if mod.renderer_path and not mod.loaded:
                btn_label += " ⚠️"

            if cols[idx].button(
                btn_label,
                key=f"nav_mod_{mod.key}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.selected_module = mod.key
                st.rerun()

    st.divider()


# ============================================================================
# CORE VIEWS
# ============================================================================

def _render_page_header(title: str, description: str = "") -> None:
    st.markdown(f'<div class="studio-page-label">{APP_NAME} | {APP_SUBTITLE}</div>', unsafe_allow_html=True)
    st.title(title)
    if description:
        st.caption(description)


def _render_overview() -> None:
    _render_page_header("Overview", f"Unified Multi-Disciplinary Dashboard for {APP_NAME}")

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
    _render_page_header("System Health", f"{APP_NAME} diagnostics, runtime performance, and module status.")

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


def _render_module(module: ModuleDefinition) -> None:
    if not module.implemented:
        _render_page_header(module.label, module.description)
        st.info(f"{module.label} is registered in the schema, but its Streamlit UI renderer is not yet implemented.")
        return

    if module.renderer is None:
        _render_page_header(module.label, module.description)
        st.error(f"{module.label} could not be loaded due to an import exception.")
        if module.import_error is not None:
            with st.expander("Import Exception & Stacktrace", expanded=True):
                st.exception(module.import_error)
                if module.traceback_text:
                    st.code(module.traceback_text, language="text")
        return

    try:
        module.renderer()
    except Exception as exc:
        st.error(f"{module.label} encountered a runtime exception during rendering.")
        with st.expander("Runtime Traceback", expanded=True):
            st.exception(exc)
            st.code(traceback.format_exc(), language="text")


# ============================================================================
# ENTRY POINT
# ============================================================================

def main() -> None:
    _render_top_navigation()

    selected = st.session_state.selected_module
    module = MODULE_REGISTRY.get(selected)

    if module is None:
        module = MODULE_REGISTRY["overview"]
        st.session_state.selected_module = "overview"

    if module.key == "overview":
        _render_overview()
    elif module.key == "system_health":
        _render_system_health()
    else:
        _render_module(module)


if __name__ == "__main__":
    main()
