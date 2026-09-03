"""Preliminary roof geometry and timber arrangement workspace.

This module intentionally separates deterministic geometry from final timber
member design. It is a planning/screening tool, not a certified EN 1995
calculation package.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import pandas as pd
import streamlit as st

from components.workspace import engineering_notice, kpi_row, result_table, section, validation_summary


ROOF_TYPES = ("Gable", "Hip", "Mono-pitch", "Flat", "Mansard", "Butterfly", "Gambrel", "Sawtooth", "Custom")
TRUSS_TYPES = ("None / rafter roof", "Fink", "Howe", "Pratt", "King-post", "Queen-post", "Scissors", "Mono", "Raised-tie", "Custom")


@dataclass(frozen=True)
class RoofGeometry:
    roof_type: str
    span_m: float
    length_m: float
    pitch_deg: float
    overhang_m: float
    truss_spacing_m: float

    def __post_init__(self) -> None:
        if self.roof_type not in ROOF_TYPES:
            raise ValueError("Unsupported roof type")
        for name in ("span_m", "length_m", "truss_spacing_m"):
            if getattr(self, name) <= 0:
                raise ValueError(f"{name} must be positive")
        if not 0 <= self.pitch_deg < 89:
            raise ValueError("pitch_deg must be between 0 and 89 degrees")
        if self.overhang_m < 0:
            raise ValueError("overhang_m cannot be negative")

    @property
    def half_span_m(self) -> float:
        return self.span_m / 2

    @property
    def rise_m(self) -> float:
        return self.half_span_m * math.tan(math.radians(self.pitch_deg))

    @property
    def rafter_length_m(self) -> float:
        return math.hypot(self.half_span_m + self.overhang_m, self.rise_m)

    @property
    def sloping_area_m2(self) -> float:
        return 2 * self.rafter_length_m * self.length_m

    @property
    def plan_area_m2(self) -> float:
        return (self.span_m + 2 * self.overhang_m) * self.length_m

    @property
    def estimated_truss_count(self) -> int:
        return max(2, math.ceil(self.length_m / self.truss_spacing_m) + 1)


def timber_screening(w_mm: float, h_mm: float, span_m: float, spacing_m: float, load_kpa: float) -> dict[str, float | str]:
    """Simple member screening using a simply supported rafter idealisation."""
    if min(w_mm, h_mm, span_m, spacing_m, load_kpa) <= 0:
        raise ValueError("Member and load inputs must be positive")
    area_mm2 = w_mm * h_mm
    inertia_mm4 = w_mm * h_mm**3 / 12
    section_modulus_mm3 = w_mm * h_mm**2 / 6
    line_load_kn_m = load_kpa * spacing_m
    moment_kn_m = line_load_kn_m * span_m**2 / 8
    shear_kn = line_load_kn_m * span_m / 2
    bending_mpa = moment_kn_m * 1e6 / section_modulus_mm3
    return {
        "Area": area_mm2,
        "I": inertia_mm4,
        "Section modulus": section_modulus_mm3,
        "Line load": line_load_kn_m,
        "Moment": moment_kn_m,
        "Shear": shear_kn,
        "Bending stress": bending_mpa,
    }


def render() -> None:
    st.title("Roof Design")
    st.caption("Roof geometry, pitch, truss arrangement and preliminary timber member screening")

    section("Roof Geometry", "Define the architectural roof envelope before selecting a structural arrangement.")
    c1, c2, c3 = st.columns(3)
    with c1:
        roof_type = st.selectbox("Roof type", ROOF_TYPES)
        span = st.number_input("Building span (m)", min_value=1.0, value=10.0, step=0.5)
    with c2:
        length = st.number_input("Building length (m)", min_value=1.0, value=20.0, step=0.5)
        pitch = st.number_input("Pitch (degrees)", min_value=0.0, max_value=80.0, value=25.0, step=1.0)
    with c3:
        overhang = st.number_input("Overhang (m)", min_value=0.0, value=0.45, step=0.05)
        spacing = st.number_input("Truss / rafter spacing (m)", min_value=0.3, value=1.2, step=0.1)

    geometry = RoofGeometry(roof_type, span, length, pitch, overhang, spacing)
    kpi_row([
        ("Rise", f"{geometry.rise_m:.2f} m", "Approximate rise from eaves to ridge for gable-type geometry"),
        ("Rafter length", f"{geometry.rafter_length_m:.2f} m", None),
        ("Roof area", f"{geometry.sloping_area_m2:.1f} m²", None),
        ("Truss positions", geometry.estimated_truss_count, None),
    ])

    section("Structural Arrangement", "Select the primary load path. Final arrangement depends on architecture, supports, bracing and wind actions.")
    a, b = st.columns(2)
    with a:
        truss_type = st.selectbox("Truss arrangement", TRUSS_TYPES)
        primary = st.selectbox("Primary system", ["Rafters", "Trusses", "Rafters + purlins", "Trusses + purlins", "Ridge beam + rafters"])
    with b:
        member_grade = st.selectbox("Timber grade", ["C16", "C24", "Glulam", "Custom / project grade"])
        roof_load = st.number_input("Preliminary characteristic roof load (kPa)", min_value=0.1, value=1.0, step=0.1)

    member = timber_screening(75.0, 200.0, geometry.rafter_length_m, spacing, roof_load)
    section("Indicative Timber Arrangement")
    result_table([
        {"Member": "Rafter", "Indicative section": "75 x 200 mm", "Role": "Roof slope primary member"},
        {"Member": "Purlin", "Indicative section": "100 x 200 mm", "Role": "Intermediate roof support"},
        {"Member": "Truss chord", "Indicative section": "75 x 200 mm", "Role": f"{truss_type} arrangement"},
        {"Member": "Ceiling tie / joist", "Indicative section": "50 x 200 mm", "Role": "Tie / ceiling support"},
        {"Member": "Wall plate", "Indicative section": "100 x 100 mm", "Role": "Load transfer to walls"},
    ])

    section("Preliminary Rafter Check")
    result_table([{k: round(v, 3) if isinstance(v, float) else v for k, v in member.items()}])
    bending_limit = 8.0
    utilisation = float(member["Bending stress"]) / bending_limit
    validation_summary(passed=1 if utilisation <= 1 else 0, warnings=1 if utilisation > 0.75 and utilisation <= 1 else 0, failures=1 if utilisation > 1 else 0, note="The illustrative bending limit is a screening parameter, not an EN 1995 design value. Verify strength class, duration factors, modification factors, buckling, connections and serviceability.")
    engineering_notice("Roof actions should be developed from EN 1991, including permanent actions, imposed/maintenance actions and wind uplift/pressure. Snow actions are project/location dependent. Timber member and connection design should then be completed to EN 1995 with the applicable National Annex.")
