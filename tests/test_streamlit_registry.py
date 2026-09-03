"""Regression tests for the application shell and registered renderers."""
from modules.enterprise_registry import MODULE_SPECS, validate_registry


def test_registry_is_valid_and_routes_are_unique() -> None:
    validate_registry()
    routes = [spec.route for spec in MODULE_SPECS]
    assert len(routes) == len(set(routes))


def test_roof_design_is_registered() -> None:
    roof = next(spec for spec in MODULE_SPECS if spec.route == "Roof Design")
    assert roof.implemented is True
    assert roof.module_path == "modules.structural.roof_design"
    assert roof.renderer_name == "render"
