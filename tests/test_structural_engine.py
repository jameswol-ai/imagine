"""Unit tests for deterministic structural screening engines."""

import math

from modules.structural.beam_design import BeamDesignEngine
from modules.structural.retaining_walls import RetainingWallEngine


def test_beam_engine_balances_standard_simply_supported_udl_case():
    result = BeamDesignEngine().run({
        "span_m": 6.0,
        "width_mm": 300.0,
        "depth_mm": 500.0,
        "cover_mm": 30.0,
        "stirrup_dia_mm": 8.0,
        "bar_dia_mm": 20.0,
        "fck_mpa": 30.0,
        "fyk_mpa": 500.0,
        "permanent_load_kn_m": 4.0,
        "variable_load_kn_m": 8.0,
    })

    assert math.isclose(result.self_weight_kn_m, 3.75, rel_tol=1e-9)
    assert math.isclose(result.uls_load_kn_m, 1.35 * 7.75 + 1.5 * 8.0, rel_tol=1e-9)
    assert math.isclose(result.uls_moment_kn_m, result.uls_load_kn_m * 36.0 / 8.0, rel_tol=1e-9)
    assert math.isclose(result.uls_shear_kn, result.uls_load_kn_m * 6.0 / 2.0, rel_tol=1e-9)
    assert result.as_required_mm2 > 0
    assert result.as_provided_mm2 >= result.as_required_mm2
    assert result.shear_capacity_mpa > 0


def test_beam_engine_rejects_invalid_geometry():
    try:
        BeamDesignEngine().run({"span_m": 0.0})
    except ValueError as exc:
        assert "span_m" in str(exc)
    else:
        raise AssertionError("Expected ValueError for zero span")


def test_retaining_wall_engine_computes_rankine_pressure_and_stability():
    result = RetainingWallEngine().run({
        "wall_id": "RW-TEST",
        "height_m": 4.0,
        "base_width_m": 3.0,
        "stem_thickness_m": 0.35,
        "base_slab_thickness_m": 0.50,
        "soil_unit_weight_kn_m3": 18.0,
        "friction_angle_deg": 30.0,
        "surcharge_kn_m2": 0.0,
        "base_friction_coefficient": 0.50,
        "toe_length_m": 0.75,
        "heel_length_m": 1.90,
    })

    expected_ka = (1.0 - math.sin(math.radians(30.0))) / (1.0 + math.sin(math.radians(30.0)))
    assert math.isclose(result.active_coefficient, expected_ka, rel_tol=1e-9)
    assert math.isclose(result.active_soil_force_kn_m, 0.5 * expected_ka * 18.0 * 16.0, rel_tol=1e-9)
    assert result.overturning_moment_kn_m > 0
    assert result.resisting_moment_kn_m > 0
    assert result.sliding_factor_of_safety > 0
    assert result.overturning_factor_of_safety > 0


def test_retaining_wall_requires_consistent_base_geometry():
    try:
        RetainingWallEngine().run({
            "height_m": 4.0,
            "base_width_m": 3.0,
            "stem_thickness_m": 0.35,
            "toe_length_m": 0.75,
            "heel_length_m": 1.0,
        })
    except ValueError as exc:
        assert "must equal base_width_m" in str(exc)
    else:
        raise AssertionError("Expected ValueError for inconsistent base geometry")
