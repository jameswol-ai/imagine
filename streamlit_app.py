"""
IMAGINE
Generative Architecture & Civil Engine

Resilient Streamlit application shell.

This file is responsible for:
    - Application configuration
    - IMAGINE navigation/sidebar
    - Centralized renderer registry
    - Safe renderer imports
    - Renderer runtime isolation
    - Projects SQLAlchemy model registration
    - Module status reporting
    - System Health diagnostics

Renderer contract:
    Every module renderer exposed to this shell must be callable with
    zero arguments, for example:

        def render_projects():
            ...

The shell does not modify database models or service signatures.
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
    page_title=f"{APP_NAME} | Generative Architecture",
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
# TYPES
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

    renderer: Renderer | None = field(
        default=None,
        repr=False,
    )

    import_error: BaseException | None = field(
        default=None,
        repr=False,
    )

    traceback_text: str = field(
        default="",
        repr=False,
    )

    loaded: bool = False


# ============================================================================
# SESSION STATE
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
# SAFE IMPORTS
# ============================================================================

def _safe_import(
    module_path: str,
) -> tuple[Any | None, BaseException | None, str]:
    """
    Import a module without allowing an import failure to crash the shell.
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


def _resolve_renderer(
    module_path: str,
    renderer_name: str,
) -> tuple[
    Renderer | None,
    BaseException | None,
    str,
]:
    """
    Import a module and resolve its zero-argument renderer.
    """

    module, import_error, import_traceback = _safe_import(
        module_path
    )

    if import_error is not None:
        return (
            None,
            import_error,
            import_traceback,
        )

    try:
        renderer = getattr(
            module,
            renderer_name,
        )

    except AttributeError:
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
                f"{module_path}.{renderer_name} is not callable."
            ),
            "",
        )

    try:
        signature = inspect.signature(renderer)

        required = [
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

        if required:
            names = ", ".join(
                parameter.name
                for parameter in required
            )

            return (
                None,
                TypeError(
                    f"{module_path}.{renderer_name} "
                    f"requires arguments ({names}). "
                    "IMAGINE renderers must expose a "
                    "zero-argument Streamlit adapter."
                ),
                "",
            )

    except (TypeError, ValueError):
        pass

    return renderer, None, ""


# ============================================================================
# PROJECT MODEL REGISTRATION
# ============================================================================

def _register_project_models() -> tuple[
    bool,
    BaseException | None,
    str,
]:
    """
    Register Projects relationship targets before ProjectService performs
    an ORM query.

    Import order matters.

    Organization
    User
    Approval
    Revision
    Project
    """

    try:
        importlib.import_module(
            "database.models.organization"
        )

        importlib.import_module(
            "database.models.user"
        )

        importlib.import_module(
            "projects.approvals.models"
        )

        importlib.import_module(
            "projects.revisions.models"
        )

        importlib.import_module(
            "projects.projects.models"
        )

        return True, None, ""

    except BaseException as exc:
        return (
            False,
            exc,
            traceback.format_exc(),
        )


(
    _PROJECT_MODELS_OK,
    _PROJECT_MODELS_ERROR,
    _PROJECT_MODELS_TRACEBACK,
) = _register_project_models()


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
        description="IMAGINE business and application overview.",
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
        description="Generative architecture workspace.",
        renderer_path="architecture.ui",
        renderer_name="render_architecture",
        implemented=True,
    ),

    ModuleDefinition(
        key="site_planning",
        label="Site Planning",
        icon="📐",
        section="ARCHITECTURE",
        description="Site planning and development.",
        renderer_path="architecture.site_planning.ui",
        renderer_name="render_site_planning",
        implemented=True,
    ),

    ModuleDefinition(
        key="zoning",
        label="Zoning",
        icon="🗺️",
        section="ARCHITECTURE",
        description="Land-use and zoning planning.",
        renderer_path="architecture.zoning.ui",
        renderer_name="render_zoning",
        implemented=True,
    ),

    ModuleDefinition(
        key="floor_planning",
        label="Floor Planning",
        icon="🏢",
        section="ARCHITECTURE",
        description="Floor plans and spatial layouts.",
        renderer_path="architecture.floor_planning.ui",
        renderer_name="render_floor_planning",
        implemented=True,
    ),

    ModuleDefinition(
        key="room_programming",
        label="Room Programming",
        icon="🚪",
        section="ARCHITECTURE",
        description="Room schedules and programming.",
        renderer_path="architecture.room_programming.ui",
        renderer_name="render_room_programming",
        implemented=True,
    ),

    ModuleDefinition(
        key="compliance",
        label="Compliance",
        icon="✅",
        section="ARCHITECTURE",
        description="Architecture and building compliance.",
        renderer_path="architecture.compliance.ui",
        renderer_name="render_compliance",
        implemented=True,
    ),

    ModuleDefinition(
        key="generative_design",
        label="Generative Design",
        icon="✨",
        section="ARCHITECTURE",
        description="Generative architectural design.",
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
        description="Project lifecycle and project records.",
        renderer_path="projects.projects.ui",
        renderer_name="render_projects",
        implemented=True,
    ),

    ModuleDefinition(
        key="approvals",
        label="Approvals",
        icon="✔️",
        section="PROJECTS",
        description="Project approvals and decisions.",
        renderer_path="projects.approvals.ui",
        renderer_name="render_approvals",
        implemented=True,
    ),

    ModuleDefinition(
        key="revisions",
        label="Revisions",
        icon="🔄",
        section="PROJECTS",
        description="Project revisions and change history.",
        renderer_path="projects.revisions.ui",
        renderer_name="render_revisions",
        implemented=True,
    ),

    ModuleDefinition(
        key="workflows",
        label="Workflows",
        icon="🔀",
        section="PROJECTS",
        description="Project workflow management.",
        renderer_path="projects.workflows.ui",
        renderer_name="render_workflows",
        implemented=True,
    ),

    ModuleDefinition(
        key="governance",
        label="Governance",
        icon="⚖️",
        section="PROJECTS",
        description="Project governance and controls.",
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
        description="IMAGINE diagnostics and module status.",
        implemented=True,
    ),
]


MODULE_REGISTRY: dict[str, ModuleDefinition] = {
    module.key: module
    for module in MODULES
}


# ============================================================================
# RENDERER LOADING
# ============================================================================

def _load_module_renderer(
    module: ModuleDefinition,
) -> None:
    """
    Resolve a module renderer without allowing failures to break startup.
    """

    if not module.implemented:
        module.loaded = False
        return

    if not module.renderer_path:
        module.loaded = True

        st.session_state.imagine_module_status[
            module.key
        ] = {
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

    st.session_state.imagine_module_status[
        module.key
    ] = {
        "loaded": module.loaded,
        "implemented": module.implemented,
        "error": error,
    }

    if error is not None:
        st.session_state.imagine_renderer_errors[
            module.key
        ] = {
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

def _select_module(
    key: str,
) -> None:
    st.session_state.imagine_selected_module = key


def _module_button_label(
    module: ModuleDefinition,
) -> str:
    label = f"{module.icon} {module.label}"

    if module.renderer_path and not module.loaded:
        label += " ⚠️"

    return label


def _render_navigation_section(
    section: str,
) -> None:
    st.markdown(
        f'<div class="imagine-section">{section}</div>',
        unsafe_allow_html=True,
    )

    section_modules = [
        module
        for module in MODULES
        if module.section == section
    ]

    for module in section_modules:
        selected = (
            st.session_state.imagine_selected_module
            == module.key
        )

        if st.button(
            _module_button_label(module),
            key=f"imagine_nav_{module.key}",
            use_container_width=True,
            type=(
                "primary"
                if selected
                else "secondary"
            ),
        ):
            _select_module(module.key)
            st.rerun()


# ============================================================================
# SIDEBAR
# ============================================================================

def _render_sidebar() -> None:
    """
    Full IMAGINE navigation panel.

    The sidebar intentionally contains navigation only. Modules remain
    responsible for rendering their own interfaces.
    """

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
                {APP_SUBTITLE}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        # ------------------------------------------------------------
        # NAVIGATION
        # ------------------------------------------------------------

        _render_navigation_section("MAIN")

        _render_navigation_section("ARCHITECTURE")

        _render_navigation_section("PROJECTS")

        _render_navigation_section("SYSTEM")

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

        if st.button(
            "🚪 Logout",
            key="imagine_logout",
            use_container_width=True,
        ):
            st.session_state.imagine_user = "admin"
            st.session_state.imagine_role = "Administrator"

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

def _render_page_header(
    title: str,
    description: str = "",
) -> None:
    st.markdown(
        '<div class="imagine-page-label">IMAGINE | Generative Architecture</div>',
        unsafe_allow_html=True,
    )

    st.title(title)

    if description:
        st.caption(description)


# ============================================================================
# OVERVIEW
# ============================================================================

def _render_overview() -> None:
    _render_page_header(
        "Overview",
        "Generative Architecture & Civil Engine",
    )

    total = len(MODULES)

    implemented = sum(
        1
        for module in MODULES
        if module.implemented
    )

    loaded = sum(
        1
        for module in MODULES
        if module.implemented
        and (
            module.loaded
            or module.key
            in {
                "overview",
                "system_health",
            }
        )
    )

    failed = sum(
        1
        for module in MODULES
        if (
            module.renderer_path
            and not module.loaded
        )
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Modules",
            total,
        )

    with col2:
        st.metric(
            "Implemented",
            implemented,
        )

    with col3:
        st.metric(
            "Ready",
            loaded,
        )

    with col4:
        st.metric(
            "Errors",
            failed,
        )

    st.subheader("System Status")

    if failed == 0:
        st.success(
            "All registered module renderers are available."
        )
    else:
        st.warning(
            f"{failed} registered module renderer(s) "
            "could not be imported."
        )

    # ------------------------------------------------------------
    # PROJECT MODEL STATUS
    # ------------------------------------------------------------

    if _PROJECT_MODELS_OK:
        st.success(
            "Projects database model registry is ready."
        )
    else:
        st.error(
            "Projects database model registry failed."
        )

        if _PROJECT_MODELS_ERROR is not None:
            with st.expander(
                "Projects model registration error"
            ):
                st.exception(
                    _PROJECT_MODELS_ERROR
                )


# ============================================================================
# SYSTEM HEALTH
# ============================================================================

def _render_system_health() -> None:
    _render_page_header(
        "System Health",
        "IMAGINE application and module diagnostics.",
    )

    # ------------------------------------------------------------
    # RUNTIME
    # ------------------------------------------------------------

    st.subheader("Runtime")

    columns = st.columns(4)

    with columns[0]:
        st.metric(
            "Python",
            (
                f"{sys.version_info.major}."
                f"{sys.version_info.minor}."
                f"{sys.version_info.micro}"
            ),
        )

    with columns[1]:
        st.metric(
            "Streamlit",
            getattr(
                st,
                "__version__",
                "unknown",
            ),
        )

    with columns[2]:
        st.metric(
            "Application",
            APP_VERSION,
        )

    with columns[3]:
        st.metric(
            "Registered Modules",
            len(MODULES),
        )

    # ------------------------------------------------------------
    # DATABASE MODEL REGISTRY
    # ------------------------------------------------------------

    st.subheader("Database Model Registry")

    if _PROJECT_MODELS_OK:
        st.success(
            "Projects ORM registration: READY"
        )
    else:
        st.error(
            "Projects ORM registration: FAILED"
        )

        if _PROJECT_MODELS_ERROR is not None:
            st.exception(
                _PROJECT_MODELS_ERROR
            )

        if _PROJECT_MODELS_TRACEBACK:
            with st.expander(
                "Complete Projects mapper/import traceback"
            ):
                st.code(
                    _PROJECT_MODELS_TRACEBACK,
                    language="text",
                )

    # ------------------------------------------------------------
    # MODULE REGISTRY
    # ------------------------------------------------------------

    st.subheader("Module Registry")

    rows: list[dict[str, str]] = []

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

        renderer = (
            f"{module.renderer_path}:"
            f"{module.renderer_name}"
            if module.renderer_path
            else "Built-in"
        )

        rows.append(
            {
                "Module": module.label,
                "Section": module.section,
                "Status": status,
                "Renderer": renderer,
            }
        )

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
    )

    # ------------------------------------------------------------
    # FAILED MODULES
    # ------------------------------------------------------------

    failed_modules = [
        module
        for module in MODULES
        if (
            module.renderer_path
            and not module.loaded
        )
    ]

    if failed_modules:
        st.subheader("Module Errors")

        for module in failed_modules:
            with st.expander(
                f"{module.icon} {module.label}"
            ):
                st.error(
                    f"{module.label} could not be loaded."
                )

                if module.import_error is not None:
                    st.exception(
                        module.import_error
                    )

                if module.traceback_text:
                    st.code(
                        module.traceback_text,
                        language="text",
                    )


# ============================================================================
# UNAVAILABLE MODULE
# ============================================================================

def _render_unavailable(
    module: ModuleDefinition,
) -> None:
    _render_page_header(
        module.label,
        module.description,
    )

    st.error(
        f"{module.label} could not be loaded."
    )

    if module.import_error is not None:
        with st.expander(
            "Complete import traceback",
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
# UNIMPLEMENTED MODULE
# ============================================================================

def _render_unimplemented(
    module: ModuleDefinition,
) -> None:
    _render_page_header(
        module.label,
        module.description,
    )

    st.info(
        f"{module.label} is registered in IMAGINE, "
        "but a Streamlit renderer has not yet been implemented."
    )


# ============================================================================
# SAFE RENDERER EXECUTION
# ============================================================================

def _render_module(
    module: ModuleDefinition,
) -> None:
    """
    Render a registered module while isolating runtime errors.
    """

    if not module.implemented:
        _render_unimplemented(module)
        return

    if module.renderer is None:
        _render_unavailable(module)
        return

    try:
        module.renderer()

    except Exception as exc:
        st.error(
            f"{module.label} could not be loaded."
        )

        st.markdown(
            f"**{module.label} runtime error**"
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
# ROUTING
# ============================================================================

def _render_current_module() -> None:
    selected = (
        st.session_state.imagine_selected_module
    )

    module = MODULE_REGISTRY.get(selected)

    if module is None:
        module = MODULE_REGISTRY["overview"]

        st.session_state.imagine_selected_module = (
            "overview"
        )

    if module.key == "overview":
        _render_overview()
        return

    if module.key == "system_health":
        _render_system_health()
        return

    _render_module(module)


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

def main() -> None:
    """
    Zero-argument Streamlit application entry point.
    """

    _render_sidebar()

    _render_current_module()


# ============================================================================
# START APPLICATION
# ============================================================================

if __name__ == "__main__":
    main()