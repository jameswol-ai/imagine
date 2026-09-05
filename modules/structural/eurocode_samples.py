"""Illustrative Eurocode family sample calculations for IMAGINE.

These examples are deliberately compact teaching/screening calculations. They
are not normative text and do not replace the adopted standard, National Annex,
project actions, material certificates, geotechnical investigation or engineer
verification.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True, slots=True)
class SampleResult:
    code: str
    title: str
    inputs: tuple[tuple[str, str], ...]
    outputs: tuple[tuple[str, str], ...]
    note: str


def _uls_floor(gk: float, qk: float) -> float:
    return 1.35 * gk + 1.50 * qk


def _wind_pressure(vb: float, ce: float = 1.0, cscd: float = 1.0) -> float:
    return 0.5 * 1.25 * vb**2 * ce * cscd / 1000.0


def _footing_area(ned: float, qa: float) -> float:
    return ned / qa


def _seismic_base_shear(mass_t: float, sa_g: float) -> float:
    return mass_t * 1000.0 * 9.81 * sa_g / 1000.0


def _timber_bending_moment(w: float, span: float) -> float:
    return w * span**2 / 8.0


def _masonry_slenderness(height: float, thickness: float) -> float:
    return height / thickness


def _aluminium_stress(load: float, area: float) -> float:
    return load / area


def build_samples() -> tuple[SampleResult, ...]:
    uls = _uls_floor(4.0, 3.0)
    wind = _wind_pressure(30.0)
    footing = _footing_area(700.0, 200.0)
    shear = _seismic_base_shear(18000.0, 0.20)
    timber_m = _timber_bending_moment(24.0, 8.0)
    masonry_sl = _masonry_slenderness(3.2, 0.20)
    alu_stress = _aluminium_stress(45000.0, 3000.0)
    return (
        SampleResult("EN 1990", "ULS floor combination", (("Gk", "4.0 kN/m2"), ("Qk", "3.0 kN/m2")), (("Illustrative Ed", f"{uls:.2f} kN/m2"),), "Screening combination only; accompanying actions, psi factors and National Annex values must be checked."),
        SampleResult("EN 1991", "Wind pressure screening", (("vb", "30 m/s"), ("rho", "1.25 kg/m3")), (("q", f"{wind:.2f} kN/m2"),), "Simplified dynamic-pressure example, not a complete EN 1991-1-4 building wind calculation."),
        SampleResult("EN 1992", "RC beam design workflow", (("MEd", "180 kNm"), ("Section", "300 x 600 mm"), ("Concrete", "C30/37")), (("Workflow", "Flexure → shear → SLS → detailing"),), "The sample demonstrates the workflow rather than issuing final reinforcement."),
        SampleResult("EN 1993", "Steel beam workflow", (("MEd", "250 kNm"), ("Steel", "S355")), (("Workflow", "Classification → resistance → buckling → SLS"),), "Section properties, restraints and member length must be established before design."),
        SampleResult("EN 1994", "Composite beam workflow", (("System", "Steel beam + RC slab"), ("Stage", "Construction + final")), (("Workflow", "Effective width → shear connection → resistance → deflection"),), "Construction-stage effects and connector design require project-specific data."),
        SampleResult("EN 1995", "Timber floor beam screening", (("w", "24 kN/m"), ("L", "8 m")), (("M", f"{timber_m:.1f} kNm"),), "Illustrative simply supported bending action; timber strength, service class, duration and stability are not checked here."),
        SampleResult("EN 1996", "Masonry slenderness screening", (("h", "3.2 m"), ("t", "200 mm")), (("h/t", f"{masonry_sl:.1f}"),), "Geometric screening only; eccentricity, restraint, material strength and load-bearing resistance must be checked."),
        SampleResult("EN 1997", "Pad footing area screening", (("NEd", "700 kN"), ("qa", "200 kPa")), (("A", f"{footing:.2f} m2"), ("Square equivalent", f"{sqrt(footing):.2f} m")), "Indicative area only; bearing resistance, settlement, sliding, overturning and geotechnical design approach remain to be verified."),
        SampleResult("EN 1998", "Seismic base-shear screening", (("Mass", "18,000 t"), ("Sa", "0.20g")), (("Base shear", f"{shear:.0f} kN"),), "Highly simplified screening relationship; actual seismic design requires hazard, spectrum, behaviour factor, modal/force procedure and National Annex inputs."),
        SampleResult("EN 1999", "Aluminium axial stress screening", (("N", "45 kN"), ("A", "3000 mm2")), (("Stress", f"{alu_stress:.1f} MPa"),), "Stress screening only; alloy, temper, buckling, local effects, connections and applicable EN 1999 provisions must be checked."),
    )


SAMPLES = build_samples()
SAMPLES_BY_CODE = {sample.code: sample for sample in SAMPLES}


def sample_for(code: str) -> SampleResult | None:
    return SAMPLES_BY_CODE.get(code)


__all__ = ["SampleResult", "SAMPLES", "SAMPLES_BY_CODE", "build_samples", "sample_for"]
