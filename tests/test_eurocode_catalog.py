from modules.structural.eurocode_data import EUROCODE_FAMILY, all_parts, family_codes, parts_for
from modules.structural.eurocode_suite import IMPLEMENTED_WORKSPACES, _unique_parts


def test_eurocode_families_cover_en1990_to_en1999():
    assert family_codes() == tuple(f"EN 199{i}" for i in range(10))


def test_catalog_part_codes_are_unique():
    parts = list(all_parts())
    assert len(parts) == len({part.code for part in parts})


def test_family_part_lists_have_no_duplicate_identifiers_after_normalisation():
    for family in family_codes():
        raw = EUROCODE_FAMILY[family]["parts"]
        assert len(_unique_parts(parts_for(family))) == len({part.code for part in parts_for(family)})
        assert raw


def test_every_part_has_required_structured_data():
    for part in all_parts():
        assert part.code.startswith("EN 199")
        assert part.title.strip()
        assert part.scope.strip()
        assert part.topics
        assert part.inputs
        assert part.outputs
        assert part.linked_tools


def test_family_lookup_returns_parts_belonging_to_family():
    for family in family_codes():
        for part in parts_for(family):
            assert part.code == family or part.code.startswith(family + "-")


def test_implemented_workspace_labels_are_nonempty():
    assert IMPLEMENTED_WORKSPACES
    assert all(label.strip() for label in IMPLEMENTED_WORKSPACES)
