"""
IMAGINE
Generative Architecture & Civil Engine
"""

from __future__ import annotations

from typing import Any, Callable

import streamlit as st

from architecture.health import (
    health_summary,
    run_startup_health_check,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="IMAGINE",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)


RenderFunction = Callable[[], Any]


# ============================================================
# SAFE IMPORT
# ============================================================

def _safe_import(
    module_name: str,
    function_name: str,
) -> RenderFunction | None:

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
# OVERVIEW
# ============================================================

def render_overview() -> None:

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
        st.metric("Projects", "0")

    with col2:
        st.metric("Design Runs", "0")

    with col3:
        st.metric("Candidates", "0")

    with col4:
        st.metric("Best Designs", "0")

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

    columns = st.columns(
        len(pipeline)
    )

    for column, step in zip(
        columns,
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


# ============================================================
# GENERATIVE DESIGN
# ============================================================

GENERATIVE_DESIGN_RENDERER = _safe_import(
    "architecture.generative_design.ui",
    "render_generative_design",
)


def render_generative_design_safe() -> None:

    st.title("✨ Generative Design")

    if GENERATIVE_DESIGN_RENDERER is None:

        st.error(
            "The Generative Design interface "
            "could not be loaded."
        )

        st.info(
            "Open System Health to identify the "
            "first failing module."
        )

        return

    try:
        GENERATIVE_DESIGN_RENDERER()

    except Exception as exc:

        st.error(
            "Generative Design encountered an error."
        )

        with st.expander(
            "Show error details"
        ):
            st.exception(exc)


# ============================================================
# PLACEHOLDER
# ============================================================

def render_placeholder(
    module_name: str,
) -> None:

    st.title(module_name)

    st.info(
        f"{module_name} is registered in IMAGINE "
        "but its full interface is not available yet."
    )


# ============================================================
# OPTIONAL RENDERERS
# ============================================================

OPTIONAL_RENDERERS: dict[
    str,
    RenderFunction | None,
] = {

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

    {
        "label": "System Health",
        "icon": "🩺",
        "route": "system_health",
        "renderer": None,
    },
]


# ============================================================
# ROUTES
# ============================================================

MODULES_BY_ROUTE: dict[
    str,
    dict[str, Any],
] = {
    module["route"]: module
    for module in MODULE_REGISTRY
}


# ============================================================
# REGISTRY VALIDATION
# ============================================================

def validate_module_registry() -> None:

    routes = [
        module["route"]
        for module in MODULE_REGISTRY
    ]

    duplicates = sorted(
        {
            route
            for route in routes
            if routes.count(route) > 1
        }
    )

    if duplicates:
        raise RuntimeError(
            "Duplicate module routes detected: "
            + ", ".join(duplicates)
        )

    if "overview" not in MODULES_BY_ROUTE:
        raise RuntimeError(
            "Overview route is missing."
        )

    if "generative_design" not in MODULES_BY_ROUTE:
        raise RuntimeError(
            "Generative Design route is missing."
        )

    if "system_health" not in MODULES_BY_ROUTE:
        raise RuntimeError(
            "System Health route is missing."
        )


validate_module_registry()


# ============================================================
# HEALTH PAGE
# ============================================================

def render_system_health() -> None:

    st.title("🩺 System Health")

    st.caption(
        "IMAGINE startup and module diagnostics"
    )

    results = run_startup_health_check()

    summary = health_summary(
        results
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Modules Checked",
            summary["total"],
        )

    with col2:
        st.metric(
            "Healthy",
            summary["healthy"],
        )

    with col3:
        st.metric(
            "Failed",
            summary["failed"],
        )

    if summary["status"] == "healthy":
        st.success(
            "All checked modules imported successfully."
        )
    else:
        st.warning(
            "IMAGINE is running in degraded mode."
        )

    st.divider()

    for result in results:

        if result.status == "ok":

            st.success(
                f"✓ {result.name}"
            )

            if result.path:
                st.caption(
                    result.path
                )

        else:

            st.error(
                f"✗ {result.name}"
            )

            if result.error:
                st.code(
                    result.error
                )

            with st.expander(
                "Complete traceback"
            ):

                st.code(
                    result.traceback_text or "",
                    language="text",
                )

            if result.path:
                st.caption(
                    result.path
                )

    st.divider()

    if st.button(
        "🔄 Run Health Check Again",
        use_container_width=True,
    ):
        st.rerun()


MODULES_BY_ROUTE[
    "system_health"
]["renderer"] = render_system_health


# ============================================================
# SESSION STATE
# ============================================================

if "active_route" not in st.session_state:

    st.session_state.active_route = (
        "overview"
    )


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
                if (
                    st.session_state.active_route
                    == route
                )
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
# ROUTE RESOLUTION
# ============================================================

active_route = st.session_state.get(
    "active_route",
    "overview",
)

module = MODULES_BY_ROUTE.get(
    active_route
)

if module is None:

    st.session_state.active_route = (
        "overview"
    )

    module = MODULES_BY_ROUTE[
        "overview"
    ]


# ============================================================
# RENDER
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