"""Smoke and regression tests for the coordinated structural calculation layer."""

from modules.structural.ec7 import Soil, rankine_active_coefficient
from modules.structural.ec8 import SeismicInput, base_shear_kn, distribute_storey_forces_kn
from modules.structural.ec3 import BoltGroup, SteelSection, bolt_shear_resistance_kn, preliminary_slenderness
from modules.structural.fea_engine import SimplySupportedBeamInput, analyse_simply_supported_beam
from modules.structural.punching_engine import PunchingShearInput, verify_punching_shear
from modules.structural.rc_foundation import PadFootingInput, RCPadFootingDesignEngine
from modules.structural.rc_slab import RCSLabDesignEngine, SlabDesignInput


def test_slab_returns_scalar_combinations_and_result() -> None:
    result = RCSLabDesignEngine.run(SlabDesignInput(5.0, 6.0, 200.0, 25.0, "One-Way Slab", "Simply Supported", 2.0, 3.0))
    assert result.uls_load_kn_m2 > result.sls_load_kn_m2
    assert result.governing_uls_name.startswith("ULS")
    assert result.governing_sls_name.startswith("SLS")


def test_ec7_rankine_coefficient() -> None:
    assert 0.3 < rankine_active_coefficient(30.0) < 0.34


def test_ec3_section_and_bolts() -> None:
    section = SteelSection(5000.0, 355.0, 8e6, 2e6, 3.0)
    result = preliminary_slenderness(section)
    assert result.gross_yield_resistance_kn > 1000.0
    assert result.governing_slenderness > 0
    assert bolt_shear_resistance_kn(BoltGroup(20.0, 4, 800.0)) > 0


def test_ec8_force_distribution_conserves_base_shear() -> None:
    base = base_shear_kn(SeismicInput(0.12, 200.0))
    forces = distribute_storey_forces_kn(base, [50.0, 70.0, 80.0], [3.0, 6.0, 9.0])
    assert abs(sum(forces) - base) < 1e-9


def test_punching_engine() -> None:
    result = verify_punching_shear(PunchingShearInput(300.0, 300.0, 160.0, 80.0, 2500.0))
    assert result.control_perimeter_mm > 0
    assert result.resistance_mpa > 0


def test_pad_footing_engine() -> None:
    inputs = PadFootingInput(2.0, 2.0, 0.5, 0.4, 0.4, 50.0, 500.0, 100.0)
    result = RCPadFootingDesignEngine.run(inputs)
    assert result.uls_axial_kn > 0
    assert result.q_max_kpa >= result.q_min_kpa


def test_analysis_engine() -> None:
    result = analyse_simply_supported_beam(SimplySupportedBeamInput(6.0, 10.0, 30.0, 0.002))
    assert result.reaction_left_kn == result.reaction_right_kn == 30.0
    assert result.maximum_moment_kn_m == 45.0
    assert result.maximum_deflection_mm > 0
