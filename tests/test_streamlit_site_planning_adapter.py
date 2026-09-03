"""Compatibility tests for Site Planning routing."""
from __future__ import annotations

import inspect

import architecture.site_planning.ui as site_planning_ui
import streamlit_app


def test_site_planning_route_is_registered() -> None:
    spec = streamlit_app.spec_for_route("Site Planning")
    assert spec is not None
    assert spec.section == "ARCHITECTURE"
    assert spec.implemented is True


def test_site_planning_renderer_is_zero_argument() -> None:
    signature = inspect.signature(site_planning_ui.render_site_planning)
    assert not signature.parameters


def test_site_planning_route_uses_registered_renderer() -> None:
    spec = streamlit_app.spec_for_route("Site Planning")
    assert spec is not None
    assert spec.module_path == "architecture.site_planning.ui"
    assert spec.renderer_name == "render_site_planning"
