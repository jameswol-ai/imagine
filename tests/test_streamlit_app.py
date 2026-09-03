"""Tests for the searchable IMAGINE Streamlit application shell."""
from __future__ import annotations

import inspect

import pandas as pd

import streamlit_app


def test_enterprise_registry_is_available() -> None:
    specs = streamlit_app.registry_snapshot()
    assert specs
    assert len(specs) >= 100


def test_expected_core_routes_are_registered() -> None:
    routes = {spec.route for spec in streamlit_app.registry_snapshot()}
    expected = {
        "Overview", "System Health", "Projects", "Approvals", "Revisions", "Zoning",
        "Site Planning", "Floor Planning", "Room Programming", "Compliance",
        "Generative Design", "Eurocode Suite", "Beam Design", "Column Design",
        "Buildings", "HVAC", "BOQ", "RFIs", "Drawings", "IMAGINE Architect",
        "Dashboards", "Assets", "Project Files",
    }
    assert expected.issubset(routes)


def test_default_route_can_be_initialized_to_overview() -> None:
    streamlit_app.st.session_state.pop("active_route", None)
    streamlit_app.init_session_state()
    assert streamlit_app.st.session_state.get("active_route") == "Overview"


def test_search_finds_modules_globally() -> None:
    results = streamlit_app.search_specs("beam", "All domains")
    assert results
    assert results[0].label == "Beam Design"


def test_search_can_filter_by_domain() -> None:
    results = streamlit_app.search_specs("design", "ARCHITECTURE")
    assert results
    assert all(spec.section == "ARCHITECTURE" for spec in results)


def test_implemented_eurocode_modules_are_searchable() -> None:
    results = streamlit_app.search_specs("EN 1990", "STRUCTURAL")
    assert results
    assert results[0].label == "EN 1990"
    assert results[0].implemented is True


def test_sidebar_uses_single_global_search() -> None:
    source = inspect.getsource(streamlit_app.render_sidebar)
    assert "st.radio" not in source
    assert "Quick Navigation" not in source
    assert "Search all workspaces" in source
    assert "Search domain" not in source
    assert "search_domains" not in source


def test_discipline_dashboard_is_available() -> None:
    assert callable(streamlit_app.render_discipline_dashboard)
    assert "STRUCTURAL" in streamlit_app.domains()


def test_home_dashboard_helpers_are_available() -> None:
    specs = streamlit_app.registry_snapshot()
    coverage = streamlit_app._coverage_frame(specs)
    assert isinstance(coverage, pd.DataFrame)
    assert {"Domain", "Ready", "Registered", "Coverage"}.issubset(coverage.columns)
    assert callable(streamlit_app.render_platform_insights)
    assert callable(streamlit_app.render_home_actions)


def test_render_selected_module_is_isolated() -> None:
    assert callable(streamlit_app.render_selected_module)
    assert callable(streamlit_app.load_renderer)
