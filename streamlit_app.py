"""
IMAGINE
Generative Architecture & Civil Engine

Main Streamlit application shell.

Responsibilities:
    - IMAGINE branding
    - Sidebar navigation
    - Centralized module registry
    - Safe renderer imports
    - Renderer runtime isolation
    - Module status
    - System Health diagnostics

Module/service/database contracts are intentionally kept outside this file.
"""

from __future__ import annotations

import importlib
import inspect
import sys
import traceback
from dataclasses import dataclass
from typing import Callable

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
# STYLING
# ============================================================================

st.markdown(
    """
    <style>
        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }

        header {
            visibility: hidden;
        }

        .block-container {
            padding-top: 1.25rem;
            padding-bottom: 2rem;
        }

        [data-testid="stSidebar"] {
            border-right: 1px solid rgba(128, 128, 128, 0.20);
        }

        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1rem;
        }

        .imagine-brand {
            font-size: 1.45rem;
            font-weight: 800;
            line-height: 1.15;
        }

        .imagine-subtitle {
            margin-top: 0.25rem;
            color: #777;
            font-size: 0.76rem;
            line-height: 1.35;
        }

        .imagine-section {
            margin-top: 1rem;
            margin-bottom: 0.35rem;
            color: #777;
            font-size: 0.67rem;
            font-weight: 800;
            letter-spacing: 0.12em;
        }

        .imagine-page-label {
            color: #777;
            font-size: 0.70rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .imagine-user {
            border: 1px solid rgba(128, 128, 128, 0.20);
            border-radius: 10px;
            padding: 0.75rem;
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
# TYPES
# ============================================================================

Renderer = Callable[[], object]


@dataclass
class ModuleDefinition:
    key: str
    label: str
    icon: str
    section: str
    description: str

    renderer_path: str | None = None
    renderer_name: str | None = None

    implemented: bool = False

    renderer: Renderer | None = None
    import_error: BaseException | None = None
    traceback_text: str = ""

    @property
    def loaded(self) -> bool:
        return self.renderer is not None


# ============================================================================
# SESSION STATE
# ============================================================================

if "imagine_selected_module" not in st.session_state:
    st.session_state.imagine_selected_module = "overview"

if "imagine_user" not in st.session_state:
    st.session_state.imagine_user = "admin"

if "imagine_role" not in st.session_state:
    st.session_state.imagine_role = "Administrator"

if "imagine_renderer_errors" not in st.session_state:
    st.session_state.imagine_renderer_errors = {}


# ============================================================================
# SAFE IMPORT SYSTEM
# ============================================================================

def safe_import(
    module_path: str,
) -> tuple[object | None, BaseException | None, str]:
    """
    Import a Python module without allowing an import error to terminate
    the Streamlit application.
    """

    try:
        module = importlib.import_module(module_path)
        return module, None, ""

    except BaseException as exc:
        return (
            None,
            exc,
            traceback.format_exc(),
        )


def resolve_renderer(
    module_path: str,
    renderer_name: str,
) -> tuple[
    Renderer | None,
    BaseException | None,
    str,
]:
    """
    Import and validate a zero-argument Streamlit renderer.
    """

    module, error, error_traceback = safe_import(
        module_path
    )

    if error is not None:
        return None, error, error_traceback

    try:
        renderer = getattr(
            module,
            renderer_name,
        )

    except AttributeError as exc:
        return (
            None,
            RuntimeError(
                f"{module_path} does not expose "
                f"{renderer_name}()."
            ),
            traceback.format_exc(),
        )

    if not callable(renderer):
        return (
            None,
            TypeError(
                f"{module_path}.{renderer_name} "
                "is not callable."
            ),
            "",
        )

    try:
        signature = inspect.signature(renderer)

        required_parameters = [
            parameter
            for parameter in signature.parameters.values()
            if (
                parameter.kind
                in (
                    inspect.Parameter.POSITIONAL_ONLY,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                )
                and parameter.default
                is inspect.Parameter.empty
            )
        ]

        if required_parameters:
            names = ", ".join(
                parameter.name
                for parameter in required_parameters
            )

            return (
                None,
                TypeError(
                    f"{module_path}.{renderer_name} "
                    f"requires arguments: {names}. "
                    "Streamlit module renderers must "
                    "be zero-argument callables."
                ),
                "",
            )

    except (TypeError, ValueError):
        pass

    return renderer, None, ""


# ============================================================================
# MODULE REGISTRY
# ============================================================================

MODULES = [
    # ------------------------------------------------------------------------
    # MAIN
    # ------------------------------------------------------------------------

    ModuleDefinition(
        key="overview",
        label="Overview",
        icon="🏠",
        section="MAIN",
        description=(
            "IMAGINE application overview and system status."
        ),
        implemented=True,
    ),

    # ------------------------------------------------------------------------
    # ARCHITECTURE
    # ------------------------------------------------------------------------

    ModuleDefinition(
        key="architecture",
        label="Architecture",
        icon="🏛️",
        section="ARCHITECTURE",
        description=(
            "Generative architecture workspace."
        ),
        renderer_path="architecture.ui",
        renderer_name="render_architecture",
        implemented=True,
    ),

    ModuleDefinition(
        key="site_planning",
        label="Site Planning",
        icon="📐",
        section="ARCHITECTURE",
        description=(
            "Site planning and development."
        ),
        renderer_path="architecture.site_planning.ui",
        renderer_name="render_site_planning",
        implemented=True,
    ),

    ModuleDefinition(
        key="zoning",
        label="Zoning",
        icon="🗺️",
        section="ARCHITECTURE",
        description=(
            "Zoning and land-use planning."
        ),
        renderer_path="architecture.zoning.ui",
        renderer_name="render_zoning",
        implemented=True,
    ),

    ModuleDefinition(
        key="floor_planning",
        label="Floor Planning",
        icon="🏢",
        section="ARCHITECTURE",
        description=(
            "Floor planning and spatial layouts."
        ),
        renderer_path="architecture.floor_planning.ui",
        renderer_name="render_floor_planning",
        implemented=True,
    ),

    ModuleDefinition(
        key="room_programming",
        label="Room Programming",
        icon="🚪",
        section="ARCHITECTURE",
        description=(
            "Room programming and space schedules."
        ),
        renderer_path="architecture.room_programming.ui",
        renderer_name="render_room_programming",
        implemented=True,
    ),

    ModuleDefinition(
        key="compliance",
        label="Compliance",
        icon="✅",
        section="ARCHITECTURE",
        description=(
            "Building and architectural compliance."
        ),
        renderer_path="architecture.compliance.ui",
        renderer_name="render_compliance",
        implemented=True,
    ),

    ModuleDefinition(
        key="generative_design",
        label="Generative Design",
        icon="✨",
        section="ARCHITECTURE",
        description=(
            "Generative architectural design."
        ),
        renderer_path="architecture.generative_design.ui",
        renderer_name="render_generative_design",
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
        description=(
            "Project lifecycle and project records."
        ),
        renderer_path="projects.projects.ui",
        renderer_name="render_projects",
        implemented=True,
    ),

    ModuleDefinition(
        key="approvals",
        label="Approvals",
        icon="✔️",
        section="PROJECTS",
        description=(
            "Project approvals and decisions."
        ),
        renderer_path="projects.approvals.ui",
        renderer_name="render_approvals",
        implemented=True,
    ),

    ModuleDefinition(
        key="revisions",
        label="Revisions",
        icon="🔄",
        section="PROJECTS",
        description=(
            "Project revisions and change history."
        ),
        renderer_path="projects.revisions.ui",
        renderer_name="render_revisions",
        implemented=True,
    ),

    ModuleDefinition(
        key="workflows",
        label="Workflows",
        icon="🔀",
        section="PROJECTS",
        description=(
            "Project workflow management."
        ),
        renderer_path="projects.workflows.ui",
        renderer_name="render_workflows",
        implemented=True,
    ),

    ModuleDefinition(
        key="governance",
        label="Governance",
        icon="⚖️",
        section="PROJECTS",
        description=(
            "Project governance and controls."
        ),
        renderer_path="projects.governance.ui",
        renderer_name="render_governance",
        implemented=True,
    ),

    # ------------------------------------------------------------------------
    # SYSTEM
    # ------------------------------------------------------------------------

    ModuleDefinition(
        key="system_health",
        label="System Health",
        icon="🩺",
        section="SYSTEM",
        description=(
            "IMAGINE application diagnostics."
        ),
        implemented=True,
    ),
]


MODULE_REGISTRY = {
    module.key: module
    for module in MODULES
}


# ============================================================================
# LOAD ALL RENDERERS
# ============================================================================

def load_renderers() -> None:
    """
    Resolve every renderer independently.

    One broken module must never prevent the remaining navigation from
    loading.
    """

    for module in MODULES:
        if not module.implemented:
            continue

        if not module.renderer_path:
            continue

        if not module.renderer_name:
            module.import_error = RuntimeError(
                f"{module.key} has a renderer path "
                "but no renderer name."
            )
            continue

        (
            renderer,
            error,
            error_traceback,
        ) = resolve_renderer(
            module.renderer_path,
            module.renderer_name,
        )

        module.renderer = renderer
        module.import_error = error
        module.traceback_text = error_traceback

        if error is not None:
            st.session_state.imagine_renderer_errors[
                module.key
            ] = {
                "error": error,
                "traceback": error_traceback,
            }


load_renderers()


# ============================================================================
# NAVIGATION
# ============================================================================

def select_module(
    module_key: str,
) -> None:
    st.session_state.imagine_selected_module = module_key


def render_sidebar_section(
    section: str,
) -> None:
    st.markdown(
        f'<div class="imagine-section">{section}</div>',
        unsafe_allow_html=True,
    )

    modules = [
        module
        for module in MODULES
        if module.section == section
    ]

    for module in modules:
        selected = (
            st.session_state.imagine_selected_module
            == module.key
        )

        status_suffix = ""

        if module.renderer_path and not module.loaded:
            status_suffix = " ⚠️"

        label = (
            f"{module.icon} "
            f"{module.label}"
            f"{status_suffix}"
        )

        if st.button(
            label,
            key=f"nav_{module.key}",
            use_container_width=True,
            type=(
                "primary"
                if selected
                else "secondary"
            ),
        ):
            select_module(module.key)
            st.rerun()


def render_sidebar() -> None:
    with st.sidebar:
        # ------------------------------------------------------------
        # BRAND
        # ------------------------------------------------------------

        st.markdown(
            f"""
            <div class="imagine-brand">
                🏗️ {APP_NAME}
            </div>
            <div class="imagine-subtitle">
                {APP_DESCRIPTION}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        # ------------------------------------------------------------
        # NAVIGATION
        # ------------------------------------------------------------

        render_sidebar_section("MAIN")

        render_sidebar_section("ARCHITECTURE")

        render_sidebar_section("PROJECTS")

        render_sidebar_section("SYSTEM")

        st.divider()

        # ------------------------------------------------------------
        # USER PANEL
        # ------------------------------------------------------------

        st.markdown(
            '<div class="imagine-section">USER PANEL</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="imagine-user">
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

        if st.button(
            "🚪 Logout",
            key="logout_button",
            use_container_width=True,
        ):
            st.session_state.imagine_selected_module = (
                "overview"
            )
            st.rerun()

        st.caption(
            f"{APP_NAME} {APP_VERSION}"
        )


# ============================================================================
# PAGE HEADER
# ============================================================================

def render_page_header(
    title: str,
    description: str = "",
) -> None:
    st.markdown(
        '<div class="imagine-page-label">'
        'IMAGINE | Generative Architecture'
        '</div>',
        unsafe_allow_html=True,
    )

    st.title(title)

    if description:
        st.caption(description)


# ============================================================================
# OVERVIEW
# ============================================================================

def render_overview() -> None:
    render_page_header(
        "Overview",
        "Generative Architecture & Civil Engine",
    )

    renderer_modules = [
        module
        for module in MODULES
        if module.renderer_path
    ]

    ready = sum(
        1
        for module in renderer_modules
        if module.loaded
    )

    errors = len(renderer_modules) - ready

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Registered Modules",
            len(MODULES),
        )

    with col2:
        st.metric(
            "Renderers Ready",
            ready,
        )

    with col3:
        st.metric(
            "Renderer Errors",
            errors,
        )

    st.subheader("IMAGINE")

    st.write(
        "Generative Architecture & Civil Engine "
        "for architecture, planning, project delivery, "
        "and civil-engineering workflows."
    )

    if errors == 0:
        st.success(
            "All registered renderers are available."
        )
    else:
        st.warning(
            f"{errors} renderer(s) require attention. "
            "Open System Health for diagnostics."
        )


# ============================================================================
# SYSTEM HEALTH
# ============================================================================

def render_system_health() -> None:
    render_page_header(
        "System Health",
        "Application, renderer, and runtime diagnostics.",
    )

    st.subheader("Runtime")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Python",
            (
                f"{sys.version_info.major}."
                f"{sys.version_info.minor}."
                f"{sys.version_info.micro}"
            ),
        )

    with col2:
        st.metric(
            "Streamlit",
            getattr(
                st,
                "__version__",
                "Unknown",
            ),
        )

    with col3:
        st.metric(
            "Application",
            APP_VERSION,
        )

    st.subheader("Module Status")

    rows = []

    for module in MODULES:
        if module.key in {
            "overview",
            "system_health",
        }:
            status = "READY"

        elif not module.implemented:
            status = "NOT IMPLEMENTED"

        elif module.loaded:
            status = "READY"

        else:
            status = "ERROR"

        rows.append(
            {
                "Module": module.label,
                "Section": module.section,
                "Status": status,
                "Renderer": (
                    f"{module.renderer_path}:"
                    f"{module.renderer_name}"
                    if module.renderer_path
                    else "Built-in"
                ),
            }
        )

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
    )

    failed = [
        module
        for module in MODULES
        if (
            module.renderer_path
            and not module.loaded
        )
    ]

    if failed:
        st.subheader("Renderer Errors")

        for module in failed:
            with st.expander(
                f"{module.icon} {module.label}"
            ):
                if module.import_error:
                    st.exception(
                        module.import_error
                    )

                if module.traceback_text:
                    st.code(
                        module.traceback_text,
                        language="text",
                    )


# ============================================================================
# ERROR / UNAVAILABLE PAGE
# ============================================================================

def render_module_error(
    module: ModuleDefinition,
) -> None:
    render_page_header(
        module.label,
        module.description,
    )

    st.error(
        f"{module.label} could not be loaded."
    )

    if module.import_error:
        with st.expander(
            "Complete error",
            expanded=True,
        ):
            st.exception(
                module.import_error
            )

            if module.traceback_text:
                st.code(
                    module.traceback_text,
                    language="text",
                )


# ============================================================================
# MODULE ROUTER
# ============================================================================

def render_selected_module() -> None:
    key = st.session_state.imagine_selected_module

    module = MODULE_REGISTRY.get(key)

    if module is None:
        st.session_state.imagine_selected_module = (
            "overview"
        )
        module = MODULE_REGISTRY["overview"]

    if key == "overview":
        render_overview()
        return

    if key == "system_health":
        render_system_health()
        return

    if not module.implemented:
        render_page_header(
            module.label,
            module.description,
        )

        st.info(
            f"{module.label} is registered in IMAGINE, "
            "but a Streamlit renderer has not yet "
            "been implemented."
        )

        return

    if module.renderer is None:
        render_module_error(module)
        return

    try:
        module.renderer()

    except Exception as exc:
        st.error(
            f"{module.label} could not load its interface."
        )

        with st.expander(
            f"Complete {module.label} error",
            expanded=True,
        ):
            st.exception(exc)

            st.code(
                traceback.format_exc(),
                language="text",
            )


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:
    render_sidebar()
    render_selected_module()


if __name__ == "__main__":
    main()