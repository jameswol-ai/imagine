"""Preliminary bill-of-quantities workspace."""
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
    def run(self, items: list[BOQItem] | None = None) -> dict:
        items = items or [BOQItem("Concrete", 120, "m³", 145.0), BOQItem("Reinforcement", 18, "t", 1200.0), BOQItem("Formwork", 850, "m²", 28.0)]
        rows = [{"Description": x.description, "Quantity": x.quantity, "Unit": x.unit, "Rate": x.rate, "Amount": x.amount} for x in items]
        total = sum(x["Amount"] for x in rows)
        return {"items": rows, "subtotal": total}


def render() -> None:
    st.subheader("Bill of Quantities")
    st.caption("Editable concept-stage quantity and rate schedule. Rates are user-supplied allowances, not market quotations.")
    if "boq_rows" not in st.session_state:
        st.session_state.boq_rows = pd.DataFrame([
            {"Description": "Concrete", "Quantity": 120.0, "Unit": "m³", "Rate": 145.0},
            {"Description": "Reinforcement", "Quantity": 18.0, "Unit": "t", "Rate": 1200.0},
            {"Description": "Formwork", "Quantity": 850.0, "Unit": "m²", "Rate": 28.0},
        ])
    edited = st.data_editor(st.session_state.boq_rows, num_rows="dynamic", use_container_width=True, hide_index=True)
    rows = []
    for record in edited.fillna(0).to_dict("records"):
        if str(record.get("Description", "")).strip():
            rows.append(BOQItem(str(record["Description"]), float(record.get("Quantity", 0)), str(record.get("Unit", "item")), float(record.get("Rate", 0))))
    result = BoQEngine().run(rows)
    total = result["subtotal"]
    a, b, c = st.columns(3)
    a.metric("Items", len(rows))
    b.metric("Subtotal", f"{total:,.2f}")
    c.metric("Average item", f"{total / len(rows):,.2f}" if rows else "0.00")
    detail = pd.DataFrame(result["items"])
    if not detail.empty:
        st.dataframe(detail, use_container_width=True, hide_index=True)
        fig = px.bar(detail, x="Description", y="Amount", title="Cost distribution")
        st.plotly_chart(fig, use_container_width=True)
