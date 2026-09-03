from modules.structural.steel_connections import (
    SteelConnectionInput,
    evaluate_connection,
    plate_bearing_capacity_kn,
    weld_shear_capacity_kn,
)


def make_input(**overrides):
    values = dict(
        shear_kn=120.0,
        axial_kn=40.0,
        bolt_diameter_mm=20.0,
        bolt_count=4,
        bolt_fu_mpa=800.0,
        plate_thickness_mm=12.0,
        plate_fu_mpa=430.0,
        edge_distance_mm=40.0,
        pitch_mm=70.0,
        weld_length_mm=250.0,
        weld_throat_mm=6.0,
        weld_fu_mpa=430.0,
    )
    values.update(overrides)
    return SteelConnectionInput(**values)


def test_bolt_and_plate_resistances_are_positive():
    inputs = make_input()
    result = evaluate_connection(inputs)
    assert result.bolt_shear_capacity_kn > 0
    assert result.plate_bearing_capacity_kn > 0
    assert result.weld_shear_capacity_kn > 0
    assert result.governing_capacity_kn > 0


def test_connection_utilisation_increases_with_demand():
    base = evaluate_connection(make_input(shear_kn=60.0))
    high = evaluate_connection(make_input(shear_kn=180.0))
    assert high.overall_utilisation > base.overall_utilisation


def test_thicker_plate_increases_or_preserves_bearing_capacity():
    thin = plate_bearing_capacity_kn(make_input(plate_thickness_mm=8.0))
    thick = plate_bearing_capacity_kn(make_input(plate_thickness_mm=16.0))
    assert thick > thin


def test_larger_weld_increases_capacity():
    short = weld_shear_capacity_kn(make_input(weld_length_mm=150.0))
    long = weld_shear_capacity_kn(make_input(weld_length_mm=300.0))
    assert long > short


def test_invalid_connection_inputs_are_rejected():
    try:
        make_input(bolt_count=0)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for zero bolts")
