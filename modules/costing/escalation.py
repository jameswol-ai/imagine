"""Cost escalation workspace for preliminary project estimates."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st


class EscalationService:
    @staticmethod
    def escalate_cost(base_cost: float, inflation_rate: float, years: int) -> dict:
        if base_cost < 0 or inflation_rate < 0 or years < 0:
            raise ValueError("Cost, inflation rate and years must be non-negative")
        future_cost = base_cost * ((1 + inflation_rate) ** years)
        return {"base_cost": base_cost, "inflation_rate": inflation_rate, "years": years, "future_cost": round(future_cost, 2)}


def render() -> None:
    st.subheader("Inflation / Escalation")
    st.caption("Scenario tool for preliminary estimating. Replace assumptions with contract indices and project-specific escalation clauses.")
    a, b, c = st.columns(3)
    base = a.number_input("Base cost", min_value=0.0, value=1_000_000.0, step=10_000.0)
    rate = b.number_input("Annual escalation (%)", min_value=0.0, value=5.0, step=0.5) / 100
    years = c.number_input("Years", min_value=0, value=3, step=1)
    result = EscalationService.escalate_cost(base, rate, int(years))
    x, y, z = st.columns(3)
    x.metric("Base", f"{base:,.2f}")
    y.metric("Escalated", f"{result['future_cost']:,.2f}")
    z.metric("Increase", f"{result['future_cost'] - base:,.2f}")
    rows = [{"Year": i, "Projected Cost": round(base * ((1 + rate) ** i), 2)} for i in range(int(years) + 1)]
    data = pd.DataFrame(rows)
    st.dataframe(data, use_container_width=True, hide_index=True)
    st.plotly_chart(px.line(data, x="Year", y="Projected Cost", markers=True, title="Escalation curve"), use_container_width=True)
