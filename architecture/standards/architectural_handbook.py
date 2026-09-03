"""Interactive architectural design handbook for the IMAGINE standards workspace.

This is a project-neutral knowledge layer. It deliberately summarizes design
principles and workflows rather than reproducing proprietary standards.
"""
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


HANDBOOK_SECTIONS: dict[str, tuple[str, ...]] = {
    "Design Basis": (
        "Project brief", "Site and climate", "Occupancy and user profile",
        "Applicable planning and building regulations", "Accessibility strategy",
        "Performance targets", "Design life and maintainability",
    ),
    "Site Planning": (
        "Plot boundaries", "Setbacks", "Access and circulation", "Parking and servicing",
        "Orientation", "Landscape and open space", "Levels and drainage", "Fire access",
    ),
    "Space Planning": (
        "Room schedule", "Net-to-gross efficiency", "Adjacencies", "Circulation",
        "Vertical circulation", "Service and core planning", "Furniture and equipment allowances",
    ),
    "Building Envelope": (
        "Daylight and openings", "Solar control", "Thermal envelope", "Moisture control",
        "Acoustics", "Fire compartmentation", "Maintenance access", "Material durability",
    ),
    "Life Safety": (
        "Occupant load", "Means of escape", "Travel distance", "Exit capacity",
        "Stairs", "Fire access", "Emergency strategy", "Refuge and accessibility",
    ),
    "Accessibility": (
        "Accessible routes", "Entrances", "Doors", "Lifts", "Sanitary facilities",
        "Ramps", "Stairs", "Wayfinding", "Controls and reach ranges",
    ),
    "Coordination": (
        "Structural grid", "MEP zones", "Ceiling and service zones", "Plant rooms",
        "BIM coordinates", "Drawing standards", "Specification coordination", "Maintenance zones",
    ),
    "Design Development": (
        "Concept options", "Developed plans", "Elevations and sections", "Schedules",
        "Material selection", "Performance review", "Authority submission", "Tender information",
    ),
}

TOPICS: dict[str, HandbookTopic] = {
    "Project brief": HandbookTopic(
        "Project brief", "Translate client objectives into measurable design requirements.",
        ("Record project type, users, capacity, operating hours and key spaces.",
         "Separate mandatory requirements from preferences and future allowances.",
         "Define functional, environmental, accessibility, fire and maintenance objectives."),
        ("Confirm area schedule and occupancy assumptions.", "Identify authority and client approval points.",
         "Record unresolved decisions and assumptions."),
        ("Brief, area schedule, room data sheets, assumptions register"),
        ("Project brief", "Applicable planning/building regulations", "Client requirements"),
    ),
    "Site Planning": HandbookTopic(
        "Site Planning", "Organize buildings, movement, landscape, servicing and site constraints.",
        ("Start from the surveyed boundary, levels, access points and known easements.",
         "Test building footprint, setbacks, parking, fire access, pedestrian movement and service access together.",
         "Coordinate finished levels and drainage strategy with civil and structural design."),
        ("Boundary and north direction confirmed.", "Setbacks and planning controls checked.",
         "Vehicle, pedestrian and emergency access coordinated.", "Levels and drainage strategy coordinated."),
        ("Site plan, access diagram, parking schedule, levels/drainage strategy"),
        ("Planning controls", "Site survey", "Local authority requirements"),
    ),
    "Space Planning": HandbookTopic(
        "Space Planning", "Convert the brief into an efficient, coordinated spatial system.",
        ("Build the room schedule before fixing the final plan.",
         "Use adjacency and circulation analysis to test functional relationships.",
         "Reserve cores, shafts, structure, plant and maintenance zones early."),
        ("Net areas reconcile with the room schedule.", "Circulation is proportionate to building use.",
         "Structural and service zones are protected.", "Furniture/equipment clearances are checked."),
        ("Room schedule, adjacency matrix, area schedule, floor plans"),
        ("Room Programming", "Floor Planning", "Accessibility requirements"),
    ),
    "Stairs": HandbookTopic(
        "Stairs", "Develop safe and coordinated vertical circulation.",
        ("Establish floor-to-floor height, required circulation capacity and available stair zone.",
         "Check riser/going proportions, flight arrangement, landings, headroom and handrail strategy against the adopted requirements.",
         "Coordinate stair geometry with structure, finishes, doors, escape routes and accessibility."),
        ("Floor-to-floor height verified.", "Riser and going checked.", "Landings and clear width checked.",
         "Headroom and guarding checked.", "Structural support and opening coordination checked."),
        ("Stair plan/section, stair schedule, structural opening, compliance checklist"),
        ("Stairs Design", "Accessibility", "Life Safety", "Structural Stairs Design"),
    ),
    "Doors and Openings": HandbookTopic(
        "Doors and Openings", "Coordinate openings for circulation, daylight, ventilation, access and structure.",
        ("Define opening function, clear width/height, swing, hardware and accessibility requirements.",
         "Coordinate openings with walls, lintels, structural frames and MEP services.",
         "Maintain a consistent opening schedule and reference system across drawings."),
        ("Opening sizes and types are scheduled.", "Door swings do not obstruct required circulation.",
         "Accessible clearances are checked.", "Lintel/structural support is coordinated."),
        ("Door/window schedule, opening drawings, lintel coordination notes"),
        ("Openings Design", "Floor Planning", "Structural Design"),
    ),
    "Daylight and Openings": HandbookTopic(
        "Daylight and Openings", "Use openings to support daylight, ventilation, views and environmental performance.",
        ("Consider orientation, room depth, glazing distribution and shading together.",
         "Balance daylight with glare, solar gain, heat loss and privacy.",
         "Coordinate window heads/sills, structure, façade drainage and maintenance access."),
        ("Primary occupied rooms have an environmental strategy.", "Solar exposure is assessed.",
         "Shading and maintenance are considered.", "Façade openings are structurally coordinated."),
        ("Opening schedule, façade studies, daylight/environmental assessment"),
        ("Building Envelope", "Energy", "Local environmental requirements"),
    ),
    "Life Safety": HandbookTopic(
        "Life Safety", "Establish an integrated strategy for safe evacuation and emergency access.",
        ("Determine occupancy and risk profile before sizing escape provisions.",
         "Develop escape routes, exits, stairs, compartmentation and emergency access as one system.",
         "Verify requirements against the authority-adopted fire and building regulations."),
        ("Occupancy assumptions documented.", "Escape routes are continuous and legible.",
         "Exit capacity and travel constraints are checked.", "Fire service access is coordinated."),
        ("Fire/life-safety plan, occupancy schedule, escape diagrams, compliance report"),
        ("Applicable fire code", "Building regulations", "Authority guidance"),
    ),
}


def _topic_data(section: str) -> list[HandbookTopic]:
    result: list[HandbookTopic] = []
    for name in HANDBOOK_SECTIONS[section]:
        if name in TOPICS:
            result.append(TOPICS[name])
    return result


def _render_topic(topic: HandbookTopic) -> None:
    st.markdown(f"## {topic.name}")
    st.caption(topic.purpose)
    left, right = st.columns(2)
    with left:
        st.markdown("### Design guidance")
        for item in topic.guidance:
            st.markdown(f"- {item}")
    with right:
        st.markdown("### Review checklist")
        for item in topic.checks:
            st.checkbox(item, key=f"arch_handbook_check_{topic.name}_{item}")
    st.markdown("### Typical deliverables")
    st.dataframe(pd.DataFrame({"Deliverable": topic.deliverables}), use_container_width=True, hide_index=True)
    st.markdown("### Reference trail")
    st.dataframe(pd.DataFrame({"Reference": topic.references}), use_container_width=True, hide_index=True)


def render_architectural_handbook() -> None:
    st.title("Architectural Design Handbook")
    st.caption(
        "Interactive architectural knowledge workspace covering briefing, site planning, space planning, envelope, life safety, accessibility and coordination."
    )

    section = st.selectbox("Handbook section", list(HANDBOOK_SECTIONS), key="architectural_handbook_section")
    topics = HANDBOOK_SECTIONS[section]
    topic_name = st.selectbox("Topic", topics, key="architectural_handbook_topic")

    k1, k2, k3 = st.columns(3)
    k1.metric("Section topics", len(topics))
    k2.metric("Detailed topics", len(_topic_data(section)))
    k3.metric("Reference mode", "Guidance")

    _render_topic(TOPICS.get(topic_name, HandbookTopic(
        topic_name,
        "Project-specific design topic requiring project data and adopted requirements.",
        ("Define the project criteria before applying dimensional or performance requirements.",
         "Coordinate architecture with structure, MEP, fire, accessibility and construction.",
         "Record assumptions so later design reviews can trace decisions."),
        ("Requirement identified.", "Design checked against project criteria.", "Specialist coordination completed."),
        ("Design drawings", "Schedules", "Compliance/check record"),
        ("Project brief", "Applicable regulations", "Authority guidance"),
    )))

    st.divider()
    st.subheader("Architecture workflow")
    workflow = [
        "Brief → Site → Zoning → Program → Floor Planning → Compliance → Generative Options → Structural/MEP Handoff",
    ]
    st.info(workflow[0])
    st.warning(
        "This handbook is a design-management and educational aid. It does not reproduce proprietary standards and does not replace statutory requirements, authority guidance, project specifications or professional review."
    )


__all__ = ["HANDBOOK_SECTIONS", "TOPICS", "HandbookTopic", "render_architectural_handbook"]
