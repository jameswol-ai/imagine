"""Contract tests for searchable and executable enterprise modules."""

from __future__ import annotations

import importlib

from modules.enterprise_registry import MODULE_SPECS


FUNCTIONAL_ROUTES = {
    "IMAGINE Architect",
    "IMAGINE Engineer",
    "IMAGINE MEP",
    "IMAGINE QS",
    "IMAGINE PM",
    "Vector Store",
    "RAG",
    "Prompt Library",
    "Dashboards",
    "KPIs",
    "Portfolio",
    "Forecasting",
    "Reporting",
    "Eurocode Suite",
    "Beam Design",
    "Retaining Walls",
    "HVAC",
    "BOQ",
    "Quantity Takeoff",
    "Procurement",
    "Forex",
    "Inflation / Escalation",
    "Risk Analysis",
    "Planning",
    "Scheduling",
    "RFIs",
    "Submittals",
    "Variations",
    "Snagging",
    "Progress Tracking",
    "Site Diaries",
    "Drawing Management",
    "Document Register",
    "Specifications",
    "Contracts",
    "Version Control",
    "Transmittals",
    "Assets",
    "Sensors",
    "Telemetry",
    "Maintenance",
    "Predictive AI",
}


def test_every_registered_route_has_a_renderer_contract() -> None:
    for spec in MODULE_SPECS:
        assert spec.route
        assert spec.label
        assert spec.section
        assert spec.module_path
        module = importlib.import_module(spec.module_path)
        renderer = getattr(module, spec.renderer_name, None)
        assert callable(renderer), f"Missing renderer for {spec.route}"


def test_legacy_demo_routes_use_the_shared_functional_workspace() -> None:
    for spec in MODULE_SPECS:
        if spec.route in FUNCTIONAL_ROUTES:
            assert spec.module_path == "modules.functional_workspace"
            assert spec.renderer_name == "render_module"
            assert spec.implemented is True


def test_shared_fallback_is_available() -> None:
    from modules.enterprise_runtime import render_module

    assert callable(render_module)
