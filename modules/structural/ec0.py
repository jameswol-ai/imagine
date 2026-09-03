"""Reusable EN 1990-style action-combination primitives.

The numerical defaults are screening defaults. Production design must use the
project's adopted National Annex and project-specific combination rules.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

DEFAULT_PSI = 0.7
GAMMA_G_UNFAVOURABLE = 1.35
GAMMA_G_FAVOURABLE = 1.0
GAMMA_Q = 1.5


@dataclass(frozen=True)
class LoadSet:
    permanent: float = 0.0
    leading_variable: float = 0.0
    accompanying_variable: float = 0.0
    wind: float = 0.0
    snow: float = 0.0

    def __post_init__(self) -> None:
        for name, value in self.__dict__.items():
            if value < 0:
                raise ValueError(f"{name} cannot be negative")


def build_uls_combinations(loads: LoadSet, psi0: float = DEFAULT_PSI) -> list[tuple[str, float]]:
    """Return a transparent set of gravity/wind/snow screening combinations."""
    if not 0 <= psi0 <= 1:
        raise ValueError("psi0 must be between 0 and 1")
    g = loads.permanent
    q = loads.leading_variable
    qa = loads.accompanying_variable
    w = loads.wind
    s = loads.snow
    return [
        ("ULS 1: 1.35G + 1.50Q + 1.50ψ₀Qacc", 1.35*g + 1.50*q + 1.50*psi0*qa),
        ("ULS 2: 1.35G + 1.50W + 1.50ψ₀Q", 1.35*g + 1.50*w + 1.50*psi0*q),
        ("ULS 3: 1.35G + 1.50S + 1.50ψ₀Q", 1.35*g + 1.50*s + 1.50*psi0*q),
        ("ULS 4: 1.00G + 1.50Q", g + 1.50*q),
    ]


def build_sls_combinations(loads: LoadSet, psi0: float = DEFAULT_PSI) -> list[tuple[str, float]]:
    """Return characteristic-style SLS screening combinations."""
    if not 0 <= psi0 <= 1:
        raise ValueError("psi0 must be between 0 and 1")
    g = loads.permanent
    q = loads.leading_variable
    qa = loads.accompanying_variable
    w = loads.wind
    s = loads.snow
    return [
        ("SLS 1: G + Q + ψ₀Qacc", g + q + psi0*qa),
        ("SLS 2: G + W + ψ₀Q", g + w + psi0*q),
        ("SLS 3: G + S + ψ₀Q", g + s + psi0*q),
    ]


def governing_combination(combinations: Iterable[tuple[str, float]]) -> tuple[str, float]:
    """Return the maximum positive scalar combination."""
    cases = list(combinations)
    if not cases:
        raise ValueError("At least one combination is required")
    return max(cases, key=lambda item: item[1])


__all__ = [
    "DEFAULT_PSI", "LoadSet", "build_uls_combinations",
    "build_sls_combinations", "governing_combination",
]
