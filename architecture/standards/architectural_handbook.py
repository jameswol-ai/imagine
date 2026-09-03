"""Interactive architectural design handbook for the IMAGINE standards workspace."""
from __future__ import annotations
from dataclasses import dataclass
import pandas as pd
import streamlit as st

@dataclass(frozen=True)
class HandbookTopic:
    name: str
    purpose: str
    guidance: tuple[str, ...]
    checks: tuple[str, ...]
    deliverables: tuple[str, ...]
    references: tuple[str, ...]

HANDBOOK_SECTIONS = {
    "Design Basis": ("Project brief", "Site and climate", "Occupancy and user profile", "Planning and building regulations", "Accessibility strategy", "Performance targets", "Design life and maintainability"),
    "Site Planning": ("Plot boundaries", "Setbacks", "Access and circulation", "Parking and servicing", "Orientation", "Landscape and open space", "Levels and drainage", "Fire access"),
    "Space Planning": ("Room schedule", "Net-to-gross efficiency", "Adjacencies", "Circulation", "Vertical circulation", "Service and core planning", "Furniture and equipment allowances"),
    "Building Envelope": ("Daylight and openings", "Solar control", "Thermal envelope", "Moisture control", "Acoustics", "Fire compartmentation", "Maintenance access", "Material durability"),
    "Life Safety": ("Occupant load", "Means of escape", "Travel distance", "Exit capacity", "Stairs", "Fire access", "Emergency strategy", "Refuge and accessibility"),
    "Accessibility": ("Accessible routes", "Entrances", "Doors", "Lifts", "Sanitary facilities", "Ramps", "Stairs", "Wayfinding", "Controls and reach ranges"),
    "Coordination": ("Structural grid", "MEP zones", "Ceiling and service zones", "Plant rooms", "BIM coordinates", "Drawing standards", "Specification coordination", "Maintenance zones"),
    "Design Development": ("Concept options", "Developed plans", "Elevations and sections", "Schedules", "Material selection", "Performance review", "Authority submission", "Tender information"),
}

TOPICS = {
    "Project brief": HandbookTopic("Project brief", "Translate client objectives into measurable design requirements.", ("Record project type, users, capacity, operating hours and key spaces.", "Separate mandatory requirements from preferences and future allowances.", "Define functional, environmental, accessibility, fire and maintenance objectives."), ("Confirm area schedule and occupancy assumptions.", "Identify authority and client approval points.", "Record unresolved decisions and assumptions."), ("Brief", "Area schedule", "Room data sheets", "Assumptions register"), ("Client requirements", "Project brief", "Applicable regulations")),
    "Site and climate": HandbookTopic("Site and climate", "Establish the physical and environmental conditions that shape the building.", ("Record boundary, survey levels, orientation, climate, access, utilities, hazards and neighbouring context.", "Use sun, wind, rainfall, heat, humidity and local environmental conditions to guide orientation and envelope strategy.", "Identify site constraints early and carry them into planning, drainage, landscape and structural decisions."), ("Survey data verified.", "North/orientation confirmed.", "Climate/environmental assumptions recorded.", "Utilities, hazards and access constraints coordinated."), ("Site analysis", "Climate summary", "Constraints plan", "Site response diagram"), ("Site survey", "Climate data", "Planning controls")),
    "Plot boundaries": HandbookTopic("Plot boundaries", "Establish the legal and surveyed limits for development.", ("Use a current survey and distinguish surveyed boundaries from assumed cadastral information.", "Record easements, rights of way, neighbouring conditions and site constraints.", "Coordinate the boundary with setbacks, access, landscape and drainage."), ("Boundary verified.", "Easements identified.", "Survey reference retained."), ("Boundary plan", "Site constraints register"), ("Survey", "Land/title information", "Planning requirements")),
    "Room schedule": HandbookTopic("Room schedule", "Convert functional requirements into a traceable area and capacity schedule.", ("Define room function, occupancy, target area, equipment, furniture and environmental needs.", "Track net area, grossing factors and future allowances.", "Keep room identifiers consistent across plans, BIM and schedules."), ("All required spaces are listed.", "Areas reconcile.", "Occupancy/capacity is documented.", "Equipment and clearance needs are captured."), ("Room schedule", "Room data sheets", "Area reconciliation"), ("Project brief", "Space standards", "Client requirements")),
    "Stairs": HandbookTopic("Stairs", "Develop safe and coordinated vertical circulation.", ("Establish floor-to-floor height, circulation capacity and available stair zone.", "Check riser/going proportions, flights, landings, headroom, handrails and guarding against adopted requirements.", "Coordinate geometry with structure, finishes, doors, escape routes and accessibility."), ("Floor-to-floor height verified.", "Riser and going checked.", "Landings and clear width checked.", "Headroom and guarding checked.", "Structural opening coordinated."), ("Stair plan/section", "Stair schedule", "Structural opening", "Compliance checklist"), ("Stairs Design", "Accessibility", "Life Safety", "Structural Stairs Design")),
    "Doors and Openings": HandbookTopic("Doors and Openings", "Coordinate openings for circulation, daylight, ventilation, access and structure.", ("Define opening function, clear width/height, swing, hardware and accessibility requirements.", "Coordinate openings with walls, lintels, structural frames and MEP services.", "Maintain a consistent opening schedule and reference system."), ("Opening sizes/types scheduled.", "Door swings coordinated.", "Accessible clearances checked.", "Lintel/support coordinated."), ("Door/window schedule", "Opening drawings", "Lintel coordination notes"), ("Openings Design", "Floor Planning", "Structural Design")),
    "Daylight and Openings": HandbookTopic("Daylight and Openings", "Use openings to support daylight, ventilation, views and environmental performance.", ("Consider orientation, room depth, glazing distribution and shading together.", "Balance daylight with glare, solar gain, heat loss and privacy.", "Coordinate window heads/sills, structure, façade drainage and maintenance access."), ("Occupied rooms have an environmental strategy.", "Solar exposure assessed.", "Shading and maintenance considered.", "Façade openings structurally coordinated."), ("Opening schedule", "Façade studies", "Daylight/environmental assessment"), ("Building Envelope", "Energy", "Local requirements")),
    "Life Safety": HandbookTopic("Life Safety", "Establish an integrated strategy for safe evacuation and emergency access.", ("Determine occupancy and risk profile before sizing escape provisions.", "Develop routes, exits, stairs, compartmentation and emergency access as one system.", "Verify requirements against the authority-adopted fire and building regulations."), ("Occupancy documented.", "Escape routes continuous.", "Exit capacity and travel constraints checked.", "Fire service access coordinated."), ("Fire/life-safety plan", "Occupancy schedule", "Escape diagrams", "Compliance report"), ("Applicable fire code", "Building regulations", "Authority guidance")),
}

for name in [n for values in HANDBOOK_SECTIONS.values() for n in values]:
    if name not in TOPICS:
        TOPICS[name] = HandbookTopic(name, "Project-specific architectural design topic requiring project data and adopted requirements.", ("Define the project criteria before applying dimensional or performance requirements.", "Coordinate architecture with structure, MEP, fire, accessibility and construction.", "Record assumptions so later reviews can trace decisions."), ("Requirement identified.", "Design checked against project criteria.", "Specialist coordination completed."), ("Design drawings", "Schedules", "Compliance/check record"), ("Project brief", "Applicable regulations", "Authority guidance"))

def _render_topic(topic: HandbookTopic) -> None:
    st.markdown(f"## {topic.name}")
    st.caption(topic.purpose)
    left, right = st.columns(2)
    with left:
        st.markdown("### Design guidance")
        for item in topic.guidance: st.markdown(f"- {item}")
    with right:
        st.markdown("### Review checklist")
        for item in topic.checks: st.checkbox(item, key=f"arch_handbook_check_{topic.name}_{item}")
    st.markdown("### Typical deliverables")
    st.dataframe(pd.DataFrame({"Deliverable": topic.deliverables}), use_container_width=True, hide_index=True)
    st.markdown("### Reference trail")
    st.dataframe(pd.DataFrame({"Reference": topic.references}), use_container_width=True, hide_index=True)

def render_architectural_handbook() -> None:
    st.title("Architectural Design Handbook")
    st.caption("Interactive architectural knowledge workspace covering briefing, site, planning, space, envelope, life safety, accessibility and coordination.")
    section = st.selectbox("Handbook section", list(HANDBOOK_SECTIONS), key="architectural_handbook_section")
    topics = HANDBOOK_SECTIONS[section]
    topic_name = st.selectbox("Topic", topics, key="architectural_handbook_topic")
    k1, k2, k3 = st.columns(3)
    k1.metric("Section topics", len(topics)); k2.metric("Detailed topics", len([n for n in topics if n in TOPICS])); k3.metric("Reference mode", "Guidance")
    _render_topic(TOPICS[topic_name])
    st.divider()
    st.subheader("Architecture workflow")
    st.info("Brief → Site → Zoning → Program → Floor Planning → Compliance → Generative Options → Structural/MEP Handoff")
    st.warning("This handbook is a design-management and educational aid. It does not replace statutory requirements, authority guidance, project specifications or professional review.")

__all__ = ["HANDBOOK_SECTIONS", "TOPICS", "HandbookTopic", "render_architectural_handbook"]
