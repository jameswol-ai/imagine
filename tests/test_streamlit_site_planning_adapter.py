"""
Tests for the Site Planning Streamlit registry adapter.
"""

from __future__ import annotations

from unittest.mock import Mock, call, patch

import pytest

import streamlit_app


# ============================================================
# SUCCESSFUL ADAPTER EXECUTION
# ============================================================


def test_render_site_planning_registered_builds_dependency_chain():
    """
    Verify that the Site Planning adapter:

    1. Constructs SitePlanningRepository first.
    2. Passes that repository into SitePlanningService.
    3. Calls render_site_planning(service).
    """

    repository = Mock(
        name="site_planning_repository"
    )

    service = Mock(
        name="site_planning_service"
    )

    render_site_planning = Mock(
        name="render_site_planning"
    )

    with (
        patch(
            "architecture.site_planning.repository.SitePlanningRepository",
            return_value=repository,
        ) as repository_class,
        patch(
            "architecture.site_planning.service.SitePlanningService",
            return_value=service,
        ) as service_class,
        patch(
            "architecture.site_planning.ui.render_site_planning",
            render_site_planning,
        ),
    ):

        streamlit_app.render_site_planning_registered()

    # --------------------------------------------------------
    # Repository must be constructed first.
    # --------------------------------------------------------

    repository_class.assert_called_once_with()

    # --------------------------------------------------------
    # Service must receive the exact repository instance.
    # --------------------------------------------------------

    service_class.assert_called_once_with(
        repository
    )

    # --------------------------------------------------------
    # Renderer must receive the exact service instance.
    # --------------------------------------------------------

    render_site_planning.assert_called_once_with(
        service
    )

    # --------------------------------------------------------
    # Verify dependency order.
    # --------------------------------------------------------

    assert repository_class.call_count == 1
    assert service_class.call_count == 1
    assert render_site_planning.call_count == 1


# ============================================================
# EXPLICIT ORDER TEST
# ============================================================


def test_render_site_planning_registered_constructs_in_order():
    """
    Verify the exact dependency construction order:

        Repository
            ↓
        Service(repository)
            ↓
        render_site_planning(service)
    """

    events: list[str] = []

    repository = Mock(
        name="site_planning_repository"
    )

    service = Mock(
        name="site_planning_service"
    )

    def build_repository():
        events.append(
            "repository"
        )

        return repository

    def build_service(
        received_repository,
    ):
        events.append(
            "service"
        )

        assert received_repository is repository

        return service

    def render(
        received_service,
    ):
        events.append(
            "renderer"
        )

        assert received_service is service

    with (
        patch(
            "architecture.site_planning.repository.SitePlanningRepository",
            side_effect=build_repository,
        ),
        patch(
            "architecture.site_planning.service.SitePlanningService",
            side_effect=build_service,
        ),
        patch(
            "architecture.site_planning.ui.render_site_planning",
            side_effect=render,
        ),
    ):

        streamlit_app.render_site_planning_registered()

    assert events == [
        "repository",
        "service",
        "renderer",
    ]


# ============================================================
# REPOSITORY CONSTRUCTION FAILURE
# ============================================================


def test_render_site_planning_registered_propagates_repository_exception():
    """
    Repository construction failures must propagate.

    The Streamlit controller owns the outer exception handling.
    The adapter must not silently swallow the exception.
    """

    error = RuntimeError(
        "repository construction failed"
    )

    with patch(
        "architecture.site_planning.repository.SitePlanningRepository",
        side_effect=error,
    ):

        with pytest.raises(
            RuntimeError,
            match="repository construction failed",
        ):

            streamlit_app.render_site_planning_registered()


# ============================================================
# SERVICE CONSTRUCTION FAILURE
# ============================================================


def test_render_site_planning_registered_propagates_service_exception():
    """
    Service construction failures must propagate.
    """

    repository = Mock(
        name="site_planning_repository"
    )

    error = RuntimeError(
        "service construction failed"
    )

    with (
        patch(
            "architecture.site_planning.repository.SitePlanningRepository",
            return_value=repository,
        ),
        patch(
            "architecture.site_planning.service.SitePlanningService",
            side_effect=error,
        ) as service_class,
        patch(
            "architecture.site_planning.ui.render_site_planning",
        ) as renderer,
    ):

        with pytest.raises(
            RuntimeError,
            match="service construction failed",
        ):

            streamlit_app.render_site_planning_registered()

    service_class.assert_called_once_with(
        repository
    )

    renderer.assert_not_called()


# ============================================================
# RENDERER EXCEPTION
# ============================================================


def test_render_site_planning_registered_propagates_renderer_exception():
    """
    render_site_planning(service) exceptions must propagate.

    This is intentional. The adapter does not catch the
    exception because streamlit_app.py already owns the
    existing renderer-level error handling.
    """

    repository = Mock(
        name="site_planning_repository"
    )

    service = Mock(
        name="site_planning_service"
    )

    error = RuntimeError(
        "site planning renderer failed"
    )

    with (
        patch(
            "architecture.site_planning.repository.SitePlanningRepository",
            return_value=repository,
        ) as repository_class,
        patch(
            "architecture.site_planning.service.SitePlanningService",
            return_value=service,
        ) as service_class,
        patch(
            "architecture.site_planning.ui.render_site_planning",
            side_effect=error,
        ) as renderer,
    ):

        with pytest.raises(
            RuntimeError,
            match="site planning renderer failed",
        ):

            streamlit_app.render_site_planning_registered()

    repository_class.assert_called_once_with()

    service_class.assert_called_once_with(
        repository
    )

    renderer.assert_called_once_with(
        service
    )


# ============================================================
# NO EXTRA ARGUMENTS
# ============================================================


def test_render_site_planning_registered_is_zero_argument():
    """
    The registry adapter itself must require no arguments.
    """

    import inspect

    signature = inspect.signature(
        streamlit_app.render_site_planning_registered
    )

    assert list(
        signature.parameters
    ) == []


# ============================================================
# REGISTRY WIRING
# ============================================================


def test_site_planning_registry_uses_adapter():
    """
    Verify that the shared module registry points Site Planning
    at the zero-argument adapter rather than the raw renderer.
    """

    module = (
        streamlit_app.MODULES_BY_ROUTE[
            "site_planning"
        ]
    )

    assert (
        module["renderer"]
        is streamlit_app.render_site_planning_registered
    )