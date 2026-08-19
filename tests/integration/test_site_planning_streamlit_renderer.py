"""
Integration tests for the zero-argument Site Planning Streamlit
renderer.

These tests verify:

1. render_route("architecture_site_planning") reaches the
   zero-argument Site Planning adapter.

2. The Site Planning adapter constructs:
       SitePlanningRepository
           ->
       SitePlanningService
           ->
       render_site_planning(service)

3. Import failures inside the adapter are caught and rendered
   through Streamlit without escaping the application shell.

4. Renderer failures are caught and rendered through Streamlit.

The existing asynchronous Site Planning service/API contract is
not modified by these tests.
"""

from __future__ import annotations

import builtins
from unittest.mock import MagicMock

import pytest


# ============================================================
# ROUTE TEST
# ============================================================


def test_render_route_reaches_site_planning_zero_argument_renderer(
    monkeypatch,
):
    """
    Verify that:

        render_route("architecture_site_planning")

    reaches the registered zero-argument Site Planning renderer.
    """

    import streamlit_app

    called = {
        "count": 0,
    }

    def fake_renderer():
        called["count"] += 1

    monkeypatch.setitem(
        streamlit_app.SPECIAL_RENDERERS,
        "architecture_site_planning",
        fake_renderer,
    )

    streamlit_app.render_route(
        "architecture_site_planning"
    )

    assert called["count"] == 1


# ============================================================
# ADAPTER SUCCESS TEST
# ============================================================


def test_site_planning_adapter_constructs_dependencies_and_renders(
    monkeypatch,
):
    """
    Verify the complete synchronous Streamlit adapter chain:

        SitePlanningRepository()
            ->
        SitePlanningService(repository)
            ->
        render_site_planning(service)
    """

    import streamlit_app

    repository = MagicMock(
        name="SitePlanningRepository"
    )

    service = MagicMock(
        name="SitePlanningService"
    )

    calls = []

    class FakeRepository:
        def __new__(cls):
            calls.append(
                "repository"
            )

            return repository

    class FakeService:
        def __new__(
            cls,
            repository_argument,
        ):
            calls.append(
                (
                    "service",
                    repository_argument,
                )
            )

            return service

    def fake_render(
        service_argument,
    ):
        calls.append(
            (
                "render",
                service_argument,
            )
        )

    # --------------------------------------------------------
    # Patch the actual source modules.
    #
    # The production adapter performs local imports, so patching
    # streamlit_app.SitePlanningRepository would not be sufficient.
    # --------------------------------------------------------

    monkeypatch.setattr(
        "architecture.site_planning.repository.SitePlanningRepository",
        FakeRepository,
    )

    monkeypatch.setattr(
        "architecture.site_planning.service.SitePlanningService",
        FakeService,
    )

    monkeypatch.setattr(
        "architecture.site_planning.ui.render_site_planning",
        fake_render,
    )

    # --------------------------------------------------------
    # Execute the zero-argument adapter.
    # --------------------------------------------------------

    streamlit_app.render_site_planning_registered()

    # --------------------------------------------------------
    # Verify dependency order.
    # --------------------------------------------------------

    assert calls == [
        "repository",
        (
            "service",
            repository,
        ),
        (
            "render",
            service,
        ),
    ]


# ============================================================
# IMPORT FAILURE TEST
# ============================================================


def test_site_planning_import_failure_is_contained(
    monkeypatch,
):
    """
    Verify that an exception raised during the adapter's local
    imports is caught by the Site Planning adapter.

    This test deliberately intercepts Python's actual import
    mechanism rather than patching attributes that may already
    exist on streamlit_app.

    Expected Streamlit behavior:

        st.error(
            "The Site Planning module could not be loaded."
        )

        with st.expander(
            "Complete import traceback",
            expanded=True,
        ):
            st.exception(exc)

    No exception should escape from the adapter.
    """

    import streamlit_app

    captured = {
        "errors": [],
        "exceptions": [],
        "expanders": [],
    }

    # --------------------------------------------------------
    # Capture st.error(...)
    # --------------------------------------------------------

    def fake_error(message):
        captured["errors"].append(
            message
        )

    monkeypatch.setattr(
        streamlit_app.st,
        "error",
        fake_error,
    )

    # --------------------------------------------------------
    # Capture st.exception(...)
    # --------------------------------------------------------

    def fake_exception(exc):
        captured["exceptions"].append(
            exc
        )

    monkeypatch.setattr(
        streamlit_app.st,
        "exception",
        fake_exception,
    )

    # --------------------------------------------------------
    # Capture st.expander(...)
    # --------------------------------------------------------

    class FakeExpander:
        def __enter__(self):
            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):
            return False

    def fake_expander(
        label,
        expanded=False,
    ):
        captured["expanders"].append(
            {
                "label": label,
                "expanded": expanded,
            }
        )

        return FakeExpander()

    monkeypatch.setattr(
        streamlit_app.st,
        "expander",
        fake_expander,
    )

    # --------------------------------------------------------
    # Intercept Python's real import mechanism.
    # --------------------------------------------------------

    real_import = builtins.__import__

    expected_message = (
        "No module named "
        "'test_site_planning_dependency'"
    )

    def failing_import(
        name,
        globals=None,
        locals=None,
        fromlist=(),
        level=0,
    ):
        """
        Fail only when the Site Planning repository module is
        imported.

        All unrelated imports continue through the real import
        mechanism.
        """

        if name == (
            "architecture.site_planning.repository"
        ):

            raise ModuleNotFoundError(
                expected_message,
                name="test_site_planning_dependency",
            )

        return real_import(
            name,
            globals,
            locals,
            fromlist,
            level,
        )

    monkeypatch.setattr(
        builtins,
        "__import__",
        failing_import,
    )

    # --------------------------------------------------------
    # Execute the adapter.
    #
    # The adapter must catch the exception internally.
    # --------------------------------------------------------

    streamlit_app.render_site_planning_registered()

    # --------------------------------------------------------
    # Verify exact Streamlit error.
    # --------------------------------------------------------

    assert captured["errors"] == [
        "The Site Planning module could not be loaded."
    ]

    # --------------------------------------------------------
    # Verify exact expander configuration.
    # --------------------------------------------------------

    assert captured["expanders"] == [
        {
            "label": "Complete import traceback",
            "expanded": True,
        }
    ]

    # --------------------------------------------------------
    # Verify the original exception reached st.exception().
    # --------------------------------------------------------

    assert len(
        captured["exceptions"]
    ) == 1

    exception = captured[
        "exceptions"
    ][0]

    assert isinstance(
        exception,
        ModuleNotFoundError,
    )

    assert (
        str(exception)
        == expected_message
    )


# ============================================================
# RENDER FAILURE TEST
# ============================================================


def test_site_planning_render_failure_is_contained(
    monkeypatch,
):
    """
    Verify that a failure inside render_site_planning(service)
    is caught by the adapter.

    Expected behavior:

        - st.error() is called.
        - the exact renderer exception reaches st.exception().
        - the exception does not escape the adapter.
    """

    import streamlit_app

    repository = MagicMock(
        name="SitePlanningRepository"
    )

    service = MagicMock(
        name="SitePlanningService"
    )

    render_error = RuntimeError(
        "Site Planning UI rendering failed"
    )

    captured = {
        "errors": [],
        "exceptions": [],
        "expanders": [],
    }

    # --------------------------------------------------------
    # Capture Streamlit error output.
    # --------------------------------------------------------

    def fake_error(message):
        captured["errors"].append(
            message
        )

    monkeypatch.setattr(
        streamlit_app.st,
        "error",
        fake_error,
    )

    # --------------------------------------------------------
    # Capture Streamlit exception output.
    # --------------------------------------------------------

    def fake_exception(exc):
        captured["exceptions"].append(
            exc
        )

    monkeypatch.setattr(
        streamlit_app.st,
        "exception",
        fake_exception,
    )

    # --------------------------------------------------------
    # Capture Streamlit expander.
    # --------------------------------------------------------

    class FakeExpander:
        def __enter__(self):
            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):
            return False

    def fake_expander(
        label,
        expanded=False,
    ):
        captured["expanders"].append(
            {
                "label": label,
                "expanded": expanded,
            }
        )

        return FakeExpander()

    monkeypatch.setattr(
        streamlit_app.st,
        "expander",
        fake_expander,
    )

    # --------------------------------------------------------
    # Replace Site Planning dependencies at their actual
    # source-module locations.
    # --------------------------------------------------------

    def fake_repository():
        return repository

    def fake_service(
        repository_argument,
    ):
        assert repository_argument is repository

        return service

    def broken_renderer(
        service_argument,
    ):
        assert service_argument is service

        raise render_error

    monkeypatch.setattr(
        "architecture.site_planning.repository.SitePlanningRepository",
        fake_repository,
    )

    monkeypatch.setattr(
        "architecture.site_planning.service.SitePlanningService",
        fake_service,
    )

    monkeypatch.setattr(
        "architecture.site_planning.ui.render_site_planning",
        broken_renderer,
    )

    # --------------------------------------------------------
    # Execute the adapter.
    #
    # No exception should escape.
    # --------------------------------------------------------

    streamlit_app.render_site_planning_registered()

    # --------------------------------------------------------
    # Verify error message.
    # --------------------------------------------------------

    assert captured["errors"] == [
        "Site Planning could not be rendered."
    ]

    # --------------------------------------------------------
    # Verify traceback expander.
    # --------------------------------------------------------

    assert captured["expanders"] == [
        {
            "label": "Complete renderer traceback",
            "expanded": True,
        }
    ]

    # --------------------------------------------------------
    # Verify exact exception.
    # --------------------------------------------------------

    assert captured["exceptions"] == [
        render_error
    ]


# ============================================================
# ROUTE FAILURE TEST
# ============================================================


def test_render_route_propagates_special_renderer_failure(
    monkeypatch,
):
    """
    Verify that render_route() correctly dispatches the
    architecture_site_planning route to the special renderer.

    This test intentionally verifies routing behavior only.

    The Site Planning adapter itself is responsible for
    converting its own import/render failures into Streamlit
    output.
    """

    import streamlit_app

    captured = {
        "called": False,
    }

    def fake_renderer():
        captured["called"] = True

        raise RuntimeError(
            "forced Site Planning failure"
        )

    monkeypatch.setitem(
        streamlit_app.SPECIAL_RENDERERS,
        "architecture_site_planning",
        fake_renderer,
    )

    with pytest.raises(
        RuntimeError,
        match="forced Site Planning failure",
    ):
        streamlit_app.render_route(
            "architecture_site_planning"
        )

    assert captured["called"] is True


# ============================================================
# COMPLETE ADAPTER CONTRACT TEST
# ============================================================


def test_site_planning_route_uses_special_renderer(
    monkeypatch,
):
    """
    Verify that the Site Planning route is registered as a
    special renderer and therefore does not go through the
    generic zero-argument renderer import mechanism.
    """

    import streamlit_app

    assert (
        "architecture_site_planning"
        in streamlit_app.SPECIAL_RENDERERS
    )

    renderer = (
        streamlit_app.SPECIAL_RENDERERS[
            "architecture_site_planning"
        ]
    )

    assert callable(
        renderer
    )


# ============================================================
# ASYNC API ISOLATION TEST
# ============================================================


def test_streamlit_adapter_does_not_require_async_renderer(
    monkeypatch,
):
    """
    Verify that the Streamlit adapter expects the synchronous
    service/UI boundary.

    The adapter should construct the synchronous service and
    pass it directly to render_site_planning().
    """

    import streamlit_app

    repository = MagicMock(
        name="SitePlanningRepository"
    )

    service = MagicMock(
        name="SitePlanningService"
    )

    captured = {
        "repository": None,
        "service": None,
    }

    def fake_repository():
        captured["repository"] = repository

        return repository

    def fake_service(
        repository_argument,
    ):
        assert repository_argument is repository

        captured["service"] = service

        return service

    def fake_renderer(
        service_argument,
    ):
        assert service_argument is service

    monkeypatch.setattr(
        "architecture.site_planning.repository.SitePlanningRepository",
        fake_repository,
    )

    monkeypatch.setattr(
        "architecture.site_planning.service.SitePlanningService",
        fake_service,
    )

    monkeypatch.setattr(
        "architecture.site_planning.ui.render_site_planning",
        fake_renderer,
    )

    streamlit_app.render_site_planning_registered()

    assert (
        captured["repository"]
        is repository
    )

    assert (
        captured["service"]
        is service
    )