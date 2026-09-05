"""Built-in sample project for demonstrating the IMAGINE workflow.

The project is deliberately an illustrative engineering dataset. Values are
not a construction design and must be replaced by project-specific surveys,
loads, materials, geotechnical information and the adopted National Annex.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st


PROJECT = {
    "name": "IMAGINE Innovation Hub",
    "type": "Commercial Innovation Hub",
    "description": "12-storey hybrid mass-timber innovation hub used as the demonstration project for the IMAGINE AEC workflow.",
    "location": "Juba, South Sudan",
    "site_area_m2": 2500.0,
    "gross_floor_area_m2": 18000.0,
    "storeys": 12,
    "grid_m": 8.0,
    "structural_system": "Hybrid mass timber + reinforced concrete core",
    "design_stage": "Preliminary design",
}

EUROCODES = [
    ("EN 1990", "Design basis", "ULS/SLS combination framework and reliability basis"),
    ("EN 1991", "Actions", "Permanent, imposed, wind and other actions"),
    ("EN 1992", "Concrete", "RC core, foundations and concrete components"),
    ("EN 1993", "Steel", "Connections, secondary steel and steel components"),
    ("EN 1994", "Composite", "Composite interface and mixed-material components"),
    ("EN 1995", "Timber", "Primary mass-timber floor and beam screening"),
    ("EN 1996", "Masonry", "Non-structural and selected masonry elements"),
    ("EN 1997", "Geotechnical", "Bearing, settlement and foundation design basis"),
    ("EN 1998", "Seismic", "Seismic screening and structural response assumptions"),
    ("EN 1999", "Aluminium", "Lightweight façade and aluminium component screening"),
]

SAMPLE_CHECKS = [
    {"Code": "EN 1990", "Sample": "ULS floor combination", "Input": "Gk 4.0 + Qk 3.0 kN/m2", "Output": "Illustrative design action = 9.9 kN/m2"},
    {"Code": "EN 1991", "Sample": "Wind pressure screening", "Input": "vb 30 m/s, exposure factor 1.0", "Output": "Dynamic pressure screening value = 0.55 kN/m2"},
    {"Code": "EN 1992", "Sample": "RC beam flexure", "Input": "MEd 180 kNm, 300 x 600 mm", "Output": "Illustrative reinforcement sizing workflow"},
    {"Code": "EN 1993", "Sample": "Steel beam resistance", "Input": "S355 I-section, MEd 250 kNm", "Output": "Illustrative utilisation workflow"},
    {"Code": "EN 1994", "Sample": "Composite beam", "Input": "Steel beam + concrete slab", "Output": "Illustrative composite resistance workflow"},
    {"Code": "EN 1995", "Sample": "Timber floor beam", "Input": "8 m span, imposed load 3.0 kN/m2", "Output": "Illustrative bending/deflection workflow"},
    {"Code": "EN 1996", "Sample": "Masonry wall", "Input": "200 mm wall, 3.2 m storey", "Output": "Illustrative compression/slenderness workflow"},
    {"Code": "EN 1997", "Sample": "Pad footing", "Input": "NEd 700 kN, qa 200 kPa", "Output": "Indicative footing area = 3.50 m2"},
    {"Code": "EN 1998", "Sample": "Seismic base shear", "Input": "Mass 18,000 t, Sa 0.20g", "Output": "Illustrative base-shear screening"},
    {"Code": "EN 1999", "Sample": "Aluminium member", "Input": "6061-T6 section, axial load 45 kN", "Output": "Illustrative resistance workflow"},
]


def render() -> None:
    st.title("IMAGINE Innovation Hub")
    st.caption("Sample project and demonstration dataset for the complete AEC workflow")
    st.warning("Demonstration dataset only. Replace all assumptions with project-specific information and verify the adopted Eurocode edition and National Annex before engineering use.")

    a, b, c, d = st.columns(4)
    a.metric("Site area", f"{PROJECT['site_area_m2']:,.0f} m2")
    b.metric("GFA", f"{PROJECT['gross_floor_area_m2']:,.0f} m2")
    c.metric("Storeys", PROJECT["storeys"])
    d.metric("Grid", f"{PROJECT['grid_m']:.0f} m")

    overview, design_basis, samples = st.tabs(["Project Overview", "Design Basis", "Eurocode Samples"])

    with overview:
        st.dataframe(pd.DataFrame([PROJECT]).T.rename(columns={0: "Value"}), use_container_width=True)
        st.markdown("### Demonstration workflow")
        st.write("Project → Architecture → Structural Design Basis → Actions → Eurocode combinations → Analysis → Member design → BIM → MEP → BOQ → Construction → Documents → Digital Twin")

    with design_basis:
        st.dataframe(pd.DataFrame(EUROCODES, columns=["Eurocode", "Discipline", "Sample application"]), use_container_width=True, hide_index=True)
        st.markdown("### Structural assumptions")
        assumptions = pd.DataFrame([
            ["Concrete", "C30/37", "Illustrative only"],
            ["Reinforcement", "B500B", "Illustrative only"],
            ["Structural steel", "S355", "Illustrative only"],
            ["Timber", "GL/CLT system", "Project-specific supplier data required"],
            ["Foundation soil", "qa = 200 kPa", "Illustrative only; geotechnical investigation required"],
            ["Wind basic velocity", "30 m/s", "Illustrative screening assumption"],
            ["Seismic acceleration", "0.20g", "Illustrative screening assumption"],
        ], columns=["Parameter", "Value", "Control"])
        st.dataframe(assumptions, use_container_width=True, hide_index=True)

    with samples:
        st.dataframe(pd.DataFrame(SAMPLE_CHECKS), use_container_width=True, hide_index=True)
        st.bar_chart(pd.DataFrame({"Sample checks": [1] * 10}, index=[row[0] for row in SAMPLE_CHECKS]))


render_module = render
__all__ = ["PROJECT", "EUROCODES", "SAMPLE_CHECKS", "render", "render_module"]
