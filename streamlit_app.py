"""
studiohome / IMAGINE
Generative Architecture & Civil Engine

Main Streamlit application shell using native st.navigation and st.Page.
"""

from __future__ import annotations

import importlib
import os
import sys
import traceback
from typing import Callable

# Ensure root directory is on Python path for Streamlit Cloud imports
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st

# ============================================================================
# APPLICATION CONFIGURATION & GLOBAL STYLES
# ============================================================================

APP_NAME = "studiohome"
APP_DESCRIPTION = "Generative Architecture & Civil Engine"
APP_VERSION = "1.0.0 Alpha"

st.set_page_config(
    page_title=f"{APP_NAME} | Generative Architecture",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        div[data-testid="stHeader"] { background-color: transparent; z-index: 100; }

        .block-container {
            padding-top: 1.25rem;
            padding-bottom: 2rem;
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

        .imagine-user-panel {
            border: 1px solid rgba(128, 128, 128, 0.20);
            border-radius: 10px;
            padding: 0.75rem;
            margin-top: 0.5rem;
        }

        .imagine-user-name { font-weight: 700; font-size: 0.90rem; }
        .imagine-user-role { color: #777; font-size: 0.75rem; margin-top: 0.15rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================================
# SAFE MODULE WRAPPER
# ============================================================================

def create_module_page_function(
    module_path: str,
    renderer_name: str,
    label: str,
    description: str,
) -> Callable[[], None]:
    """Wraps dynamic module renderers in error handling for st.Page execution."""

    def page_wrapper() -> None:
        st.caption(f"{APP_NAME} | Generative Architecture")
        st.title(label)
        if description:
            st.caption(description)

        try:
            module = importlib.import_module(module_path)
            renderer = getattr(module, renderer_name)
            renderer()
        except ModuleNotFoundError:
            st.info(f"**{label}** module is registered, but not yet implemented in this build.")
        except Exception as exc:
            st.error(f"Failed to execute module **{label}**.")
            with st.expander("Diagnostic Traceback", expanded=True):
                st.exception(exc)
                st.code(traceback.format_exc(), language="text")

    return page_wrapper

# ============================================================================
# BUILT-IN PAGE RENDERERS
# ============================================================================

def render_overview() -> None:
    st.caption(f"{APP_NAME} | Generative Architecture")
    st.title("Overview")
    st.caption("Generative Architecture & Civil Engine")

    col1, col2, col3 = st.columns(3)
    col1.metric("Engine Status", "Online")
    col2.metric("Architecture Modules", "7 Active")
    col3.metric("Project Workflows", "5 Active")

    st.subheader("Core Capabilities")
    st.write(
        "Welcome to **studiohome**, an integrated AI-driven design environment for "
        "architectural planning, generative design, compliance evaluation, and civil workflow management."
    )

def render_system_health() -> None:
    st.caption(f"{APP_NAME} | Generative Architecture")
    st.title("System Health")
    st.caption("Diagnostics and Environment Details")

    st.subheader("Runtime")
    col1, col2, col3 = st.columns(3)
    col1.metric("Python", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    col2.metric("Streamlit", getattr(st, "__version__", "Unknown"))
    col3.metric("Application", APP_VERSION)

# ============================================================================
# NATIVE STREAMLIT MULTI-PAGE NAVIGATION SETUP
# ============================================================================

pages = {
    "MAIN": [
        st.Page(render_overview, title="Overview", icon="🏠", default=True),
    ],
    "ARCHITECTURE": [
        st.Page(
            create_module_page_function("architecture.ui", "render_architecture", "Architecture", "Generative architecture workspace."),
            title="Architecture", icon="🏛️", url_path="architecture",
        ),
        st.Page(
            create_module_page_function("architecture.zoning.ui", "render_zoning", "Zoning", "Zoning and land-use planning."),
            title="Zoning", icon="🗺️", url_path="zoning",
        ),
        st.Page(
            create_module_page_function("architecture.site_planning.ui", "render_site_planning", "Site Planning", "Site planning and development."),
            title="Site Planning", icon="📐", url_path="site-planning",
        ),
        st.Page(
            create_module_page_function("architecture.floor_planning.ui", "render_floor_planning", "Floor Planning", "Floor planning and spatial layouts."),
            title="Floor Planning", icon="🏢", url_path="floor-planning",
        ),
        st.Page(
            create_module_page_function("architecture.room_programming.ui", "render_room_programming", "Room Programming", "Room space schedules."),
            title="Room Programming", icon="🚪", url_path="room-programming",
        ),
        st.Page(
            create_module_page_function("architecture.compliance.ui", "render_compliance", "Compliance", "Architectural compliance inspection."),
            title="Compliance", icon="✅", url_path="compliance",
        ),
        st.Page(
            create_module_page_function("architecture.generative_design.ui", "render_generative_design", "Generative Design", "AI floorplan layout generator."),
            title="Generative Design", icon="✨", url_path="generative-design",
        ),
    ],
    "PROJECTS": [
        st.Page(
            create_module_page_function("projects.projects.ui", "render_projects", "Projects", "Project lifecycle records."),
            title="Projects", icon="📁", url_path="projects",
        ),
        st.Page(
            create_module_page_function("projects.approvals.ui", "render_approvals", "Approvals", "Project approvals and decisions."),
            title="Approvals", icon="✔️", url_path="approvals",
        ),
        st.Page(
            create_module_page_function("projects.revisions.ui", "render_revisions", "Revisions", "Project revisions and change history."),
            title="Revisions", icon="🔄", url_path="revisions",
        ),
        st.Page(
            create_module_page_function("projects.workflows.ui", "render_workflows", "Workflows", "Project workflow management."),
            title="Workflows", icon="🔀", url_path="workflows",
        ),
        st.Page(
            create_module_page_function("projects.governance.ui", "render_governance", "Governance", "Project governance and controls."),
            title="Governance", icon="⚖️", url_path="governance",
        ),
    ],
    "SYSTEM": [
        st.Page(render_system_health, title="System Health", icon="🩺", url_path="system-health"),
    ],
}

# Instantiate navigation
pg = st.navigation(pages)

# ============================================================================
# CUSTOM SIDEBAR HEADER & USER PANEL
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

# Execute native routing (renders the sidebar page choices)
pg.run()

# Append custom user panel beneath navigation links in sidebar
with st.sidebar:
    st.divider()
    st.caption("USER SESSION")
    st.markdown(
        """
        <div class="imagine-user-panel">
            <div class="imagine-user-name">👤 Admin</div>
            <div class="imagine-user-role">Role: Administrator</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
