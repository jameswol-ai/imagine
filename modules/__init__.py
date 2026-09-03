"""IMAGINE Streamlit module package.

Specialist workspaces remain discoverable through the central registry. Routes
without a specialist implementation use a route-aware enterprise workspace,
so every registered page remains usable without pretending to be a deep domain
engine or an external integration.
"""
from __future__ import annotations

import importlib

from modules.ui_sanitizer import install_emoji_free_ui

install_emoji_free_ui()

_registry = importlib.import_module("modules.enterprise_registry")
from modules.enterprise_registry import ModuleSpec


def _normalise_specs() -> tuple[ModuleSpec, ...]:
    """Keep specialist renderers intact and provide a functional route fallback."""
    specs: list[ModuleSpec] = []
    for spec in _registry.MODULE_SPECS:
        if spec.implemented and spec.module_path:
            specs.append(spec)
        else:
            specs.append(
                ModuleSpec(
                    route=spec.route,
                    label=spec.label,
                    section=spec.section,
                    module_path="modules.enterprise_missing",
                    renderer_name="render",
                    implemented=True,
                )
            )
    return tuple(specs)


_registry.MODULE_SPECS = _normalise_specs()
_registry.MODULES_BY_ROUTE = {spec.route: spec for spec in _registry.MODULE_SPECS}

__all__ = ["install_emoji_free_ui", "ModuleSpec"]
