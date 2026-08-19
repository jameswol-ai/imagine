"""
IMAGINE
Generative Architecture & Civil Engine

Main Streamlit application entry point.
"""

from __future__ import annotations

from typing import Any, Callable

import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="IMAGINE",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# TYPES
# ============================================================

RenderFunction = Callable[[], Any]


# ============================================================
# SAFE IMPORT HELPERS
# ============================================================

def _safe_import(
    module_name: str,
    function_name: str,
) -> RenderFunction | None:
    """
    Import a renderer without allowing an optional module
    failure to crash the entire Streamlit application.
    """

    try:
        module = __import__(
            module_name,
            fromlist=[function_name],
        )

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
# PLACEHOLDER RENDERER
# ============================================================

def render_placeholder(
    module_name: str = "Module",
) -> None:
    """Render a safe placeholder for modules not yet implemented."""

    st.title(module_name)

    st.info(
        f"{module_name} is registered in IMAGINE, "
        "but its full interface is not available yet."
    )


# ============================================================
# OVERVIEW
# ============================================================

def render_overview() -> None:
    """Render the IMAGINE overview dashboard."""

    st.title("🏗️ IMAGINE")

    st.caption(
        "Generative Architecture & Civil Engine"
    )

    st.markdown(
        """
        ## Project Overview

        IMAGINE connects architectural constraints,
        planning, programming, compliance and generative
        design into one workflow.
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
            "Candidates",
            "0",
        )

    with col4:
        st.metric(
            "Best Designs",
            "0",
        )

    st.divider()

    st.subheader("Design Pipeline")

    pipeline = [
        "Project",
        "Zoning",
        "Site Planning",
        "Floor Planning",
        "Room Programming",
        "Compliance",
        "Generative Design",
    ]

    cols = st.columns(len(pipeline))

    for column, step in zip(
        cols,
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

    st.subheader("System Status")

    status_col1, status_col2 = st.columns(2)

    with status_col1:
        st.success(
            "IMAGINE application is running."
        )

    with status_col2:
        st.info(
            "Generative Design is constraint-driven."
        )


# ============================================================
# GENERATIVE DESIGN
# ============================================================

GENERATIVE_DESIGN_RENDERER = _safe_import(
    "architecture.generative_design.ui",
    "render_generative_design",
)


def render_generative_design_safe() -> None:
    """
    Render Generative Design.

    If the architecture module has an import/runtime problem,
    show a controlled diagnostic instead of crashing the app.
    """

    if GENERATIVE_DESIGN_RENDERER is None:
        st.title("✨ Generative Design")

        st.error(
            "The Generative Design interface could not be loaded."
        )

        st.warning(
            "The rest of IMAGINE remains available. "
            "Check the Generative Design module imports."
        )

        with st.expander(
            "Diagnostic information"
        ):
            st.code(
                "architecture.generative_design.ui."
                "render_generative_design"
            )

        return

    try:
        GENERATIVE_DESIGN_RENDERER()

    except Exception as exc:
        st.title("✨ Generative Design")

        st.error(
            "Generative Design encountered an error."
        )

        with st.expander(
            "Show error details"
        ):
            st.exception(exc)


# ============================================================
# OPTIONAL MODULE RENDERERS
# ============================================================

OPTIONAL_RENDERERS: dict[str, RenderFunction | None] = {
    "projects": _safe_import(
        "architecture.projects.ui",
        "render_projects",
    ),
    "zoning": _safe_import(
        "architecture.zoning.ui",
        "render_zoning",
    ),
    "site_planning": _safe_import(
        "architecture.site_planning.ui",
        "render_site_planning",
    ),
    "floor_planning": _safe_import(
        "architecture.floor_planning.ui",
        "render_floor_planning",
    ),
    "room_programming": _safe_import(
        "architecture.room_programming.ui",
        "render_room_programming",
    ),
    "compliance": _safe_import(
        "architecture.compliance.ui",
        "render_compliance",
    ),
}


# ============================================================
# MODULE REGISTRY
# ============================================================

MODULE_REGISTRY: list[dict[str, Any]] = [
    {
        "label": "Overview",
        "icon": "🏠",
        "route": "overview",
        "renderer": render_overview,
    },
    {
        "label": "Projects",
        "icon": "📁",
        "route": "projects",
        "renderer": OPTIONAL_RENDERERS["projects"],
    },
    {
        "label": "Zoning",
        "icon": "📐",
        "route": "zoning",
        "renderer": OPTIONAL_RENDERERS["zoning"],
    },
    {
        "label": "Site Planning",
        "icon": "🌐",
        "route": "site_planning",
        "renderer": OPTIONAL_RENDERERS["site_planning"],
    },
    {
        "label": "Floor Planning",
        "icon": "🏢",
        "route": "floor_planning",
        "renderer": OPTIONAL_RENDERERS["floor_planning"],
    },
    {
        "label": "Room Programming",
        "icon": "🚪",
        "route": "room_programming",
        "renderer": OPTIONAL_RENDERERS["room_programming"],
    },
    {
        "label": "Compliance",
        "icon": "✅",
        "route": "compliance",
        "renderer": OPTIONAL_RENDERERS["compliance"],
    },
    {
        "label": "Generative Design",
        "icon": "✨",
        "route": "generative_design",
        "renderer": render_generative_design_safe,
    },
]


# ============================================================
# ROUTE MAP
# ============================================================

MODULES_BY_ROUTE: dict[str, dict[str, Any]] = {
    module["route"]: module
    for module in MODULE_REGISTRY
}


# ============================================================
# VALIDATE REGISTRY
# ============================================================

def validate_module_registry() -> None:
    """Validate module route uniqueness."""

    routes = [
        module["route"]
        for module in MODULE_REGISTRY
    ]

    duplicates = {
        route
        for route in routes
        if routes.count(route) > 1
    }

    if duplicates:
        raise RuntimeError(
            "Duplicate module routes detected: "
            + ", ".join(
                sorted(duplicates)
            )
        )

    if "overview" not in MODULES_BY_ROUTE:
        raise RuntimeError(
            "Overview route is missing."
        )

    generative_design = (
        MODULES_BY_ROUTE.get(
            "generative_design"
        )
    )

    if generative_design is None:
        raise RuntimeError(
            "Generative Design route is missing."
        )


validate_module_registry()


# ============================================================
# SESSION STATE
# ============================================================

if "active_route" not in st.session_state:
    st.session_state.active_route = "overview"


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        # 🏗️ IMAGINE

        **Generative Architecture & Civil Engine**
        """
    )

    st.divider()

    st.caption("NAVIGATION")

    for module in MODULE_REGISTRY:

        route = module["route"]

        label = (
            f'{module["icon"]} '
            f'{module["label"]}'
        )

        if st.button(
            label,
            key=f"nav_{route}",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.active_route == route
                else "secondary"
            ),
        ):
            st.session_state.active_route = route
            st.rerun()

    st.divider()

    st.caption(
        "IMAGINE • Generative Architecture"
    )


# ============================================================
# ACTIVE MODULE
# ============================================================

active_route = st.session_state.get(
    "active_route",
    "overview",
)

module = MODULES_BY_ROUTE.get(
    active_route,
)

if module is None:
    st.session_state.active_route = "overview"
    module = MODULES_BY_ROUTE["overview"]


# ============================================================
# RENDER ACTIVE MODULE
# ============================================================

renderer = module.get(
    "renderer"
)

if callable(renderer):

    try:
        renderer()

    except Exception as exc:
        st.error(
            f'{module["label"]} could not be rendered.'
        )

        with st.expander(
            "Show error details"
        ):
            st.exception(exc)

else:
    render_placeholder(
        module["label"]
    )