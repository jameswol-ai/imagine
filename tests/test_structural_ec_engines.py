import math

from modules.structural.beam_design import BeamDesignEngine
from modules.structural.ec0 import LoadSet, build_sls_combinations, build_uls_combinations, governing_combination
from modules.structural.ec1 import AreaActions, line_load_from_area
from modules.structural.ec2 import (
    ConcreteDesignProperties,
    SteelDesignProperties,
    effective_depth_mm,
    maximum_longitudinal_reinforcement_mm2,
    minimum_tension_reinforcement_mm2,
    provided_bar_area_mm2,
    required_flexural_reinforcement_mm2,
    vrdc_mpa,
)


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


def test_ec2_material_design_strengths():
    concrete = ConcreteDesignProperties(30.0)
    steel = SteelDesignProperties(500.0)
    assert math.isclose(concrete.fcd_mpa, 0.85 * 30.0 / 1.5)
    assert math.isclose(steel.fyd_mpa, 500.0 / 1.15)
    assert concrete.fctm_mpa > 0


def test_ec2_effective_depth_and_reinforcement_are_deterministic():
    d = effective_depth_mm(500.0, 30.0, 8.0, 20.0)
    assert d == 452.0
    as_req = required_flexural_reinforcement_mm2(100.0, 300.0, d, 500.0 / 1.15)
    as_min = minimum_tension_reinforcement_mm2(300.0, d, 30.0, 500.0)
    as_max = maximum_longitudinal_reinforcement_mm2(300.0, 500.0)
    assert as_req > 0
    assert as_min > 0
    assert as_max == 6000.0
    assert provided_bar_area_mm2(20.0) == math.pi * 20.0**2 / 4.0


def test_ec2_vrdc_is_positive_for_reinforced_section():
    value = vrdc_mpa(30.0, 300.0, 452.0, 1000.0)
    assert value > 0


def test_beam_engine_uses_shared_ec2_layer():
    result = BeamDesignEngine().run()
    assert result.effective_depth_mm == 452.0
    assert result.fyd_mpa == 500.0 / 1.15
    assert result.as_required_mm2 > 0
    assert result.shear_capacity_mpa > 0
