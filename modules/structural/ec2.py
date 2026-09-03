"""Reusable EN 1992-1-1-style reinforced-concrete calculation primitives.

The functions in this module are deliberately small and deterministic so beam,
slab, column and foundation engines can share the same material and
reinforcement calculations. They are screening primitives, not a complete
Eurocode implementation. Project-specific National Annex values, exposure,
durability, detailing, second-order effects and all applicable limit states
must be verified by the engineer responsible for the design.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class ConcreteDesignProperties:
    """Design properties for normal-weight concrete."""
    fck_mpa: float
    gamma_c: float = 1.50
    alpha_cc: float = 0.85
    def __post_init__(self) -> None:
        if self.fck_mpa <= 0: raise ValueError("fck_mpa must be greater than zero")
        if self.gamma_c <= 0: raise ValueError("gamma_c must be greater than zero")
        if self.alpha_cc <= 0: raise ValueError("alpha_cc must be greater than zero")
    @property
    def fcd_mpa(self) -> float: return self.alpha_cc * self.fck_mpa / self.gamma_c
    @property
    def fctm_mpa(self) -> float:
        if self.fck_mpa <= 50.0: return 0.30 * self.fck_mpa ** (2.0 / 3.0)
        return 2.12 * math.log(1.0 + self.fck_mpa / 10.0)


@dataclass(frozen=True)
class SteelDesignProperties:
    """Design properties for reinforcing steel."""
    fyk_mpa: float
    gamma_s: float = 1.15
    def __post_init__(self) -> None:
        if self.fyk_mpa <= 0: raise ValueError("fyk_mpa must be greater than zero")
        if self.gamma_s <= 0: raise ValueError("gamma_s must be greater than zero")
    @property
    def fyd_mpa(self) -> float: return self.fyk_mpa / self.gamma_s


def effective_depth_mm(overall_depth_mm: float, cover_mm: float, stirrup_dia_mm: float, main_bar_dia_mm: float) -> float:
    """Return effective depth; zero stirrup diameter is valid for slabs."""
    values = {"overall_depth_mm": overall_depth_mm, "cover_mm": cover_mm, "main_bar_dia_mm": main_bar_dia_mm}
    if any(value <= 0 for value in values.values()):
        raise ValueError("geometry values must be greater than zero")
    if stirrup_dia_mm < 0:
        raise ValueError("stirrup_dia_mm cannot be negative")
    d = overall_depth_mm - cover_mm - stirrup_dia_mm - main_bar_dia_mm / 2.0
    if d <= 0: raise ValueError("effective depth must be greater than zero")
    return d


def minimum_tension_reinforcement_mm2(width_mm: float, effective_depth_mm_value: float, fck_mpa: float, fyk_mpa: float) -> float:
    if min(width_mm, effective_depth_mm_value, fck_mpa, fyk_mpa) <= 0: raise ValueError("width, effective depth, fck and fyk must be greater than zero")
    fctm = ConcreteDesignProperties(fck_mpa).fctm_mpa
    return max(0.26 * fctm / fyk_mpa * width_mm * effective_depth_mm_value, 0.0013 * width_mm * effective_depth_mm_value)


def maximum_longitudinal_reinforcement_mm2(width_mm: float, depth_mm: float) -> float:
    if width_mm <= 0 or depth_mm <= 0: raise ValueError("width and depth must be greater than zero")
    return 0.04 * width_mm * depth_mm


def required_flexural_reinforcement_mm2(moment_kn_m: float, width_mm: float, effective_depth_mm_value: float, fyd_mpa: float, *, z_factor: float = 0.95) -> float:
    if moment_kn_m < 0: raise ValueError("moment_kn_m cannot be negative")
    if min(width_mm, effective_depth_mm_value, fyd_mpa) <= 0: raise ValueError("width, effective depth and fyd must be greater than zero")
    if not 0 < z_factor <= 1: raise ValueError("z_factor must be between zero and one")
    z_mm = min(z_factor * effective_depth_mm_value, effective_depth_mm_value)
    return moment_kn_m * 1e6 / (fyd_mpa * z_mm)


def provided_bar_area_mm2(bar_dia_mm: float, spacing_mm: float | None = None, width_mm: float = 1000.0) -> float:
    if bar_dia_mm <= 0: raise ValueError("bar_dia_mm must be greater than zero")
    area = math.pi * bar_dia_mm**2 / 4.0
    if spacing_mm is None: return area
    if spacing_mm <= 0 or width_mm <= 0: raise ValueError("spacing and width must be greater than zero")
    return width_mm / spacing_mm * area


def vrdc_mpa(fck_mpa: float, width_mm: float, effective_depth_mm_value: float, as_tension_mm2: float, gamma_c: float = 1.50) -> float:
    if min(fck_mpa, width_mm, effective_depth_mm_value, gamma_c) <= 0: raise ValueError("fck, width, effective depth and gamma_c must be greater than zero")
    if as_tension_mm2 < 0: raise ValueError("as_tension_mm2 cannot be negative")
    rho_l = min(as_tension_mm2 / (width_mm * effective_depth_mm_value), 0.02)
    k = min(2.0, 1.0 + math.sqrt(200.0 / effective_depth_mm_value))
    return (0.18 / gamma_c) * k * (100.0 * rho_l * fck_mpa) ** (1.0 / 3.0)


__all__ = ["ConcreteDesignProperties", "SteelDesignProperties", "effective_depth_mm", "minimum_tension_reinforcement_mm2", "maximum_longitudinal_reinforcement_mm2", "required_flexural_reinforcement_mm2", "provided_bar_area_mm2", "vrdc_mpa"]
