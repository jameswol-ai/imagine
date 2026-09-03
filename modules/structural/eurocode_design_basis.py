"""Non-copyrighted Eurocode design-basis metadata for IMAGINE.

This layer describes engineering inputs, parameter ownership, verification
families and calculation handoffs. It does not reproduce Eurocode text or
claim that defaults are National Annex values. Project-specific values must
be supplied and verified against the adopted edition and National Annex.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DesignParameter:
    key: str
    label: str
    unit: str
    source: str
    required: bool = True
    note: str = ""


@dataclass(frozen=True)
class Verification:
    code: str
    name: str
    category: str
    parameters: tuple[str, ...]
    result: str
    workspace: str | None = None


@dataclass(frozen=True)
class DesignBasis:
    code: str
    discipline: str
    parameters: tuple[DesignParameter, ...]
    verifications: tuple[Verification, ...]


PARAMETERS = (
    DesignParameter("gamma_G", "Permanent-action partial factor", "-", "National Annex / project basis", note="Do not use as an application-wide default."),
    DesignParameter("gamma_Q", "Variable-action partial factor", "-", "National Annex / project basis", note="Verify for the adopted design situation."),
    DesignParameter("psi_0", "Combination factor for accompanying variable action", "-", "National Annex / project basis"),
    DesignParameter("psi_1", "Frequent combination factor", "-", "National Annex / project basis"),
    DesignParameter("psi_2", "Quasi-permanent combination factor", "-", "National Annex / project basis"),
    DesignParameter("concrete_class", "Concrete strength class", "-", "Material specification"),
    DesignParameter("reinforcement_grade", "Reinforcement grade", "-", "Material specification"),
    DesignParameter("steel_grade", "Structural steel grade", "-", "Material specification"),
    DesignParameter("timber_grade", "Structural timber grade", "-", "Material specification"),
    DesignParameter("masonry_class", "Masonry unit / strength class", "-", "Material specification"),
    DesignParameter("aluminium_alloy", "Aluminium alloy / temper", "-", "Material specification"),
    DesignParameter("exposure_class", "Environmental exposure classification", "-", "Project durability basis"),
    DesignParameter("fire_duration", "Required fire exposure duration", "min", "Fire strategy / project basis"),
    DesignParameter("basic_wind_velocity", "Basic wind velocity", "m/s", "Site / National Annex"),
    DesignParameter("snow_load_ground", "Characteristic ground snow load", "kN/m²", "Site / National Annex"),
    DesignParameter("seismic_reference", "Seismic hazard / reference parameters", "project", "National Annex / hazard study"),
    DesignParameter("soil_parameter_set", "Geotechnical design parameter set", "project", "Ground investigation"),
)


BASIS_BY_CODE: dict[str, DesignBasis] = {
    "EN 1990": DesignBasis(
        "EN 1990", "Basis", PARAMETERS[0:5],
        (
            Verification("EN 1990", "Ultimate limit state combinations", "ULS", ("gamma_G", "gamma_Q", "psi_0"), "Governing design combination", "Load Combinations"),
            Verification("EN 1990", "Serviceability combinations", "SLS", ("psi_0", "psi_1", "psi_2"), "Characteristic / frequent / quasi-permanent effects", "Load Combinations"),
        ),
    ),
    "EN 1991": DesignBasis(
        "EN 1991", "Actions", PARAMETERS[12:15],
        (
            Verification("EN 1991", "Wind action model", "Actions", ("basic_wind_velocity",), "Velocity pressure and structural action", "Wind Actions"),
            Verification("EN 1991", "Snow action model", "Actions", ("snow_load_ground",), "Roof snow load cases", "Structural Analysis"),
        ),
    ),
    "EN 1992": DesignBasis(
        "EN 1992", "Concrete", PARAMETERS[5:7] + (PARAMETERS[11],),
        (
            Verification("EN 1992", "Reinforced-concrete member resistance", "ULS", ("concrete_class", "reinforcement_grade", "exposure_class"), "Resistance / utilisation / reinforcement", "Beam Design"),
            Verification("EN 1992", "Serviceability and detailing", "SLS", ("concrete_class", "reinforcement_grade", "exposure_class"), "Crack / deflection / detailing outputs", "RC Detailing"),
        ),
    ),
    "EN 1993": DesignBasis(
        "EN 1993", "Steel", (PARAMETERS[7],),
        (
            Verification("EN 1993", "Steel member resistance", "ULS", ("steel_grade",), "Resistance / utilisation / buckling", "Steel Members"),
            Verification("EN 1993", "Steel connection resistance", "ULS", ("steel_grade",), "Connection resistance / utilisation", "Steel Connections"),
        ),
    ),
    "EN 1994": DesignBasis(
        "EN 1994", "Composite", (PARAMETERS[5], PARAMETERS[7]),
        (Verification("EN 1994", "Composite member resistance", "ULS", ("concrete_class", "steel_grade"), "Composite resistance", "Steel Members"),),
    ),
    "EN 1995": DesignBasis(
        "EN 1995", "Timber", (PARAMETERS[8],),
        (Verification("EN 1995", "Timber member resistance", "ULS/SLS", ("timber_grade",), "Member resistance and serviceability", "Structural Analysis"),),
    ),
    "EN 1996": DesignBasis(
        "EN 1996", "Masonry", (PARAMETERS[9],),
        (Verification("EN 1996", "Masonry wall resistance", "ULS", ("masonry_class",), "Wall / pier resistance", "Structural Analysis"),),
    ),
    "EN 1997": DesignBasis(
        "EN 1997", "Geotechnical", (PARAMETERS[16],),
        (Verification("EN 1997", "Geotechnical bearing and stability", "ULS", ("soil_parameter_set",), "Bearing / sliding / settlement inputs", "Foundation Design"),),
    ),
    "EN 1998": DesignBasis(
        "EN 1998", "Seismic", (PARAMETERS[15],),
        (Verification("EN 1998", "Seismic action and storey distribution", "Seismic", ("seismic_reference",), "Base shear / storey force distribution", "Seismic Actions"),),
    ),
    "EN 1999": DesignBasis(
        "EN 1999", "Aluminium", (PARAMETERS[10],),
        (Verification("EN 1999", "Aluminium member resistance", "ULS", ("aluminium_alloy",), "Member resistance / utilisation", "Structural Analysis"),),
    ),
}


def design_basis(code: str) -> DesignBasis | None:
    """Return the design-basis metadata for a Eurocode family."""
    return BASIS_BY_CODE.get(code.strip().upper())


def all_verifications() -> tuple[Verification, ...]:
    """Return all registered verification handoffs."""
    return tuple(v for basis in BASIS_BY_CODE.values() for v in basis.verifications)


__all__ = ["DesignBasis", "DesignParameter", "Verification", "BASIS_BY_CODE", "PARAMETERS", "all_verifications", "design_basis"]
