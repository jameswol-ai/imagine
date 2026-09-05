"""Transparent project and cost forecasting workspace."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st


class ForecastingService:
    @staticmethod
    def linear_forecast(current_value: float, growth_rate: float, periods: int) -> list[float]:
        results: list[float] = []
        value = float(current_value)
        for _ in range(int(periods)):
            value *= 1 + float(growth_rate)
            results.append(round(value, 2))
        return results


def render() -> None:
    st.subheader("Forecasting")
    st.caption("Scenario forecasting using a transparent compound-growth assumption. This is planning analysis, not a prediction guarantee.")
    a, b, c = st.columns(3)
    current = a.number_input("Current value", min_value=0.0, value=100000.0, step=1000.0)
    growth = b.number_input("Annual growth", min_value=-0.99, max_value=5.0, value=0.05, step=0.01, format="%.2f")
    periods = c.number_input("Periods", min_value=1, max_value=30, value=5, step=1)
    values = ForecastingService.linear_forecast(current, growth, periods)
    frame = pd.DataFrame({"Period": range(1, periods + 1), "Forecast": values})
    st.metric("Terminal value", f"{values[-1]:,.2f}")
    st.plotly_chart(px.line(frame, x="Period", y="Forecast", markers=True, title="Forecast trajectory"), use_container_width=True)
    st.dataframe(frame, hide_index=True, use_container_width=True)


__all__ = ["ForecastingService", "render"]
