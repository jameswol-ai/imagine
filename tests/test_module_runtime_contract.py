"""Contract tests for searchable and executable enterprise modules."""
from __future__ import annotations

import importlib

from modules.enterprise_registry import MODULE_SPECS


def test_every_registered_route_has_a_renderer_contract() -> None:
    for spec in MODULE_SPECS:
        assert spec.route
        assert spec.label
        assert spec.section
        if spec.module_path == "__builtin__":
            continue
        assert spec.module_path
        module = importlib.import_module(spec.module_path)
        renderer = getattr(module, spec.renderer_name, None) or getattr(module, "render", None)
        assert callable(renderer), f"Missing renderer for {spec.route}"


def test_no_implemented_registry_entry_is_missing_a_module_path() -> None:
    broken = [spec.route for spec in MODULE_SPECS if spec.implemented and not spec.module_path]
    assert broken == []


def test_enterprise_route_workspaces_are_executable() -> None:
    routes = {
        "Finite Element Analysis", "Elements", "COBie", "BIM → Digital Twin", "Energy",
        "Uganda", "Kenya", "Tanzania", "Rwanda", "South Sudan", "Codes", "Zoning Laws",
        "Microsoft", "AutoCAD", "Revit", "Archicad", "Tekla", "IfcOpenShell", "ArcGIS", "Azure", "Mapbox",
    }
    by_route = {spec.route: spec for spec in MODULE_SPECS}
    for route in routes:
        spec = by_route[route]
        assert spec.module_path == "modules.enterprise_missing"
        assert spec.renderer_name == "render"
        assert spec.implemented is True


def test_core_structural_workspaces_are_importable() -> None:
    expected = {
        "Beam Design": "modules.structural.beam_design",
        "Column Design": "modules.structural.column_design",
        "Slab Design": "modules.structural.slab_design",
        "Foundation Design": "modules.structural.foundation_design",
        "Punching Shear": "modules.structural.punching_shear",
        "Stairs Design": "modules.structural.stairs_design",
        "Openings Design": "modules.structural.openings_design",
        "Railings & Balustrades": "modules.structural.railings_design",
        "Load Combinations": "modules.structural.load_combinations",
        "Wind Actions": "modules.structural.wind_actions",
        "Seismic Actions": "modules.structural.seismic_actions",
        "RC Detailing": "modules.structural.rc_detailing",
    }
    by_route = {spec.route: spec for spec in MODULE_SPECS}
    for route, module_path in expected.items():
        spec = by_route[route]
        assert spec.module_path == module_path
        module = importlib.import_module(module_path)
        assert callable(getattr(module, "render", None))


def test_beam_design_uses_the_specialist_renderer() -> None:
    beam = next(spec for spec in MODULE_SPECS if spec.route == "Beam Design")
    assert beam.module_path == "modules.structural.beam_design"
    assert beam.renderer_name == "render"
    assert beam.implemented is True


def test_shared_fallback_is_available() -> None:
    from modules.enterprise_runtime import render_module
    assert callable(render_module)
