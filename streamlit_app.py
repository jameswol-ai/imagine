"""
IMAGINE
Generative Architecture & Civil Engine

Resilient Streamlit application shell.

Responsibilities
----------------
- Configure the Streamlit application.
- Provide centralized navigation.
- Maintain a centralized renderer registry.
- Keep renderer imports isolated.
- Prevent one broken module from crashing the entire application.
- Register Projects SQLAlchemy models before Projects services execute.
- Provide module-status diagnostics.
- Provide System Health diagnostics.
- Preserve the zero-argument Streamlit renderer contract.

IMPORTANT
---------
Individual modules remain responsible for their own database/service
contracts. This shell intentionally does not rewrite those contracts.
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
# APPLICATION CONSTANTS
# ============================================================================

APP_NAME = "IMAGINE"
APP_SUBTITLE = "Generative Architecture & Civil Engine"
APP_VERSION = "1.0.0 Alpha"


# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title=f"{APP_NAME} | Generative Architecture",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================================
# GLOBAL CSS
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
            border-right: 1px solid rgba(128, 128, 128, 0.18);
        }

        .imagine-brand {
            font-size: 1.45rem;
            font-weight: 800;
            letter-spacing: 0.02em;
        }

        .imagine-subtitle {
            color: #777;
            font-size: 0.82rem;
            margin-top: -0.25rem;
        }

        .module-card {
            border: 1px solid rgba(128, 128, 128, 0.18);
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 0.75rem;
        }

        .status-ok {
            color: #16803c;
            font-weight: 700;
        }

        .status-error {
            color: #c62828;
            font-weight: 700;
        }

        .status-warning {
            color: #b26a00;
            font-weight: 700;
        }

        .status-muted {
            color: #777;
        }

        .section-label {
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.1em;
            color: #777;
            margin-top: 1rem;
            margin-bottom: 0.35rem;
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


# ============================================================================
# SAFE IMPORT HELPERS
# ============================================================================

def _safe_import(
    module_path: str,
) -> tuple[Any | None, BaseException | None, str]:
    """
    Import a module without allowing an import failure to crash IMAGINE.
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
) -> tuple[Renderer | None, BaseException | None, str]:
    """
    Import a module and resolve its renderer.

    Renderer contract:
        render_<module>() -> Any

    The shell intentionally accepts only a zero-argument callable.
    """

    module, import_error, import_traceback = _safe_import(module_path)

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
                f"{module_path}.{renderer_name} is not callable."
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
            return (
                None,
                TypeError(
                    f"{module_path}.{renderer_name} does not "
                    "satisfy the zero-argument renderer contract. "
                    f"Required parameters: "
                    f"{', '.join(p.name for p in required_parameters)}"
                ),
                "",
            )

    except (TypeError, ValueError):
        # Some callables do not expose signatures. The callable itself
        # remains usable, so do not reject it here.
        pass

    return renderer, None, ""


# ============================================================================
# PROJECT MODEL REGISTRATION
# ============================================================================

def _register_project_models() -> tuple[bool, BaseException | None, str]:
    """
    Register the complete Projects SQLAlchemy model graph before any
    Projects service query executes.

    This deliberately imports relationship targets before Project.

    The application shell does not modify database models.
    """

    try:
        # Core model dependencies.
        importlib.import_module(
            "database.models.organization"
        )

        importlib.import_module(
            "database.models.user"
        )

        # Projects relationship targets first.
        importlib.import_module(
            "projects.approvals.models"
        )

        importlib.import_module(
            "projects.revisions.models"
        )

        # Project itself last.
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


_PROJECT_MODELS_OK, _PROJECT_MODELS_ERROR, _PROJECT_MODELS_TRACEBACK = (
    _register_project_models()
)


# ============================================================================
# MODULE DEFINITIONS
# ============================================================================

MODULES: list[ModuleDefinition] = [
    # ------------------------------------------------------------------------
    # OVERVIEW
    # ------------------------------------------------------------------------

    ModuleDefinition(
        key="overview",
        label="Overview",
        icon="🏠",
        section="MAIN",
        description="IMAGINE system overview and health.",
        renderer_path=None,
        renderer_name="",
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
        description="Site planning and site development.",
        renderer_path="architecture.site_planning.ui",
        renderer_name="render_site_planning",
        implemented=True,
    ),

    ModuleDefinition(
        key="zoning",
        label="Zoning",
        icon="🗺️",
        section="ARCHITECTURE",
        description="Zoning and land-use planning.",
        renderer_path="architecture.zoning.ui",
        renderer_name="render_zoning",
        implemented=True,
    ),

    ModuleDefinition(
        key="floor_planning",
        label="Floor Planning",
        icon="🏢",
        section="ARCHITECTURE",
        description="Floor layout and planning.",
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
        description="Building and design compliance.",
        renderer_path="architecture.compliance.ui",
        renderer_name="render_compliance",
        implemented=True,
    ),

    ModuleDefinition(
        key="generative_design",
        label="Generative Design",
        icon="✨",
        section="ARCHITECTURE",
        description="Generative design and concept development.",
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
        description="Project approval workflows.",
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
        description="Application diagnostics and module status.",
        renderer_path=None,
        renderer_name="",
        implemented=True,
    ),
]


# ============================================================================
# MODULE REGISTRY
# ============================================================================

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
    Resolve a renderer without allowing a broken module to break the shell.
    """

    if not module.implemented:
        module.loaded = False
        return

    if not module.renderer_path:
        module.loaded = True
        return

    renderer, error, error_traceback = _resolve_renderer(
        module.renderer_path,
        module.renderer_name,
    )

    module.renderer = renderer
    module.import_error = error
    module.traceback_text = error_traceback
    module.loaded = renderer is not None

    if error is not None:
        st.session_state.imagine_renderer_errors[
            module.key
        ] = {
            "error": error,
            "traceback": error_traceback,
        }

    st.session_state.imagine_module_status[
        module.key
    ] = {
        "loaded": module.loaded,
        "implemented": module.implemented,
        "error": error,
    }


def _load_all_renderers() -> None:
    """
    Resolve all renderer imports once per Streamlit process/session.
    """

    for module in MODULES:
        if module.key in (
            "overview",
            "system_health",
        ):
            continue

        _load_module_renderer(module)


# Load renderers after the model-registration attempt.
_load_all_renderers()


# ============================================================================
# UI HELPERS
# ============================================================================

def _module_status(
    module: ModuleDefinition,
) -> str:
    if not module.implemented:
        return "Not implemented"

    if module.loaded:
        return "Ready"

    return "Unavailable"


def _render_brand() -> None:
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


def _render_sidebar() -> None:
    with st.sidebar:
        _render_brand()

        st.divider()

        sections: list[str] = []

        for module in MODULES:
            if module.section not in sections:
                sections.append(module.section)

        for section in sections:
            st.markdown(
                f'<div class="section-label">{section}</div>',
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

                label = f"{module.icon} {module.label}"

                if not module.implemented:
                    label += " · unavailable"
                elif (
                    module.renderer_path
                    and not module.loaded
                ):
                    label += " · error"

                if st.button(
                    label,
                    key=f"nav_{module.key}",
                    use_container_width=True,
                    type="primary" if selected else "secondary",
                ):
                    st.session_state.imagine_selected_module = (
                        module.key
                    )
                    st.rerun()

        st.divider()

        st.caption(
            f"{APP_NAME} {APP_VERSION}"
        )


def _render_page_header(
    title: str,
    subtitle: str,
) -> None:
    st.title(title)
    if subtitle:
        st.caption(subtitle)


# ============================================================================
# OVERVIEW
# ============================================================================

def _render_overview() -> None:
    _render_page_header(
        "IMAGINE",
        "Generative Architecture & Civil Engine",
    )

    st.info(
        "Welcome to IMAGINE. Select a module from the navigation panel "
        "to begin."
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
            in (
                "overview",
                "system_health",
            )
        )
    )

    failed = sum(
        1
        for module in MODULES
        if (
            module.implemented
            and module.renderer_path
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
            "Unavailable",
            failed,
        )

    st.subheader("Application Status")

    if failed == 0:
        st.success(
            "All registered renderers are available."
        )
    else:
        st.warning(
            f"{failed} registered renderer(s) could not be loaded."
        )

    if not _PROJECT_MODELS_OK:
        st.error(
            "The Projects SQLAlchemy model registry could not "
            "be initialized."
        )

        if _PROJECT_MODELS_ERROR is not None:
            with st.expander(
                "Projects model registration error"
            ):
                st.exception(
                    _PROJECT_MODELS_ERROR
                )

    else:
        st.success(
            "Projects SQLAlchemy models registered successfully."
        )


# ============================================================================
# SYSTEM HEALTH
# ============================================================================

def _render_system_health() -> None:
    _render_page_header(
        "System Health",
        "IMAGINE application diagnostics.",
    )

    st.subheader("Runtime")

    runtime_columns = st.columns(3)

    with runtime_columns[0]:
        st.metric(
            "Python",
            f"{sys.version_info.major}."
            f"{sys.version_info.minor}."
            f"{sys.version_info.micro}",
        )

    with runtime_columns[1]:
        st.metric(
            "Streamlit",
            getattr(
                st,
                "__version__",
                "unknown",
            ),
        )

    with runtime_columns[2]:
        st.metric(
            "Modules",
            len(MODULES),
        )

    st.subheader("Projects ORM")

    if _PROJECT_MODELS_OK:
        st.success(
            "Projects model registration: READY"
        )
    else:
        st.error(
            "Projects model registration: FAILED"
        )

        if _PROJECT_MODELS_ERROR is not None:
            st.exception(
                _PROJECT_MODELS_ERROR
            )

        if _PROJECT_MODELS_TRACEBACK:
            with st.expander(
                "Complete Projects model traceback"
            ):
                st.code(
                    _PROJECT_MODELS_TRACEBACK,
                    language="text",
                )

    st.subheader("Renderer Registry")

    rows: list[dict[str, Any]] = []

    for module in MODULES:
        if module.key == "overview":
            status = "Ready"

        elif module.key == "system_health":
            status = "Ready"

        elif not module.implemented:
            status = "Not implemented"

        elif module.loaded:
            status = "Ready"

        else:
            status = "Failed"

        rows.append(
            {
                "Module": module.label,
                "Section": module.section,
                "Status": status,
                "Renderer": (
                    f"{module.renderer_path}."
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

    failed_modules = [
        module
        for module in MODULES
        if (
            module.renderer_path
            and not module.loaded
        )
    ]

    if failed_modules:
        st.subheader("Renderer Errors")

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
# SAFE RENDERER EXECUTION
# ============================================================================

def _render_registered_module(
    module: ModuleDefinition,
) -> None:
    """
    Execute a renderer while isolating runtime errors.

    Every registered renderer is expected to have a zero-argument
    Streamlit adapter.
    """

    if not module.implemented:
        _render_unimplemented(module)
        return

    if module.renderer is None:
        _render_renderer_unavailable(module)
        return

    try:
        module.renderer()

    except Exception as exc:
        st.error(
            f"{module.label} could not be loaded."
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


def _render_unimplemented(
    module: ModuleDefinition,
) -> None:
    _render_page_header(
        module.label,
        module.description,
    )

    st.info(
        f"{module.label} is registered in IMAGINE, "
        "but its interactive interface is not available yet."
    )


def _render_renderer_unavailable(
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
# ROUTING
# ============================================================================

def _render_current_module() -> None:
    selected_key = (
        st.session_state.imagine_selected_module
    )

    module = MODULE_REGISTRY.get(
        selected_key
    )

    if module is None:
        st.session_state.imagine_selected_module = (
            "overview"
        )

        module = MODULE_REGISTRY["overview"]

    if module.key == "overview":
        _render_overview()
        return

    if module.key == "system_health":
        _render_system_health()
        return

    _render_registered_module(module)


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main() -> None:
    """
    Main zero-argument Streamlit application entry point.
    """

    _render_sidebar()

    _render_current_module()


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()