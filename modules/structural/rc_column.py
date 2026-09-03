"""Deterministic preliminary reinforced-concrete column screening engine.

The engine covers section properties, EC2-style material strengths, minimum and
maximum longitudinal reinforcement, slenderness, minimum eccentricity, axial
resistance and a transparent biaxial interaction screening. It is not a full
EN 1992-1-1 second-order column design solver.
"""
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Mapping
from modules.structural.ec2 import ConcreteDesignProperties, SteelDesignProperties

@dataclass(frozen=True)
class ColumnScreeningResult:
    width_mm: float
    depth_mm: float
    unbraced_length_m: float
    concrete_area_mm2: float
    steel_area_mm2: float
    concrete_design_strength_mpa: float
    steel_design_strength_mpa: float
    minimum_steel_area_mm2: float
    maximum_steel_area_mm2: float
    slenderness_y: float
    slenderness_z: float
    slenderness_limit: float
    is_slender_y: bool
    is_slender_z: bool
    minimum_eccentricity_y_mm: float
    minimum_eccentricity_z_mm: float
    axial_capacity_kn: float
    axial_utilisation: float
    moment_capacity_y_kn_m: float
    moment_capacity_z_kn_m: float
    moment_utilisation_y: float
    moment_utilisation_z: float
    biaxial_interaction_utilisation: float
    status: str

class RCColumnScreeningEngine:
    """Preliminary EC2-style column screening calculations."""
    def run(self, inputs: Mapping[str, float] | None = None) -> ColumnScreeningResult:
        v = dict(inputs or {})
        b, h, l0 = float(v.get("width_mm",350)), float(v.get("depth_mm",350)), float(v.get("unbraced_length_m",3.6))
        fck, fyk = float(v.get("fck_mpa",30)), float(v.get("fyk_mpa",500))
        gc, gs = float(v.get("gamma_c",1.5)), float(v.get("gamma_s",1.15))
        alpha_cc, n_ed = float(v.get("alpha_cc",0.85)), float(v.get("n_ed_kn",1200))
        as_used = float(v.get("steel_area_mm2",0))
        my_ed, mz_ed = float(v.get("my_ed_kn_m",0)), float(v.get("mz_ed_kn_m",0))
        for name, value in {"width_mm":b,"depth_mm":h,"unbraced_length_m":l0,"fck_mpa":fck,"fyk_mpa":fyk,"gamma_c":gc,"gamma_s":gs}.items():
            if value <= 0: raise ValueError(f"{name} must be greater than zero")
        if n_ed < 0 or as_used < 0 or my_ed < 0 or mz_ed < 0: raise ValueError("loads and steel area cannot be negative")
        concrete, steel = ConcreteDesignProperties(fck,gamma_c=gc,alpha_cc=alpha_cc), SteelDesignProperties(fyk,gamma_s=gs)
        ac = b*h
        as_min = max(0.10*n_ed*1000/steel.fyd_mpa, 0.002*ac)
        as_max = 0.04*ac
        as_used = as_used if as_used > 0 else as_min
        iy, iz = h/math.sqrt(12), b/math.sqrt(12)
        ly, lz = l0*1000/iy, l0*1000/iz
        n_rel = n_ed*1000/(ac*concrete.fcd_mpa)
        lambda_lim = 20*0.7*1.1*0.7/math.sqrt(n_rel) if n_rel > 0 else float("inf")
        e0_y, e0_z = max(h/30,20), max(b/30,20)
        axial_capacity = ((ac-as_used)*concrete.fcd_mpa + as_used*steel.fyd_mpa)/1000
        axial_u = n_ed/axial_capacity if axial_capacity else float("inf")
        # Transparent first-order moment screening using plastic axial capacity
        # and section modulus. Second-order amplification is intentionally not hidden here.
        z_y = b*h*h/6.0
        z_z = h*b*b/6.0
        moment_capacity_y = (z_y*concrete.fcd_mpa + as_used*steel.fyd_mpa*max(h/2-e0_y,1))/1e6
        moment_capacity_z = (z_z*concrete.fcd_mpa + as_used*steel.fyd_mpa*max(b/2-e0_z,1))/1e6
        mu_y = my_ed/moment_capacity_y if moment_capacity_y else float("inf")
        mu_z = mz_ed/moment_capacity_z if moment_capacity_z else float("inf")
        biaxial = axial_u + mu_y + mu_z
        reinforcement_ok = as_min <= as_used <= as_max
        status = "PASS" if reinforcement_ok and biaxial <= 1.0 else "REVIEW"
        return ColumnScreeningResult(b,h,l0,ac,as_used,concrete.fcd_mpa,steel.fyd_mpa,as_min,as_max,ly,lz,lambda_lim,ly>lambda_lim,lz>lambda_lim,e0_y,e0_z,axial_capacity,axial_u,moment_capacity_y,moment_capacity_z,mu_y,mu_z,biaxial,status)

__all__ = ["ColumnScreeningResult", "RCColumnScreeningEngine"]
