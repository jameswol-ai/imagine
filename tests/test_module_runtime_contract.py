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


def test_unimplemented_routes_are_safe_functional_workspaces() -> None:
    for spec in MODULE_SPECS:
        if spec.route in {"Finite Element Analysis", "Elements", "COBie", "BIM Digital Twin", "Energy"}:
            assert spec.module_path == "modules.functional_workspace"
            assert spec.renderer_name == "render_module"
            assert spec.implemented is True


def test_beam_design_uses_the_specialist_renderer() -> None:
    beam = next(spec for spec in MODULE_SPECS if spec.route == "Beam Design")
    assert beam.module_path == "modules.structural.beam_design"
    assert beam.renderer_name == "render"
    assert beam.implemented is True


def test_shared_fallback_is_available() -> None:
    from modules.enterprise_runtime import render_module

    assert callable(render_module)
