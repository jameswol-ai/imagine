"""Small deterministic 2D Euler-Bernoulli beam analysis engine.

This is an educational/preliminary analysis kernel for simply supported beams
with uniformly distributed load. It is not a general-purpose finite-element
solver and does not replace project structural analysis software.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SimplySupportedBeamInput:
    span_m: float
    udl_kn_m: float
    elastic_modulus_gpa: float
    second_moment_m4: float

    def __post_init__(self) -> None:
        if min(self.span_m, self.elastic_modulus_gpa, self.second_moment_m4) <= 0:
            raise ValueError("span, elastic modulus and second moment must be positive")
        if self.udl_kn_m < 0:
            raise ValueError("udl cannot be negative")


@dataclass(frozen=True)
class BeamAnalysisResult:
    reaction_left_kn: float
    reaction_right_kn: float
    maximum_shear_kn: float
    maximum_moment_kn_m: float
    maximum_deflection_mm: float


def analyse_simply_supported_beam(inputs: SimplySupportedBeamInput) -> BeamAnalysisResult:
    l = inputs.span_m
    w = inputs.udl_kn_m
    reactions = w * l / 2.0
    moment = w * l**2 / 8.0
    e_pa = inputs.elastic_modulus_gpa * 1e9
    i_m4 = inputs.second_moment_m4
    deflection_m = 5.0 * (w * 1000.0) * l**4 / (384.0 * e_pa * i_m4)
    return BeamAnalysisResult(reactions, reactions, reactions, moment, deflection_m * 1000.0)


__all__ = ["SimplySupportedBeamInput", "BeamAnalysisResult", "analyse_simply_supported_beam"]
