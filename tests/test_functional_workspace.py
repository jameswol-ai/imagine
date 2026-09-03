from modules.functional_workspace import PROFILES, _calculate


def test_required_domain_profiles_exist():
    expected = {
        "EN 1990", "EN 1991", "EN 1992", "EN 1993", "EN 1994", "EN 1995", "EN 1996", "EN 1997", "EN 1998",
        "Finite Element Analysis", "Transformers", "Generators", "Cable Sizing", "Solar PV", "Stormwater",
        "Sewer Networks", "Firefighting", "Cashflow", "Planning", "Scheduling", "Variations",
    }
    assert expected.issubset(PROFILES)


def test_en1990_calculation():
    result, unit = _calculate("EN 1990", {"gk": 100.0, "qk": 50.0})
    assert result == 210.0
    assert unit == "kN"


def test_cable_sizing_calculation_is_positive():
    result, unit = _calculate("Cable Sizing", {"power": 100.0, "voltage": 400.0, "pf": 0.9, "density": 3.0})
    assert result > 0
    assert unit == "mm2"


def test_solar_pv_calculation():
    result, unit = _calculate("Solar PV", {"daily_energy": 1000.0, "sun_hours": 5.0, "system_eff": 0.8})
    assert result == 250.0
    assert unit == "kWp"
