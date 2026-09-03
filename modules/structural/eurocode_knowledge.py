"""Engineering knowledge layer for the IMAGINE Eurocode suite.

The catalog contains non-copyrighted engineering metadata: design domains,
input schemas, output schemas, check families, dependencies and hand-off
routes. It deliberately does not reproduce normative Eurocode text.

Values such as partial factors, combination factors, wind maps, snow maps,
seismic parameters and material coefficients are project/National-Annex
controlled and must be supplied or verified for the adopted jurisdiction.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DesignCheck:
    id: str
    name: str
    family: str
    purpose: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    tools: tuple[str, ...]
    status: str = "catalogued"


@dataclass(frozen=True, slots=True)
class ParameterSpec:
    key: str
    label: str
    unit: str
    source: str
    required: bool = True
    project_controlled: bool = True


FAMILIES = {
    "EN 1990": {
        "title": "Basis of structural design",
        "domain": "Design basis and verification",
        "parts": ("EN 1990",),
        "checks": ("design_situation", "uls_combination", "sls_combination", "robustness"),
    },
    "EN 1991": {
        "title": "Actions on structures",
        "domain": "Actions and load models",
        "parts": ("EN 1991-1-1", "EN 1991-1-2", "EN 1991-1-3", "EN 1991-1-4", "EN 1991-1-5", "EN 1991-1-6", "EN 1991-1-7", "EN 1991-2"),
        "checks": ("self_weight", "imposed_load", "snow", "wind", "thermal", "execution", "accidental", "traffic"),
    },
    "EN 1992": {
        "title": "Design of concrete structures",
        "domain": "Reinforced and prestressed concrete",
        "parts": ("EN 1992-1-1", "EN 1992-1-2", "EN 1992-2", "EN 1992-3", "EN 1992-4"),
        "checks": ("rc_flexure", "rc_shear", "rc_axial", "rc_crack", "rc_deflection", "rc_detailing", "rc_fire", "anchor"),
    },
    "EN 1993": {
        "title": "Design of steel structures",
        "domain": "Steel members, joints and structures",
        "parts": ("EN 1993-1-1", "EN 1993-1-2", "EN 1993-1-3", "EN 1993-1-4", "EN 1993-1-5", "EN 1993-1-6", "EN 1993-1-7", "EN 1993-1-8", "EN 1993-1-9", "EN 1993-1-10", "EN 1993-1-11", "EN 1993-2", "EN 1993-3-1", "EN 1993-3-2", "EN 1993-4-1", "EN 1993-4-2", "EN 1993-4-3", "EN 1993-5", "EN 1993-6"),
        "checks": ("steel_section", "steel_tension", "steel_compression", "steel_bending", "steel_shear", "steel_buckling", "steel_ltb", "steel_joint", "steel_fatigue", "steel_fire"),
    },
    "EN 1994": {
        "title": "Design of composite steel and concrete structures",
        "domain": "Composite members and bridges",
        "parts": ("EN 1994-1-1", "EN 1994-1-2", "EN 1994-2"),
        "checks": ("composite_beam", "composite_slab", "composite_column", "shear_connection", "composite_fire", "composite_bridge"),
    },
    "EN 1995": {
        "title": "Design of timber structures",
        "domain": "Timber members, connections and bridges",
        "parts": ("EN 1995-1-1", "EN 1995-1-2", "EN 1995-2"),
        "checks": ("timber_bending", "timber_shear", "timber_compression", "timber_stability", "timber_connection", "timber_fire"),
    },
    "EN 1996": {
        "title": "Design of masonry structures",
        "domain": "Masonry walls and elements",
        "parts": ("EN 1996-1-1", "EN 1996-1-2", "EN 1996-2", "EN 1996-3"),
        "checks": ("masonry_compression", "masonry_shear", "masonry_slenderness", "masonry_lateral", "masonry_fire"),
    },
    "EN 1997": {
        "title": "Geotechnical design",
        "domain": "Ground investigation and geotechnical verification",
        "parts": ("EN 1997-1", "EN 1997-2"),
        "checks": ("bearing", "sliding", "overturning", "settlement", "slope", "retaining", "pile", "groundwater"),
    },
    "EN 1998": {
        "title": "Design for earthquake resistance",
        "domain": "Seismic analysis and detailing",
        "parts": ("EN 1998-1", "EN 1998-2", "EN 1998-3", "EN 1998-4", "EN 1998-5", "EN 1998-6"),
        "checks": ("seismic_hazard", "response_spectrum", "equivalent_static", "modal", "ductility", "capacity_design", "seismic_foundation"),
    },
    "EN 1999": {
        "title": "Design of aluminium structures",
        "domain": "Aluminium members, joints and shells",
        "parts": ("EN 1999-1-1", "EN 1999-1-2", "EN 1999-1-3", "EN 1999-1-4", "EN 1999-1-5"),
        "checks": ("aluminium_section", "aluminium_member", "aluminium_buckling", "aluminium_joint", "aluminium_fatigue", "aluminium_fire"),
    },
}


PARAMETERS = (
    ParameterSpec("gamma_G", "Permanent action factor", "-", "EN 1990 / National Annex"),
    ParameterSpec("gamma_Q", "Variable action factor", "-", "EN 1990 / National Annex"),
    ParameterSpec("psi_0", "Combination factor", "-", "EN 1990 / National Annex"),
    ParameterSpec("psi_1", "Frequent combination factor", "-", "EN 1990 / National Annex"),
    ParameterSpec("psi_2", "Quasi-permanent combination factor", "-", "EN 1990 / National Annex"),
    ParameterSpec("fck", "Concrete characteristic strength", "MPa", "EN 1992 / material specification"),
    ParameterSpec("fyk", "Reinforcement characteristic strength", "MPa", "EN 1992 / material specification"),
    ParameterSpec("fy", "Steel yield strength", "MPa", "EN 1993 / material specification"),
    ParameterSpec("E", "Elastic modulus", "GPa", "material model"),
    ParameterSpec("cover", "Nominal concrete cover", "mm", "EN 1992 / project specification"),
    ParameterSpec("wind_basic_velocity", "Basic wind velocity", "m/s", "EN 1991-1-4 / National Annex"),
    ParameterSpec("snow_ground_load", "Characteristic ground snow load", "kN/m²", "EN 1991-1-3 / National Annex"),
    ParameterSpec("agR", "Reference peak ground acceleration", "m/s²", "EN 1998 / National Annex"),
    ParameterSpec("soil_class", "Ground type / soil class", "-", "EN 1998 / geotechnical report"),
)


CHECKS = (
    DesignCheck("design_situation", "Design situation selection", "EN 1990", "Establish persistent, transient, accidental or seismic design basis.", ("project_type", "design_situation", "consequence_class"), ("design_basis",), ("Structural Analysis",)),
    DesignCheck("uls_combination", "ULS action combinations", "EN 1990", "Generate governing ultimate combinations from project actions.", ("G", "Q", "wind", "snow", "combination_factors"), ("design_action", "governing_combination"), ("Load Combinations",)),
    DesignCheck("sls_combination", "SLS combinations", "EN 1990", "Generate characteristic, frequent and quasi-permanent serviceability cases.", ("G", "Q", "combination_factors"), ("service_action",), ("Load Combinations",)),
    DesignCheck("self_weight", "Self-weight and imposed actions", "EN 1991", "Build building action cases from geometry, density and occupancy information.", ("geometry", "density", "occupancy"), ("permanent_load", "imposed_load"), ("Structural Analysis",)),
    DesignCheck("snow", "Snow action model", "EN 1991", "Prepare roof snow load cases using project and National Annex parameters.", ("snow_ground_load", "roof_geometry", "snow_coefficients"), ("roof_snow_load",), ("Structural Analysis", "Roof Design")),
    DesignCheck("wind", "Wind action model", "EN 1991", "Prepare wind pressure and member actions from exposure and geometry.", ("wind_basic_velocity", "terrain", "height", "coefficients"), ("velocity_pressure", "surface_pressure", "member_load"), ("Wind Actions",)),
    DesignCheck("rc_flexure", "RC flexural resistance", "EN 1992", "Screen reinforced-concrete flexural resistance and reinforcement demand.", ("section", "materials", "MEd"), ("As_required", "MRd", "utilisation"), ("Beam Design", "Slab Design"), "implemented"),
    DesignCheck("rc_shear", "RC shear resistance", "EN 1992", "Screen reinforced-concrete shear resistance and shear reinforcement demand.", ("section", "materials", "VEd"), ("VRd", "Asw_required", "utilisation"), ("Beam Design",), "implemented"),
    DesignCheck("rc_axial", "RC axial interaction", "EN 1992", "Screen axial force and moment interaction for reinforced concrete members.", ("section", "reinforcement", "NEd", "MEd"), ("NRd", "MRd", "utilisation"), ("Column Design",), "implemented"),
    DesignCheck("rc_detailing", "RC detailing schedule", "EN 1992", "Transform reinforcement demand into a traceable detailing record.", ("section", "cover", "bar_diameter", "spacing"), ("bar_count", "steel_area", "schedule"), ("RC Detailing",), "implemented"),
    DesignCheck("steel_member", "Steel member resistance", "EN 1993", "Screen member resistance for tension, compression, bending and shear.", ("steel_grade", "section", "length", "actions"), ("resistance", "utilisation"), ("Steel Members",), "implemented"),
    DesignCheck("steel_joint", "Steel connection resistance", "EN 1993", "Screen bolt/weld connection demand and resistance.", ("bolt_grade", "weld_size", "plate_geometry", "actions"), ("connection_resistance", "utilisation"), ("Steel Connections",), "implemented"),
    DesignCheck("bearing", "Foundation bearing resistance", "EN 1997", "Screen bearing pressure and geotechnical resistance.", ("foundation_geometry", "soil_parameters", "actions"), ("bearing_pressure", "bearing_resistance", "utilisation"), ("Foundation Design",), "implemented"),
    DesignCheck("retaining", "Retaining wall stability", "EN 1997", "Screen sliding, overturning and bearing response of retaining systems.", ("wall_geometry", "soil", "water", "surcharge"), ("sliding_utilisation", "overturning_utilisation", "bearing"), ("Retaining Walls",), "implemented"),
    DesignCheck("response_spectrum", "Seismic response spectrum", "EN 1998", "Prepare project seismic demand for structural analysis.", ("agR", "soil_class", "importance", "damping"), ("spectrum",), ("Seismic Actions",)),
    DesignCheck("equivalent_static", "Equivalent static seismic distribution", "EN 1998", "Distribute base shear through storeys using project mass and height data.", ("base_shear", "storey_masses", "storey_heights"), ("storey_forces",), ("Seismic Actions",), "implemented"),
)


def family_codes() -> tuple[str, ...]:
    return tuple(FAMILIES)


def family(code: str) -> dict[str, object]:
    return FAMILIES[code]


def checks_for(code: str) -> tuple[DesignCheck, ...]:
    return tuple(c for c in CHECKS if c.family == code)


def check_by_id(check_id: str) -> DesignCheck:
    for check in CHECKS:
        if check.id == check_id:
            return check
    raise KeyError(check_id)


def search_catalog(query: str) -> tuple[DesignCheck, ...]:
    needle = query.strip().lower()
    if not needle:
        return CHECKS
    return tuple(
        c for c in CHECKS
        if needle in " ".join((c.id, c.name, c.family, c.purpose, *c.inputs, *c.outputs, *c.tools)).lower()
    )


def validate_catalog() -> None:
    ids = [c.id for c in CHECKS]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Duplicate Eurocode check identifiers detected")
    for code, data in FAMILIES.items():
        if not code.startswith("EN 199") or not data.get("parts"):
            raise RuntimeError(f"Invalid Eurocode family: {code}")
    for check in CHECKS:
        if check.family not in FAMILIES:
            raise RuntimeError(f"Unknown Eurocode family: {check.family}")
        if not check.inputs or not check.outputs:
            raise RuntimeError(f"Incomplete check schema: {check.id}")


validate_catalog()

__all__ = ["CHECKS", "FAMILIES", "PARAMETERS", "DesignCheck", "ParameterSpec", "check_by_id", "checks_for", "family", "family_codes", "search_catalog", "validate_catalog"]
