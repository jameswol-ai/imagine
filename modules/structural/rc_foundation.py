"""Pure preliminary reinforced-concrete pad footing engine.

The engine provides transparent bearing, eccentricity, pressure, flexural and
one-way shear screening. It is not a complete EN 1992/EN 1997 foundation
design and must be checked against the project geotechnical report, National
Annex, settlement criteria, detailing and professional design requirements.
"""

from __future__ import annotations

from dataclasses import dataclass

from modules.structural.ec0 import LoadSet, build_uls_combinations, governing_combination
from modules.structural.ec2 import minimum_tension_reinforcement_mm2, provided_bar_area_mm2, required_flexural_reinforcement_mm2, vrdc_mpa
from modules.structural.ec7 import Soil, bearing_utilisation, ultimate_bearing_capacity_kpa


@dataclass(frozen=True)
class PadFootingInput:
    width_m: float
    length_m: float
    depth_m: float
    column_width_m: float
    column_length_m: float
    cover_mm: float
    permanent_load_kn: float
    imposed_load_kn: float
    moment_x_kn_m: float = 0.0
    moment_y_kn_m: float = 0.0
    soil: Soil = Soil(18.0, 10.0, 30.0, 200.0)
    fck_mpa: float = 30.0
    fyk_mpa: float = 500.0
    bar_dia_mm: float = 16.0
    spacing_mm: float = 200.0
    gamma_c: float = 1.5
    gamma_s: float = 1.15
    psi0: float = 0.7

    def __post_init__(self) -> None:
        values = (self.width_m, self.length_m, self.depth_m, self.column_width_m, self.column_length_m, self.cover_mm, self.fck_mpa, self.fyk_mpa, self.bar_dia_mm, self.spacing_mm, self.gamma_c, self.gamma_s)
        if any(v <= 0 for v in values):
            raise ValueError("geometry, materials and reinforcement values must be positive")
        if self.permanent_load_kn < 0 or self.imposed_load_kn < 0:
            raise ValueError("loads cannot be negative")
        if self.width_m <= self.column_width_m or self.length_m <= self.column_length_m:
            raise ValueError("footing plan dimensions must exceed column dimensions")


@dataclass(frozen=True)
class PadFootingResult:
    uls_axial_kn: float
    eccentricity_x_m: float
    eccentricity_y_m: float
    q_max_kpa: float
    q_min_kpa: float
    allowable_bearing_kpa: float
    bearing_utilisation: float
    design_moment_x_kn_m: float
    design_moment_y_kn_m: float
    effective_depth_mm: float
    as_required_x_mm2_m: float
    as_required_y_mm2_m: float
    as_provided_mm2_m: float
    one_way_shear_stress_mpa: float
    vrdc_mpa: float
    bearing_ok: bool
    flexure_ok: bool
    shear_ok: bool

    @property
    def overall_ok(self) -> bool:
        return self.bearing_ok and self.flexure_ok and self.shear_ok


class RCPadFootingDesignEngine:
    """Deterministic preliminary isolated footing screening engine."""

    @staticmethod
    def run(inputs: PadFootingInput) -> PadFootingResult:
        g = inputs.permanent_load_kn
        q = inputs.imposed_load_kn
        _, n_ed = governing_combination(build_uls_combinations(LoadSet(permanent=g, leading_variable=q), psi0=inputs.psi0))
        ex = abs(inputs.moment_x_kn_m) / max(n_ed, 1e-9)
        ey = abs(inputs.moment_y_kn_m) / max(n_ed, 1e-9)
        q0 = n_ed / (inputs.width_m * inputs.length_m)
        qx = 6.0 * abs(inputs.moment_x_kn_m) / (inputs.width_m * inputs.length_m**2)
        qy = 6.0 * abs(inputs.moment_y_kn_m) / (inputs.length_m * inputs.width_m**2)
        q_max = q0 + qx + qy
        q_min = max(0.0, q0 - qx - qy)
        allowable = inputs.soil.allowable_bearing_kpa

        projection_x = (inputs.width_m - inputs.column_width_m) / 2.0
        projection_y = (inputs.length_m - inputs.column_length_m) / 2.0
        mx = q_max * inputs.length_m * projection_x**2 / 2.0 / max(inputs.length_m, 1e-9)
        my = q_max * inputs.width_m * projection_y**2 / 2.0 / max(inputs.width_m, 1e-9)
        d = inputs.depth_m * 1000.0 - inputs.cover_mm - inputs.bar_dia_mm / 2.0
        fyd = inputs.fyk_mpa / inputs.gamma_s
        as_x = max(required_flexural_reinforcement_mm2(mx, inputs.width_m * 1000.0, d, fyd), minimum_tension_reinforcement_mm2(inputs.width_m * 1000.0, d, inputs.fck_mpa, inputs.fyk_mpa))
        as_y = max(required_flexural_reinforcement_mm2(my, inputs.length_m * 1000.0, d, fyd), minimum_tension_reinforcement_mm2(inputs.length_m * 1000.0, d, inputs.fck_mpa, inputs.fyk_mpa))
        provided = provided_bar_area_mm2(inputs.bar_dia_mm, inputs.spacing_mm, inputs.width_m * 1000.0)
        v_ed = q_max * max(projection_x - d / 1000.0, 0.0) / 1000.0
        shear_stress = v_ed * 1000.0 / (inputs.width_m * 1000.0 * d)
        vrdc = vrdc_mpa(inputs.fck_mpa, inputs.width_m * 1000.0, d, provided, inputs.gamma_c)
        util = bearing_utilisation(q_max, allowable)
        return PadFootingResult(n_ed, ex, ey, q_max, q_min, allowable, util, mx, my, d, as_x, as_y, provided, shear_stress, vrdc, q_max <= allowable and q_min >= 0.0 and ex <= inputs.width_m / 6 and ey <= inputs.length_m / 6, provided >= as_x and provided >= as_y, shear_stress <= vrdc)


__all__ = ["PadFootingInput", "PadFootingResult", "RCPadFootingDesignEngine"]
