"""IMAGINE Streamlit module package.

The package installs the global emoji-free UI policy and normalizes the
enterprise registry so every registered route has a callable renderer.

Specialist modules are preserved where they are already implemented. Legacy
/demo renderers are routed through the shared domain-aware functional
workspace until their specialist engines are production-ready.
"""

from __future__ import annotations

import importlib

from modules.ui_sanitizer import install_emoji_free_ui

install_emoji_free_ui()

_enterprise_registry = importlib.import_module("modules.enterprise_registry")
from modules.enterprise_registry import ModuleSpec


# These modules previously exposed demonstration engines or hard-coded demo
# records. Route them through the shared functional workspace so the UI is
# data-entry driven, validated, persistent, and exportable instead of showing
# static demonstration output.
_FUNCTIONAL_ROUTES = {
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
    "Integrated MEP Analysis",
    "Ventilation",
    "Chilled Water",
    "Energy Simulation",
    "Electrical Load Analysis",
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


# Complete the Eurocode navigation set without coupling the registry to
# renderer imports.
_existing_routes = {spec.route for spec in _enterprise_registry.MODULE_SPECS}
_extra_specs = tuple(
    spec
    for spec in (
        ModuleSpec("EN 1994", "EN 1994", "STRUCTURAL", "modules.functional_workspace", "render_module", True),
        ModuleSpec("EN 1996", "EN 1996", "STRUCTURAL", "modules.functional_workspace", "render_module", True),
    )
    if spec.route not in _existing_routes
)

_NORMALIZED_SPECS: list[ModuleSpec] = []
for _spec in (*_enterprise_registry.MODULE_SPECS, *_extra_specs):
    if _spec.route in _FUNCTIONAL_ROUTES:
        _NORMALIZED_SPECS.append(
            ModuleSpec(
                route=_spec.route,
                label=_spec.label,
                section=_spec.section,
                module_path="modules.functional_workspace",
                renderer_name="render_module",
                implemented=True,
            )
        )
    elif _spec.implemented and _spec.module_path:
        _NORMALIZED_SPECS.append(_spec)
    else:
        _NORMALIZED_SPECS.append(
            ModuleSpec(
                route=_spec.route,
                label=_spec.label,
                section=_spec.section,
                module_path="modules.functional_workspace",
                renderer_name="render_module",
                implemented=True,
            )
        )

_enterprise_registry.MODULE_SPECS = tuple(_NORMALIZED_SPECS)
_enterprise_registry.MODULES_BY_ROUTE = {
    spec.route: spec for spec in _enterprise_registry.MODULE_SPECS
}

__all__ = ["install_emoji_free_ui"]
