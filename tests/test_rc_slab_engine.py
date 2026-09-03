import math

import pytest

from modules.structural.slab_engine import RCSLabDesignEngine, SlabDesignInput


def make_input(**overrides):
    values = dict(
        lx_m=4.0,
        ly_m=8.0,
        thickness_mm=175.0,
        cover_mm=25.0,
        slab_type="One-Way Slab",
        support_condition="Simply Supported",
        permanent_load_kn_m2=2.0,
        imposed_load_kn_m2=3.0,
        fck_mpa=30.0,
        fyk_mpa=500.0,
        bar_dia_x_mm=10.0,
        spacing_x_mm=200.0,
        bar_dia_y_mm=10.0,
        spacing_y_mm=200.0,
    )
    values.update(overrides)
    return SlabDesignInput(**values)


def test_one_way_slab_engine_is_deterministic():
    result = RCSLabDesignEngine.run(make_input())
    assert math.isclose(result.self_weight_kn_m2, 4.375)
    assert result.uls_load_kn_m2 > result.sls_load_kn_m2
    assert result.moment_x_kn_m > 0
    assert result.as_required_x_mm2_m > 0
    assert result.as_provided_x_mm2_m > 0
    assert result.vrdc_mpa > 0


def test_two_way_slab_generates_both_direction_moments():
    result = RCSLabDesignEngine.run(make_input(ly_m=5.0, slab_type="Two-Way Rectangular Slab"))
    assert result.aspect_ratio == 1.25
    assert result.moment_x_kn_m > 0
    assert result.moment_y_kn_m > 0
    assert result.as_required_x_mm2_m > 0
    assert result.as_required_y_mm2_m > 0


def test_slab_invalid_geometry_is_rejected():
    with pytest.raises(ValueError, match="thickness"):
        make_input(thickness_mm=35.0)


def test_slab_engine_reports_boolean_verifications():
    result = RCSLabDesignEngine.run(make_input())
    assert isinstance(result.flexure_x_ok, bool)
    assert isinstance(result.flexure_y_ok, bool)
    assert isinstance(result.shear_ok, bool)
    assert isinstance(result.deflection_ok, bool)
    assert result.overall_ok == all((result.flexure_x_ok, result.flexure_y_ok, result.shear_ok, result.deflection_ok))
