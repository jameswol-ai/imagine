from modules.enterprise_registry import MODULES_BY_ROUTE, MODULE_SPECS, validate_registry


def test_enterprise_registry_is_valid():
    validate_registry()
    assert MODULE_SPECS
    assert len(MODULES_BY_ROUTE) == len(MODULE_SPECS)


def test_core_domains_are_registered():
    sections = {spec.section for spec in MODULE_SPECS}
    assert {
        "PLATFORM",
        "PROJECTS",
        "ARCHITECTURE",
        "STRUCTURAL",
        "BIM",
        "MEP",
        "COSTING",
        "CONSTRUCTION",
        "DOCUMENTS",
        "ANALYTICS",
        "DIGITAL TWIN",
    }.issubset(sections)


def test_database_first_project_routes_are_real():
    expected = {
        "Projects": "projects.projects.ui",
        "Approvals": "projects.approvals.ui",
        "Revisions": "projects.revisions.ui",
    }

    for route, module_path in expected.items():
        spec = MODULES_BY_ROUTE[route]
        assert spec.implemented is True
        assert spec.module_path == module_path
