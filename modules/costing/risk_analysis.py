"""Cost risk and contingency workspace."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st


class RiskAnalysisService:
    @staticmethod
    def contingency(project_cost: float, risk_percentage: float = 0.10) -> dict:
        if project_cost < 0 or not 0 <= risk_percentage <= 1:
            raise ValueError("Project cost must be non-negative and risk must be between 0 and 100%")
        contingency = project_cost * risk_percentage
        return {"base_cost": project_cost, "risk_percentage": risk_percentage, "contingency": round(contingency, 2), "recommended_budget": round(project_cost + contingency, 2)}

    @staticmethod
    def risk_rating(risk_percentage: float) -> str:
        if risk_percentage < 0.05:
            return "Low"
        if risk_percentage < 0.15:
            return "Medium"
        return "High"


def render() -> None:
    st.subheader("Cost Risk Analysis")
    st.caption("Preliminary contingency scenario. Use a structured risk register and project-specific risk model for commercial decisions.")
    a, b = st.columns(2)
    cost = a.number_input("Base project cost", min_value=0.0, value=2_000_000.0, step=50_000.0)
    risk = b.slider("Contingency / risk allowance (%)", 0.0, 50.0, 10.0, 0.5) / 100
    result = RiskAnalysisService.contingency(cost, risk)
    x, y, z = st.columns(3)
    x.metric("Risk rating", RiskAnalysisService.risk_rating(risk))
    y.metric("Contingency", f"{result['contingency']:,.2f}")
    z.metric("Recommended budget", f"{result['recommended_budget']:,.2f}")
    scenarios = pd.DataFrame([{"Risk": p, "Contingency": cost * p / 100, "Budget": cost * (1 + p / 100)} for p in range(0, 51, 5)])
    st.dataframe(scenarios, use_container_width=True, hide_index=True)
    st.plotly_chart(px.line(scenarios, x="Risk", y="Budget", markers=True, title="Budget sensitivity to risk allowance"), use_container_width=True)
