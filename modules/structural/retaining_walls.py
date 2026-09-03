"""Retaining-wall preliminary design engine.

The module performs transparent Rankine active-earth-pressure calculations and
external stability screening for a gravity/cantilever wall idealised as a
1 m strip. It is intentionally preliminary: groundwater, seismic actions,
passive resistance, layered soils, base shear keys, structural RC design,
sloping backfill and National Annex choices require project-specific checks.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Mapping

import pandas as pd
import streamlit as st


@dataclass(frozen=True)
class RetainingWallResult:
    wall_id: str
    height_m: float
    base_width_m: float
    stem_thickness_m: float
    soil_unit_weight_kn_m3: float
    friction_angle_deg: float
    surcharge_kn_m2: float
    wall_weight_kn_m: float
    active_coefficient: float
    active_soil_force_kn_m: float
    surcharge_force_kn_m: float
    total_lateral_force_kn_m: float
    overturning_moment_kn_m: float
    resisting_moment_kn_m: float
    sliding_resistance_kn_m: float
    sliding_factor_of_safety: float
    overturning_factor_of_safety: float
    resultant_from_toe_m: float
    eccentricity_m: float
    base_pressure_max_kpa: float
    base_pressure_min_kpa: float
    status: str


class RetainingWallEngine:
    """Rankine earth-pressure and external-stability screening engine."""

    def run(self, inputs: Mapping[str, float] | None = None) -> RetainingWallResult:
        values = dict(inputs or {})

        wall_id = str(values.get("wall_id", "RW-101"))
        h = float(values.get("height_m", 4.0))
        base = float(values.get("base_width_m", 3.0))
        stem = float(values.get("stem_thickness_m", 0.35))
        gamma_soil = float(values.get("soil_unit_weight_kn_m3", 18.0))
        phi_deg = float(values.get("friction_angle_deg", 30.0))
        surcharge = float(values.get("surcharge_kn_m2", 10.0))
        gamma_wall = float(values.get("wall_unit_weight_kn_m3", 24.0))
        mu = float(values.get("base_friction_coefficient", 0.50))
        toe = float(values.get("toe_length_m", 0.75))
        heel = float(values.get("heel_length_m", 1.90))

        positive = {
            "height_m": h,
            "base_width_m": base,
            "stem_thickness_m": stem,
            "soil_unit_weight_kn_m3": gamma_soil,
            "friction_angle_deg": phi_deg,
            "wall_unit_weight_kn_m3": gamma_wall,
            "base_friction_coefficient": mu,
            "toe_length_m": toe,
            "heel_length_m": heel,
        }
        for name, value in positive.items():
            if value <= 0:
                raise ValueError(f"{name} must be greater than zero")
        if surcharge < 0:
            raise ValueError("surcharge_kn_m2 cannot be negative")
        if not 0 < phi_deg < 60:
            raise ValueError("friction_angle_deg must be between 0 and 60 degrees")
        if abs(toe + stem + heel - base) > 1e-6:
            raise ValueError("toe_length_m + stem_thickness_m + heel_length_m must equal base_width_m")

        phi = math.radians(phi_deg)
        ka = (1.0 - math.sin(phi)) / (1.0 + math.sin(phi))

        # Rankine active pressure for level, drained backfill, per metre run.
        soil_force = 0.5 * ka * gamma_soil * h**2
        surcharge_force = ka * surcharge * h
        total_force = soil_force + surcharge_force

        # Soil component acts at h/3; surcharge component at h/2.
        overturning = soil_force * h / 3.0 + surcharge_force * h / 2.0

        # Simplified wall self-weight: rectangular stem + base slab.
        stem_weight = stem * h * gamma_wall
        base_slab_thickness = float(values.get("base_slab_thickness_m", 0.50))
        base_weight = base * base_slab_thickness * gamma_wall
        wall_weight = stem_weight + base_weight

        # Vertical soil over heel contributes to stabilising moment.
        heel_soil_weight = heel * h * gamma_soil
        vertical_total = wall_weight + heel_soil_weight
        wall_moment = wall_weight * (base / 2.0)
        heel_moment = heel_soil_weight * (toe + stem + heel / 2.0)
        resisting = wall_moment + heel_moment

        sliding_resistance = mu * vertical_total
        fs_slide = sliding_resistance / total_force if total_force else math.inf
        fs_overturn = resisting / overturning if overturning else math.inf

        resultant = (resisting - overturning) / vertical_total if vertical_total else 0.0
        eccentricity = base / 2.0 - resultant
        q_avg = vertical_total / base
        q_max = q_avg * (1.0 + 6.0 * eccentricity / base)
        q_min = q_avg * (1.0 - 6.0 * eccentricity / base)

        # Conservative preliminary screening targets, configurable by caller.
        fs_slide_req = float(values.get("required_fs_sliding", 1.50))
        fs_overturn_req = float(values.get("required_fs_overturning", 2.00))
        no_tension = abs(eccentricity) <= base / 6.0
        sliding_ok = fs_slide >= fs_slide_req
        overturn_ok = fs_overturn >= fs_overturn_req
        status = "PASS" if sliding_ok and overturn_ok and no_tension and q_min >= 0 else "REVIEW"

        return RetainingWallResult(
            wall_id=wall_id,
            height_m=h,
            base_width_m=base,
            stem_thickness_m=stem,
            soil_unit_weight_kn_m3=gamma_soil,
            friction_angle_deg=phi_deg,
            surcharge_kn_m2=surcharge,
            wall_weight_kn_m=wall_weight,
            active_coefficient=ka,
            active_soil_force_kn_m=soil_force,
            surcharge_force_kn_m=surcharge_force,
            total_lateral_force_kn_m=total_force,
            overturning_moment_kn_m=overturning,
            resisting_moment_kn_m=resisting,
            sliding_resistance_kn_m=sliding_resistance,
            sliding_factor_of_safety=fs_slide,
            overturning_factor_of_safety=fs_overturn,
            resultant_from_toe_m=resultant,
            eccentricity_m=eccentricity,
            base_pressure_max_kpa=q_max,
            base_pressure_min_kpa=q_min,
            status=status,
        )


class RetainingWallService:
    """Compatibility facade for callers using the former service name."""

    @staticmethod
    def preliminary_stability(wall_id, wall_height, wall_thickness):
        ratio = wall_height / wall_thickness
        return {
            "wall_id": wall_id,
            "height_m": wall_height,
            "thickness_m": wall_thickness,
            "height_thickness_ratio": round(ratio, 2),
            "status": "OK" if ratio < 15 else "REVIEW",
        }


def render() -> None:
    st.title("Retaining Wall Design")
    st.caption(
        "Preliminary Rankine active-pressure and external-stability screening. "
        "Project-specific geotechnical and structural verification is required."
    )

    with st.form("retaining_wall_design_form"):
        c1, c2 = st.columns(2)
        with c1:
            wall_id = st.text_input("Wall identifier", "RW-101")
            h = st.number_input("Retained height H (m)", min_value=0.5, value=4.0, step=0.1)
            base = st.number_input("Base width B (m)", min_value=0.5, value=3.0, step=0.1)
            stem = st.number_input("Stem thickness (m)", min_value=0.15, value=0.35, step=0.05)
            base_slab = st.number_input("Base slab thickness (m)", min_value=0.15, value=0.50, step=0.05)
        with c2:
            gamma = st.number_input("Backfill unit weight (kN/m³)", min_value=10.0, value=18.0, step=0.5)
            phi = st.number_input("Soil friction angle φ (°)", min_value=5.0, max_value=55.0, value=30.0, step=1.0)
            surcharge = st.number_input("Uniform surcharge (kN/m²)", min_value=0.0, value=10.0, step=1.0)
            mu = st.number_input("Base friction coefficient μ", min_value=0.1, value=0.50, step=0.05)
            required_slide = st.number_input("Required sliding FS", min_value=1.0, value=1.50, step=0.10)
            required_overturn = st.number_input("Required overturning FS", min_value=1.0, value=2.00, step=0.10)

        submitted = st.form_submit_button("Calculate retaining wall", type="primary")

    if not submitted:
        return

    toe = base * 0.25
    heel = base - toe - stem
    try:
        result = RetainingWallEngine().run({
            "wall_id": wall_id,
            "height_m": h,
            "base_width_m": base,
            "stem_thickness_m": stem,
            "base_slab_thickness_m": base_slab,
            "soil_unit_weight_kn_m3": gamma,
            "friction_angle_deg": phi,
            "surcharge_kn_m2": surcharge,
            "base_friction_coefficient": mu,
            "toe_length_m": toe,
            "heel_length_m": heel,
            "required_fs_sliding": required_slide,
            "required_fs_overturning": required_overturn,
        })
    except ValueError as exc:
        st.error(str(exc))
        return

    a, b, c, d = st.columns(4)
    a.metric("Active Ka", f"{result.active_coefficient:.3f}")
    b.metric("Lateral force", f"{result.total_lateral_force_kn_m:.1f} kN/m")
    c.metric("Sliding FS", f"{result.sliding_factor_of_safety:.2f}")
    d.metric("Overturning FS", f"{result.overturning_factor_of_safety:.2f}")

    table = pd.DataFrame([
        ["Active soil force", result.active_soil_force_kn_m, "kN/m"],
        ["Surcharge force", result.surcharge_force_kn_m, "kN/m"],
        ["Overturning moment", result.overturning_moment_kn_m, "kNm/m"],
        ["Resisting moment", result.resisting_moment_kn_m, "kNm/m"],
        ["Resultant from toe", result.resultant_from_toe_m, "m"],
        ["Eccentricity", result.eccentricity_m, "m"],
        ["Maximum base pressure", result.base_pressure_max_kpa, "kPa"],
        ["Minimum base pressure", result.base_pressure_min_kpa, "kPa"],
    ], columns=["Parameter", "Value", "Unit"])
    st.dataframe(table, use_container_width=True, hide_index=True)

    if result.status == "PASS":
        st.success("Preliminary sliding, overturning and no-tension checks pass.")
    else:
        st.warning("External stability screening requires review. Check soil parameters, groundwater, bearing capacity and structural design.")

    st.info(
        "Scope: 1 m wall strip, level drained backfill, Rankine active pressure, no passive resistance. "
        "This is an engineering screening aid, not a certified geotechnical design."
    )


__all__ = ["RetainingWallEngine", "RetainingWallResult", "RetainingWallService", "render"]
