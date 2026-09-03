"""Structural design handbook and Eurocode family navigator.

This module is an educational engineering reference layer. It intentionally
summarises the scope of EN 1990-EN 1999 rather than reproducing copyrighted
standards. Numerical design provisions must be taken from the adopted edition
and National Annex and verified by the responsible engineer.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

EUROCODES = [
    ("EN 1990", "Basis of structural design", "Reliability, limit states, actions, combinations and design situations."),
    ("EN 1991", "Actions on structures", "Permanent, imposed, snow, wind, thermal, accidental, traffic and execution actions."),
    ("EN 1992", "Design of concrete structures", "Reinforced and prestressed concrete, durability, detailing, fire and special structures."),
    ("EN 1993", "Design of steel structures", "Steel members, stability, connections, fatigue, shells and fire design."),
    ("EN 1994", "Design of composite steel and concrete structures", "Composite beams, slabs, columns and frames, including construction-stage considerations."),
    ("EN 1995", "Design of timber structures", "Solid timber, engineered timber, joints, stability, serviceability and fire."),
    ("EN 1996", "Design of masonry structures", "Unreinforced and reinforced masonry, lateral loads, stability, detailing and fire."),
    ("EN 1997", "Geotechnical design", "Ground investigation, foundations, retaining structures, slopes and geotechnical limit states."),
    ("EN 1998", "Design for earthquake resistance", "Seismic actions, analysis, ductility, detailing and earthquake-resistant foundations."),
    ("EN 1999", "Design of aluminium structures", "Aluminium member resistance, stability, connections, fatigue and fire considerations."),
]

MATERIALS = [
    ("Concrete", "C20/25 to high-strength classes", "fck, fctm, density, Ecm, durability/exposure, creep and shrinkage."),
    ("Reinforcing steel", "B500 class family", "fyk, fyd, ductility, bar diameter, anchorage and lap detailing."),
    ("Structural steel", "S235 / S275 / S355 / S460", "fy, fu, thickness effects, toughness and weldability."),
    ("Timber", "C14 / C16 / C18 / C24 / C30", "Strength class, stiffness, density, service class and duration effects."),
    ("Engineered timber", "Glulam / LVL / CLT", "Product-specific strength and stiffness properties must be declared."),
    ("Masonry", "Units, mortar and grout", "Unit strength, mortar class, characteristic masonry strength and execution."),
    ("Aluminium", "Alloy and temper dependent", "Alloy strength, thickness, buckling, welding and connection behaviour."),
    ("Steel-concrete composite", "Composite system", "Steel, concrete, shear connection and construction-stage compatibility."),
    ("Geotechnical materials", "Soil / rock", "Unit weight, effective strength, stiffness, groundwater and site investigation data."),
]

DESIGN_STAGES = [
    "Project brief and design basis",
    "Structural system selection",
    "Actions and load paths",
    "EN 1990 combinations",
    "EN 1991 action assessment",
    "Material and member design",
    "Global analysis and stability",
    "Serviceability and robustness",
    "Connections and detailing",
    "Foundation and ground interaction",
    "Seismic / accidental / fire checks where applicable",
    "Drawings, schedules, specifications and independent verification",
]


def render() -> None:
    st.title("Structural Design Handbook")
    st.caption("Engineering reference navigator covering the Eurocode family, structural materials, design workflow and coordination topics.")

    tabs = st.tabs(["Eurocode Family", "Building Materials", "Design Workflow", "Design Topics"])
    with tabs[0]:
        st.subheader("EN 1990 to EN 1999")
        df = pd.DataFrame(EUROCODES, columns=["Code", "Title", "Primary scope"])
        st.dataframe(df, use_container_width=True, hide_index=True)
        selected = st.selectbox("Open handbook topic", [row[0] for row in EUROCODES], key="structural_handbook_code")
        row = next(item for item in EUROCODES if item[0] == selected)
        st.markdown(f"### {row[0]} · {row[1]}")
        st.write(row[2])
        st.info("The handbook provides scope and workflow guidance. It does not reproduce the standard text or constitute a code check.")

    with tabs[1]:
        st.subheader("Building Materials")
        st.dataframe(pd.DataFrame(MATERIALS, columns=["Material", "Typical classes / family", "Design data to establish"]), use_container_width=True, hide_index=True)
        material = st.selectbox("Material reference", [row[0] for row in MATERIALS], key="structural_material")
        selected_material = next(row for row in MATERIALS if row[0] == material)
        st.markdown(f"**{selected_material[0]}**")
        st.write(selected_material[2])
        st.warning("Material properties are project/product dependent. Use manufacturer declarations, material certificates, test data and the adopted design standard for final values.")

    with tabs[2]:
        st.subheader("Structural Design Workflow")
        st.dataframe(pd.DataFrame({"Stage": list(range(1, len(DESIGN_STAGES) + 1)), "Activity": DESIGN_STAGES}), use_container_width=True, hide_index=True)
        st.markdown("**Core load path:** Architecture → actions → combinations → analysis → member design → connections → foundations → detailing → verification.")

    with tabs[3]:
        topics = [
            "Design basis and National Annex selection",
            "Load paths and tributary areas",
            "ULS / SLS combinations",
            "Durability and exposure",
            "Strength and stability",
            "Deflection, crack width and vibration",
            "Robustness and accidental actions",
            "Fire resistance",
            "Seismic design",
            "Connections and anchorage",
            "Construction-stage effects",
            "Quality control and design verification",
        ]
        st.dataframe(pd.DataFrame({"Structural topic": topics}), use_container_width=True, hide_index=True)

    st.warning("IMAGINE structural calculations are preliminary engineering tools unless a module explicitly documents a validated design scope. Confirm the adopted Eurocode edition, National Annex, project actions, material data, geotechnical report and all applicable limit states before relying on a result for construction or approval.")


__all__ = ["EUROCODES", "MATERIALS", "DESIGN_STAGES", "render"]
