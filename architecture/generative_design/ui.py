"""Deterministic architectural massing candidate generator."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st


def _candidates(width: float, depth: float, setback: float, floors: int, w_solar: float, w_circ: float, w_view: float, w_cost: float) -> pd.DataFrame:
    build_w = max(1.0, width - 2.0 * setback)
    build_d = max(1.0, depth - 2.0 * setback)
    rows = []
    for index, scale in enumerate((0.72, 0.80, 0.88, 0.94, 1.00), start=1):
        footprint = build_w * build_d * scale
        aspect = max(build_w, build_d) / max(1.0, min(build_w, build_d))
        solar = max(0.0, min(1.0, 0.62 + 0.25 * (1.0 - abs(scale - 0.88)) + 0.08 * w_solar))
        circulation = max(0.0, min(1.0, 0.70 + 0.22 * (1.0 - abs(scale - 0.80)) + 0.05 * w_circ))
        regularity = max(0.0, min(1.0, 1.0 - abs(aspect - 1.5) / 3.0 + 0.05 * w_cost))
        view = max(0.0, min(1.0, 0.68 + 0.18 * (1.0 - scale) + 0.08 * w_view))
        score = 0.30 * solar + 0.25 * circulation + 0.20 * regularity + 0.15 * view + 0.10 * (1.0 - abs(scale - 0.80))
        rows.append({"Candidate": f"Layout {index:02d}", "Footprint (m²)": round(footprint, 1), "GFA (m²)": round(footprint * floors, 1), "Solar score": round(solar, 3), "Circulation score": round(circulation, 3), "Structural regularity": round(regularity, 3), "View score": round(view, 3), "Composite score": round(score, 3)})
    return pd.DataFrame(rows).sort_values("Composite score", ascending=False).reset_index(drop=True)


def render_generative_design() -> None:
    """Generate and compare deterministic massing candidates from constraints."""
    st.title("Generative Architectural Design")
    st.caption("Constraint-driven massing synthesis. Candidate scores are transparent heuristics, not an AI claim or permit-ready design.")

    left, right = st.columns([1, 2], gap="large")
    with left:
        width = st.number_input("Site width (m)", min_value=10.0, value=40.0, step=1.0, key="gd_width")
        depth = st.number_input("Site depth (m)", min_value=10.0, value=30.0, step=1.0, key="gd_depth")
        setback = st.number_input("Setback (m)", min_value=0.0, value=3.0, step=0.5, key="gd_setback")
        floors = st.number_input("Maximum storeys", min_value=1, max_value=50, value=4, step=1, key="gd_floors")
        st.markdown("**Objective weights**")
        w_solar = st.slider("Solar", 0.0, 1.0, 0.8, 0.05, key="gd_solar")
        w_circ = st.slider("Circulation", 0.0, 1.0, 0.9, 0.05, key="gd_circ")
        w_view = st.slider("Views", 0.0, 1.0, 0.6, 0.05, key="gd_view")
        w_cost = st.slider("Structural efficiency", 0.0, 1.0, 0.5, 0.05, key="gd_cost")
        generate = st.button("Generate candidates", type="primary", use_container_width=True, key="gd_generate")

    candidates = _candidates(width, depth, setback, int(floors), w_solar, w_circ, w_view, w_cost)
    best = candidates.iloc[0]
    with right:
        if generate:
            st.success("Five deterministic constrained massing candidates generated.")
        else:
            st.info("Candidates update from the current constraints. Generate to record the current comparison.")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Preferred candidate", best["Candidate"])
        m2.metric("Footprint", f"{best['Footprint (m²)']:,.0f} m²")
        m3.metric("GFA", f"{best['GFA (m²)']:,.0f} m²")
        m4.metric("Composite", f"{best['Composite score']:.3f}")
        st.dataframe(candidates, use_container_width=True, hide_index=True)
        chart = candidates.melt(id_vars="Candidate", value_vars=["Solar score", "Circulation score", "Structural regularity", "View score"], var_name="Objective", value_name="Score")
        fig = px.bar(chart, x="Candidate", y="Score", color="Objective", barmode="group", height=350)
        st.plotly_chart(fig, use_container_width=True)
        st.warning("The preferred option is an optimization heuristic. Verify geometry, setbacks, access, daylight, fire strategy, structure and local planning requirements before design development.")
