"""Preliminary EN 1996 masonry wall resistance screening."""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class MasonryWallInput:
    thickness_mm: float
    height_m: float
    wall_length_m: float
    masonry_compressive_strength_mpa: float
    partial_factor: float = 2.0
    axial_demand_kn: float = 0.0
    eccentricity_mm: float = 0.0

    def __post_init__(self) -> None:
        for name, value in {
            "thickness_mm": self.thickness_mm,
            "height_m": self.height_m,
            "wall_length_m": self.wall_length_m,
            "masonry_compressive_strength_mpa": self.masonry_compressive_strength_mpa,
            "partial_factor": self.partial_factor,
        }.items():
            if value <= 0:
                raise ValueError(f"{name} must be greater than zero")
        if self.axial_demand_kn < 0:
            raise ValueError("axial_demand_kn cannot be negative")


@dataclass(frozen=True)
class MasonryWallResult:
    area_m2: float
    slenderness: float
    design_compressive_strength_mpa: float
    eccentricity_ratio: float
    capacity_kn: float
    utilisation: float
    status: str


def screen_masonry_wall(inputs: MasonryWallInput) -> MasonryWallResult:
    area = inputs.thickness_mm / 1000.0 * inputs.wall_length_m
    slenderness = inputs.height_m / (inputs.thickness_mm / 1000.0)
    f_d = inputs.masonry_compressive_strength_mpa / inputs.partial_factor
    eccentricity_ratio = abs(inputs.eccentricity_mm) / inputs.thickness_mm
    reduction = max(0.0, 1.0 - 2.0 * eccentricity_ratio)
    capacity = area * f_d * 1000.0 * reduction
    utilisation = inputs.axial_demand_kn / capacity if capacity > 0 else float("inf")
    status = "PASS" if utilisation <= 1.0 and slenderness <= 27.0 and eccentricity_ratio <= 0.5 else "REVIEW"
    return MasonryWallResult(area, slenderness, f_d, eccentricity_ratio, capacity, utilisation, status)


__all__ = ["MasonryWallInput", "MasonryWallResult", "screen_masonry_wall"]
