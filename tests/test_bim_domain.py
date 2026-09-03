"""Regression tests for BIM navigation and shared data contracts."""
from modules.enterprise_registry import MODULES_BY_ROUTE, validate_registry
from modules.bim.core import BIMElement, asdict_element


def test_bim_routes_are_registered():
    validate_registry()
    expected = [
        "BIM Dashboard", "Buildings", "Storeys", "Spaces", "Elements",
        "Assemblies & Types", "IFC", "COBie", "BIM Coordination",
        "BIM Quantities", "BIM → Costing / BOQ", "BIM → Digital Twin",
    ]
    assert all(route in MODULES_BY_ROUTE for route in expected)
    assert all(MODULES_BY_ROUTE[route].section == "BIM" for route in expected)
    assert all(MODULES_BY_ROUTE[route].implemented for route in expected)


def test_bim_element_contract_is_serializable():
    element = BIMElement(
        id="ELM-001", building_id="BLDG-001", storey_id="STRY-001",
        category="Wall", name="External Wall", type_name="Wall 200mm", quantity=10,
        unit="m²", guid="IMAGINE-ELM-001",
    )
    payload = asdict_element(element)
    assert payload["building_id"] == "BLDG-001"
    assert payload["category"] == "Wall"
    assert payload["quantity"] == 10


def test_bim_module_imports_expose_render():
    from modules.bim import dashboard, elements, assemblies, cobie, coordination, quantities, costing_handoff, digital_twin
    for module in (dashboard, elements, assemblies, cobie, coordination, quantities, costing_handoff, digital_twin):
        assert callable(module.render)
