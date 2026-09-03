"""Preliminary EN 1998 seismic action primitives.

Use only for early-stage screening. The actual seismic design must use the
project seismic hazard, soil class, National Annex, behaviour factor,
regularity rules and structural analysis required for the project.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SeismicInput:
    seismic_coefficient: float
    total_mass_t: float
    behaviour_factor: float = 3.0
    importance_factor: float = 1.0

    def __post_init__(self) -> None:
        if self.seismic_coefficient < 0 or self.total_mass_t < 0:
            raise ValueError("seismic coefficient and mass cannot be negative")
        if self.behaviour_factor <= 0 or self.importance_factor <= 0:
            raise ValueError("behaviour and importance factors must be positive")


def base_shear_kn(inputs: SeismicInput, gravity_m_s2: float = 9.80665) -> float:
    """Equivalent-static base shear screening value Vb = Sd(T) m lambda."""
    if gravity_m_s2 <= 0:
        raise ValueError("gravity must be positive")
    return inputs.seismic_coefficient * inputs.total_mass_t * gravity_m_s2 * inputs.importance_factor / inputs.behaviour_factor


def distribute_storey_forces_kn(base_shear_kn_value: float, storey_masses_t: list[float], storey_heights_m: list[float]) -> list[float]:
    """Distribute base shear in proportion to m_i h_i."""
    if base_shear_kn_value < 0 or len(storey_masses_t) != len(storey_heights_m) or not storey_masses_t:
        raise ValueError("base shear must be nonnegative and storey arrays must have equal nonzero length")
    weights = [m * h for m, h in zip(storey_masses_t, storey_heights_m)]
    if any(m < 0 for m in storey_masses_t) or any(h <= 0 for h in storey_heights_m) or sum(weights) <= 0:
        raise ValueError("storey masses must be nonnegative and heights positive")
    return [base_shear_kn_value * w / sum(weights) for w in weights]


__all__ = ["SeismicInput", "base_shear_kn", "distribute_storey_forces_kn"]
