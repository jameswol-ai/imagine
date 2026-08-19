"""
Integration tests for the zero-argument Site Planning
Streamlit renderer.

These tests verify that:

    render_site_planning_registered()

can construct the Site Planning repository/service stack
and delegate to:

    render_site_planning(service)

without changing the existing async service API.
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock

import pytest


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# STREAMLIT MOCK
# ============================================================


class FakeStreamlit:
    """Minimal Streamlit surface required by the adapter."""

    def __init__(self) -> None:
        self.errors: list[str] = []
        self.infos: list[str] = []

    def title(self, value: str) -> None:
        pass

    def error(self, value: str) -> None:
        self.errors.append(value)

    def info(self, value: str) -> None:
        self.infos.append(value)

    def warning(self, value: str) -> None:
        pass

    def caption(self, value: str) -> None:
        pass

    def markdown(self, value: str, **kwargs) -> None:
        pass

    def divider(self) -> None:
        pass

    def subheader(self, value: str) -> None:
        pass

    def columns(self, count: int):
        return [self for _ in range(count)]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False


# ============================================================
# LOAD APPLICATION ADAPTER
# ============================================================


def load_renderer(monkeypatch):
    """
    Import the Streamlit application after replacing Streamlit
    with a minimal test double.

    The test intentionally imports the existing application
    shell rather than duplicating its renderer.
    """

    fake_st = FakeStreamlit()

    monkeypatch.setitem(
        sys.modules,
        "streamlit",
        fake_st,
    )

    import streamlit_app

    return streamlit_app, fake_st


# ============================================================
# SUCCESS PATH
# ============================================================


def test_site_planning_zero_argument_renderer_reaches_ui(
    monkeypatch,
):
    """
    Verify that the zero-argument adapter:

        render_site_planning_registered()

    constructs the repository/service stack and calls:

        render_site_planning(service)
    """

    streamlit_app, fake_st = load_renderer(
        monkeypatch
    )

    repository = MagicMock(
        name="SitePlanningRepository"
    )

    service = MagicMock(
        name="SitePlanningService"
    )

    render_ui = MagicMock(
        name="render_site_planning"
    )

    # --------------------------------------------------------
    # Replace the three Site Planning dependencies.
    # --------------------------------------------------------

    repository_module = ModuleType(
        "architecture.site_planning.repository"
    )

    repository_module.SitePlanningRepository = (
        lambda: repository
    )

    service_module = ModuleType(
        "architecture.site_planning.service"
    )

    service_module.SitePlanningService = (
        lambda repo: service
    )

    ui_module = ModuleType(
        "architecture.site_planning.ui"
    )

    ui_module.render_site_planning = render_ui

    monkeypatch.setitem(
        sys.modules,
        "architecture.site_planning.repository",
        repository_module,
    )

    monkeypatch.setitem(
        sys.modules,
        "architecture.site_planning.service",
        service_module,
    )

    monkeypatch.setitem(
        sys.modules,
        "architecture.site_planning.ui",
        ui_module,
    )

    # --------------------------------------------------------
    # Execute zero-argument adapter.
    # --------------------------------------------------------

    streamlit_app.render_site_planning_registered()

    # --------------------------------------------------------
    # Verify dependency chain.
    # --------------------------------------------------------

    render_ui.assert_called_once_with(
        service
    )

    assert fake_st.errors == []


# ============================================================
# IMPORT FAILURE
# ============================================================


def test_site_planning_import_failure_isolated(
    monkeypatch,
):
    """
    Verify that an import failure is caught by the adapter
    instead of escaping into the application shell.
    """

    streamlit_app, fake_st = load_renderer(
        monkeypatch
    )

    def fail_import(name, *args, **kwargs):
        if name.startswith(
            "architecture.site_planning."
        ):
            raise ModuleNotFoundError(
                "Simulated Site Planning import failure"
            )

        return __import__(
            name,
            *args,
            **kwargs,
        )

    monkeypatch.setattr(
        "builtins.__import__",
        fail_import,
    )

    # The adapter must not raise.
    streamlit_app.render_site_planning_registered()

    assert fake_st.errors

    assert any(
        "Site Planning module could not be loaded"
        in message
        for message in fake_st.errors
    )


# ============================================================
# RENDER FAILURE
# ============================================================


def test_site_planning_render_failure_is_isolated(
    monkeypatch,
):
    """
    Verify that a renderer exception is caught and presented
    as a Site Planning error instead of crashing the shell.
    """

    streamlit_app, fake_st = load_renderer(
        monkeypatch
    )

    repository = MagicMock(
        name="SitePlanningRepository"
    )

    service = MagicMock(
        name="SitePlanningService"
    )

    def failing_renderer(service):
        raise RuntimeError(
            "Simulated Site Planning renderer failure"
        )

    repository_module = ModuleType(
        "architecture.site_planning.repository"
    )

    repository_module.SitePlanningRepository = (
        lambda: repository
    )

    service_module = ModuleType(
        "architecture.site_planning.service"
    )

    service_module.SitePlanningService = (
        lambda repo: service
    )

    ui_module = ModuleType(
        "architecture.site_planning.ui"
    )

    ui_module.render_site_planning = (
        failing_renderer
    )

    monkeypatch.setitem(
        sys.modules,
        "architecture.site_planning.repository",
        repository_module,
    )

    monkeypatch.setitem(
        sys.modules,
        "architecture.site_planning.service",
        service_module,
    )

    monkeypatch.setitem(
        sys.modules,
        "architecture.site_planning.ui",
        ui_module,
    )

    # --------------------------------------------------------
    # Adapter must catch renderer failure.
    # --------------------------------------------------------

    streamlit_app.render_site_planning_registered()

    assert fake_st.errors

    assert any(
        "Site Planning could not be rendered"
        in message
        for message in fake_st.errors
    )