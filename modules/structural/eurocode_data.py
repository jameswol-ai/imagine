"""Structured Eurocode knowledge catalog for IMAGINE.

This file intentionally stores metadata, scope, parts, design topics, inputs,
outputs and implementation status rather than reproducing copyrighted standard
text. It is designed to drive navigation, checklists, calculators and future
clause-level integrations.

Always verify the adopted edition, corrigenda, National Annex and project
requirements against the authoritative standard before engineering use.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EurocodePart:
    code: str
    title: str
    scope: str
    topics: tuple[str, ...]
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    linked_tools: tuple[str, ...]


EUROCODE_FAMILY: dict[str, dict[str, object]] = {
    "EN 1990": {
        "title": "Basis of structural design",
        "parts": ("EN 1990",),
        "topics": ("reliability", "design situations", "limit states", "actions", "combinations", "serviceability", "robustness", "execution", "assessment"),
    },
    "EN 1991": {
        "title": "Actions on structures",
        "parts": ("EN 1991-1-1", "EN 1991-1-2", "EN 1991-1-3", "EN 1991-1-4", "EN 1991-1-5", "EN 1991-1-6", "EN 1991-1-7", "EN 1991-1-1", "EN 1991-2", "EN 1991-1-3", "EN 1991-1-4"),
        "topics": ("densities", "self-weight", "imposed loads", "fire", "snow", "wind", "thermal actions", "execution", "accidental actions", "traffic loads", "bridges"),
    },
    "EN 1992": {
        "title": "Design of concrete structures",
        "parts": ("EN 1992-1-1", "EN 1992-1-2", "EN 1992-2", "EN 1992-3", "EN 1992-4"),
        "topics": ("materials", "durability", "flexure", "shear", "torsion", "compression", "tension", "cracking", "deflection", "detailing", "fire", "prestressing", "bridges", "liquid-retaining structures", "fastenings"),
    },
    "EN 1993": {
        "title": "Design of steel structures",
        "parts": ("EN 1993-1-1", "EN 1993-1-2", "EN 1993-1-3", "EN 1993-1-4", "EN 1993-1-5", "EN 1993-1-6", "EN 1993-1-7", "EN 1993-1-8", "EN 1993-1-9", "EN 1993-1-10", "EN 1993-1-11", "EN 1993-2", "EN 1993-3-1", "EN 1993-3-2", "EN 1993-4-1", "EN 1993-4-2", "EN 1993-4-3", "EN 1993-5", "EN 1993-6"),
        "topics": ("cross-sections", "member resistance", "buckling", "lateral torsional buckling", "connections", "welding", "bolting", "fatigue", "fracture toughness", "stainless steel", "cold-formed members", "shells", "towers", "masts", "chimneys", "cranes", "storage tanks", "piles", "supporting structures"),
    },
    "EN 1994": {
        "title": "Design of composite steel and concrete structures",
        "parts": ("EN 1994-1-1", "EN 1994-1-2", "EN 1994-2"),
        "topics": ("composite beams", "composite slabs", "composite columns", "frames", "shear connection", "construction stages", "fire", "bridges"),
    },
    "EN 1995": {
        "title": "Design of timber structures",
        "parts": ("EN 1995-1-1", "EN 1995-1-2", "EN 1995-2"),
        "topics": ("solid timber", "glulam", "LVL", "CLT", "bending", "shear", "compression", "tension", "stability", "connections", "serviceability", "fire", "bridges"),
    },
    "EN 1996": {
        "title": "Design of masonry structures",
        "parts": ("EN 1996-1-1", "EN 1996-1-2", "EN 1996-2", "EN 1996-3"),
        "topics": ("masonry materials", "compressive strength", "walls", "piers", "slenderness", "lateral loads", "openings", "connections", "execution", "fire", "simplified design"),
    },
    "EN 1997": {
        "title": "Geotechnical design",
        "parts": ("EN 1997-1", "EN 1997-2"),
        "topics": ("ground investigation", "geotechnical parameters", "limit states", "bearing resistance", "settlement", "sliding", "overturning", "retaining structures", "slopes", "anchors", "piles", "groundwater", "testing"),
    },
    "EN 1998": {
        "title": "Design for earthquake resistance",
        "parts": ("EN 1998-1", "EN 1998-2", "EN 1998-3", "EN 1998-4", "EN 1998-5", "EN 1998-6"),
        "topics": ("seismic hazard", "response spectra", "ground conditions", "regularity", "modal analysis", "equivalent static analysis", "ductility", "capacity design", "reinforced concrete", "steel", "masonry", "bridges", "tanks", "pipelines", "foundations", "towers"),
    },
    "EN 1999": {
        "title": "Design of aluminium structures",
        "parts": ("EN 1999-1-1", "EN 1999-1-2", "EN 1999-1-3", "EN 1999-1-4", "EN 1999-1-5", "EN 1999-1-1"),
        "topics": ("alloys", "cross-sections", "member resistance", "buckling", "welding", "bolted connections", "fatigue", "cold-formed products", "shells", "fire", "fracture"),
    },
}


PARTS: tuple[EurocodePart, ...] = (
    EurocodePart("EN 1990", "Basis of structural design", "Reliability, design situations and limit-state verification.", ("design basis", "ULS", "SLS", "combinations", "robustness"), ("actions", "combination factors", "partial factors", "design situation"), ("governing combinations", "design effects", "verification basis"), ("Load Combinations", "Structural Analysis")),
    EurocodePart("EN 1991-1-1", "Densities, self-weight and imposed loads", "General actions for buildings.", ("densities", "self-weight", "imposed floor loads", "roofs", "areas"), ("material density", "geometry", "occupancy category"), ("permanent load", "imposed load"), ("Load Combinations", "Structural Analysis")),
    EurocodePart("EN 1991-1-2", "Actions on structures exposed to fire", "Thermal actions and fire design basis.", ("nominal fires", "thermal actions", "gas temperatures", "fire exposure"), ("fire scenario", "exposure", "duration"), ("thermal action", "fire design inputs"), ("Structural Analysis")),
    EurocodePart("EN 1991-1-3", "Snow loads", "Snow actions on buildings and structures.", ("ground snow", "roof snow", "drifting", "exceptional snow"), ("location", "altitude", "roof geometry", "snow coefficients"), ("snow load", "roof load cases"), ("Wind Actions", "Structural Analysis")),
    EurocodePart("EN 1991-1-4", "Wind actions", "Wind actions on structures.", ("basic wind velocity", "exposure", "terrain", "pressure", "force coefficients", "dynamic effects"), ("location", "wind velocity", "terrain", "height", "geometry", "coefficients"), ("velocity pressure", "surface pressure", "member load"), ("Wind Actions", "Structural Analysis")),
    EurocodePart("EN 1991-1-5", "Thermal actions", "Thermal effects in structures.", ("temperature profiles", "uniform temperature", "temperature differences", "restraint"), ("climate", "material", "geometry", "temperature range"), ("thermal strain", "thermal action"), ("Structural Analysis")),
    EurocodePart("EN 1991-1-6", "Actions during execution", "Actions and design situations during construction.", ("construction loads", "temporary conditions", "execution stages"), ("construction sequence", "temporary works", "equipment"), ("execution load cases", "temporary combinations"), ("Construction", "Structural Analysis")),
    EurocodePart("EN 1991-1-7", "Accidental actions", "Accidental and robustness-related actions.", ("impact", "explosion", "local damage", "robustness"), ("hazard", "scenario", "consequence class"), ("accidental load case", "robustness checks"), ("Structural Analysis")),
    EurocodePart("EN 1991-2", "Traffic loads on bridges", "Traffic actions for road and rail bridge structures.", ("road traffic", "rail traffic", "pedestrian loads", "dynamic effects"), ("bridge geometry", "traffic model", "lanes", "dynamic factor"), ("traffic load models", "design effects"), ("Structural Analysis")),
    EurocodePart("EN 1992-1-1", "Concrete structures: general rules and buildings", "General rules for reinforced and prestressed concrete structures.", ("materials", "durability", "ULS", "SLS", "flexure", "shear", "torsion", "compression", "detailing", "anchorage", "laps"), ("concrete class", "reinforcement", "geometry", "loads", "cover", "exposure"), ("required reinforcement", "resistance", "crack/deflection checks", "detailing schedule"), ("Beam Design", "Column Design", "Slab Design", "RC Detailing")),
    EurocodePart("EN 1992-1-2", "Concrete structures: structural fire design", "Fire resistance of concrete structures.", ("thermal properties", "fire exposure", "member resistance", "spalling", "detailing"), ("fire duration", "section", "materials", "restraint"), ("fire resistance", "temperature effects"), ("Structural Analysis", "RC Detailing")),
    EurocodePart("EN 1992-2", "Concrete bridges", "Concrete bridge design provisions.", ("deck systems", "prestressing", "fatigue", "serviceability", "detailing"), ("bridge geometry", "traffic actions", "materials"), ("bridge member design", "fatigue checks"), ("Structural Analysis")),
    EurocodePart("EN 1992-3", "Liquid retaining and containment structures", "Concrete structures retaining liquids or granular materials.", ("watertightness", "cracking", "restraint", "durability"), ("liquid level", "exposure", "geometry", "restraint"), ("crack control", "reinforcement", "wall/slab design"), ("Slab Design", "Foundation Design")),
    EurocodePart("EN 1992-4", "Fastening for use in concrete", "Design of fastenings in concrete.", ("anchors", "tension", "shear", "concrete breakout", "edge effects"), ("anchor type", "concrete", "edge distance", "loads"), ("anchor resistance", "utilisation"), ("Steel Connections")),
    EurocodePart("EN 1993-1-1", "Steel structures: general rules", "General rules for structural steel members and frames.", ("cross-section classification", "tension", "compression", "bending", "shear", "buckling", "interaction"), ("steel grade", "section", "length", "restraint", "loads"), ("member resistance", "buckling resistance", "utilisation"), ("Steel Members", "Section Shapes")),
    EurocodePart("EN 1993-1-2", "Steel structures: structural fire design", "Fire design of steel structures.", ("thermal analysis", "temperature", "reduced properties", "fire resistance"), ("fire exposure", "section factor", "protection", "loads"), ("steel temperature", "fire resistance"), ("Steel Members")),
    EurocodePart("EN 1993-1-3", "Cold-formed thin-gauge members", "Cold-formed and sheeting products.", ("local buckling", "distortional effects", "effective widths", "connections"), ("thickness", "section geometry", "material", "restraint"), ("effective section", "member resistance"), ("Steel Members", "Section Shapes")),
    EurocodePart("EN 1993-1-5", "Plated structural elements", "Buckling and resistance of plated elements.", ("plate buckling", "shear buckling", "stiffeners", "effective widths"), ("plate dimensions", "thickness", "stiffeners", "stress pattern"), ("plate resistance", "stability checks"), ("Steel Members")),
    EurocodePart("EN 1993-1-8", "Design of joints", "Structural steel connection design.", ("bolts", "welds", "component method", "joint resistance", "stiffness"), ("bolt grade", "weld size", "plate geometry", "loads"), ("connection resistance", "bolt/weld schedule", "utilisation"), ("Steel Connections")),
    EurocodePart("EN 1993-1-9", "Fatigue", "Fatigue assessment of steel structures.", ("stress ranges", "detail categories", "cycles", "fatigue damage"), ("load spectrum", "detail category", "cycles", "stress range"), ("fatigue resistance", "damage ratio"), ("Steel Members", "Steel Connections")),
    EurocodePart("EN 1993-1-10", "Material toughness", "Material selection for fracture toughness and through-thickness properties.", ("toughness", "thickness", "temperature", "lamellar tearing"), ("steel grade", "thickness", "temperature", "stress"), ("material selection check", "toughness requirement"), ("Building Materials")),
    EurocodePart("EN 1993-1-11", "Tension components", "Design of tension components and cables.", ("cables", "tension members", "connections", "fatigue"), ("tension", "geometry", "material", "connection"), ("tension resistance", "connection check"), ("Steel Members", "Steel Connections")),
    EurocodePart("EN 1994-1-1", "Composite structures: general rules", "Composite steel-concrete buildings.", ("composite beams", "slabs", "columns", "shear connection", "construction stages"), ("steel section", "concrete slab", "connectors", "loads", "construction sequence"), ("composite resistance", "connector requirement", "deflection"), ("Steel Members", "Slab Design")),
    EurocodePart("EN 1994-1-2", "Composite structures: fire design", "Fire design of composite members.", ("temperature", "fire resistance", "reduced properties", "protection"), ("fire exposure", "materials", "section", "protection"), ("fire resistance", "temperature"), ("Structural Analysis")),
    EurocodePart("EN 1994-2", "Composite bridges", "Composite steel-concrete bridges.", ("deck", "girders", "shear connection", "fatigue", "construction"), ("traffic actions", "geometry", "materials", "construction sequence"), ("bridge member design", "fatigue checks"), ("Structural Analysis")),
    EurocodePart("EN 1995-1-1", "Timber structures: general rules", "Timber building structures.", ("strength classes", "bending", "shear", "compression", "stability", "connections", "serviceability"), ("timber grade", "service class", "load duration", "geometry", "loads"), ("member resistance", "connection resistance", "deflection"), ("Roof Design", "Building Materials")),
    EurocodePart("EN 1995-1-2", "Timber structures: fire design", "Fire design of timber structures.", ("charring", "reduced section", "fire resistance", "connections"), ("fire exposure", "section", "protection", "material"), ("fire resistance", "residual section"), ("Roof Design")),
    EurocodePart("EN 1995-2", "Timber bridges", "Timber bridge structures.", ("bridge members", "connections", "fatigue", "serviceability"), ("traffic actions", "timber properties", "geometry"), ("bridge member design", "serviceability checks"), ("Structural Analysis")),
    EurocodePart("EN 1996-1-1", "Masonry structures: general rules", "General design of reinforced and unreinforced masonry.", ("compressive resistance", "shear", "lateral loads", "slenderness", "walls", "piers"), ("unit strength", "mortar", "wall geometry", "loads", "restraint"), ("wall resistance", "stability", "reinforcement"), ("Openings Design", "Building Materials")),
    EurocodePart("EN 1996-1-2", "Masonry structures: fire design", "Fire design of masonry.", ("fire resistance", "thermal exposure", "walls", "partitions"), ("wall type", "thickness", "fire exposure"), ("fire resistance"), ("Openings Design")),
    EurocodePart("EN 1996-2", "Masonry: materials and execution", "Selection of materials and execution principles.", ("units", "mortar", "workmanship", "movement", "durability"), ("unit type", "mortar", "exposure", "execution class"), ("material specification", "execution requirements"), ("Building Materials", "Construction")),
    EurocodePart("EN 1996-3", "Masonry: simplified calculation methods", "Simplified design approaches for selected masonry structures.", ("simplified resistance", "walls", "piers", "loads"), ("geometry", "material", "load case"), ("simplified resistance", "utilisation"), ("Openings Design")),
    EurocodePart("EN 1997-1", "Geotechnical design: general rules", "Geotechnical design principles and limit states.", ("ground model", "bearing", "sliding", "overturning", "piles", "retaining", "slopes"), ("soil parameters", "groundwater", "geometry", "loads", "design approach"), ("geotechnical resistance", "settlement", "stability"), ("Foundation Design", "Retaining Walls")),
    EurocodePart("EN 1997-2", "Ground investigation and testing", "Ground investigation, sampling and testing.", ("investigation", "field tests", "laboratory tests", "ground parameters"), ("investigation plan", "test results", "ground profile"), ("design parameters", "ground model"), ("Foundation Design")),
    EurocodePart("EN 1998-1", "Earthquake resistance: buildings", "Seismic design of buildings.", ("hazard", "spectra", "regularity", "analysis", "ductility", "capacity design", "detailing"), ("seismic zone", "soil class", "importance", "mass", "damping", "behaviour factor"), ("base shear", "storey forces", "member actions", "detailing requirements"), ("Seismic Actions", "Structural Analysis")),
    EurocodePart("EN 1998-2", "Earthquake resistance: bridges", "Seismic design of bridges.", ("bridge dynamics", "ductility", "bearings", "piers", "foundations"), ("mass", "geometry", "seismic parameters", "soil"), ("seismic bridge actions", "member demands"), ("Structural Analysis")),
    EurocodePart("EN 1998-3", "Assessment and retrofitting", "Assessment and strengthening of existing structures.", ("existing structures", "assessment", "capacity", "retrofitting", "uncertainty"), ("survey", "material tests", "existing drawings", "seismic demand"), ("capacity assessment", "retrofit scheme"), ("Structural Analysis", "RC Detailing")),
    EurocodePart("EN 1998-4", "Earthquake resistance: tanks, silos and pipelines", "Seismic design of special structures.", ("tanks", "silos", "pipelines", "dynamic response", "soil interaction"), ("contents", "mass", "geometry", "seismic parameters"), ("seismic actions", "member demands"), ("Structural Analysis")),
    EurocodePart("EN 1998-5", "Earthquake resistance: foundations, retaining structures and geotechnical aspects", "Seismic geotechnical design.", ("foundations", "retaining walls", "liquefaction", "soil interaction", "slopes"), ("soil parameters", "groundwater", "seismic parameters", "geometry"), ("seismic geotechnical checks", "foundation actions"), ("Foundation Design", "Retaining Walls")),
    EurocodePart("EN 1998-6", "Earthquake resistance: towers, masts and chimneys", "Seismic design of slender structures.", ("towers", "masts", "chimneys", "dynamic response"), ("mass", "height", "frequency", "seismic parameters"), ("seismic response", "member actions"), ("Structural Analysis")),
    EurocodePart("EN 1999-1-1", "Aluminium structures: general rules", "General design rules for aluminium structures.", ("alloys", "cross-sections", "resistance", "buckling", "connections"), ("alloy", "temper", "section", "loads", "restraint"), ("member resistance", "stability", "utilisation"), ("Section Shapes", "Steel Members")),
    EurocodePart("EN 1999-1-2", "Aluminium structures: fire design", "Fire design of aluminium structures.", ("temperature", "reduced properties", "fire resistance"), ("fire exposure", "alloy", "section", "protection"), ("fire resistance", "temperature"), ("Structural Analysis")),
    EurocodePart("EN 1999-1-3", "Aluminium structures: fatigue", "Fatigue design of aluminium structures.", ("stress ranges", "detail categories", "cycles", "damage"), ("load spectrum", "detail", "stress range", "cycles"), ("fatigue resistance", "damage"), ("Steel Members", "Steel Connections")),
    EurocodePart("EN 1999-1-4", "Aluminium structures: cold-formed structural sheeting", "Cold-formed aluminium products.", ("local buckling", "effective sections", "sheeting", "connections"), ("thickness", "geometry", "alloy", "restraint"), ("effective section", "member resistance"), ("Section Shapes")),
    EurocodePart("EN 1999-1-5", "Aluminium structures: shell structures", "Aluminium shell design.", ("shell buckling", "imperfections", "stability", "reinforcement"), ("shell geometry", "thickness", "alloy", "loads"), ("shell resistance", "stability"), ("Structural Analysis")),
)


def family_codes() -> tuple[str, ...]:
    return tuple(EUROCODE_FAMILY)


def parts_for(code: str) -> tuple[EurocodePart, ...]:
    if code.startswith("EN 1990"):
        return tuple(p for p in PARTS if p.code == "EN 1990")
    return tuple(p for p in PARTS if p.code.startswith(code + "-") or p.code == code)


def all_parts() -> tuple[EurocodePart, ...]:
    return PARTS


__all__ = ["EurocodePart", "EUROCODE_FAMILY", "PARTS", "family_codes", "parts_for", "all_parts"]
