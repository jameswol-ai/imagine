"""
IMAGINE
Generative Architecture & Civil Engine

Main Streamlit application shell using native st.navigation and st.Page,
configured for Streamlit Cloud deployment with isolated renderer diagnostics.
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
APP_VERSION = "1.0.0 Alpha"

st.set_page_config(
    page_title=f"{APP_NAME} | Generative Architecture",
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
        /* Hide standard header chrome, but preserve top spacing and sidebar toggle */
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
    """Initialize shell-level session state."""
    if "imagine_user" not in st.session_state:
        st.session_state.imagine_user = "admin"

    if "imagine_role" not in st.session_state:
        st.session_state.imagine_role = "Administrator"

    if "imagine_renderer_errors" not in st.session_state:
        st.session_state.imagine_renderer_errors = {}


initialize_session_state()

# ============================================================================
# MODULE REGISTRY DEFINITION
# ============================================================================

MODULE_REGISTRY: list[ModuleMeta] = [
    ModuleMeta("architecture", "Architecture", "🏛️", "ARCHITECTURE", "Generative architecture workspace.", "architecture.ui", "render_architecture"),
    ModuleMeta("zoning", "Zoning", "🗺️", "ARCHITECTURE", "Zoning and land-use planning.", "architecture.zoning.ui", "render_zoning"),
    ModuleMeta("site_planning", "Site Planning", "📐", "ARCHITECTURE", "Site planning and development.", "architecture.site_planning.ui", "render_site_planning"),
    ModuleMeta("floor_planning", "Floor Planning", "🏢", "ARCHITECTURE", "Floor planning and spatial layouts.", "architecture.floor_planning.ui", "render_floor_planning"),
    ModuleMeta("room_programming", "Room Programming", "🚪", "ARCHITECTURE", "Room space schedules.", "architecture.room_programming.ui", "render_room_programming"),
    ModuleMeta("compliance", "Compliance", "✅", "ARCHITECTURE", "Architectural compliance inspection.", "architecture.compliance.ui", "render_compliance"),
    ModuleMeta("generative_design", "Generative Design", "✨", "ARCHITECTURE", "Generative architectural design.", "architecture.generative_design.ui", "render_generative_design"),
    ModuleMeta("projects", "Projects", "📁", "PROJECTS", "Project lifecycle records.", "projects.projects.ui", "render_projects"),
    ModuleMeta("approvals", "Approvals", "✔️", "PROJECTS", "Project approvals and decisions.", "projects.approvals.ui", "render_approvals"),
    ModuleMeta("revisions", "Revisions", "🔄", "PROJECTS", "Project revisions and change history.", "projects.revisions.ui", "render_revisions"),
    ModuleMeta("workflows", "Workflows", "🔀", "PROJECTS", "Project workflow management.", "projects.workflows.ui", "render_workflows"),
    ModuleMeta("governance", "Governance", "⚖️", "PROJECTS", "Project governance and controls.", "projects.governance.ui", "render_governance"),
]

# ============================================================================
# DYNAMIC MODULE RUNNER & ERROR ISOLATION
# ============================================================================

def render_page_header(title: str, description: str = "") -> None:
    st.markdown(
        f'<div class="imagine-page-label">{APP_NAME} | Generative Architecture</div>',
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
            st.info(f"{meta.label} is registered in {APP_NAME}, but a renderer has not yet been implemented.")
            return

        try:
            # 1. Import module
            module = importlib.import_module(meta.renderer_path)
            
            # 2. Get renderer attribute
            if not hasattr(module, meta.renderer_name):
                raise AttributeError(f"Module '{meta.renderer_path}' does not expose '{meta.renderer_name}()'.")

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

            # 4. Execute renderer
            renderer()

            # Clear error if previously failed
            st.session_state.imagine_renderer_errors.pop(meta.key, None)

        except ModuleNotFoundError as exc:
            st.session_state.imagine_renderer_errors[meta.key] = {
                "error": exc,
                "traceback": traceback.format_exc(),
            }
            st.info(f"**{meta.label}** module is registered, but the file (`{meta.renderer_path}`) was not found.")

        except Exception as exc:
            st.session_state.imagine_renderer_errors[meta.key] = {
                "error": exc,
                "traceback": traceback.format_exc(),
            }
            st.error(f"{meta.label} could not load its interface.")
            with st.expander("Diagnostic Traceback", expanded=True):
                st.exception(exc)
                st.code(traceback.format_exc(), language="text")

    return page_wrapper

# ============================================================================
# BUILT-IN SYSTEM PAGES
# ============================================================================

def render_overview() -> None:
    render_page_header("Overview", "Generative Architecture & Civil Engine")

    failed = len(st.session_state.imagine_renderer_errors)
    total = len(MODULE_REGISTRY)
    ready = total - failed

    col1, col2, col3 = st.columns(3)
    col1.metric("Registered Renderers", total)
    col2.metric("Ready", ready)
    col3.metric("Errors / Unresolved", failed)

    st.subheader(APP_NAME)
    st.write(
        f"Welcome to **{APP_NAME}**, an integrated AI-driven design environment for "
        "architectural planning, generative layout optimization, compliance evaluation, and civil workflow management."
    )

    if failed == 0:
        st.success("All registered renderers are available.")
    else:
        st.warning(f"{failed} registered module(s) currently have import/runtime warnings. Check System Health for details.")


def render_system_health() -> None:
    render_page_header("System Health", f"{APP_NAME} application and renderer diagnostics.")

    st.subheader("Runtime Environment")
    col1, col2, col3 = st.columns(3)
    col1.metric("Python", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    col2.metric("Streamlit", getattr(st, "__version__", "Unknown"))
    col3.metric("Application", APP_VERSION)

    st.subheader("Module Diagnostics")
    rows = []
    for meta in MODULE_REGISTRY:
        err = st.session_state.imagine_renderer_errors.get(meta.key)
        status = "ERROR / MISSING" if err else "READY"
        rows.append({
            "Module": meta.label,
            "Section": meta.section,
            "Status": status,
            "Renderer": f"{meta.renderer_path}.{meta.renderer_name}" if meta.renderer_path else "Built-in",
        })

    st.dataframe(rows, use_container_width=True, hide_index=True)

    if st.session_state.imagine_renderer_errors:
        st.subheader("Traceback Details")
        for key, err_info in st.session_state.imagine_renderer_errors.items():
            meta = next((m for m in MODULE_REGISTRY if m.key == key), None)
            label = meta.label if meta else key
            with st.expander(f"⚠️ {label}", expanded=False):
                st.exception(err_info["error"])
                st.code(err_info["traceback"], language="text")

# ============================================================================
# NATIVE STREAMLIT MULTI-PAGE NAVIGATION SETUP
# ============================================================================

pages_dict = {
    "MAIN": [
        st.Page(render_overview, title="Overview", icon="🏠", default=True),
    ],
    "ARCHITECTURE": [
        st.Page(
            create_module_page_function(m),
            title=m.label,
            icon=m.icon,
            url_path=m.key.replace("_", "-"),
        )
        for m in MODULE_REGISTRY
        if m.section == "ARCHITECTURE"
    ],
    "PROJECTS": [
        st.Page(
            create_module_page_function(m),
            title=m.label,
            icon=m.icon,
            url_path=m.key.replace("_", "-"),
        )
        for m in MODULE_REGISTRY
        if m.section == "PROJECTS"
    ],
    "SYSTEM": [
        st.Page(render_system_health, title="System Health", icon="🩺", url_path="system-health"),
    ],
}

pg = st.navigation(pages_dict)

# ============================================================================
# SIDEBAR HEADER & USER SESSION PANEL
# ============================================================================

with st.sidebar:
    st.markdown(
        f"""
        <div class="imagine-brand">🏗️ {APP_NAME}</div>
        <div class="imagine-subtitle">{APP_DESCRIPTION}</div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

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
