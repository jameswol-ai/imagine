"""Contract tests for searchable and executable enterprise modules."""

from __future__ import annotations

import importlib

from modules.enterprise_registry import MODULE_SPECS


def test_every_registered_route_has_a_renderer_contract() -> None:
    for spec in MODULE_SPECS:
        assert spec.route
        assert spec.label
        assert spec.section
        assert spec.module_path
        module = importlib.import_module(spec.module_path)
        renderer = getattr(module, spec.renderer_name, None)
        assert callable(renderer), f"Missing renderer for {spec.route}"


def test_shared_fallback_is_available() -> None:
    from modules.enterprise_runtime import render_module

    assert callable(render_module)
