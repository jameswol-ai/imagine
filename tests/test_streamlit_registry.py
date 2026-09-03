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


def test_structural_analysis_is_registered() -> None:
    analysis = next(spec for spec in MODULE_SPECS if spec.route == "Structural Analysis")
    assert analysis.implemented is True
    assert analysis.module_path == "modules.structural.structural_analysis"
    assert analysis.renderer_name == "render"


def test_project_workspaces_with_renderers_are_marked_ready() -> None:
    for route in ("Projects", "Approvals", "Revisions", "Workflows", "Governance"):
        spec = next(item for item in MODULE_SPECS if item.route == route)
        assert spec.implemented is True
        assert spec.module_path
        assert spec.renderer_name
