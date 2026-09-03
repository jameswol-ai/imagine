"""Small, reusable EN 1991 action helpers for structural modules.

These functions deliberately separate characteristic actions from EN 1990
combination factors so beams, slabs, foundations and walls can share them.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AreaActions:
    permanent_kn_m2: float = 0.0
    imposed_kn_m2: float = 0.0
    wind_kn_m2: float = 0.0
    snow_kn_m2: float = 0.0

    def __post_init__(self) -> None:
        for name, value in self.__dict__.items():
            if value < 0:
                raise ValueError(f"{name} cannot be negative")

    def to_line_load(self, tributary_width_m: float) -> dict[str, float]:
        if tributary_width_m <= 0:
            raise ValueError("tributary_width_m must be greater than zero")
        return {
            "G": self.permanent_kn_m2 * tributary_width_m,
            "Q": self.imposed_kn_m2 * tributary_width_m,
            "wind": self.wind_kn_m2 * tributary_width_m,
            "snow": self.snow_kn_m2 * tributary_width_m,
        }


def self_weight_kn_m3(density_kn_m3: float = 25.0) -> float:
    """Return the adopted nominal unit weight used by a module."""
    if density_kn_m3 <= 0:
        raise ValueError("density_kn_m3 must be greater than zero")
    return float(density_kn_m3)


def line_load_from_area(area_load_kn_m2: float, tributary_width_m: float) -> float:
    if area_load_kn_m2 < 0:
        raise ValueError("area_load_kn_m2 cannot be negative")
    if tributary_width_m <= 0:
        raise ValueError("tributary_width_m must be greater than zero")
    return area_load_kn_m2 * tributary_width_m


__all__ = ["AreaActions", "self_weight_kn_m3", "line_load_from_area"]
