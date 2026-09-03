"""Pure preliminary reinforced-concrete slab design engine.

Screening implementation inspired by EN 1992-1-1. The simplified two-way
coefficients, span/depth screening and shear model are not a substitute for a
project-specific EC2 design, National Annex, detailing checks or professional
verification.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from modules.structural.ec0 import LoadSet, build_sls_combinations, build_uls_combinations, governing_combination
from modules.structural.ec2 import (
    effective_depth_mm,
    minimum_tension_reinforcement_mm2,
    provided_bar_area_mm2,
    required_flexural_reinforcement_mm2,
    vrdc_mpa,
)

SlabType = Literal["One-Way Slab", "Two-Way Rectangular Slab"]
SupportCondition = Literal["Simply Supported", "One End Continuous", "Both Ends Continuous", "Cantilever"]


@dataclass(frozen=True)
class SlabDesignInput:
    lx_m: float
    ly_m: float
    thickness_mm: float
    cover_mm: float
    slab_type: SlabType
    support_condition: SupportCondition
    permanent_load_kn_m2: float
    imposed_load_kn_m2: float
    fck_mpa: float = 30.0
    fyk_mpa: float = 500.0
    gamma_c: float = 1.50
    gamma_s: float = 1.15
    alpha_cc: float = 0.85
    bar_dia_x_mm: float = 10.0
    spacing_x_mm: float = 200.0
    bar_dia_y_mm: float = 10.0
    spacing_y_mm: float = 200.0
    psi0: float = 0.7
    unit_width_mm: float = 1000.0
    slab_density_kn_m3: float = 25.0

    def __post_init__(self) -> None:
        positive = {
            "lx_m": self.lx_m, "ly_m": self.ly_m, "thickness_mm": self.thickness_mm,
            "cover_mm": self.cover_mm, "fck_mpa": self.fck_mpa, "fyk_mpa": self.fyk_mpa,
            "gamma_c": self.gamma_c, "gamma_s": self.gamma_s, "bar_dia_x_mm": self.bar_dia_x_mm,
            "spacing_x_mm": self.spacing_x_mm, "bar_dia_y_mm": self.bar_dia_y_mm,
            "spacing_y_mm": self.spacing_y_mm, "unit_width_mm": self.unit_width_mm,
            "slab_density_kn_m3": self.slab_density_kn_m3,
        }
        if any(v <= 0 for v in positive.values()):
            raise ValueError("geometry, material, reinforcement and density values must be greater than zero")
        if self.permanent_load_kn_m2 < 0 or self.imposed_load_kn_m2 < 0:
            raise ValueError("loads cannot be negative")
        if not 0 <= self.psi0 <= 1:
            raise ValueError("psi0 must be between zero and one")
        if self.thickness_mm <= self.cover_mm + self.bar_dia_x_mm / 2:
            raise ValueError("slab thickness is too small for the specified cover and reinforcement")


@dataclass(frozen=True)
class SlabDesignResult:
    aspect_ratio: float
    effective_depth_x_mm: float
    effective_depth_y_mm: float
    self_weight_kn_m2: float
    permanent_load_kn_m2: float
    imposed_load_kn_m2: float
    uls_load_kn_m2: float
    sls_load_kn_m2: float
    moment_x_kn_m: float
    moment_y_kn_m: float
    as_required_x_mm2_m: float
    as_required_y_mm2_m: float
    as_min_x_mm2_m: float
    as_min_y_mm2_m: float
    as_provided_x_mm2_m: float
    as_provided_y_mm2_m: float
    v_ed_kn_m: float
    vrdc_mpa: float
    shear_stress_mpa: float
    actual_ld: float
    allowable_ld: float
    flexure_x_ok: bool
    flexure_y_ok: bool
    shear_ok: bool
    deflection_ok: bool
    governing_uls_name: str
    governing_sls_name: str

    @property
    def overall_ok(self) -> bool:
        return self.flexure_x_ok and self.flexure_y_ok and self.shear_ok and self.deflection_ok


class RCSLabDesignEngine:
    """Deterministic preliminary slab engine for a one-metre design strip."""

    _K_SYS = {
        "Simply Supported": 1.0,
        "One End Continuous": 1.3,
        "Both Ends Continuous": 1.5,
        "Cantilever": 0.4,
    }

    @classmethod
    def run(cls, inputs: SlabDesignInput) -> SlabDesignResult:
        steel_fyd = inputs.fyk_mpa / inputs.gamma_s
        self_weight = inputs.thickness_mm / 1000.0 * inputs.slab_density_kn_m3
        permanent = inputs.permanent_load_kn_m2 + self_weight
        actions = LoadSet(permanent=permanent, leading_variable=inputs.imposed_load_kn_m2)
        uls_name, uls = governing_combination(build_uls_combinations(actions, psi0=inputs.psi0))
        sls_name, sls = governing_combination(build_sls_combinations(actions, psi0=inputs.psi0))

        # effective_depth_mm expects the reinforcement diameter in mm.
        dx = effective_depth_mm(inputs.thickness_mm, inputs.cover_mm, 0.0, inputs.bar_dia_x_mm)
        dy = max(dx - inputs.bar_dia_x_mm / 2.0 - inputs.bar_dia_y_mm / 2.0, 1.0)
        ratio = inputs.ly_m / inputs.lx_m

        one_way = inputs.slab_type == "One-Way Slab" or ratio > 2.0
        if one_way:
            factor = {
                "Simply Supported": 8.0,
                "One End Continuous": 10.0,
                "Both Ends Continuous": 12.0,
                "Cantilever": 2.0,
            }[inputs.support_condition]
            mx = uls * inputs.lx_m**2 / factor
            my = 0.20 * mx
        else:
            ratio4 = ratio**4
            vx = 1.0 / (1.0 + ratio4)
            vy = ratio4 / (1.0 + ratio4)
            mx = vx * uls * inputs.lx_m**2 / 8.0
            my = vy * uls * inputs.lx_m**2 / 8.0

        as_req_x = required_flexural_reinforcement_mm2(mx, inputs.unit_width_mm, dx, steel_fyd)
        as_req_y = required_flexural_reinforcement_mm2(my, inputs.unit_width_mm, dy, steel_fyd)
        as_min_x = minimum_tension_reinforcement_mm2(inputs.unit_width_mm, dx, inputs.fck_mpa, inputs.fyk_mpa)
        as_min_y = minimum_tension_reinforcement_mm2(inputs.unit_width_mm, dy, inputs.fck_mpa, inputs.fyk_mpa)
        as_provided_x = provided_bar_area_mm2(inputs.bar_dia_x_mm, inputs.spacing_x_mm, inputs.unit_width_mm)
        as_provided_y = provided_bar_area_mm2(inputs.bar_dia_y_mm, inputs.spacing_y_mm, inputs.unit_width_mm)

        v_ed = uls * inputs.lx_m / 2.0 if inputs.support_condition != "Cantilever" else uls * inputs.lx_m
        shear_stress = v_ed * 1000.0 / (inputs.unit_width_mm * dx)
        vrdc = vrdc_mpa(inputs.fck_mpa, inputs.unit_width_mm, dx, as_provided_x, inputs.gamma_c)

        basic_ld = 20.0 * cls._K_SYS[inputs.support_condition]
        modification = min(1.5, as_provided_x / max(as_req_x, 1e-9))
        allowable_ld = basic_ld * modification
        actual_ld = inputs.lx_m * 1000.0 / dx

        req_x = max(as_req_x, as_min_x)
        req_y = max(as_req_y, as_min_y)
        return SlabDesignResult(
            aspect_ratio=ratio,
            effective_depth_x_mm=dx,
            effective_depth_y_mm=dy,
            self_weight_kn_m2=self_weight,
            permanent_load_kn_m2=permanent,
            imposed_load_kn_m2=inputs.imposed_load_kn_m2,
            uls_load_kn_m2=uls,
            sls_load_kn_m2=sls,
            moment_x_kn_m=mx,
            moment_y_kn_m=my,
            as_required_x_mm2_m=req_x,
            as_required_y_mm2_m=req_y,
            as_min_x_mm2_m=as_min_x,
            as_min_y_mm2_m=as_min_y,
            as_provided_x_mm2_m=as_provided_x,
            as_provided_y_mm2_m=as_provided_y,
            v_ed_kn_m=v_ed,
            vrdc_mpa=vrdc,
            shear_stress_mpa=shear_stress,
            actual_ld=actual_ld,
            allowable_ld=allowable_ld,
            flexure_x_ok=as_provided_x >= req_x,
            flexure_y_ok=as_provided_y >= req_y,
            shear_ok=shear_stress <= vrdc,
            deflection_ok=actual_ld <= allowable_ld,
            governing_uls_name=uls_name,
            governing_sls_name=sls_name,
        )


__all__ = ["SlabDesignInput", "SlabDesignResult", "RCSLabDesignEngine"]
