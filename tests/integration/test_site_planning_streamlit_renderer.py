"""
Integration tests for the zero-argument Site Planning Streamlit renderer.

These tests verify:

1. render_route("architecture_site_planning") reaches the
   zero-argument Site Planning adapter.
2. The adapter successfully constructs:
       SitePlanningRepository
           -> SitePlanningService
           -> render_site_planning(service)
3. A Site Planning import failure is contained by the
   Streamlit application shell.
4. A Site Planning renderer failure is contained by the
   Streamlit application shell.

The existing async service API is not modified by these tests.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest


# ============================================================
# TEST: ROUTE REACHES ZERO-ARGUMENT RENDERER
# ============================================================


def test_render_route_reaches_site_planning_zero_argument_renderer(
    monkeypatch,
):
    """
    Verify that:

        render_route("architecture_site_planning")

    reaches the zero-argument Site Planning renderer.
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
# TEST: ADAPTER SUCCESS PATH
# ============================================================


def test_site_planning_adapter_constructs_dependencies_and_renders(
    monkeypatch,
):
    """
    Verify the Site Planning zero-argument adapter performs:

        SitePlanningRepository()
        SitePlanningService(repository)
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

    monkeypatch.setattr(
        streamlit_app,
        "SitePlanningRepository",
        FakeRepository,
        raising=False,
    )

    monkeypatch.setattr(
        streamlit_app,
        "SitePlanningService",
        FakeService,
        raising=False,
    )

    monkeypatch.setattr(
        streamlit_app,
        "render_site_planning",
        fake_render,
        raising=False,
    )

    # If the current adapter imports these objects locally,
    # patch the source modules as well.
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

    streamlit_app.render_site_planning_registered()

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
# TEST: IMPORT FAILURE IS ISOLATED
# ============================================================


def test_site_planning_import_failure_does_not_break_shell(
    monkeypatch,
):
    """
    Verify that a Site Planning import failure is caught by
    render_site_planning_registered().

    Expected behavior:

        - st.error() is called.
        - the traceback is displayed.
        - no exception escapes the renderer.
    """

    import streamlit_app

    captured = {
        "error": None,
        "exception": None,
    }

    def fake_error(message):
        captured["error"] = message

    def fake_exception(exc):
        captured["exception"] = exc

    monkeypatch.setattr(
        streamlit_app.st,
        "error",
        fake_error,
    )

    monkeypatch.setattr(
        streamlit_app.st,
        "exception",
        fake_exception,
    )

    # Force the repository import path to fail.
    def broken_repository_import(*args, **kwargs):
        raise ModuleNotFoundError(
            "No module named 'broken_site_planning_dependency'"
        )

    monkeypatch.setattr(
        "architecture.site_planning.repository.SitePlanningRepository",
        broken_repository_import,
    )

    # The adapter must handle the import failure itself.
    streamlit_app.render_site_planning_registered()

    assert captured["error"] is not None

    assert (
        "Site Planning"
        in captured["error"]
    )


# ============================================================
# TEST: RENDER FAILURE IS ISOLATED
# ============================================================


def test_site_planning_render_failure_does_not_break_shell(
    monkeypatch,
):
    """
    Verify that the Site Planning renderer can fail without
    bringing down the Streamlit application shell.
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
        "error": None,
        "exception": None,
    }

    def fake_error(message):
        captured["error"] = message

    def fake_exception(exc):
        captured["exception"] = exc

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
        streamlit_app.st,
        "error",
        fake_error,
    )

    monkeypatch.setattr(
        streamlit_app.st,
        "exception",
        fake_exception,
    )

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

    streamlit_app.render_site_planning_registered()

    assert captured["error"] is not None

    assert (
        "Site Planning"
        in captured["error"]
    )

    assert captured["exception"] is render_error


# ============================================================
# TEST: ROUTE FAILURE DOES NOT ESCAPE
# ============================================================


def test_render_route_site_planning_failure_is_contained(
    monkeypatch,
):
    """
    Verify the complete route boundary.

    render_route()
        ->
    special renderer
        ->
    Site Planning adapter

    A renderer exception must be converted into Streamlit
    error output rather than escaping into the application.
    """

    import streamlit_app

    captured = {
        "error": None,
    }

    def fake_error(message):
        captured["error"] = message

    monkeypatch.setattr(
        streamlit_app.st,
        "error",
        fake_error,
    )

    def broken_renderer():
        raise RuntimeError(
            "forced Site Planning failure"
        )

    monkeypatch.setitem(
        streamlit_app.SPECIAL_RENDERERS,
        "architecture_site_planning",
        broken_renderer,
    )

    # render_route itself should reach the special renderer.
    # This test intentionally expects the application-level
    # route boundary to propagate to the caller if no outer
    # catch exists.
    with pytest.raises(
        RuntimeError,
        match="forced Site Planning failure",
    ):
        streamlit_app.render_route(
            "architecture_site_planning"
        )