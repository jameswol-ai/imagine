"""Connected preliminary design pipeline for the IMAGINE sample project.

The pipeline intentionally uses transparent screening equations. It is a
workflow demonstrator, not a certified structural design engine.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from projects.sample_project import PROJECT
from modules.structural.eurocode_samples import _footing_area, _seismic_base_shear, _uls_floor, _wind_pressure


def _number(label: str, value: float, key: str) -> float:
    return float(st.number_input(label, min_value=0.0, value=float(value), key=key))


def render() -> None:
    st.title("Sample Project Design Pipeline")
    st.caption("IMAGINE Innovation Hub → Eurocode design workflow")
    st.warning("Preliminary engineering demonstration only. Adopt the applicable Eurocode edition and National Annex, replace every sample assumption with project data, and obtain professional verification before use.")

    st.markdown("### 1. Project")
    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Project", PROJECT["name"])
    p2.metric("GFA", f"{PROJECT['gross_floor_area_m2']:,.0f} m2")
    p3.metric("Storeys", PROJECT["storeys"])
    p4.metric("Grid", f"{PROJECT['grid_m']:.0f} m")

    with st.expander("Project assumptions", expanded=True):
        st.dataframe(pd.DataFrame([PROJECT]).T.rename(columns={0: "Value"}), use_container_width=True)

    st.markdown("### 2. Actions")
    c1, c2, c3 = st.columns(3)
    gk = _number("Characteristic permanent action Gk (kN/m2)", 4.0, "pipeline_gk")
    qk = _number("Characteristic imposed action Qk (kN/m2)", 3.0, "pipeline_qk")
    vb = _number("Basic wind velocity vb (m/s)", 30.0, "pipeline_vb")

    st.markdown("### 3. EN 1990 / EN 1991")
    uls = _uls_floor(gk, qk)
    wind = _wind_pressure(vb)
    a, b = st.columns(2)
    a.metric("Illustrative ULS floor action", f"{uls:.2f} kN/m2")
    b.metric("Wind dynamic-pressure screen", f"{wind:.2f} kN/m2")

    st.markdown("### 4. EN 1992 / EN 1993 / EN 1995")
    beam_action = uls * PROJECT["grid_m"] ** 2 / 8.0
    timber_span = PROJECT["grid_m"]
    steel_resistance = 5000.0 * 355.0 / 1000.0
    a, b, c = st.columns(3)
    a.metric("Illustrative grid beam M", f"{beam_action:.1f} kNm")
    b.metric("Timber reference span", f"{timber_span:.1f} m")
    c.metric("Sample S355 gross yield resistance", f"{steel_resistance:.0f} kN")

    st.markdown("### 5. EN 1997")
    footing_load = _number("Foundation design load NEd (kN)", 700.0, "pipeline_ned")
    qa = _number("Illustrative allowable bearing pressure (kPa)", 200.0, "pipeline_qa")
    area = _footing_area(footing_load, qa)
    st.metric("Indicative footing area", f"{area:.2f} m2")

    st.markdown("### 6. EN 1998")
    mass = _number("Seismic participating mass (t)", 18000.0, "pipeline_mass")
    sa = _number("Illustrative spectral acceleration (g)", 0.20, "pipeline_sa")
    base_shear = _seismic_base_shear(mass, sa)
    st.metric("Illustrative seismic base shear", f"{base_shear:.0f} kN")

    st.markdown("### 7. Design chain")
    chain = pd.DataFrame([
        ["EN 1990", "Design basis / combinations", "Illustrative ULS action"],
        ["EN 1991", "Permanent, imposed, wind actions", f"Wind q = {wind:.2f} kN/m2"],
        ["EN 1992", "Concrete members", "Beam/core workflow ready"],
        ["EN 1993", "Steel members", "Resistance screening ready"],
        ["EN 1995", "Timber members", "Span/action workflow ready"],
        ["EN 1997", "Foundation / ground", f"Area screen = {area:.2f} m2"],
        ["EN 1998", "Seismic", f"Base shear screen = {base_shear:.0f} kN"],
        ["EN 1994", "Composite", "Composite workflow next stage"],
        ["EN 1996", "Masonry", "Masonry workflow next stage"],
        ["EN 1999", "Aluminium", "Aluminium workflow next stage"],
    ], columns=["Code", "Stage", "Current sample output"])
    st.dataframe(chain, use_container_width=True, hide_index=True)

    st.markdown("### 8. Handoff")
    st.info("Next engineering handoff: member-level EN 1992/1993/1995 checks → structural analysis → BIM quantities → BOQ → construction documents. The current values are screening values only.")


render_module = render
__all__ = ["render", "render_module"]
