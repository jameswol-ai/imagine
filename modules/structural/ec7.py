"""Preliminary EN 1997-inspired geotechnical screening primitives."""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Soil:
    unit_weight_kn_m3: float
    cohesion_kpa: float
    friction_angle_deg: float
    allowable_bearing_kpa: float
    gamma_m: float = 1.0

    def __post_init__(self) -> None:
        if self.unit_weight_kn_m3 <= 0 or self.allowable_bearing_kpa <= 0:
            raise ValueError("soil unit weight and bearing resistance must be positive")
        if self.cohesion_kpa < 0 or not 0 <= self.friction_angle_deg < 90:
            raise ValueError("invalid cohesion or friction angle")
        if self.gamma_m <= 0:
            raise ValueError("gamma_m must be positive")


def rankine_active_coefficient(friction_angle_deg: float) -> float:
    if not 0 <= friction_angle_deg < 90:
        raise ValueError("friction angle must be in [0, 90) degrees")
    phi = math.radians(friction_angle_deg)
    return (1.0 - math.sin(phi)) / (1.0 + math.sin(phi))


def ultimate_bearing_capacity_kpa(soil: Soil, width_m: float, depth_m: float, surcharge_kpa: float = 0.0) -> float:
    """Terzaghi-style strip-footing screening capacity."""
    if width_m <= 0 or depth_m < 0 or surcharge_kpa < 0:
        raise ValueError("width must be positive; depth and surcharge cannot be negative")
    phi = math.radians(soil.friction_angle_deg)
    n_q = math.exp(math.pi * math.tan(phi)) * math.tan(math.pi / 4 + phi / 2) ** 2
    n_c = (n_q - 1.0) / math.tan(phi) if soil.friction_angle_deg > 1e-9 else 5.7
    n_gamma = 2.0 * (n_q + 1.0) * math.tan(phi)
    q = soil.unit_weight_kn_m3 * depth_m
    return soil.cohesion_kpa * n_c + q * n_q + 0.5 * soil.unit_weight_kn_m3 * width_m * n_gamma + surcharge_kpa * n_q


def bearing_utilisation(applied_kpa: float, allowable_kpa: float) -> float:
    if applied_kpa < 0 or allowable_kpa <= 0:
        raise ValueError("applied pressure cannot be negative and allowable pressure must be positive")
    return applied_kpa / allowable_kpa


__all__ = ["Soil", "rankine_active_coefficient", "ultimate_bearing_capacity_kpa", "bearing_utilisation"]
