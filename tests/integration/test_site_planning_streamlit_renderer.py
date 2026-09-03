"""Integration contract for the current Site Planning Streamlit renderer."""
from __future__ import annotations

import inspect

import architecture.site_planning.ui as site_planning_ui


def test_site_planning_renderer_is_zero_argument() -> None:
    signature = inspect.signature(site_planning_ui.render_site_planning)
    assert not signature.parameters


def test_site_planning_renderer_is_callable() -> None:
    assert callable(site_planning_ui.render_site_planning)
