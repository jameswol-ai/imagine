"""Foreign-exchange scenario workspace."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st


class ForexService:
    RATES = {"USD": 1.0, "UGX": 3700.0, "KES": 129.49, "TZS": 2625.0, "RWF": 1350.0, "SSP": 4626.40}

    @classmethod
    def convert_usd(cls, amount_usd: float, currency: str) -> dict:
        if amount_usd < 0 or currency not in cls.RATES:
            raise ValueError("Amount must be non-negative and currency must be supported")
        rate = cls.RATES[currency]
        return {"currency": currency, "exchange_rate": rate, "amount_local": round(amount_usd * rate, 2)}

    @classmethod
    def supported_currencies(cls) -> list[str]:
        return list(cls.RATES)


def render() -> None:
    st.subheader("Foreign Exchange")
    st.caption("Indicative project-cost conversion. Rates are editable assumptions and must be refreshed before commercial decisions.")
    a, b = st.columns(2)
    amount = a.number_input("USD amount", min_value=0.0, value=100_000.0, step=5_000.0)
    currency = b.selectbox("Target currency", ForexService.supported_currencies(), index=1)
    result = ForexService.convert_usd(amount, currency)
    x, y = st.columns(2)
    x.metric("Exchange rate", f"{result['exchange_rate']:,.4f} {currency}/USD")
    y.metric("Converted value", f"{result['amount_local']:,.2f} {currency}")
    rows = [{"Currency": code, "Rate / USD": rate, "Converted Amount": round(amount * rate, 2)} for code, rate in ForexService.RATES.items()]
    data = pd.DataFrame(rows)
    st.dataframe(data, use_container_width=True, hide_index=True)
    st.plotly_chart(px.bar(data, x="Currency", y="Converted Amount", title="Equivalent project value by currency"), use_container_width=True)
