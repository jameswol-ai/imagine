"""Preliminary punching-shear verification primitive for RC slabs and footings."""

from __future__ import annotations

from dataclasses import dataclass
import math

from modules.structural.ec2 import vrdc_mpa


@dataclass(frozen=True)
class PunchingShearInput:
    column_width_mm: float
    column_length_mm: float
    effective_depth_mm: float
    applied_shear_kn: float
    tension_steel_mm2: float
    control_perimeter_factor: float = 4.0
    fck_mpa: float = 30.0
    gamma_c: float = 1.5

    def __post_init__(self) -> None:
        if min(self.column_width_mm, self.column_length_mm, self.effective_depth_mm, self.control_perimeter_factor, self.fck_mpa, self.gamma_c) <= 0:
            raise ValueError("geometry and material values must be positive")
        if self.applied_shear_kn < 0 or self.tension_steel_mm2 < 0:
            raise ValueError("shear and reinforcement cannot be negative")


@dataclass(frozen=True)
class PunchingShearResult:
    control_perimeter_mm: float
    shear_stress_mpa: float
    resistance_mpa: float
    utilisation: float
    ok: bool


def verify_punching_shear(inputs: PunchingShearInput) -> PunchingShearResult:
    perimeter = inputs.control_perimeter_factor * (inputs.column_width_mm + inputs.column_length_mm) / 2.0
    stress = inputs.applied_shear_kn * 1000.0 / (perimeter * inputs.effective_depth_mm)
    resistance = vrdc_mpa(inputs.fck_mpa, perimeter, inputs.effective_depth_mm, inputs.tension_steel_mm2, inputs.gamma_c)
    utilisation = stress / max(resistance, 1e-12)
    return PunchingShearResult(perimeter, stress, resistance, utilisation, utilisation <= 1.0)


__all__ = ["PunchingShearInput", "PunchingShearResult", "verify_punching_shear"]
