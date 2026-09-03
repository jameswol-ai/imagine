"""Preliminary HVAC load and plant sizing workspace."""
from __future__ import annotations

from dataclasses import dataclass

import plotly.graph_objects as go
import streamlit as st


@dataclass(frozen=True)
class HVACInputs:
    floor_area_m2: float
    occupancy: int
    sensible_load_w_m2: float
    fresh_air_l_s_person: float
    system_efficiency: float = 0.85


def calculate_hvac(inputs: HVACInputs) -> dict[str, float]:
    area_load_kw = inputs.floor_area_m2 * inputs.sensible_load_w_m2 / 1000.0
    people_load_kw = inputs.occupancy * 0.075
    total_kw = area_load_kw + people_load_kw
    plant_kw = total_kw / max(inputs.system_efficiency, 0.01)
    fresh_air_m3_h = inputs.occupancy * inputs.fresh_air_l_s_person * 3.6
    return {
        "area_load_kw": area_load_kw,
        "people_load_kw": people_load_kw,
        "total_load_kw": total_kw,
        "plant_capacity_kw": plant_kw,
        "fresh_air_m3_h": fresh_air_m3_h,
    }


class HVACAnalysisEngine:
    def run(self, inputs: HVACInputs | dict | None = None) -> dict[str, float]:
        if inputs is None:
            inputs = HVACInputs(1000, 80, 90, 10)
        if isinstance(inputs, dict):
            inputs = HVACInputs(**inputs)
        return calculate_hvac(inputs)


def render() -> None:
    st.subheader("HVAC Preliminary Load Study")
    st.caption("Concept-stage load screening. Final HVAC design requires climate data, envelope properties, internal gains, ventilation standards and equipment selections.")
    c1, c2 = st.columns(2)
    with c1:
        area = st.number_input("Conditioned floor area (m²)", 50.0, 1_000_000.0, 1000.0, 50.0)
        occupancy = st.number_input("Occupants", 1, 100000, 80)
    with c2:
        load = st.number_input("Sensible load allowance (W/m²)", 10.0, 500.0, 90.0, 5.0)
        fresh = st.number_input("Fresh air (L/s/person)", 2.0, 50.0, 10.0, 1.0)
    efficiency = st.slider("System allowance / efficiency", 0.50, 1.00, 0.85, 0.01)
    result = HVACAnalysisEngine().run(HVACInputs(area, occupancy, load, fresh, efficiency))
    a, b, c, d = st.columns(4)
    a.metric("Cooling load", f"{result['total_load_kw']:.1f} kW")
    b.metric("Indicative plant", f"{result['plant_capacity_kw']:.1f} kW")
    c.metric("Fresh air", f"{result['fresh_air_m3_h']:.0f} m³/h")
    d.metric("Load intensity", f"{result['total_load_kw'] / area * 1000:.0f} W/m²")
    fig = go.Figure(go.Bar(x=["Area gains", "Occupancy gains", "Plant allowance"], y=[result['area_load_kw'], result['people_load_kw'], result['plant_capacity_kw']]))
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=20, b=20), yaxis_title="kW")
    st.plotly_chart(fig, use_container_width=True)
