"""
Tests for the IMAGINE Streamlit application module registry.
"""

from __future__ import annotations

import pytest

import streamlit_app
from architecture.generative_design.ui import (
    render_generative_design,
)


# =====================================================================
# MODULE_REGISTRY
# =====================================================================

def test_module_registry_is_not_empty() -> None:
    """
    The module registry must contain application modules.
    """

    assert streamlit_app.MODULE_REGISTRY

    assert len(
        streamlit_app.MODULE_REGISTRY
    ) > 0


def test_module_registry_contains_expected_core_routes() -> None:
    """
    Verify the core routes currently exposed by IMAGINE.
    """

    routes = {
        module.route
        for module in streamlit_app.MODULE_REGISTRY
    }

    expected_routes = {
        "Overview",
        "Projects",
        "Zoning",
        "Site Planning",
        "Floor Planning",
        "Room Programming",
        "Compliance",
        "Generative Design",
        "Structural",
        "MEP",
        "Costing",
        "Construction Planning",
        "RFIs",
        "Submittals",
        "Variations",
        "Snagging",
        "Drawings",
        "Specifications",
        "Contracts",
        "Reports",
        "AI Architect",
        "AI Engineer",
        "AI MEP",
        "AI QS",
        "AI PM",
        "Dashboards",
        "KPIs",
        "Portfolio",
        "Forecasting",
        "Administration",
    }

    assert expected_routes.issubset(
        routes
    )


def test_module_registry_entries_have_required_fields() -> None:
    """
    Every module definition must contain the fields required by
    the application router and sidebar.
    """

    for module in streamlit_app.MODULE_REGISTRY:

        assert module.route
        assert module.label
        assert module.icon
        assert module.section
        assert callable(
            module.renderer
        )


# =====================================================================
# MODULES_BY_ROUTE
# =====================================================================

def test_modules_by_route_contains_every_registry_entry() -> None:
    """
    Every registry entry must be indexed by its route.
    """

    assert len(
        streamlit_app.MODULES_BY_ROUTE
    ) == len(
        streamlit_app.MODULE_REGISTRY
    )

    for module in streamlit_app.MODULE_REGISTRY:

        assert (
            streamlit_app.MODULES_BY_ROUTE[
                module.route
            ]
            is module
        )


def test_modules_by_route_has_no_unregistered_routes() -> None:
    """
    The route index must not contain routes that are absent from
    the registry.
    """

    registry_routes = {
        module.route
        for module in streamlit_app.MODULE_REGISTRY
    }

    indexed_routes = set(
        streamlit_app.MODULES_BY_ROUTE
    )

    assert indexed_routes == registry_routes


# =====================================================================
# DUPLICATE ROUTES
# =====================================================================

def test_duplicate_route_detection() -> None:
    """
    _validate_module_registry() must reject duplicate routes.
    """

    original_registry = (
        streamlit_app.MODULE_REGISTRY
    )

    duplicate_module = (
        original_registry[0]
    )

    monkeypatched_registry = (
        *original_registry,
        duplicate_module,
    )

    # The validation function reads MODULE_REGISTRY directly,
    # so temporarily replace it with a duplicated registry.
    streamlit_app.MODULE_REGISTRY = (
        monkeypatched_registry
    )

    try:

        with pytest.raises(
            RuntimeError,
            match="Duplicate module routes detected",
        ):
            streamlit_app._validate_module_registry()

    finally:

        streamlit_app.MODULE_REGISTRY = (
            original_registry
        )


# =====================================================================
# DEFAULT ROUTE
# =====================================================================

def test_default_route_is_overview() -> None:
    """
    Overview must remain the application's default route.
    """

    assert (
        streamlit_app.DEFAULT_ROUTE
        == "Overview"
    )


def test_overview_exists_in_registry() -> None:
    """
    The default Overview route must exist in the registry.
    """

    assert (
        "Overview"
        in streamlit_app.MODULES_BY_ROUTE
    )


def test_overview_is_the_default_module() -> None:
    """
    The Overview registry entry must be resolvable through the
    default route.
    """

    overview = (
        streamlit_app.MODULES_BY_ROUTE[
            streamlit_app.DEFAULT_ROUTE
        ]
    )

    assert overview.route == "Overview"
    assert overview.label == "Overview"
    assert overview.icon == "🏠"
    assert overview.section == "PLATFORM"
    assert callable(
        overview.renderer
    )


# =====================================================================
# GENERATIVE DESIGN
# =====================================================================

def test_generative_design_route_exists() -> None:
    """
    Generative Design must remain registered.
    """

    assert (
        "Generative Design"
        in streamlit_app.MODULES_BY_ROUTE
    )


def test_generative_design_module_metadata() -> None:
    """
    Verify the expected Generative Design registry metadata.
    """

    module = (
        streamlit_app.MODULES_BY_ROUTE[
            "Generative Design"
        ]
    )

    assert module.route == "Generative Design"
    assert module.label == "Generative Design"
    assert module.icon == "✨"
    assert module.section == "ARCHITECTURE"


def test_generative_design_uses_real_renderer() -> None:
    """
    Generative Design must use the actual UI renderer rather than
    a placeholder renderer.
    """

    module = (
        streamlit_app.MODULES_BY_ROUTE[
            "Generative Design"
        ]
    )

    assert (
        module.renderer
        is render_generative_design
    )


def test_registry_validation_requires_real_generative_design_renderer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Registry validation must reject a Generative Design entry whose
    renderer has been replaced with a placeholder or another function.
    """

    original_registry = (
        streamlit_app.MODULE_REGISTRY
    )

    generative_design = (
        streamlit_app.MODULES_BY_ROUTE[
            "Generative Design"
        ]
    )

    replacement = streamlit_app.ModuleDefinition(
        route=generative_design.route,
        label=generative_design.label,
        icon=generative_design.icon,
        section=generative_design.section,
        renderer=lambda: None,
    )

    modified_registry = tuple(
        replacement
        if module.route == "Generative Design"
        else module
        for module in original_registry
    )

    monkeypatch.setattr(
        streamlit_app,
        "MODULE_REGISTRY",
        modified_registry,
    )

    with pytest.raises(
        RuntimeError,
        match=(
            "Generative Design must use "
            "render_generative_design"
        ),
    ):
        streamlit_app._validate_module_registry()


# =====================================================================
# REGISTRY VALIDATION
# =====================================================================

def test_module_registry_validation_passes() -> None:
    """
    The production registry must pass its own integrity validation.
    """

    streamlit_app._validate_module_registry()