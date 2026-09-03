"""Preliminary water-supply and plumbing demand workspace."""

from __future__ import annotations

import math

import pandas as pd
import plotly.express as px
import streamlit as st


class PlumbingService:
    @staticmethod
    def water_demand(occupants: int, litres_per_person: float = 150) -> dict:
        if occupants < 1:
            raise ValueError("Occupants must be at least 1.")
        daily = occupants * litres_per_person
        return {"occupants": occupants, "daily_demand_liters": round(daily, 2)}

    @staticmethod
    def wsfu(bathrooms: int, area_m2: float) -> dict:
        if bathrooms < 1 or area_m2 <= 0:
            raise ValueError("Bathrooms must be at least 1 and area must be positive.")
        units = bathrooms * 8 + math.ceil(area_m2 / 100.0) * 4
        peak_flow = math.sqrt(units) * 0.25
        return {"wsfu": units, "peak_flow_lps": round(peak_flow, 2)}


def render() -> None:
    st.subheader("Water Supply & Drainage Screening")
    st.caption("Preliminary domestic water demand and fixture-unit screening. Final pipe sizing, storage, drainage gradients and sanitary design require project-specific standards and specialist verification.")

    c1, c2 = st.columns(2)
    with c1:
        occupants = st.number_input("Occupants", min_value=1, value=80, step=1)
        litres = st.number_input("Water allowance (L/person/day)", min_value=10.0, value=150.0, step=5.0)
    with c2:
        area = st.number_input("Floor area (m²)", min_value=1.0, value=1000.0, step=50.0)
        bathrooms = st.number_input("Bathrooms / fixture groups", min_value=1, value=8, step=1)

    demand = PlumbingService.water_demand(occupants, litres)
    fixture = PlumbingService.wsfu(bathrooms, area)
    peak_daily = demand["daily_demand_liters"]

    a, b, c = st.columns(3)
    a.metric("Daily demand", f"{peak_daily:,.0f} L/day")
    b.metric("Fixture units", f"{fixture['wsfu']:,.0f}")
    c.metric("Peak flow", f"{fixture['peak_flow_lps']:.2f} L/s")

    frame = pd.DataFrame({"Indicator": ["Daily water demand (L/day)", "Fixture units", "Peak flow (L/s)"], "Value": [peak_daily, fixture["wsfu"], fixture["peak_flow_lps"]]})
    st.plotly_chart(px.bar(frame, x="Indicator", y="Value", title="Plumbing demand indicators"), use_container_width=True)
    st.dataframe(frame, use_container_width=True, hide_index=True)


__all__ = ["PlumbingService", "render"]
