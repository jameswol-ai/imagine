"""
IMAGINE
Generative Architecture & Engineering Platform

Main Streamlit application controller.

Navigation is driven by the shared module registry.

The application shell is responsible for:
    - Streamlit configuration
    - Sidebar navigation
    - Module routing
    - Application-level session state

Business logic belongs inside individual modules.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Final

import streamlit as st

from architecture.generative_design.ui import (
    render_generative_design,
)


# =====================================================================
# TYPES
# =====================================================================

Renderer = Callable[[], None]


@dataclass(frozen=True)
class ModuleDefinition:
    """
    Definition of one IMAGINE application module.
    """

    route: str
    label: str
    icon: str
    section: str
    renderer: Renderer


# =====================================================================
# CONSTANTS
# =====================================================================

DEFAULT_ROUTE: Final[str] = "Overview"


# =====================================================================
# GENERIC PLACEHOLDER RENDERER
# =====================================================================

def render_placeholder(
    title: str,
    description: str,
) -> Renderer:
    """
    Create a renderer for a module that has not yet been implemented.

    The returned function matches the Renderer protocol used by the
    module registry.
    """

    def renderer() -> None:
        st.title(title)
        st.info(description)

    return renderer


# =====================================================================
# MODULE REGISTRY
# =====================================================================

MODULE_REGISTRY: tuple[ModuleDefinition, ...] = (
    # -----------------------------------------------------------------
    # PLATFORM
    # -----------------------------------------------------------------

    ModuleDefinition(
        route="Overview",
        label="Overview",
        icon="🏠",
        section="PLATFORM",
        renderer=render_placeholder(
            "🏠 IMAGINE",
            "Platform overview is being integrated.",
        ),
    ),

    # -----------------------------------------------------------------
    # PROJECTS
    # -----------------------------------------------------------------

    ModuleDefinition(
        route="Projects",
        label="Projects",
        icon="📁",
        section="PROJECTS",
        renderer=render_placeholder(
            "📁 Projects",
            "Project management module is being integrated.",
        ),
    ),

    # -----------------------------------------------------------------
    # ARCHITECTURE
    # -----------------------------------------------------------------

    ModuleDefinition(
        route="Zoning",
        label="Zoning",
        icon="📐",
        section="ARCHITECTURE",
        renderer=render_placeholder(
            "📐 Zoning",
            "Zoning module is being integrated.",
        ),
    ),

    ModuleDefinition(
        route="Site Planning",
        label="Site Planning",
        icon="🗺️",
        section="ARCHITECTURE",
        renderer=render_placeholder(
            "🗺️ Site Planning",
            "Site Planning module is being integrated.",
        ),
    ),

    ModuleDefinition(
        route="Floor Planning",
        label="Floor Planning",
        icon="🏢",
        section="ARCHITECTURE",
        renderer=render_placeholder(
            "🏢 Floor Planning",
            "Floor Planning module is being integrated.",
        ),
    ),

    ModuleDefinition(
        route="Room Programming",
        label="Room Programming",
        icon="🚪",
        section="ARCHITECTURE",
        renderer=render_placeholder(
            "🚪 Room Programming",
            "Room Programming module is being integrated.",
        ),
    ),

    ModuleDefinition(
        route="Compliance",
        label="Compliance",
        icon="✅",
        section="ARCHITECTURE",
        renderer=render_placeholder(
            "✅ Compliance",
            "Compliance module is being integrated.",
        ),
    ),

    ModuleDefinition(
        route="Generative Design",
        label="Generative Design",
        icon="✨",
        section="ARCHITECTURE",
        renderer=render_generative_design,
    ),

    # -----------------------------------------------------------------
    # ENGINEERING
    # -----------------------------------------------------------------

    ModuleDefinition(
        route="Structural",
        label="Structural",
        icon="🏗️",
        section="ENGINEERING",
        renderer=render_placeholder(
            "🏗️ Structural Engineering",
            "Structural engineering module is being integrated.",
        ),
    ),

    ModuleDefinition(
        route="MEP",
        label="MEP",
        icon="⚡",
        section="ENGINEERING",
        renderer=render_placeholder(
            "⚡ MEP Engineering",
            "MEP engineering module is being integrated.",
        ),
    ),

    # -----------------------------------------------------------------
    # COST MANAGEMENT
    # -----------------------------------------------------------------

    ModuleDefinition(
        route="Costing",
        label="Costing",
        icon="💰",
        section="COST MANAGEMENT",
        renderer=render_placeholder(
            "💰 Cost Management",
            "Costing module is being integrated.",
        ),
    ),

    # -----------------------------------------------------------------
    # CONSTRUCTION
    # -----------------------------------------------------------------

    ModuleDefinition(
        route="Construction Planning",
        label="Planning",
        icon="📅",
        section="CONSTRUCTION",
        renderer=render_placeholder(
            "📅 Construction Planning",
            "Construction planning module is being integrated.",
        ),
    ),

    ModuleDefinition(
        route="RFIs",
        label="RFIs",
        icon="📋",
        section="CONSTRUCTION",
        renderer=render_placeholder(
            "📋 Requests for Information",
            "RFI module is being integrated.",
        ),
    ),

    ModuleDefinition(
        route="Submittals",
        label="Submittals",
        icon="📄",
        section="CONSTRUCTION",
        renderer=render_placeholder(
            "📄 Submittals",
            "Submittals module is being integrated.",
        ),
    ),

    ModuleDefinition(
        route="Variations",
        label="Variations",
        icon="🔧",
        section="CONSTRUCTION",
        renderer=render_placeholder(
            "🔧 Variations",
            "Variation management module is being integrated.",
        ),
    ),

    ModuleDefinition(
        route="Snagging",
        label="Snagging",
        icon="🐛",
        section="CONSTRUCTION",
        renderer=render_placeholder(
            "🐛 Snagging",
            "Snagging module is being integrated.",
        ),
    ),

    # -----------------------------------------------------------------
    # DOCUMENTS
    # -----------------------------------------------------------------

    ModuleDefinition(
        route="Drawings",
        label="Drawings",
        icon="📐",
        section="DOCUMENTS",
        renderer=render_placeholder(
            "📐 Drawing Management",
            "Drawing management module is being integrated.",
        ),
    ),

    ModuleDefinition(
        route="Specifications",
        label="Specifications",
        icon="📑",
        section="DOCUMENTS",
        renderer=render_placeholder(
            "📑 Specifications",
            "Specifications module is being integrated.",
        ),
    ),

    ModuleDefinition(
        route="Contracts",
        label="Contracts",
        icon="📝",
        section="DOCUMENTS",
        renderer=render_placeholder(
            "📝 Contracts",
            "Contracts module is being integrated.",
        ),
    ),

    ModuleDefinition(
        route="Reports",
        label="Reports",
        icon="📚",
        section="DOCUMENTS",
        renderer=render_placeholder(
            "📚 Reports",
            "Reports module is being integrated.",
        ),
    ),

    # -----------------------------------------------------------------
    # AI
    # -----------------------------------------------------------------

    ModuleDefinition(
        route="AI Architect",
        label="IMAGINE Architect",
        icon="🤖",
        section="AI",
        renderer=render_placeholder(
            "🤖 IMAGINE Architect",
            "AI Architect module is being integrated.",
        ),
    ),

    ModuleDefinition(
        route="AI Engineer",
        label="IMAGINE Engineer",
        icon="🏗️",
        section="AI",
        renderer=render_placeholder(
            "🏗️ IMAGINE Engineer",
            "AI Engineer module is being integrated.",
        ),
    ),

    ModuleDefinition(
        route="AI MEP",
        label="IMAGINE MEP",
        icon="⚡",
        section="AI",
        renderer=render_placeholder(
            "⚡ IMAGINE MEP",
            "AI MEP module is being integrated.",
        ),
    ),

    ModuleDefinition(
        route="AI QS",
        label="IMAGINE QS",
        icon="💰",
        section="AI",
        renderer=render_placeholder(
            "💰 IMAGINE QS",
            "AI Quantity Surveyor module is being integrated.",
        ),
    ),

    ModuleDefinition(
        route="AI PM",
        label="IMAGINE PM",
        icon="📋",
        section="AI",
        renderer=render_placeholder(
            "📋 IMAGINE PM",
            "AI Project Manager module is being integrated.",
        ),
    ),

    # -----------------------------------------------------------------
    # ANALYTICS
    # -----------------------------------------------------------------

    ModuleDefinition(
        route="Dashboards",
        label="Dashboards",
        icon="📊",
        section="ANALYTICS",
        renderer=render_placeholder(
            "📊 Dashboards",
            "Analytics dashboards are being integrated.",
        ),
    ),

    ModuleDefinition(
        route="KPIs",
        label="KPIs",
        icon="📈",
        section="ANALYTICS",
        renderer=render_placeholder(
            "📈 KPIs",
            "KPI module is being integrated.",
        ),
    ),

    ModuleDefinition(
        route="Portfolio",
        label="Portfolio",
        icon="🏢",
        section="ANALYTICS",
        renderer=render_placeholder(
            "🏢 Portfolio",
            "Portfolio analytics are being integrated.",
        ),
    ),

    ModuleDefinition(
        route="Forecasting",
        label="Forecasting",
        icon="🔮",
        section="ANALYTICS",
        renderer=render_placeholder(
            "🔮 Forecasting",
            "Forecasting module is being integrated.",
        ),
    ),

    # -----------------------------------------------------------------
    # ADMINISTRATION
    # -----------------------------------------------------------------

    ModuleDefinition(
        route="Administration",
        label="Administration",
        icon="⚙️",
        section="ADMINISTRATION",
        renderer=render_placeholder(
            "⚙️ Administration",
            "Administration module is being integrated.",
        ),
    ),
)


# =====================================================================
# REGISTRY INDEXES
# =====================================================================

MODULES_BY_ROUTE: dict[str, ModuleDefinition] = {
    module.route: module
    for module in MODULE_REGISTRY
}


# =====================================================================
# VALIDATE REGISTRY
# =====================================================================

def _validate_module_registry() -> None:
    """
    Validate registry integrity during application startup.
    """

    routes = [
        module.route
        for module in MODULE_REGISTRY
    ]

    if len(routes) != len(set(routes)):
        duplicates = sorted(
            {
                route
                for route in routes
                if routes.count(route) > 1
            }
        )

        raise RuntimeError(
            "Duplicate module routes detected: "
            f"{duplicates}"
        )

    if DEFAULT_ROUTE not in MODULES_BY_ROUTE:
        raise RuntimeError(
            f"Default route '{DEFAULT_ROUTE}' "
            "is missing from MODULE_REGISTRY."
        )

    generative_design = MODULES_BY_ROUTE.get(
        "Generative Design"
    )

    if generative_design is None:
        raise RuntimeError(
            "Generative Design route is missing "
            "from MODULE_REGISTRY."
        )

    if generative_design.renderer is not render_generative_design:
        raise RuntimeError(
            "Generative Design must use "
            "render_generative_design."
        )


_validate_module_registry()


# =====================================================================
# APPLICATION STATE
# =====================================================================

if "active_module" not in st.session_state:
    st.session_state.active_module = DEFAULT_ROUTE


# =====================================================================
# NAVIGATION
# =====================================================================

def navigate_to(route: str) -> None:
    """
    Navigate to a registered application route.
    """

    if route not in MODULES_BY_ROUTE:
        route = DEFAULT_ROUTE

    st.session_state.active_module = route


# =====================================================================
# SIDEBAR
# =====================================================================

with st.sidebar:

    # -----------------------------------------------------------------
    # Brand
    # -----------------------------------------------------------------

    st.markdown(
        """
        # 🏗️ IMAGINE

        **Generative Architecture & Engineering**
        """
    )

    st.divider()

    # -----------------------------------------------------------------
    # Render modules grouped by section
    # -----------------------------------------------------------------

    sections: list[str] = []

    for module in MODULE_REGISTRY:

        if module.section not in sections:
            sections.append(
                module.section
            )

    for section in sections:

        st.markdown(
            f"### {section}"
        )

        for module in MODULE_REGISTRY:

            if module.section != section:
                continue

            if st.button(
                f"{module.icon} {module.label}",
                use_container_width=True,
                key=f"nav_{module.route}",
            ):
                navigate_to(
                    module.route
                )


# =====================================================================
# MAIN ROUTER
# =====================================================================

active_route = st.session_state.get(
    "active_module",
    DEFAULT_ROUTE,
)


# ---------------------------------------------------------------------
# Fallback behavior
# ---------------------------------------------------------------------

if active_route not in MODULES_BY_ROUTE:

    st.session_state.active_module = DEFAULT_ROUTE

    st.rerun()


# ---------------------------------------------------------------------
# Resolve registered module
# ---------------------------------------------------------------------

module = MODULES_BY_ROUTE[
    active_route
]


# ---------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------

module.renderer()
