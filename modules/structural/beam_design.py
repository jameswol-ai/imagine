"""Preliminary reinforced-concrete beam design workspace.

The engine provides transparent, deterministic screening calculations for a
simply supported beam under uniformly distributed permanent and variable
loads. It is intentionally labelled preliminary and is not a substitute for
project-specific EN 1992 design, detailing, national annexes, or professional
verification.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Mapping

import pandas as pd
import streamlit as st


@dataclass(frozen=True)
class BeamDesignResult:
    span_m: float
    self_weight_kn_m: float
    permanent_load_kn_m: float
    variable_load_kn_m: float
    uls_load_kn_m: float
    sls_load_kn_m: float
    uls_moment_kn_m: float
    uls_shear_kn: float
    sls_moment_kn_m: float
    effective_depth_mm: float
    fcd_mpa: float
    fyd_mpa: float
    as_required_mm2: float
    as_min_mm2: float
    as_max_mm2: float
    as_provided_mm2: float
    shear_stress_mpa: float
    shear_capacity_mpa: float
    bending_utilisation: float
    shear_utilisation: float
    status: str


class BeamDesignEngine:
    """Deterministic preliminary EN 1992 beam screening calculations."""

    def run(self, inputs: Mapping[str, float] | None = None) -> BeamDesignResult:
        values = dict(inputs or {})

        span = float(values.get("span_m", 6.0))
        width = float(values.get("width_mm", 300.0))
        depth = float(values.get("depth_mm", 500.0))
        cover = float(values.get("cover_mm", 30.0))
        stirrup = float(values.get("stirrup_dia_mm", 8.0))
        bar_dia = float(values.get("bar_dia_mm", 20.0))
        fck = float(values.get("fck_mpa", 30.0))
        fyk = float(values.get("fyk_mpa", 500.0))
        gamma_c = float(values.get("gamma_c", 1.5))
        gamma_s = float(values.get("gamma_s", 1.15))
        permanent = float(values.get("permanent_load_kn_m", 4.0))
        variable = float(values.get("variable_load_kn_m", 8.0))
        alpha_cc = float(values.get("alpha_cc", 0.85))

        for name, value in {
            "span_m": span,
            "width_mm": width,
            "depth_mm": depth,
            "cover_mm": cover,
            "stirrup_dia_mm": stirrup,
            "bar_dia_mm": bar_dia,
            "fck_mpa": fck,
            "fyk_mpa": fyk,
            "gamma_c": gamma_c,
            "gamma_s": gamma_s,
            "permanent_load_kn_m": permanent,
            "variable_load_kn_m": variable,
        }.items():
            if value <= 0:
                raise ValueError(f"{name} must be greater than zero")

        if depth * 1.0 <= cover + stirrup + bar_dia / 2:
            raise ValueError("Beam depth is too small for the specified cover and reinforcement")

        self_weight = width / 1000.0 * depth / 1000.0 * 25.0
        gk = permanent + self_weight
        qk = variable
        quls = 1.35 * gk + 1.50 * qk
        qsls = gk + qk

        med = quls * span**2 / 8.0
        ved = quls * span / 2.0
        msls = qsls * span**2 / 8.0

        d = depth - cover - stirrup - bar_dia / 2.0
        fcd = alpha_cc * fck / gamma_c
        fyd = fyk / gamma_s

        z = min(0.95 * d, d)
        as_required = med * 1e6 / (0.87 * fyk * z)
        fctm = 0.30 * fck ** (2.0 / 3.0)
        as_min = max(0.26 * fctm / fyk * width * d, 0.0013 * width * d)
        as_max = 0.04 * width * depth
        as_provided = math.ceil(as_required / (math.pi * bar_dia**2 / 4.0)) * (
            math.pi * bar_dia**2 / 4.0
        )

        rho_l = min(as_provided / (width * d), 0.02)
        k = min(2.0, 1.0 + math.sqrt(200.0 / d))
        c_rd_c = 0.18 / gamma_c
        vrdc = c_rd_c * k * (100.0 * rho_l * fck) ** (1.0 / 3.0)
        v_ed = ved * 1000.0 / (width * d)

        bending_util = as_required / as_provided if as_provided else float("inf")
        shear_util = v_ed / vrdc if vrdc else float("inf")
        reinforcement_ok = as_min <= as_provided <= as_max
        status = "PASS" if bending_util <= 1.0 and shear_util <= 1.0 and reinforcement_ok else "REVIEW"

        return BeamDesignResult(
            span_m=span,
            self_weight_kn_m=self_weight,
            permanent_load_kn_m=gk,
            variable_load_kn_m=qk,
            uls_load_kn_m=quls,
            sls_load_kn_m=qsls,
            uls_moment_kn_m=med,
            uls_shear_kn=ved,
            sls_moment_kn_m=msls,
            effective_depth_mm=d,
            fcd_mpa=fcd,
            fyd_mpa=fyd,
            as_required_mm2=as_required,
            as_min_mm2=as_min,
            as_max_mm2=as_max,
            as_provided_mm2=as_provided,
            shear_stress_mpa=v_ed,
            shear_capacity_mpa=vrdc,
            bending_utilisation=bending_util,
            shear_utilisation=shear_util,
            status=status,
        )


def render() -> None:
    """Render the interactive beam screening workspace."""
    st.title("Reinforced Concrete Beam Design")
    st.caption(
        "Preliminary simply supported beam screening using transparent EN 1992-based equations. "
        "Final design requires project-specific code checks, detailing and professional verification."
    )

    with st.form("beam_design_form"):
        geometry, materials = st.columns(2)
        with geometry:
            st.subheader("Geometry")
            span = st.number_input("Span (m)", min_value=0.5, value=6.0, step=0.1)
            width = st.number_input("Width b (mm)", min_value=150.0, value=300.0, step=25.0)
            depth = st.number_input("Overall depth h (mm)", min_value=200.0, value=500.0, step=25.0)
            cover = st.number_input("Nominal cover (mm)", min_value=15.0, value=30.0, step=5.0)
            stirrup = st.number_input("Stirrup diameter (mm)", min_value=6.0, value=8.0, step=2.0)
            bar_dia = st.number_input("Main bar diameter (mm)", min_value=10.0, value=20.0, step=2.0)

        with materials:
            st.subheader("Materials and loading")
            fck = st.number_input("Concrete fck (MPa)", min_value=12.0, value=30.0, step=5.0)
            fyk = st.number_input("Reinforcement fyk (MPa)", min_value=250.0, value=500.0, step=50.0)
            permanent = st.number_input("Additional permanent load (kN/m)", min_value=0.0, value=4.0, step=0.5)
            variable = st.number_input("Variable load (kN/m)", min_value=0.0, value=8.0, step=0.5)
            gamma_c = st.number_input("Concrete partial factor gamma_c", min_value=1.0, value=1.5, step=0.05)
            gamma_s = st.number_input("Steel partial factor gamma_s", min_value=1.0, value=1.15, step=0.05)
            alpha_cc = st.number_input("alpha_cc", min_value=0.5, max_value=1.0, value=0.85, step=0.05)

        submitted = st.form_submit_button("Calculate beam design", type="primary")

    if not submitted:
        return

    try:
        result = BeamDesignEngine().run(
            {
                "span_m": span,
                "width_mm": width,
                "depth_mm": depth,
                "cover_mm": cover,
                "stirrup_dia_mm": stirrup,
                "bar_dia_mm": bar_dia,
                "fck_mpa": fck,
                "fyk_mpa": fyk,
                "permanent_load_kn_m": permanent,
                "variable_load_kn_m": variable,
                "gamma_c": gamma_c,
                "gamma_s": gamma_s,
                "alpha_cc": alpha_cc,
            }
        )
    except ValueError as exc:
        st.error(str(exc))
        return

    st.subheader("Design summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ULS moment", f"{result.uls_moment_kn_m:.1f} kNm")
    c2.metric("ULS shear", f"{result.uls_shear_kn:.1f} kN")
    c3.metric("Required As", f"{result.as_required_mm2:.0f} mm²")
    c4.metric("Screening status", result.status)

    table = pd.DataFrame(
        [
            ["Self-weight", result.self_weight_kn_m, "kN/m"],
            ["ULS line load", result.uls_load_kn_m, "kN/m"],
            ["SLS line load", result.sls_load_kn_m, "kN/m"],
            ["Effective depth", result.effective_depth_mm, "mm"],
            ["Design concrete strength", result.fcd_mpa, "MPa"],
            ["Design steel strength", result.fyd_mpa, "MPa"],
            ["Minimum As", result.as_min_mm2, "mm²"],
            ["Provided As", result.as_provided_mm2, "mm²"],
            ["Maximum As", result.as_max_mm2, "mm²"],
            ["Shear stress", result.shear_stress_mpa, "MPa"],
            ["Shear resistance", result.shear_capacity_mpa, "MPa"],
            ["Bending utilisation", result.bending_utilisation, "ratio"],
            ["Shear utilisation", result.shear_utilisation, "ratio"],
        ],
        columns=["Parameter", "Value", "Unit"],
    )
    st.dataframe(table, use_container_width=True, hide_index=True)

    if result.status == "PASS":
        st.success("Preliminary bending, minimum/maximum reinforcement and shear screening checks pass.")
    else:
        st.warning("The preliminary screening requires review. Check reinforcement limits, shear, detailing and all project-specific code requirements.")

    st.info("This workspace is a preliminary engineering aid. It does not certify a structural design or replace the applicable Eurocode National Annex.")


__all__ = ["BeamDesignEngine", "BeamDesignResult", "render"]
