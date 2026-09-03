"""IMAGINE Streamlit module package."""

from __future__ import annotations

import importlib

from modules.ui_sanitizer import install_emoji_free_ui

install_emoji_free_ui()

# Preload and normalize the enterprise registry before streamlit_app imports it.
# Specialist renderers remain untouched. Routes without a specialist renderer
# receive a domain-aware functional workspace so no registered route is dead.
_enterprise_registry = importlib.import_module("modules.enterprise_registry")
from modules.enterprise_registry import ModuleSpec


# Complete the Eurocode navigation set without forcing the large registry file
# to become coupled to renderer imports.
_existing_routes = {spec.route for spec in _enterprise_registry.MODULE_SPECS}
_extra_specs = tuple(
    spec
    for spec in (
        ModuleSpec("EN 1994", "EN 1994", "STRUCTURAL", "modules.functional_workspace", "render_module", True),
        ModuleSpec("EN 1996", "EN 1996", "STRUCTURAL", "modules.functional_workspace", "render_module", True),
    )
    if spec.route not in _existing_routes
)

_NORMALIZED_SPECS = []
for _spec in (*_enterprise_registry.MODULE_SPECS, *_extra_specs):
    if _spec.implemented and _spec.module_path:
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
