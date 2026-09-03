"""Interactive structural design handbook and Eurocode family navigator.

The handbook is an educational engineering reference layer. It summarizes
scope, design intent, workflow and review prompts without reproducing
copyrighted standard text. Numerical design provisions must come from the
adopted edition, National Annex, project specification and verified engineering
calculations.
"""
from __future__ import annotations
from dataclasses import dataclass
import pandas as pd
import streamlit as st

@dataclass(frozen=True)
class DesignTopic:
    code: str
    title: str
    scope: str
    guidance: tuple[str, ...]
    checks: tuple[str, ...]
    outputs: tuple[str, ...]
    linked_tools: tuple[str, ...]

EUROCODES = [
    ("EN 1990", "Basis of structural design", "Reliability, limit states, design situations, actions and combinations."),
    ("EN 1991", "Actions on structures", "Permanent, imposed, snow, wind, thermal, accidental, traffic and execution actions."),
    ("EN 1992", "Design of concrete structures", "Reinforced and prestressed concrete, durability, detailing, fire and special structures."),
    ("EN 1993", "Design of steel structures", "Steel members, stability, connections, fatigue, shells and fire design."),
    ("EN 1994", "Design of composite steel and concrete structures", "Composite beams, slabs, columns, frames and construction-stage effects."),
    ("EN 1995", "Design of timber structures", "Solid and engineered timber, joints, stability, serviceability and fire."),
    ("EN 1996", "Design of masonry structures", "Unreinforced/reinforced masonry, stability, lateral actions, detailing and fire."),
    ("EN 1997", "Geotechnical design", "Ground investigation, foundations, retaining structures, slopes and geotechnical limit states."),
    ("EN 1998", "Design for earthquake resistance", "Seismic actions, analysis, ductility, detailing and earthquake-resistant foundations."),
    ("EN 1999", "Design of aluminium structures", "Aluminium resistance, stability, connections, fatigue and fire considerations."),
]

MATERIALS = [
    ("Concrete", "C20/25 to high-strength classes", "Strength, stiffness, density, durability/exposure, creep and shrinkage."),
    ("Reinforcing steel", "B500 family", "Characteristic strength, ductility, anchorage, laps and detailing."),
    ("Structural steel", "S235 / S275 / S355 / S460", "Strength, thickness effects, toughness, stability and weldability."),
    ("Timber", "C14 / C16 / C18 / C24 / C30", "Strength class, stiffness, density, service class and load-duration effects."),
    ("Engineered timber", "Glulam / LVL / CLT", "Product-specific strength, stiffness, connection and fire data."),
    ("Masonry", "Units, mortar and grout", "Unit strength, mortar class, characteristic masonry strength and execution."),
    ("Aluminium", "Alloy and temper dependent", "Alloy strength, thickness, buckling, welding and connection behaviour."),
    ("Composite", "Steel + concrete system", "Steel, concrete, shear connection and construction-stage compatibility."),
    ("Soil / rock", "Geotechnical materials", "Unit weight, effective strength, stiffness, groundwater and investigation data."),
]

DESIGN_STAGES = [
    "Project brief and structural design basis", "Structural system and load-path selection",
    "Actions and tributary areas", "EN 1990 combinations and design situations",
    "EN 1991 action assessment", "Material and member design",
    "Global analysis, stability and second-order effects", "Serviceability, durability and robustness",
    "Connections, anchorage and detailing", "Foundation and ground interaction",
    "Seismic, accidental and fire checks where applicable", "Drawings, schedules, specifications and independent verification",
]

TOPICS = {
    "EN 1990": DesignTopic("EN 1990", "Basis of structural design", EUROCODES[0][2],
        ("Define design situations, limit states, reliability assumptions and the adopted National Annex.", "Separate permanent, variable and accidental actions before forming combinations.", "Identify governing ULS and SLS cases and retain traceable combination names."),
        ("Design situations documented.", "ULS combinations reviewed.", "SLS combinations reviewed.", "Governing effects recorded."),
        ("Design basis", "Load combination schedule", "Governing action table"), ("EC0 Load Combinations", "Structural Analysis")),
    "EN 1991": DesignTopic("EN 1991", "Actions on structures", EUROCODES[1][2],
        ("Build an action register for self-weight, imposed actions, environmental actions and project-specific effects.", "Trace area loads into line loads and member actions using the actual load path.", "Use project location, geometry and adopted National Annex data for environmental actions."),
        ("Action sources identified.", "Load areas documented.", "Wind/snow/thermal effects considered where applicable.", "Execution actions considered where relevant."),
        ("Action register", "Load take-off", "Load-path diagram", "Combination inputs"), ("EC1 Actions", "Beam Design", "Structural Analysis")),
    "EN 1992": DesignTopic("EN 1992", "Design of concrete structures", EUROCODES[2][2],
        ("Establish concrete and reinforcement properties, exposure/durability requirements and member geometry.", "Check resistance and serviceability using the adopted concrete design model and detailing rules.", "Coordinate reinforcement, anchorage, openings, construction joints and fire requirements."),
        ("Materials and exposure class established.", "ULS resistance checked.", "Deflection/cracking reviewed where required.", "Reinforcement detailing coordinated."),
        ("Beam/column/slab/foundation calculations", "Reinforcement schedule", "Design notes"), ("Beam Design", "Column Design", "Slab Design", "Foundation Design", "Punching Shear")),
    "EN 1993": DesignTopic("EN 1993", "Design of steel structures", EUROCODES[3][2],
        ("Define steel grade, cross-section, restraint, buckling lengths and connection assumptions.", "Check cross-section resistance, member stability and relevant interaction effects.", "Coordinate connections, fabrication, corrosion protection, fire and erection conditions."),
        ("Section classification considered.", "Buckling restraints documented.", "Member resistance checked.", "Connections and erection conditions coordinated."),
        ("Steel member schedule", "Connection design", "Stability notes", "Fabrication information"), ("Steel Members", "Steel Connections", "Section Shapes")),
    "EN 1994": DesignTopic("EN 1994", "Composite structures", EUROCODES[4][2],
        ("Define steel and concrete components, effective interaction and construction sequence.", "Consider composite action, construction-stage effects and serviceability.", "Coordinate deck/slab reinforcement, connectors, beams and temporary works."),
        ("Construction stage defined.", "Composite interaction assumptions documented.", "Shear connection checked.", "Deflection and cracking reviewed."),
        ("Composite design basis", "Connector schedule", "Construction-stage checks"), ("Steel Members", "Slab Design", "Structural Analysis")),
    "EN 1995": DesignTopic("EN 1995", "Design of timber structures", EUROCODES[5][2],
        ("Establish timber product, strength class, service class and load-duration assumptions.", "Check bending, shear, compression/tension, stability and connection behaviour.", "Account for moisture, fire, durability, creep and construction details."),
        ("Product properties verified.", "Service class established.", "Stability checked.", "Connections and moisture protection coordinated."),
        ("Timber member schedule", "Connection notes", "Roof structure calculations"), ("Roof Design", "Building Materials")),
    "EN 1996": DesignTopic("EN 1996", "Design of masonry structures", EUROCODES[6][2],
        ("Define masonry unit, mortar, workmanship and characteristic strength.", "Trace vertical and lateral actions through walls, piers, floors and foundations.", "Check slenderness, stability, openings, support conditions and detailing."),
        ("Masonry properties verified.", "Wall slenderness checked.", "Openings/lintels coordinated.", "Support conditions verified."),
        ("Masonry wall schedule", "Lintel coordination", "Stability checks"), ("Openings Design", "Building Materials")),
    "EN 1997": DesignTopic("EN 1997", "Geotechnical design", EUROCODES[7][2],
        ("Use the ground investigation and establish soil/rock parameters, groundwater and geotechnical design approach.", "Separate geotechnical and structural actions and verify the relevant limit states.", "Coordinate foundation, retaining-wall, excavation and drainage assumptions with the geotechnical report."),
        ("Ground model documented.", "Design parameters traceable.", "Bearing/sliding/overturning checks considered where applicable.", "Groundwater addressed."),
        ("Foundation design basis", "Retaining-wall calculations", "Geotechnical assumptions register"), ("Foundation Design", "Retaining Walls")),
    "EN 1998": DesignTopic("EN 1998", "Earthquake resistance", EUROCODES[8][2],
        ("Establish seismic hazard, importance, soil conditions, structural system and ductility assumptions.", "Select an analysis approach appropriate to the structure and adopted code provisions.", "Coordinate ductility, capacity design, diaphragms, foundations and non-structural elements."),
        ("Seismic parameters verified.", "Structural regularity assessed.", "Analysis method justified.", "Ductile detailing requirements coordinated."),
        ("Seismic design basis", "Storey force distribution", "Analysis results", "Detailing notes"), ("Structural Analysis", "Foundation Design")),
    "EN 1999": DesignTopic("EN 1999", "Aluminium structures", EUROCODES[9][2],
        ("Identify alloy, temper, product form and connection method before design.", "Consider reduced stiffness, buckling, local effects, fatigue and connection behaviour.", "Coordinate fabrication, corrosion environment, dissimilar-metal interfaces and fire assumptions."),
        ("Alloy/product data verified.", "Stability considered.", "Connections checked.", "Durability/interface conditions addressed."),
        ("Aluminium member schedule", "Connection design basis", "Durability notes"), ("Building Materials", "Section Shapes")),
}

def _render_topic(topic: DesignTopic) -> None:
    st.markdown(f"## {topic.code} · {topic.title}")
    st.caption(topic.scope)
    left, right = st.columns(2)
    with left:
        st.markdown("### Design guidance")
        for item in topic.guidance: st.markdown(f"- {item}")
    with right:
        st.markdown("### Review checklist")
        for item in topic.checks: st.checkbox(item, key=f"struct_handbook_{topic.code}_{item}")
    st.markdown("### Typical outputs")
    st.dataframe(pd.DataFrame({"Output": topic.outputs}), use_container_width=True, hide_index=True)
    st.markdown("### Linked IMAGINE workspaces")
    st.dataframe(pd.DataFrame({"Workspace": topic.linked_tools}), use_container_width=True, hide_index=True)

def render() -> None:
    st.title("Structural Design Handbook")
    st.caption("Interactive structural knowledge workspace covering EN 1990 to EN 1999, materials, design workflow, member design and engineering review.")
    tabs = st.tabs(["Eurocode Family", "Building Materials", "Design Workflow", "Design Topics"])
    with tabs[0]:
        st.subheader("Eurocode family navigator")
        st.dataframe(pd.DataFrame(EUROCODES, columns=["Code", "Title", "Primary scope"]), use_container_width=True, hide_index=True)
        selected = st.selectbox("Open code workspace", [row[0] for row in EUROCODES], key="structural_handbook_code")
        _render_topic(TOPICS[selected])
    with tabs[1]:
        st.subheader("Building materials")
        st.dataframe(pd.DataFrame(MATERIALS, columns=["Material", "Typical classes / family", "Design data to establish"]), use_container_width=True, hide_index=True)
        selected_material = st.selectbox("Material reference", [row[0] for row in MATERIALS], key="structural_handbook_material")
        row = next(item for item in MATERIALS if item[0] == selected_material)
        a, b = st.columns(2); a.metric("Material family", row[0]); b.metric("Reference class", row[1])
        st.markdown("### Design data to establish"); st.write(row[2])
        st.warning("Material properties are project/product dependent. Use manufacturer declarations, material certificates, test data and the adopted design standard for final values.")
    with tabs[2]:
        st.subheader("Structural design workflow")
        st.dataframe(pd.DataFrame({"Stage": range(1, len(DESIGN_STAGES) + 1), "Activity": DESIGN_STAGES}), use_container_width=True, hide_index=True)
        st.info("Core load path: Architecture → actions → combinations → analysis → member design → connections → foundations → detailing → verification.")
    with tabs[3]:
        selected_topic = st.selectbox("Design topic", list(TOPICS), key="structural_handbook_topic")
        _render_topic(TOPICS[selected_topic])
    st.warning("IMAGINE structural handbook content is a preliminary engineering knowledge aid. Confirm the adopted Eurocode edition, National Annex, project actions, material data, geotechnical report, fire/seismic requirements and all applicable limit states before relying on a result for construction or approval. Independent professional verification remains required.")

__all__ = ["EUROCODES", "MATERIALS", "DESIGN_STAGES", "TOPICS", "DesignTopic", "render"]
