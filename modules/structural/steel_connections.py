"""Preliminary EN 1993 steel connection design workspace.

The module deliberately separates transparent connection screening from full
connection design. It covers bolt shear, plate bearing and a simple welded
connection screen, with explicit utilisation and demand/capacity reporting.
Project-specific connection geometry, bolt-hole dimensions, weld throat,
block tearing, prying, slip, fatigue, ductility and the adopted National
Annex require engineering verification.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import pandas as pd
import streamlit as st

from modules.structural.ec3 import BoltGroup, bolt_shear_resistance_kn


@dataclass(frozen=True)
class SteelConnectionInput:
    shear_kn: float
    axial_kn: float
    bolt_diameter_mm: float
    bolt_count: int
    bolt_fu_mpa: float
    plate_thickness_mm: float
    plate_fu_mpa: float
    edge_distance_mm: float
    pitch_mm: float
    weld_length_mm: float
    weld_throat_mm: float
    weld_fu_mpa: float
    gamma_m2: float = 1.25

    def __post_init__(self) -> None:
        positive = {
            "shear_kn": self.shear_kn,
            "bolt_diameter_mm": self.bolt_diameter_mm,
            "bolt_fu_mpa": self.bolt_fu_mpa,
            "plate_thickness_mm": self.plate_thickness_mm,
            "plate_fu_mpa": self.plate_fu_mpa,
            "edge_distance_mm": self.edge_distance_mm,
            "pitch_mm": self.pitch_mm,
            "weld_length_mm": self.weld_length_mm,
            "weld_throat_mm": self.weld_throat_mm,
            "weld_fu_mpa": self.weld_fu_mpa,
            "gamma_m2": self.gamma_m2,
        }
        for name, value in positive.items():
            if value <= 0:
                raise ValueError(f"{name} must be greater than zero")
        if self.bolt_count <= 0:
            raise ValueError("bolt_count must be greater than zero")
        if self.axial_kn < 0:
            raise ValueError("axial_kn cannot be negative")


@dataclass(frozen=True)
class SteelConnectionResult:
    bolt_shear_capacity_kn: float
    plate_bearing_capacity_kn: float
    weld_shear_capacity_kn: float
    governing_capacity_kn: float
    shear_utilisation: float
    weld_utilisation: float
    axial_bolt_utilisation: float
    overall_utilisation: float
    status: str


def plate_bearing_capacity_kn(inputs: SteelConnectionInput) -> float:
    """Conservative preliminary plate bearing screen per bolt."""
    d0 = inputs.bolt_diameter_mm + 2.0
    edge_factor = min(inputs.edge_distance_mm / (3.0 * d0), 1.0)
    pitch_factor = min(inputs.pitch_mm / (3.0 * d0), 1.0)
    alpha_b = max(0.25, min(edge_factor, pitch_factor))
    per_bolt = 2.5 * alpha_b * inputs.bolt_diameter_mm * inputs.plate_thickness_mm * inputs.plate_fu_mpa / inputs.gamma_m2
    return inputs.bolt_count * per_bolt / 1000.0


def weld_shear_capacity_kn(inputs: SteelConnectionInput) -> float:
    """Preliminary fillet-weld shear resistance using 0.6 fu A/gamma."""
    area = inputs.weld_length_mm * inputs.weld_throat_mm
    return 0.6 * inputs.weld_fu_mpa * area / inputs.gamma_m2 / 1000.0


def evaluate_connection(inputs: SteelConnectionInput) -> SteelConnectionResult:
    group = BoltGroup(
        bolt_diameter_mm=inputs.bolt_diameter_mm,
        bolt_count=inputs.bolt_count,
        bolt_fu_mpa=inputs.bolt_fu_mpa,
        gamma_m2=inputs.gamma_m2,
        plate_thickness_mm=inputs.plate_thickness_mm,
        plate_fu_mpa=inputs.plate_fu_mpa,
    )
    bolt_capacity = bolt_shear_resistance_kn(group)
    bearing_capacity = plate_bearing_capacity_kn(inputs)
    weld_capacity = weld_shear_capacity_kn(inputs)
    governing = min(bolt_capacity, bearing_capacity)
    shear_util = inputs.shear_kn / governing if governing else math.inf
    weld_util = inputs.shear_kn / weld_capacity if weld_capacity else math.inf
    axial_capacity = bolt_capacity
    axial_util = inputs.axial_kn / axial_capacity if axial_capacity else math.inf
    interaction = math.sqrt(shear_util**2 + axial_util**2)
    overall = max(shear_util, weld_util, interaction)
    return SteelConnectionResult(
        bolt_shear_capacity_kn=bolt_capacity,
        plate_bearing_capacity_kn=bearing_capacity,
        weld_shear_capacity_kn=weld_capacity,
        governing_capacity_kn=governing,
        shear_utilisation=shear_util,
        weld_utilisation=weld_util,
        axial_bolt_utilisation=axial_util,
        overall_utilisation=overall,
        status="PASS" if overall <= 1.0 else "REVIEW",
    )


def render() -> None:
    """Render the preliminary steel connection design workspace."""
    st.title("Steel Connections")
    st.caption("Preliminary EC3 connection screening for bolted and welded load paths. Full connection detailing requires project-specific verification.")

    left, right = st.columns([1, 2], gap="large")
    with left:
        shear = st.number_input("Design shear VEd (kN)", min_value=0.0, value=120.0, step=5.0, key="sc_shear")
        axial = st.number_input("Design axial NEd (kN)", min_value=0.0, value=40.0, step=5.0, key="sc_axial")
        bolt_dia = st.number_input("Bolt diameter (mm)", min_value=6.0, value=20.0, step=1.0, key="sc_bolt_dia")
        bolt_count = st.number_input("Number of bolts", min_value=1, value=4, step=1, key="sc_bolt_count")
        bolt_fu = st.number_input("Bolt ultimate strength fu (MPa)", min_value=100.0, value=800.0, step=25.0, key="sc_bolt_fu")
        plate_t = st.number_input("Plate thickness (mm)", min_value=3.0, value=12.0, step=1.0, key="sc_plate_t")
        plate_fu = st.number_input("Plate ultimate strength fu (MPa)", min_value=200.0, value=430.0, step=10.0, key="sc_plate_fu")
        edge = st.number_input("Bolt edge distance (mm)", min_value=5.0, value=40.0, step=1.0, key="sc_edge")
        pitch = st.number_input("Bolt pitch (mm)", min_value=10.0, value=70.0, step=5.0, key="sc_pitch")
        weld_length = st.number_input("Effective weld length (mm)", min_value=10.0, value=250.0, step=10.0, key="sc_weld_length")
        weld_throat = st.number_input("Weld throat (mm)", min_value=2.0, value=6.0, step=0.5, key="sc_weld_throat")
        weld_fu = st.number_input("Weld ultimate strength (MPa)", min_value=200.0, value=430.0, step=10.0, key="sc_weld_fu")
        run = st.button("Evaluate connection", type="primary", use_container_width=True, key="sc_run")

    inputs = SteelConnectionInput(
        shear_kn=shear, axial_kn=axial, bolt_diameter_mm=bolt_dia, bolt_count=int(bolt_count),
        bolt_fu_mpa=bolt_fu, plate_thickness_mm=plate_t, plate_fu_mpa=plate_fu,
        edge_distance_mm=edge, pitch_mm=pitch, weld_length_mm=weld_length,
        weld_throat_mm=weld_throat, weld_fu_mpa=weld_fu,
    )
    result = evaluate_connection(inputs)

    with right:
        if run:
            if result.status == "PASS":
                st.success(f"Connection screening passes at utilisation {result.overall_utilisation:.2f}.")
            else:
                st.warning(f"Connection requires review at utilisation {result.overall_utilisation:.2f}.")
        else:
            st.info("Results update from the current connection inputs. Evaluate to record the current screening result.")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Governing capacity", f"{result.governing_capacity_kn:.1f} kN")
        c2.metric("Bolt shear", f"{result.bolt_shear_capacity_kn:.1f} kN")
        c3.metric("Plate bearing", f"{result.plate_bearing_capacity_kn:.1f} kN")
        c4.metric("Overall utilisation", f"{result.overall_utilisation:.2f}")

        schedule = pd.DataFrame([
            {"Check": "Bolt group shear", "Resistance (kN)": result.bolt_shear_capacity_kn, "Demand (kN)": shear, "Utilisation": result.shear_utilisation},
            {"Check": "Plate bearing", "Resistance (kN)": result.plate_bearing_capacity_kn, "Demand (kN)": shear, "Utilisation": shear / result.plate_bearing_capacity_kn},
            {"Check": "Fillet weld shear", "Resistance (kN)": result.weld_shear_capacity_kn, "Demand (kN)": shear, "Utilisation": result.weld_utilisation},
            {"Check": "Bolt axial screen", "Resistance (kN)": result.bolt_shear_capacity_kn, "Demand (kN)": axial, "Utilisation": result.axial_bolt_utilisation},
        ])
        st.subheader("Connection check schedule")
        st.dataframe(schedule.round(3), use_container_width=True, hide_index=True)

        st.subheader("Design interpretation")
        if result.overall_utilisation <= 0.75:
            st.info("The preliminary load path has useful screening reserve. Continue to detailed geometry and interaction checks.")
        elif result.overall_utilisation <= 1.0:
            st.warning("The preliminary connection is close to its screening resistance. Detailed EC3 connection verification is required.")
        else:
            st.error("The preliminary connection exceeds at least one screening resistance. Increase connection capacity or revise the load path.")
        st.caption("This screen does not cover bolt tension, combined shear/tension interaction to the full EC3 rules, block tearing, prying, slip resistance, weld eccentricity, fatigue, ductility or detailed plate failure modes.")


__all__ = ["SteelConnectionInput", "SteelConnectionResult", "plate_bearing_capacity_kn", "weld_shear_capacity_kn", "evaluate_connection", "render"]
