from modules.structural.ec0 import LoadSet, build_sls_combinations, build_uls_combinations, governing_combination
from modules.structural.ec1 import AreaActions, line_load_from_area


def test_ec0_governing_uls_is_deterministic():
    loads = LoadSet(permanent=5.0, leading_variable=3.0, accompanying_variable=2.0, wind=0.8, snow=0.5)
    cases = build_uls_combinations(loads)
    name, value = governing_combination(cases)
    assert name.startswith("ULS 1")
    assert value == 1.35 * 5.0 + 1.5 * 3.0 + 1.5 * 0.7 * 2.0


def test_ec0_sls_returns_expected_cases():
    loads = LoadSet(permanent=5.0, leading_variable=3.0)
    cases = build_sls_combinations(loads)
    assert len(cases) == 3
    assert cases[0][1] == 8.0


def test_ec1_area_actions_convert_to_line_loads():
    actions = AreaActions(permanent_kn_m2=4.0, imposed_kn_m2=2.0)
    line = actions.to_line_load(3.0)
    assert line["G"] == 12.0
    assert line["Q"] == 6.0


def test_ec1_rejects_negative_actions():
    try:
        line_load_from_area(-1.0, 2.0)
    except ValueError as exc:
        assert "cannot be negative" in str(exc)
    else:
        raise AssertionError("negative area action should fail")
