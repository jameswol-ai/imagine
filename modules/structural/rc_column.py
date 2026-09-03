"""Deterministic preliminary reinforced-concrete column screening engine.

This module separates column calculations from Streamlit presentation. It
covers section properties, EC2-style material strengths, reinforcement limits,
slenderness screening and minimum eccentricity. It intentionally does not
pretend to replace the full EN 1992-1-1 column procedure: second-order effects,
creep, biaxial interaction, imperfections, confinement, fire and detailing
checks require project-specific inputs and verification.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Mapping

from modules.structural.ec2 import ConcreteDesignProperties, SteelDesignProperties


@dataclass(frozen=True)
class ColumnScreeningResult:
    width_mm: float
    depth_mm: float
    unbraced_length_m: float
    concrete_area_mm2: float
    steel_area_mm2: float
    concrete_design_strength_mpa: float
    steel_design_strength_mpa: float
    minimum_steel_area_mm2: float
    maximum_steel_area_mm2: float
    slenderness_y: float
    slenderness_z: float
    slenderness_limit: float
    is_slender_y: bool
    is_slender_z: bool
    minimum_eccentricity_y_mm: float
    minimum_eccentricity_z_mm: float
    axial_capacity_kn: float
    axial_utilisation: float
    status: str


class RCColumnScreeningEngine:
    """Preliminary EC2-style column screening calculations."""

    def run(self, inputs: Mapping[str, float] | None = None) -> ColumnScreeningResult:
        values = dict(inputs or {})
        b = float(values.get("width_mm", 350.0))
        h = float(values.get("depth_mm", 350.0))
        l0 = float(values.get("unbraced_length_m", 3.6))
        fck = float(values.get("fck_mpa", 30.0))
        fyk = float(values.get("fyk_mpa", 500.0))
        gamma_c = float(values.get("gamma_c", 1.5))
        gamma_s = float(values.get("gamma_s", 1.15))
        alpha_cc = float(values.get("alpha_cc", 0.85))
        n_ed = float(values.get("n_ed_kn", 1200.0))
        steel_area = float(values.get("steel_area_mm2", 0.0))

        for name, value in {
            "width_mm": b,
            "depth_mm": h,
            "unbraced_length_m": l0,
            "fck_mpa": fck,
            "fyk_mpa": fyk,
            "gamma_c": gamma_c,
            "gamma_s": gamma_s,
        }.items():
            if value <= 0:
                raise ValueError(f"{name} must be greater than zero")
        if n_ed < 0 or steel_area < 0:
            raise ValueError("n_ed_kn and steel_area_mm2 cannot be negative")

        concrete = ConcreteDesignProperties(fck, gamma_c=gamma_c, alpha_cc=alpha_cc)
        steel = SteelDesignProperties(fyk, gamma_s=gamma_s)

        ac = b * h
        as_min = max(0.10 * n_ed * 1000.0 / steel.fyd_mpa, 0.002 * ac)
        as_max = 0.04 * ac
        as_used = steel_area if steel_area > 0 else as_min

        iy = h / math.sqrt(12.0)
        iz = b / math.sqrt(12.0)
        lambda_y = l0 * 1000.0 / iy
        lambda_z = l0 * 1000.0 / iz

        n_rel = n_ed * 1000.0 / (ac * concrete.fcd_mpa) if ac * concrete.fcd_mpa > 0 else 0.0
        lambda_lim = 20.0 * 0.7 * 1.1 * 0.7 / math.sqrt(n_rel) if n_rel > 0 else float("inf")

        e0_y = max(h / 30.0, 20.0)
        e0_z = max(b / 30.0, 20.0)

        axial_capacity = ((ac - as_used) * concrete.fcd_mpa + as_used * steel.fyd_mpa) / 1000.0
        axial_utilisation = n_ed / axial_capacity if axial_capacity > 0 else float("inf")

        reinforcement_ok = as_min <= as_used <= as_max
        capacity_ok = axial_utilisation <= 1.0
        status = "PASS" if reinforcement_ok and capacity_ok else "REVIEW"

        return ColumnScreeningResult(
            width_mm=b,
            depth_mm=h,
            unbraced_length_m=l0,
            concrete_area_mm2=ac,
            steel_area_mm2=as_used,
            concrete_design_strength_mpa=concrete.fcd_mpa,
            steel_design_strength_mpa=steel.fyd_mpa,
            minimum_steel_area_mm2=as_min,
            maximum_steel_area_mm2=as_max,
            slenderness_y=lambda_y,
            slenderness_z=lambda_z,
            slenderness_limit=lambda_lim,
            is_slender_y=lambda_y > lambda_lim,
            is_slender_z=lambda_z > lambda_lim,
            minimum_eccentricity_y_mm=e0_y,
            minimum_eccentricity_z_mm=e0_z,
            axial_capacity_kn=axial_capacity,
            axial_utilisation=axial_utilisation,
            status=status,
        )


__all__ = ["ColumnScreeningResult", "RCColumnScreeningEngine"]
