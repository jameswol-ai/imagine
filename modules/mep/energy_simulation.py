"""Preliminary building energy-performance workspace."""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import plotly.express as px
import streamlit as st


class EnergySimulationService:
    @staticmethod
    def annual_energy_use(area_m2, eui=180):
        return {"area_m2": area_m2, "eui": eui, "annual_energy_kwh": round(area_m2 * eui, 2)}

    @staticmethod
    def carbon_emissions(annual_energy_kwh, emission_factor=0.35):
        emissions = annual_energy_kwh * emission_factor
        return {"co2_kg": round(emissions, 2), "co2_tonnes": round(emissions / 1000.0, 2)}

    @staticmethod
    def building_performance(area_m2):
        energy = EnergySimulationService.annual_energy_use(area_m2)
        carbon = EnergySimulationService.carbon_emissions(energy["annual_energy_kwh"])
        return {"generated_at": datetime.now(timezone.utc).isoformat(), "energy": energy, "carbon": carbon}


def render() -> None:
    st.subheader("Building Energy Simulation")
    st.caption("Preliminary energy-use and carbon screening using an assumed EUI and emission factor. A validated simulation requires climate, envelope, schedules, systems and calibrated assumptions.")

    c1, c2 = st.columns(2)
    with c1:
        area = st.number_input("Floor area (m²)", min_value=1.0, value=1000.0, step=50.0)
        eui = st.number_input("Energy use intensity (kWh/m²/year)", min_value=1.0, value=180.0, step=5.0)
    with c2:
        factor = st.number_input("Emission factor (kg CO₂/kWh)", min_value=0.0, value=0.35, step=0.01)
        operating_years = st.number_input("Assessment period (years)", min_value=1, value=1, step=1)

    energy = EnergySimulationService.annual_energy_use(area, eui)
    carbon = EnergySimulationService.carbon_emissions(energy["annual_energy_kwh"], factor)
    period_energy = energy["annual_energy_kwh"] * operating_years
    period_carbon = carbon["co2_kg"] * operating_years

    a, b, c, d = st.columns(4)
    a.metric("Annual energy", f"{energy['annual_energy_kwh']:,.0f} kWh")
    b.metric("EUI", f"{energy['eui']:,.0f} kWh/m²/yr")
    c.metric("Annual carbon", f"{carbon['co2_tonnes']:,.2f} tCO₂")
    d.metric("Assessment carbon", f"{period_carbon / 1000:,.2f} tCO₂")

    frame = pd.DataFrame({"Metric": ["Annual energy", "Assessment-period energy", "Annual carbon", "Assessment-period carbon"], "Value": [energy["annual_energy_kwh"], period_energy, carbon["co2_kg"], period_carbon]})
    st.plotly_chart(px.bar(frame, x="Metric", y="Value", title="Energy and carbon screening"), use_container_width=True)
    st.dataframe(frame, use_container_width=True, hide_index=True)


__all__ = ["EnergySimulationService", "render"]
