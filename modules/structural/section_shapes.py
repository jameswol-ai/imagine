"""Structural section shape utilities for preliminary member sizing."""
from __future__ import annotations
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class RectangularSection:
    width_mm: float
    depth_mm: float
    def __post_init__(self) -> None:
        if self.width_mm <= 0 or self.depth_mm <= 0:
            raise ValueError("section dimensions must be greater than zero")
    @property
    def area_mm2(self) -> float: return self.width_mm * self.depth_mm
    @property
    def ix_mm4(self) -> float: return self.width_mm * self.depth_mm**3 / 12.0
    @property
    def iy_mm4(self) -> float: return self.depth_mm * self.width_mm**3 / 12.0
    @property
    def rx_mm(self) -> float: return math.sqrt(self.ix_mm4 / self.area_mm2)
    @property
    def ry_mm(self) -> float: return math.sqrt(self.iy_mm4 / self.area_mm2)
    @property
    def z_x_mm3(self) -> float: return self.ix_mm4 / (self.depth_mm / 2.0)
    @property
    def z_y_mm3(self) -> float: return self.iy_mm4 / (self.width_mm / 2.0)

@dataclass(frozen=True)
class CircularSection:
    diameter_mm: float
    def __post_init__(self) -> None:
        if self.diameter_mm <= 0: raise ValueError("diameter must be greater than zero")
    @property
    def area_mm2(self) -> float: return math.pi * self.diameter_mm**2 / 4.0
    @property
    def i_mm4(self) -> float: return math.pi * self.diameter_mm**4 / 64.0
    @property
    def r_mm(self) -> float: return math.sqrt(self.i_mm4 / self.area_mm2)
    @property
    def z_mm3(self) -> float: return self.i_mm4 / (self.diameter_mm / 2.0)

def section_catalogue() -> list[dict[str, object]]:
    return [
        {"Shape": "Rectangular", "Typical use": "RC beam / column", "Inputs": "b × h"},
        {"Shape": "Circular", "Typical use": "RC column / pile", "Inputs": "diameter"},
        {"Shape": "I / H", "Typical use": "Steel beam / column", "Inputs": "section catalogue or dimensions"},
        {"Shape": "RHS / SHS", "Typical use": "Steel hollow section", "Inputs": "B × H × t"},
        {"Shape": "CHS", "Typical use": "Steel circular hollow section", "Inputs": "D × t"},
    ]

__all__ = ["RectangularSection", "CircularSection", "section_catalogue"]
