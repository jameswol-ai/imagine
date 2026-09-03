"""Preliminary electrical load and transformer sizing workspace."""

from __future__ import annotations

import math

import pandas as pd
import plotly.express as px
import streamlit as st


class ElectricalService:
    LOAD_DENSITIES = {"Residential": 35, "Commercial": 65, "Industrial": 85}

    @classmethod
    def connected_load(cls, area_m2, occupancy_type="Commercial", power_factor=0.85):
        density = cls.LOAD_DENSITIES.get(occupancy_type, 50)
        connected_kw = area_m2 * density / 1000.0
        connected_kva = connected_kw / max(power_factor, 0.01)
        return {"connected_kw": round(connected_kw, 2), "connected_kva": round(connected_kva, 2)}

    @staticmethod
    def transformer_sizing(demand_kva):
        return {"transformer_kva": math.ceil(demand_kva / 50.0) * 50}

    @staticmethod
    def demand_load(connected_kva, diversity_factor=0.80):
        return {"demand_kva": round(connected_kva * diversity_factor, 2)}


def render() -> None:
    st.subheader("Electrical Load Analysis")
    st.caption("Preliminary connected-load and demand screening. Final electrical design requires the project equipment schedule, supply characteristics, applicable standards and specialist verification.")

    c1, c2 = st.columns(2)
    with c1:
        area = st.number_input("Floor area (m²)", min_value=1.0, value=1000.0, step=50.0)
        occupancy = st.selectbox("Occupancy type", list(ElectricalService.LOAD_DENSITIES))
    with c2:
        pf = st.number_input("Power factor", min_value=0.50, max_value=1.00, value=0.85, step=0.01)
        diversity = st.number_input("Diversity factor", min_value=0.10, max_value=1.00, value=0.80, step=0.05)

    connected = ElectricalService.connected_load(area, occupancy, pf)
    demand = ElectricalService.demand_load(connected["connected_kva"], diversity)
    transformer = ElectricalService.transformer_sizing(demand["demand_kva"])

    a, b, c = st.columns(3)
    a.metric("Connected load", f"{connected['connected_kw']:,.1f} kW")
    b.metric("Maximum demand", f"{demand['demand_kva']:,.1f} kVA")
    c.metric("Indicative transformer", f"{transformer['transformer_kva']:,.0f} kVA")

    frame = pd.DataFrame({"Indicator": ["Connected kVA", "Demand kVA", "Transformer kVA"], "Value": [connected["connected_kva"], demand["demand_kva"], transformer["transformer_kva"]]})
    st.plotly_chart(px.bar(frame, x="Indicator", y="Value", title="Electrical capacity screening"), use_container_width=True)
    st.dataframe(frame, use_container_width=True, hide_index=True)


__all__ = ["ElectricalService", "render"]
