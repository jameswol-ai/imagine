"""Integrated preliminary MEP analysis workspace.

The calculation helpers in this module are screening-level engineering tools.
Project-specific standards, climate data, equipment selections, diversity,
ventilation requirements and professional verification remain necessary for
final design.
"""

from __future__ import annotations

import math

import pandas as pd
import plotly.express as px
import streamlit as st

from modules.mep.electrical import ElectricalService
from modules.mep.hvac import HVACService
from modules.mep.plumbing import PlumbingService


class MEPAnalysis:
    HVAC_DENSITIES = {
        "Residential": 120,
        "Commercial": 160,
        "Industrial": 100,
    }

    ELECTRICAL_DENSITIES = {
        "Residential": 35,
        "Commercial": 65,
        "Industrial": 85,
    }

    @classmethod
    def cooling_load(cls, area_m2: float, occupancy_type: str = "Residential") -> dict:
        density = cls.HVAC_DENSITIES.get(occupancy_type, 120)
        cooling_kw = area_m2 * density / 1000.0
        cooling_tr = cooling_kw / 3.517
        airflow_cfm = cooling_tr * 400
        return {
            "area_m2": round(area_m2, 2),
            "cooling_kw": round(cooling_kw, 2),
            "cooling_tr": round(cooling_tr, 2),
            "airflow_cfm": round(airflow_cfm, 0),
        }

    @classmethod
    def electrical_load(
        cls,
        area_m2: float,
        occupancy_type: str = "Residential",
        power_factor: float = 0.85,
    ) -> dict:
        density = cls.ELECTRICAL_DENSITIES.get(occupancy_type, 50)
        connected_kw = area_m2 * density / 1000.0
        connected_kva = connected_kw / max(power_factor, 0.01)
        return {
            "connected_kw": round(connected_kw, 2),
            "connected_kva": round(connected_kva, 2),
        }

    @staticmethod
    def maximum_demand(connected_kva: float, diversity_factor: float = 0.8) -> dict:
        demand_kva = connected_kva * diversity_factor
        transformer = math.ceil((demand_kva * 1.25) / 50.0) * 50
        return {"max_demand_kva": round(demand_kva, 2), "transformer_kva": transformer}

    @staticmethod
    def plumbing_demand(occupants: int, litres_per_person: float = 150) -> dict:
        daily_demand = occupants * litres_per_person
        return {"occupants": occupants, "daily_demand_liters": round(daily_demand, 2)}

    @staticmethod
    def wsfu_calculation(bathrooms: int, area_m2: float) -> dict:
        wsfu = bathrooms * 8 + math.ceil(area_m2 / 100.0) * 4
        peak_flow = math.sqrt(wsfu) * 0.25
        return {"wsfu": wsfu, "peak_flow_lps": round(peak_flow, 2)}

    @classmethod
    def full_building_analysis(
        cls,
        area_m2: float,
        occupancy_type: str,
        occupants: int,
        bathrooms: int,
    ) -> dict:
        hvac = cls.cooling_load(area_m2, occupancy_type)
        electrical = cls.electrical_load(area_m2, occupancy_type)
        demand = cls.maximum_demand(electrical["connected_kva"])
        plumbing = cls.plumbing_demand(occupants)
        wsfu = cls.wsfu_calculation(bathrooms, area_m2)
        return {
            "hvac": hvac,
            "electrical": electrical,
            "demand": demand,
            "plumbing": plumbing,
            "wsfu": wsfu,
        }


def _engine_analysis(area: float, occupancy_type: str, occupants: int, bathrooms: int) -> dict:
    """Use the specialist services where available, with the integrated engine as fallback."""
    try:
        hvac = HVACService.cooling_load(area, occupancy_type)
    except (AttributeError, TypeError):
        hvac = MEPAnalysis.cooling_load(area, occupancy_type)

    try:
        electrical = ElectricalService.connected_load(area, occupancy_type)
        demand = ElectricalService.demand_load(electrical["connected_kva"])
        transformer = ElectricalService.transformer_sizing(demand["demand_kva"])
    except (AttributeError, TypeError):
        electrical = MEPAnalysis.electrical_load(area, occupancy_type)
        demand = MEPAnalysis.maximum_demand(electrical["connected_kva"])
        transformer = {"transformer_kva": demand["transformer_kva"]}

    try:
        plumbing = PlumbingService.water_demand(occupants)
    except (AttributeError, TypeError):
        plumbing = MEPAnalysis.plumbing_demand(occupants)

    try:
        wsfu = PlumbingService.wsfu(bathrooms, area)
    except (AttributeError, TypeError):
        wsfu = MEPAnalysis.wsfu_calculation(bathrooms, area)

    return {
        "HVAC": hvac,
        "Electrical": {**electrical, **demand, **transformer},
        "Plumbing": plumbing,
        "Water supply": wsfu,
    }


def render() -> None:
    st.subheader("Integrated MEP Analysis")
    st.caption("Preliminary coordination workspace for HVAC, electrical and plumbing demand. Validate final systems against the applicable project standards and specialist design requirements.")

    with st.form("mep_integrated_analysis"):
        c1, c2 = st.columns(2)
        with c1:
            area = st.number_input("Building floor area (m²)", min_value=1.0, value=1000.0, step=50.0)
            occupants = st.number_input("Occupants", min_value=1, value=80, step=1)
        with c2:
            occupancy_type = st.selectbox("Occupancy type", ["Residential", "Commercial", "Industrial"])
            bathrooms = st.number_input("Bathrooms / fixture groups", min_value=1, value=8, step=1)
        submitted = st.form_submit_button("Run MEP analysis", type="primary", use_container_width=True)

    if "mep_result" not in st.session_state or submitted:
        st.session_state.mep_result = _engine_analysis(area, occupancy_type, occupants, bathrooms)

    result = st.session_state.mep_result
    hvac = result["HVAC"]
    electrical = result["Electrical"]
    plumbing = result["Plumbing"]
    water = result["Water supply"]

    cooling_kw = float(hvac.get("cooling_kw", hvac.get("total_load_kw", 0.0)))
    connected_kva = float(electrical.get("connected_kva", 0.0))
    demand_kva = float(electrical.get("demand_kva", electrical.get("max_demand_kva", 0.0)))
    daily_water = float(plumbing.get("daily_demand_liters", plumbing.get("daily_demand_liters_day", 0.0)))
    peak_flow = float(water.get("peak_flow_lps", 0.0))

    a, b, c, d = st.columns(4)
    a.metric("Cooling", f"{cooling_kw:,.1f} kW")
    b.metric("Connected", f"{connected_kva:,.1f} kVA")
    c.metric("Maximum demand", f"{demand_kva:,.1f} kVA")
    d.metric("Water demand", f"{daily_water:,.0f} L/day")

    chart_df = pd.DataFrame({"System": ["HVAC", "Electrical demand", "Water peak flow"], "Value": [cooling_kw, demand_kva, peak_flow]})
    st.plotly_chart(px.bar(chart_df, x="System", y="Value", title="Integrated MEP screening indicators"), use_container_width=True)

    st.subheader("Calculated outputs")
    st.dataframe(
        pd.DataFrame([
            {"System": "HVAC", "Primary result": f"{cooling_kw:.2f} kW", "Detail": str(hvac)},
            {"System": "Electrical", "Primary result": f"{demand_kva:.2f} kVA", "Detail": str(electrical)},
            {"System": "Plumbing", "Primary result": f"{daily_water:.0f} L/day", "Detail": str(plumbing)},
            {"System": "Water supply", "Primary result": f"{peak_flow:.2f} L/s", "Detail": str(water)},
        ]),
        use_container_width=True,
        hide_index=True,
    )


__all__ = ["MEPAnalysis", "render"]
