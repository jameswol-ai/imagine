from modules.structural.eurocode_data import all_parts, family_codes, parts_for
from modules.structural.eurocode_knowledge import CHECKS, FAMILIES, PARAMETERS, check_by_id, checks_for, search_catalog, validate_catalog


def test_eurocode_families_are_complete():
    assert family_codes() == tuple(f"EN 199{i}" for i in range(10))
    assert set(FAMILIES) == set(family_codes())


def test_catalog_part_identifiers_are_unique():
    codes = [part.code for part in all_parts()]
    assert len(codes) == len(set(codes))
    assert all(code.startswith("EN 199") for code in codes)


def test_every_family_has_parts_and_checks():
    for code in family_codes():
        assert parts_for(code)
        assert checks_for(code)


def test_check_schemas_are_resolvable():
    assert CHECKS
    for check in CHECKS:
        assert check_by_id(check.id) is check
        assert check.inputs
        assert check.outputs
        assert check.family in FAMILIES


def test_parameter_keys_are_unique():
    keys = [parameter.key for parameter in PARAMETERS]
    assert len(keys) == len(set(keys))


def test_catalog_validation_and_search():
    validate_catalog()
    results = search_catalog("wind")
    assert results
    assert any(check.family == "EN 1991" for check in results)
