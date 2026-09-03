"""Bill of quantities and quantity-takeoff workspace."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import plotly.express as px
import streamlit as st


@dataclass(frozen=True)
class BOQItem:
    description: str
    quantity: float
    unit: str
    rate: float

    @property
    def amount(self) -> float:
        return self.quantity * self.rate


class BoQEngine:
    DEFAULT_ITEMS = [
        BOQItem("Concrete", 120.0, "m³", 145.0),
        BOQItem("Reinforcement", 18.0, "t", 1200.0),
        BOQItem("Formwork", 850.0, "m²", 28.0),
    ]

    def run(self, items: list[BOQItem] | None = None) -> dict:
        if items is None:
            items = list(self.DEFAULT_ITEMS)
        rows = [{"Description": x.description, "Quantity": x.quantity, "Unit": x.unit, "Rate": x.rate, "Amount": x.amount} for x in items]
        return {"items": rows, "subtotal": round(sum(x["Amount"] for x in rows), 2)}


def render() -> None:
    st.subheader("Bill of Quantities / Quantity Takeoff")
    st.caption("Editable concept-stage schedule. Rates are allowances and should be replaced by the approved rate library or tender rates.")
    if "boq_rows" not in st.session_state:
        st.session_state.boq_rows = pd.DataFrame([x.__dict__ for x in BoQEngine.DEFAULT_ITEMS])
    edited = st.data_editor(st.session_state.boq_rows, num_rows="dynamic", use_container_width=True, hide_index=True, key="boq_editor")
    st.session_state.boq_rows = edited.copy()
    rows: list[BOQItem] = []
    for record in edited.fillna(0).to_dict("records"):
        description = str(record.get("description", record.get("Description", ""))).strip()
        if not description:
            continue
        quantity = float(record.get("quantity", record.get("Quantity", 0)) or 0)
        rate = float(record.get("rate", record.get("Rate", 0)) or 0)
        unit = str(record.get("unit", record.get("Unit", "item")))
        if quantity < 0 or rate < 0:
            st.error("Quantity and rate cannot be negative.")
            return
        rows.append(BOQItem(description, quantity, unit, rate))
    result = BoQEngine().run(rows)
    detail = pd.DataFrame(result["items"])
    a, b, c = st.columns(3)
    a.metric("Measured items", len(rows))
    b.metric("Subtotal", f"{result['subtotal']:,.2f}")
    c.metric("Average item", f"{result['subtotal'] / len(rows):,.2f}" if rows else "0.00")
    if detail.empty:
        st.info("Add a quantity item to begin the takeoff.")
        return
    st.dataframe(detail, use_container_width=True, hide_index=True)
    st.plotly_chart(px.bar(detail, x="Description", y="Amount", title="Cost distribution"), use_container_width=True)
