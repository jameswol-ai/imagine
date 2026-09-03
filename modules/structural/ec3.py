"""Small EN 1993-inspired steel design primitives for preliminary screening.

These equations are intentionally transparent and incomplete. Section
classification, buckling curves, interaction checks, fatigue, connection
ductility and the adopted National Annex must be verified for real design.
"""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class SteelSection:
    area_mm2: float
    fy_mpa: float
    iy_mm4: float
    iz_mm4: float
    length_m: float
    gamma_m0: float = 1.0
    gamma_m1: float = 1.0

    def __post_init__(self) -> None:
        if min(self.area_mm2, self.fy_mpa, self.iy_mm4, self.iz_mm4, self.length_m) <= 0:
            raise ValueError("section properties and length must be greater than zero")
        if min(self.gamma_m0, self.gamma_m1) <= 0:
            raise ValueError("partial factors must be greater than zero")


@dataclass(frozen=True)
class SteelScreeningResult:
    gross_yield_resistance_kn: float
    radius_y_mm: float
    radius_z_mm: float
    slenderness_y: float
    slenderness_z: float
    governing_slenderness: float


def section_yield_resistance_kn(section: SteelSection) -> float:
    """Gross-section axial yield resistance Npl,Rd in kN."""
    return section.area_mm2 * section.fy_mpa / section.gamma_m0 / 1000.0


def radius_of_gyration_mm(moment_of_inertia_mm4: float, area_mm2: float) -> float:
    if moment_of_inertia_mm4 <= 0 or area_mm2 <= 0:
        raise ValueError("moment of inertia and area must be greater than zero")
    return math.sqrt(moment_of_inertia_mm4 / area_mm2)


def preliminary_slenderness(section: SteelSection) -> SteelScreeningResult:
    ry = radius_of_gyration_mm(section.iy_mm4, section.area_mm2)
    rz = radius_of_gyration_mm(section.iz_mm4, section.area_mm2)
    ly = section.length_m * 1000.0 / ry
    lz = section.length_m * 1000.0 / rz
    return SteelScreeningResult(
        gross_yield_resistance_kn=section_yield_resistance_kn(section),
        radius_y_mm=ry,
        radius_z_mm=rz,
        slenderness_y=ly,
        slenderness_z=lz,
        governing_slenderness=max(ly, lz),
    )


@dataclass(frozen=True)
class BoltGroup:
    bolt_diameter_mm: float
    bolt_count: int
    bolt_fu_mpa: float
    gamma_m2: float = 1.25
    plate_thickness_mm: float = 10.0
    plate_fu_mpa: float = 430.0

    def __post_init__(self) -> None:
        if self.bolt_diameter_mm <= 0 or self.bolt_count <= 0 or self.bolt_fu_mpa <= 0:
            raise ValueError("bolt properties must be positive")
        if self.plate_thickness_mm <= 0 or self.plate_fu_mpa <= 0 or self.gamma_m2 <= 0:
            raise ValueError("plate and partial-factor properties must be positive")


def bolt_shear_resistance_kn(group: BoltGroup, alpha_v: float = 0.6) -> float:
    """Preliminary bolt shear resistance using 0.6 fu A per bolt."""
    if not 0 < alpha_v <= 1:
        raise ValueError("alpha_v must be between zero and one")
    area = math.pi * group.bolt_diameter_mm**2 / 4.0
    return group.bolt_count * alpha_v * group.bolt_fu_mpa * area / group.gamma_m2 / 1000.0


__all__ = ["SteelSection", "SteelScreeningResult", "section_yield_resistance_kn", "preliminary_slenderness", "BoltGroup", "bolt_shear_resistance_kn"]
