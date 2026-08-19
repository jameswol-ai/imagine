"""
IMAGINE
Generative Architecture & Civil Engine

Main Streamlit application shell.

This file is responsible for:
    - Application configuration
    - Sidebar navigation
    - Centralized renderer registry
    - Safe renderer imports
    - Renderer error isolation
    - Module status
    - System Health diagnostics

IMPORTANT:
    This shell does not modify database, service, schema, or model
    contracts. Individual modules own their own business logic.
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
# GLOBAL STYLING
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
            margin-bottom: 0.75rem;
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

        .imagine-status {
            font-size: 0.72rem;
            color: #777;
            margin-top: 0.4rem;
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
    """
    Definition of a navigable IMAGINE module.
    """

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

def initialize_session_state() -> None:
    """
    Initialize shell-level session state.

    Existing module-specific session state is left untouched.
    """

    if "imagine_selected_module" not in st.session_state:
        st.session_state.imagine_selected_module = "overview"

    if "imagine_user" not in st.session_state:
        st.session_state.imagine_user = "admin"

    if "imagine_role" not in st.session_state:
        st.session_state.imagine_role = "Administrator"

    if "imagine_renderer_errors" not in st.session_state:
        st.session_state.imagine_renderer_errors = {}


# ============================================================================
# SAFE IMPORTS
# ============================================================================

def safe_import(
    module_path: str,
) -> tuple[object | None, BaseException | None, str]:
    """
    Safely import a renderer module.

    A broken module cannot prevent the main application from loading.
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
    Import a renderer and verify that it can be called without
    required positional arguments.
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
                    f"requires arguments: {names}. "
                    "IMAGINE renderers must expose "
                    "a zero-argument render function."
                ),
                "",
            )

    except (TypeError, ValueError):
        pass

    return renderer, None, ""


# ============================================================================
# CENTRALIZED MODULE REGISTRY
# ============================================================================

def build_module_registry() -> list[ModuleDefinition]:
    """
    Build the centralized IMAGINE renderer registry.

    Existing module paths are used as-is.
    """

    return [
        # ====================================================================
        # MAIN
        # ====================================================================

        ModuleDefinition(
            key="overview",
            label="Overview",
            icon="🏠",
            section="MAIN",
            description=(
                "IMAGINE application overview."
            ),
            implemented=True,
        ),

        # ====================================================================
        # ARCHITECTURE
        # ====================================================================

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
                "Architectural and building compliance."
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

        # ====================================================================
        # PROJECTS
        # ====================================================================

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

        # ====================================================================
        # SYSTEM
        # ====================================================================

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


# ============================================================================
# RENDERER REGISTRATION
# ============================================================================

def register_renderers(
    modules: list[ModuleDefinition],
) -> None:
    """
    Resolve all registered renderers independently.
    """

    errors = st.session_state.imagine_renderer_errors

    for module in modules:
        if not module.implemented:
            continue

        if not module.renderer_path:
            continue

        if not module.renderer_name:
            module.import_error = RuntimeError(
                f"{module.key} has no renderer name."
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
            errors[module.key] = {
                "error": error,
                "traceback": error_traceback,
            }


# ============================================================================
# SIDEBAR
# ============================================================================

def render_sidebar(
    modules: list[ModuleDefinition],
) -> None:
    """
    Explicitly render the complete IMAGINE sidebar.

    This function is called directly from main().
    """

    with st.sidebar:

        # --------------------------------------------------------------------
        # BRAND
        # --------------------------------------------------------------------

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

        # --------------------------------------------------------------------
        # NAVIGATION
        # --------------------------------------------------------------------

        sections = [
            "MAIN",
            "ARCHITECTURE",
            "PROJECTS",
            "SYSTEM",
        ]

        for section in sections:

            st.markdown(
                f"""
                <div class="imagine-section">
                    {section}
                </div>
                """,
                unsafe_allow_html=True,
            )

            section_modules = [
                module
                for module in modules
                if module.section == section
            ]

            for module in section_modules:

                selected = (
                    st.session_state.imagine_selected_module
                    == module.key
                )

                # Renderer status.
                if (
                    module.renderer_path
                    and module.import_error is not None
                ):
                    status = " ⚠️"
                else:
                    status = ""

                button_label = (
                    f"{module.icon} "
                    f"{module.label}"
                    f"{status}"
                )

                if st.button(
                    button_label,
                    key=f"sidebar_{module.key}",
                    use_container_width=True,
                    type=(
                        "primary"
                        if selected
                        else "secondary"
                    ),
                ):
                    st.session_state.imagine_selected_module = (
                        module.key
                    )

                    st.rerun()

        st.divider()

        # --------------------------------------------------------------------
        # USER PANEL
        # --------------------------------------------------------------------

        st.markdown(
            """
            <div class="imagine-section">
                USER PANEL
            </div>
            """,
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
            key="sidebar_logout",
            use_container_width=True,
        ):
            st.session_state.imagine_selected_module = (
                "overview"
            )

            st.session_state.imagine_user = "admin"
            st.session_state.imagine_role = "Administrator"

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
        """
        <div class="imagine-page-label">
            IMAGINE | Generative Architecture
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.title(title)

    if description:
        st.caption(description)


# ============================================================================
# OVERVIEW
# ============================================================================

def render_overview(
    modules: list[ModuleDefinition],
) -> None:

    render_page_header(
        "Overview",
        "Generative Architecture & Civil Engine",
    )

    renderer_modules = [
        module
        for module in modules
        if module.renderer_path
    ]

    ready = sum(
        1
        for module in renderer_modules
        if module.renderer is not None
    )

    failed = sum(
        1
        for module in renderer_modules
        if module.import_error is not None
    )

    total = len(renderer_modules)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Registered Renderers",
            total,
        )

    with col2:
        st.metric(
            "Ready",
            ready,
        )

    with col3:
        st.metric(
            "Errors",
            failed,
        )

    st.subheader("IMAGINE")

    st.write(
        "Generative Architecture & Civil Engine "
        "for architectural planning, project delivery, "
        "and civil-engineering workflows."
    )

    if failed == 0:
        st.success(
            "All registered renderers are available."
        )
    else:
        st.warning(
            f"{failed} registered renderer(s) "
            "currently have import errors. "
            "Open System Health for diagnostics."
        )


# ============================================================================
# SYSTEM HEALTH
# ============================================================================

def render_system_health(
    modules: list[ModuleDefinition],
) -> None:

    render_page_header(
        "System Health",
        "IMAGINE application and renderer diagnostics.",
    )

    # ------------------------------------------------------------------------
    # Runtime
    # ------------------------------------------------------------------------

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
            "IMAGINE",
            APP_VERSION,
        )

    # ------------------------------------------------------------------------
    # Module table
    # ------------------------------------------------------------------------

    st.subheader("Module Status")

    rows = []

    for module in modules:

        if module.key in {
            "overview",
            "system_health",
        }:
            status = "READY"

        elif not module.implemented:
            status = "NOT IMPLEMENTED"

        elif module.renderer is not None:
            status = "READY"

        else:
            status = "ERROR"

        rows.append(
            {
                "Module": module.label,
                "Section": module.section,
                "Status": status,
                "Renderer": (
                    (
                        f"{module.renderer_path}."
                        f"{module.renderer_name}"
                    )
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

    # ------------------------------------------------------------------------
    # Errors
    # ------------------------------------------------------------------------

    failures = [
        module
        for module in modules
        if (
            module.renderer_path
            and module.renderer is None
        )
    ]

    if not failures:
        st.success(
            "No renderer import failures detected."
        )
        return

    st.subheader("Renderer Diagnostics")

    for module in failures:

        with st.expander(
            f"{module.icon} {module.label}",
            expanded=False,
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
# MODULE ERROR
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
# UNIMPLEMENTED MODULE
# ============================================================================

def render_unimplemented_module(
    module: ModuleDefinition,
) -> None:

    render_page_header(
        module.label,
        module.description,
    )

    st.info(
        f"{module.label} is registered in IMAGINE, "
        "but a Streamlit renderer has not yet "
        "been implemented."
    )


# ============================================================================
# MODULE ROUTER
# ============================================================================

def render_selected_module(
    modules: list[ModuleDefinition],
) -> None:

    registry = {
        module.key: module
        for module in modules
    }

    selected_key = (
        st.session_state.imagine_selected_module
    )

    module = registry.get(selected_key)

    # ------------------------------------------------------------------------
    # Invalid navigation state
    # ------------------------------------------------------------------------

    if module is None:

        st.session_state.imagine_selected_module = (
            "overview"
        )

        module = registry["overview"]

    # ------------------------------------------------------------------------
    # Built-in pages
    # ------------------------------------------------------------------------

    if module.key == "overview":
        render_overview(modules)
        return

    if module.key == "system_health":
        render_system_health(modules)
        return

    # ------------------------------------------------------------------------
    # Not implemented
    # ------------------------------------------------------------------------

    if not module.implemented:
        render_unimplemented_module(module)
        return

    # ------------------------------------------------------------------------
    # Renderer import failed
    # ------------------------------------------------------------------------

    if module.renderer is None:
        render_module_error(module)
        return

    # ------------------------------------------------------------------------
    # Execute renderer
    # ------------------------------------------------------------------------

    try:
        module.renderer()

    except Exception as exc:

        # Store the runtime error without killing the application.
        st.session_state.imagine_renderer_errors[
            module.key
        ] = {
            "error": exc,
            "traceback": traceback.format_exc(),
        }

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
# MAIN APPLICATION
# ============================================================================

def main() -> None:
    """
    Main IMAGINE application entry point.

    Sidebar creation is deliberately explicit here.
    """

    # ------------------------------------------------------------------------
    # Session state
    # ------------------------------------------------------------------------

    initialize_session_state()

    # ------------------------------------------------------------------------
    # Build registry
    # ------------------------------------------------------------------------

    modules = build_module_registry()

    # ------------------------------------------------------------------------
    # Resolve renderers
    # ------------------------------------------------------------------------

    register_renderers(modules)

    # ------------------------------------------------------------------------
    # EXPLICIT SIDEBAR
    #
    # This is intentionally called directly from main().
    # ------------------------------------------------------------------------

    render_sidebar(modules)

    # ------------------------------------------------------------------------
    # Main content
    # ------------------------------------------------------------------------

    render_selected_module(modules)


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()