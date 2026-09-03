"""Preliminary EN 1994 composite steel-concrete design primitives.

The implementation is intentionally a transparent screening layer. It does
not replace the complete EN 1994 procedure, National Annex, construction
stage checks, shear connection design, buckling, vibration or fire design.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CompositeBeamInput:
    steel_area_mm2: float
    steel_fy_mpa: float
    concrete_area_mm2: float
    concrete_fck_mpa: float
    effective_width_mm: float
    steel_lever_arm_mm: float
    concrete_lever_arm_mm: float
    gamma_m0: float = 1.0
    gamma_c: float = 1.5
    axial_demand_kn: float = 0.0
    moment_demand_kn_m: float = 0.0

    def __post_init__(self) -> None:
        for name, value in {
            "steel_area_mm2": self.steel_area_mm2,
            "steel_fy_mpa": self.steel_fy_mpa,
            "concrete_area_mm2": self.concrete_area_mm2,
            "concrete_fck_mpa": self.concrete_fck_mpa,
            "effective_width_mm": self.effective_width_mm,
            "steel_lever_arm_mm": self.steel_lever_arm_mm,
            "concrete_lever_arm_mm": self.concrete_lever_arm_mm,
            "gamma_m0": self.gamma_m0,
            "gamma_c": self.gamma_c,
        }.items():
            if value <= 0:
                raise ValueError(f"{name} must be greater than zero")
        if self.axial_demand_kn < 0 or self.moment_demand_kn_m < 0:
            raise ValueError("demands cannot be negative")


@dataclass(frozen=True)
class CompositeBeamResult:
    steel_tension_capacity_kn: float
    concrete_compression_capacity_kn: float
    composite_compression_capacity_kn: float
    simplified_moment_capacity_kn_m: float
    axial_utilisation: float
    moment_utilisation: float
    interaction_utilisation: float
    status: str


def design_composite_beam(inputs: CompositeBeamInput) -> CompositeBeamResult:
    steel = inputs.steel_area_mm2 * inputs.steel_fy_mpa / inputs.gamma_m0 / 1000.0
    concrete = inputs.effective_width_mm * inputs.concrete_area_mm2 / inputs.effective_width_mm * inputs.concrete_fck_mpa / inputs.gamma_c / 1000.0
    compression = min(steel, concrete)
    moment = compression * abs(inputs.steel_lever_arm_mm - inputs.concrete_lever_arm_mm) / 1000.0
    axial_u = inputs.axial_demand_kn / compression if compression else float("inf")
    moment_u = inputs.moment_demand_kn_m / moment if moment else float("inf")
    interaction = axial_u + moment_u
    return CompositeBeamResult(steel, concrete, compression, moment, axial_u, moment_u, interaction, "PASS" if interaction <= 1.0 else "REVIEW")


__all__ = ["CompositeBeamInput", "CompositeBeamResult", "design_composite_beam"]
