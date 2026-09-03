"""Non-copyrighted engineering knowledge schemas for the IMAGINE Eurocode Suite.

This module stores design domains, checks, parameters, dependencies and
handoff metadata. It intentionally does not reproduce normative Eurocode text.
All numerical values that depend on an adopted edition, National Annex,
project specification, site data or material certification must be supplied or
verified by the project team.
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
    dependencies: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ParameterSpec:
    key: str
    label: str
    unit: str
    source: str
    group: str
    required: bool = True
    project_controlled: bool = True
    description: str = ""


FAMILIES = {
    "EN 1990": {"title": "Basis of structural design", "domain": "Design basis and verification", "parts": ("EN 1990",)},
    "EN 1991": {"title": "Actions on structures", "domain": "Actions and load models", "parts": ("EN 1991-1-1", "EN 1991-1-2", "EN 1991-1-3", "EN 1991-1-4", "EN 1991-1-5", "EN 1991-1-6", "EN 1991-1-7", "EN 1991-2")},
    "EN 1992": {"title": "Design of concrete structures", "domain": "Reinforced and prestressed concrete", "parts": ("EN 1992-1-1", "EN 1992-1-2", "EN 1992-2", "EN 1992-3", "EN 1992-4")},
    "EN 1993": {"title": "Design of steel structures", "domain": "Steel members, joints and structures", "parts": ("EN 1993-1-1", "EN 1993-1-2", "EN 1993-1-3", "EN 1993-1-4", "EN 1993-1-5", "EN 1993-1-6", "EN 1993-1-7", "EN 1993-1-8", "EN 1993-1-9", "EN 1993-1-10", "EN 1993-1-11", "EN 1993-2", "EN 1993-3-1", "EN 1993-3-2", "EN 1993-4-1", "EN 1993-4-2", "EN 1993-4-3", "EN 1993-5", "EN 1993-6")},
    "EN 1994": {"title": "Design of composite steel and concrete structures", "domain": "Composite members and bridges", "parts": ("EN 1994-1-1", "EN 1994-1-2", "EN 1994-2")},
    "EN 1995": {"title": "Design of timber structures", "domain": "Timber members, connections and bridges", "parts": ("EN 1995-1-1", "EN 1995-1-2", "EN 1995-2")},
    "EN 1996": {"title": "Design of masonry structures", "domain": "Masonry walls and elements", "parts": ("EN 1996-1-1", "EN 1996-1-2", "EN 1996-2", "EN 1996-3")},
    "EN 1997": {"title": "Geotechnical design", "domain": "Ground investigation and geotechnical verification", "parts": ("EN 1997-1", "EN 1997-2")},
    "EN 1998": {"title": "Design for earthquake resistance", "domain": "Seismic analysis and detailing", "parts": ("EN 1998-1", "EN 1998-2", "EN 1998-3", "EN 1998-4", "EN 1998-5", "EN 1998-6")},
    "EN 1999": {"title": "Design of aluminium structures", "domain": "Aluminium members, joints and shells", "parts": ("EN 1999-1-1", "EN 1999-1-2", "EN 1999-1-3", "EN 1999-1-4", "EN 1999-1-5")},
}


# Parameter schema. These are keys and provenance fields, not universal values.
PARAMETERS = (
    ParameterSpec("gamma_G", "Permanent action factor", "-", "EN 1990 / National Annex", "EN 1990"),
    ParameterSpec("gamma_Q", "Variable action factor", "-", "EN 1990 / National Annex", "EN 1990"),
    ParameterSpec("psi_0", "Combination factor", "-", "EN 1990 / National Annex", "EN 1990"),
    ParameterSpec("psi_1", "Frequent combination factor", "-", "EN 1990 / National Annex", "EN 1990"),
    ParameterSpec("psi_2", "Quasi-permanent combination factor", "-", "EN 1990 / National Annex", "EN 1990"),
    ParameterSpec("consequence_class", "Consequence class", "-", "EN 1990 / project brief", "EN 1990"),
    ParameterSpec("design_situation", "Design situation", "-", "EN 1990 / project brief", "EN 1990"),
    ParameterSpec("density", "Material density", "kN/m³", "EN 1991-1-1 / material data", "EN 1991"),
    ParameterSpec("occupancy_category", "Imposed-load category", "-", "EN 1991-1-1 / project use", "EN 1991"),
    ParameterSpec("fire_duration", "Fire design duration", "min", "EN 1991-1-2 / fire strategy", "EN 1991"),
    ParameterSpec("snow_ground_load", "Characteristic ground snow load", "kN/m²", "EN 1991-1-3 / National Annex", "EN 1991"),
    ParameterSpec("wind_basic_velocity", "Basic wind velocity", "m/s", "EN 1991-1-4 / National Annex", "EN 1991"),
    ParameterSpec("terrain_category", "Terrain / exposure category", "-", "EN 1991-1-4 / site", "EN 1991"),
    ParameterSpec("thermal_range", "Design temperature range", "K", "EN 1991-1-5 / National Annex", "EN 1991"),
    ParameterSpec("accidental_action", "Accidental action model", "kN or kN/m²", "EN 1991-1-7 / project hazard", "EN 1991"),
    ParameterSpec("fck", "Concrete characteristic strength", "MPa", "EN 1992 / material specification", "EN 1992"),
    ParameterSpec("fyk", "Reinforcement characteristic strength", "MPa", "EN 1992 / material specification", "EN 1992"),
    ParameterSpec("cover", "Nominal concrete cover", "mm", "EN 1992 / durability design", "EN 1992"),
    ParameterSpec("exposure_class", "Concrete exposure class", "-", "EN 1992 / project durability basis", "EN 1992"),
    ParameterSpec("prestress", "Prestressing force", "kN", "EN 1992 / prestressing system", "EN 1992", False),
    ParameterSpec("fy", "Steel yield strength", "MPa", "EN 1993 / material certificate", "EN 1993"),
    ParameterSpec("fu", "Steel ultimate strength", "MPa", "EN 1993 / material certificate", "EN 1993"),
    ParameterSpec("steel_section", "Steel section properties", "-", "EN 1993 / section database", "EN 1993"),
    ParameterSpec("buckling_length", "Member buckling length", "m", "EN 1993 / analysis model", "EN 1993"),
    ParameterSpec("bolt_grade", "Bolt grade", "-", "EN 1993 / product standard", "EN 1993", False),
    ParameterSpec("weld_size", "Weld throat/size", "mm", "EN 1993 / connection design", "EN 1993", False),
    ParameterSpec("timber_grade", "Timber strength class", "-", "EN 1995 / material certificate", "EN 1995"),
    ParameterSpec("service_class", "Timber service class", "-", "EN 1995 / exposure", "EN 1995"),
    ParameterSpec("masonry_unit", "Masonry unit type", "-", "EN 1996 / product data", "EN 1996"),
    ParameterSpec("fm", "Masonry compressive strength", "MPa", "EN 1996 / product data", "EN 1996"),
    ParameterSpec("soil_classification", "Ground classification", "-", "EN 1997 / investigation", "EN 1997"),
    ParameterSpec("phi", "Effective friction angle", "deg", "EN 1997 / ground investigation", "EN 1997"),
    ParameterSpec("cohesion", "Effective cohesion", "kPa", "EN 1997 / ground investigation", "EN 1997"),
    ParameterSpec("gamma_soil", "Soil unit weight", "kN/m³", "EN 1997 / ground investigation", "EN 1997"),
    ParameterSpec("groundwater_level", "Groundwater level", "m", "EN 1997 / investigation", "EN 1997", False),
    ParameterSpec("agR", "Reference peak ground acceleration", "m/s²", "EN 1998 / National Annex", "EN 1998"),
    ParameterSpec("soil_type", "Seismic ground type", "-", "EN 1998 / geotechnical report", "EN 1998"),
    ParameterSpec("importance_factor", "Seismic importance factor", "-", "EN 1998 / National Annex", "EN 1998"),
    ParameterSpec("behaviour_factor", "Seismic behaviour factor", "-", "EN 1998 / design system", "EN 1998"),
    ParameterSpec("aluminium_alloy", "Aluminium alloy/temper", "-", "EN 1999 / material certificate", "EN 1999"),
    ParameterSpec("aluminium_fu", "Aluminium ultimate strength", "MPa", "EN 1999 / material certificate", "EN 1999"),
)


def _c(id, name, family, purpose, inputs, outputs, tools, status="catalogued", dependencies=()):
    return DesignCheck(id, name, family, purpose, tuple(inputs), tuple(outputs), tuple(tools), status, tuple(dependencies))


CHECKS = (
    _c("design_situation", "Design situation selection", "EN 1990", "Establish the governing project design situation and verification basis.", ("project_type", "design_situation", "consequence_class"), ("design_basis",), ("Structural Analysis",)),
    _c("uls_combination", "ULS action combinations", "EN 1990", "Generate project-specific ultimate action cases.", ("G", "Q", "wind", "snow", "gamma_G", "gamma_Q", "psi_0"), ("design_action", "governing_combination"), ("Load Combinations",), "implemented", ("design_situation",)),
    _c("sls_characteristic", "SLS characteristic combination", "EN 1990", "Prepare characteristic serviceability action cases.", ("G", "Q", "psi_0"), ("service_action",), ("Load Combinations",), "implemented", ("design_situation",)),
    _c("sls_frequent", "SLS frequent combination", "EN 1990", "Prepare frequent serviceability action cases.", ("G", "Q", "psi_1"), ("service_action",), ("Load Combinations",), "implemented", ("design_situation",)),
    _c("sls_quasi_permanent", "SLS quasi-permanent combination", "EN 1990", "Prepare quasi-permanent serviceability action cases.", ("G", "Q", "psi_2"), ("service_action",), ("Load Combinations",), "implemented", ("design_situation",)),
    _c("robustness", "Robustness assessment", "EN 1990", "Record robustness strategy and accidental-damage verification pathway.", ("consequence_class", "accidental_action", "structural_system"), ("robustness_strategy", "damage_scenarios"), ("Structural Analysis",)),
    _c("self_weight", "Self-weight and imposed actions", "EN 1991", "Build building action cases from geometry, density and occupancy data.", ("geometry", "density", "occupancy_category"), ("permanent_load", "imposed_load"), ("Structural Analysis",), "implemented"),
    _c("snow", "Snow action model", "EN 1991", "Prepare project roof snow load cases.", ("snow_ground_load", "roof_geometry", "snow_coefficients"), ("roof_snow_load", "load_cases"), ("Roof Design", "Structural Analysis")),
    _c("wind", "Wind action model", "EN 1991", "Prepare wind pressure and member actions from site exposure and geometry.", ("wind_basic_velocity", "terrain_category", "height", "geometry"), ("velocity_pressure", "surface_pressure", "member_load"), ("Wind Actions",), "implemented"),
    _c("thermal", "Thermal action model", "EN 1991", "Prepare restrained and unrestrained thermal action cases.", ("thermal_range", "geometry", "material"), ("thermal_strain", "thermal_action"), ("Structural Analysis",)),
    _c("execution", "Execution-stage actions", "EN 1991", "Represent temporary construction actions and stages.", ("construction_sequence", "equipment", "temporary_works"), ("execution_load_cases",), ("Structural Analysis", "Construction")),
    _c("accidental", "Accidental action model", "EN 1991", "Record accidental hazard scenarios for structural verification.", ("accidental_action", "hazard", "consequence_class"), ("accidental_load_case",), ("Structural Analysis",)),
    _c("traffic", "Bridge traffic action model", "EN 1991", "Prepare bridge traffic load models and effects.", ("bridge_geometry", "traffic_model", "lanes"), ("traffic_load_cases", "design_effects"), ("Structural Analysis",)),
    _c("rc_flexure", "RC flexural resistance", "EN 1992", "Screen reinforced-concrete flexural resistance and reinforcement demand.", ("section", "fck", "fyk", "MEd"), ("As_required", "MRd", "utilisation"), ("Beam Design", "Slab Design"), "implemented", ("uls_combination",)),
    _c("rc_shear", "RC shear resistance", "EN 1992", "Screen concrete shear resistance and shear reinforcement demand.", ("section", "fck", "fyk", "VEd"), ("VRd", "Asw_required", "utilisation"), ("Beam Design",), "implemented", ("uls_combination",)),
    _c("rc_axial", "RC axial interaction", "EN 1992", "Screen axial force and moment interaction.", ("section", "fck", "fyk", "NEd", "MEd"), ("NRd", "MRd", "utilisation"), ("Column Design",), "implemented", ("uls_combination",)),
    _c("rc_crack", "RC crack-control screening", "EN 1992", "Screen serviceability reinforcement and crack-control demand.", ("section", "cover", "exposure_class", "service_action"), ("crack_width_screen", "reinforcement"), ("Beam Design", "Slab Design"), "catalogued", ("sls_characteristic",)),
    _c("rc_deflection", "RC deflection screening", "EN 1992", "Screen deflection response against project criteria.", ("section", "materials", "service_action", "span"), ("deflection", "utilisation"), ("Beam Design", "Slab Design"), "catalogued", ("sls_quasi_permanent",)),
    _c("rc_detailing", "RC detailing schedule", "EN 1992", "Transform reinforcement demand into a traceable detailing record.", ("section", "cover", "bar_diameter", "spacing"), ("bar_count", "steel_area", "schedule"), ("RC Detailing",), "implemented"),
    _c("rc_fire", "RC fire design pathway", "EN 1992", "Prepare fire-resistance inputs and member verification pathway.", ("fire_duration", "section", "materials", "fire_exposure"), ("fire_resistance", "temperature_effects"), ("Structural Analysis", "RC Detailing")),
    _c("anchor", "Concrete fastening", "EN 1992", "Screen anchor demand and concrete failure modes.", ("anchor_type", "fck", "edge_distance", "loads"), ("anchor_resistance", "utilisation"), ("Steel Connections",)),
    _c("steel_section", "Steel cross-section classification", "EN 1993", "Classify a steel cross-section and establish resistance pathway.", ("steel_section", "fy", "fu", "stress_distribution"), ("section_class", "resistance_basis"), ("Section Shapes", "Steel Members"), "implemented"),
    _c("steel_tension", "Steel tension member", "EN 1993", "Screen tension resistance and connection effects.", ("steel_section", "fy", "fu", "tension"), ("tension_resistance", "utilisation"), ("Steel Members",), "implemented", ("steel_section",)),
    _c("steel_compression", "Steel compression member", "EN 1993", "Screen compression and buckling resistance.", ("steel_section", "fy", "buckling_length", "compression"), ("buckling_resistance", "utilisation"), ("Steel Members",), "implemented", ("steel_section",)),
    _c("steel_bending", "Steel bending member", "EN 1993", "Screen bending and shear resistance.", ("steel_section", "fy", "MEd", "VEd"), ("MRd", "VRd", "utilisation"), ("Steel Members",), "implemented", ("steel_section",)),
    _c("steel_ltb", "Lateral-torsional buckling", "EN 1993", "Screen lateral-torsional stability of beams.", ("steel_section", "fy", "buckling_length", "restraint", "MEd"), ("LTB_resistance", "utilisation"), ("Steel Members",)),
    _c("steel_joint", "Steel connection resistance", "EN 1993", "Screen bolted and welded connection demand.", ("bolt_grade", "weld_size", "plate_geometry", "actions"), ("connection_resistance", "utilisation"), ("Steel Connections",), "implemented"),
    _c("steel_fatigue", "Steel fatigue assessment", "EN 1993", "Screen fatigue demand using a project load spectrum.", ("load_spectrum", "detail_category", "stress_range", "cycles"), ("fatigue_resistance", "damage_ratio"), ("Steel Members", "Steel Connections")),
    _c("steel_fire", "Steel fire design pathway", "EN 1993", "Prepare fire resistance assessment inputs for steel members.", ("fire_duration", "section_factor", "protection", "loads"), ("steel_temperature", "fire_resistance"), ("Steel Members",)),
    _c("steel_toughness", "Steel material toughness", "EN 1993", "Record material toughness and fracture-control requirements.", ("steel_grade", "thickness", "temperature", "stress"), ("material_selection_check",), ("Building Materials",)),
    _c("composite_beam", "Composite beam resistance", "EN 1994", "Screen composite beam resistance through construction and final stages.", ("steel_section", "concrete_slab", "connectors", "actions"), ("composite_resistance", "connector_requirement"), ("Steel Members",), dependencies=("uls_combination",)),
    _c("composite_slab", "Composite slab pathway", "EN 1994", "Prepare composite slab design inputs and construction stages.", ("slab_geometry", "deck", "concrete", "actions"), ("slab_resistance", "construction_stage_check"), ("Slab Design",)),
    _c("composite_column", "Composite column resistance", "EN 1994", "Screen composite column axial and moment resistance.", ("steel_section", "concrete", "reinforcement", "NEd", "MEd"), ("NRd", "MRd", "utilisation"), ("Column Design",)),
    _c("shear_connection", "Composite shear connection", "EN 1994", "Screen longitudinal shear transfer and connector demand.", ("connectors", "steel_section", "slab", "actions"), ("connector_capacity", "connector_count"), ("Steel Connections",)),
    _c("composite_fire", "Composite fire pathway", "EN 1994", "Prepare fire-resistance pathway for composite members.", ("fire_duration", "materials", "section", "protection"), ("fire_resistance",), ("Structural Analysis",)),
    _c("timber_bending", "Timber bending resistance", "EN 1995", "Screen bending resistance of timber members.", ("timber_grade", "service_class", "section", "MEd"), ("MRd", "utilisation"), ("Structural Analysis",)),
    _c("timber_shear", "Timber shear resistance", "EN 1995", "Screen shear resistance of timber members.", ("timber_grade", "section", "VEd"), ("VRd", "utilisation"), ("Structural Analysis",)),
    _c("timber_stability", "Timber stability", "EN 1995", "Screen stability and slenderness effects.", ("timber_grade", "section", "buckling_length", "compression"), ("stability_resistance", "utilisation"), ("Structural Analysis",)),
    _c("timber_connection", "Timber connection pathway", "EN 1995", "Prepare fastener and connection design inputs.", ("timber_grade", "fastener", "geometry", "actions"), ("connection_resistance", "fastener_schedule"), ("Steel Connections",)),
    _c("timber_fire", "Timber fire pathway", "EN 1995", "Prepare fire design inputs for timber members.", ("fire_duration", "timber_grade", "section", "protection"), ("fire_resistance",), ("Structural Analysis",)),
    _c("masonry_compression", "Masonry compression resistance", "EN 1996", "Screen compressive resistance of masonry walls and piers.", ("masonry_unit", "fm", "geometry", "NEd"), ("NRd", "utilisation"), ("Structural Analysis",)),
    _c("masonry_shear", "Masonry shear resistance", "EN 1996", "Screen in-plane shear resistance.", ("masonry_unit", "fm", "geometry", "VEd"), ("VRd", "utilisation"), ("Structural Analysis",)),
    _c("masonry_slenderness", "Masonry slenderness", "EN 1996", "Screen wall slenderness and stability.", ("geometry", "restraint", "masonry_unit"), ("slenderness", "stability_check"), ("Structural Analysis",)),
    _c("masonry_lateral", "Masonry lateral load pathway", "EN 1996", "Prepare lateral-load resistance checks for walls.", ("wall_geometry", "lateral_load", "restraint"), ("wall_resistance", "utilisation"), ("Structural Analysis",)),
    _c("bearing", "Foundation bearing resistance", "EN 1997", "Screen foundation bearing pressure and geotechnical resistance.", ("foundation_geometry", "soil_parameters", "actions"), ("bearing_pressure", "bearing_resistance", "utilisation"), ("Foundation Design",), "implemented", ("uls_combination",)),
    _c("settlement", "Foundation settlement", "EN 1997", "Screen total and differential settlement against project criteria.", ("foundation_geometry", "soil_layers", "service_action"), ("settlement", "differential_settlement"), ("Foundation Design",), dependencies=("sls_quasi_permanent",)),
    _c("sliding", "Geotechnical sliding", "EN 1997", "Screen sliding resistance of foundations and retaining systems.", ("soil_parameters", "foundation_geometry", "horizontal_action"), ("sliding_resistance", "utilisation"), ("Foundation Design", "Retaining Walls")),
    _c("overturning", "Geotechnical overturning", "EN 1997", "Screen overturning equilibrium for foundations and retaining systems.", ("soil_parameters", "geometry", "moments"), ("stability_ratio", "utilisation"), ("Foundation Design", "Retaining Walls")),
    _c("retaining", "Retaining wall stability", "EN 1997", "Screen sliding, overturning and bearing response of retaining systems.", ("wall_geometry", "soil", "water", "surcharge"), ("sliding_utilisation", "overturning_utilisation", "bearing"), ("Retaining Walls",), "implemented"),
    _c("pile", "Pile foundation pathway", "EN 1997", "Prepare axial, lateral and group pile verification inputs.", ("pile_geometry", "soil_profile", "actions", "groundwater_level"), ("pile_resistance", "settlement", "utilisation"), ("Foundation Design",)),
    _c("groundwater", "Groundwater and hydraulic effects", "EN 1997", "Record groundwater conditions for effective-stress and stability checks.", ("groundwater_level", "soil_profile", "drainage"), ("pore_pressure", "hydraulic_case"), ("Foundation Design", "Retaining Walls")),
    _c("seismic_hazard", "Seismic hazard basis", "EN 1998", "Record project seismic hazard and site classification inputs.", ("agR", "soil_type", "importance_factor"), ("seismic_design_basis",), ("Seismic Actions",)),
    _c("response_spectrum", "Seismic response spectrum", "EN 1998", "Prepare project seismic demand for structural analysis.", ("agR", "soil_type", "importance_factor", "damping"), ("spectrum",), ("Seismic Actions",)),
    _c("equivalent_static", "Equivalent static seismic distribution", "EN 1998", "Distribute base shear using project mass and height data.", ("base_shear", "storey_masses", "storey_heights", "behaviour_factor"), ("storey_forces",), ("Seismic Actions",), "implemented", ("response_spectrum",)),
    _c("modal", "Modal seismic analysis pathway", "EN 1998", "Prepare modal analysis data and participation checks.", ("mass_model", "stiffness_model", "spectrum"), ("periods", "modal_forces", "participation"), ("Structural Analysis",), dependencies=("response_spectrum",)),
    _c("ductility", "Seismic ductility pathway", "EN 1998", "Record ductility class and detailing requirements for the structural system.", ("structural_system", "behaviour_factor", "ductility_class"), ("ductility_basis", "detailing_requirements"), ("Seismic Actions", "RC Detailing")),
    _c("capacity_design", "Seismic capacity-design pathway", "EN 1998", "Coordinate hierarchy of resistance and seismic detailing demands.", ("analysis_actions", "member_resistances", "structural_system"), ("capacity_design_actions",), ("Structural Analysis", "RC Detailing", "Steel Connections")),
    _c("seismic_foundation", "Seismic foundation pathway", "EN 1998", "Coordinate seismic actions with foundation and ground response.", ("seismic_actions", "soil_parameters", "foundation_geometry"), ("seismic_foundation_actions",), ("Foundation Design",)),
    _c("aluminium_section", "Aluminium cross-section resistance", "EN 1999", "Screen aluminium section classification and resistance pathway.", ("aluminium_alloy", "section", "actions"), ("section_class", "resistance"), ("Section Shapes",)),
    _c("aluminium_member", "Aluminium member resistance", "EN 1999", "Screen aluminium member resistance under project actions.", ("aluminium_alloy", "section", "length", "actions"), ("member_resistance", "utilisation"), ("Steel Members",)),
    _c("aluminium_buckling", "Aluminium stability", "EN 1999", "Screen buckling and stability of aluminium members.", ("aluminium_alloy", "section", "buckling_length", "compression"), ("buckling_resistance", "utilisation"), ("Steel Members",)),
    _c("aluminium_joint", "Aluminium connection pathway", "EN 1999", "Prepare bolted/welded aluminium connection checks.", ("aluminium_alloy", "geometry", "fasteners", "actions"), ("connection_resistance", "utilisation"), ("Steel Connections",)),
    _c("aluminium_fatigue", "Aluminium fatigue pathway", "EN 1999", "Prepare fatigue assessment data for aluminium structures.", ("load_spectrum", "detail_category", "stress_range", "cycles"), ("fatigue_resistance", "damage_ratio"), ("Steel Members", "Steel Connections")),
    _c("aluminium_fire", "Aluminium fire pathway", "EN 1999", "Prepare fire design inputs for aluminium structures.", ("fire_duration", "section", "thermal_properties", "loads"), ("fire_resistance", "temperature"), ("Structural Analysis",)),
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
    return tuple(c for c in CHECKS if needle in " ".join((c.id, c.name, c.family, c.purpose, *c.inputs, *c.outputs, *c.tools)).lower())


def validate_catalog() -> None:
    family_ids = set(FAMILIES)
    check_ids = [c.id for c in CHECKS]
    parameter_ids = [p.key for p in PARAMETERS]
    if len(check_ids) != len(set(check_ids)):
        raise RuntimeError("Duplicate Eurocode check identifiers detected")
    if len(parameter_ids) != len(set(parameter_ids)):
        raise RuntimeError("Duplicate Eurocode parameter identifiers detected")
    if set(family_ids) != {f"EN 199{i}" for i in range(10)}:
        raise RuntimeError("Eurocode family coverage must contain EN 1990 through EN 1999")
    for check in CHECKS:
        if check.family not in FAMILIES:
            raise RuntimeError(f"Unknown Eurocode family: {check.family}")
        if not check.inputs or not check.outputs or not check.tools:
            raise RuntimeError(f"Incomplete check schema: {check.id}")
        for dependency in check.dependencies:
            if dependency not in check_ids:
                raise RuntimeError(f"Unknown dependency {dependency!r} for {check.id}")


validate_catalog()

__all__ = [
    "CHECKS", "FAMILIES", "PARAMETERS", "DesignCheck", "ParameterSpec",
    "check_by_id", "checks_for", "family", "family_codes", "search_catalog",
    "validate_catalog",
]
