"""Streamlit workspace for preliminary structural analysis."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from .fea_engine import SimplySupportedBeamInput, analyse_simply_supported_beam


def render() -> None:
    """Render the preliminary structural analysis workspace."""
    st.title("Structural Analysis")
    st.caption(
        "Preliminary 2D simply supported beam analysis using the IMAGINE analysis kernel. "
        "This is not a general finite-element solver."
    )

    with st.form("structural_analysis_form"):
        c1, c2 = st.columns(2)
        with c1:
            span = st.number_input("Span (m)", min_value=0.1, value=6.0, step=0.1)
            udl = st.number_input("Uniform load (kN/m)", min_value=0.0, value=10.0, step=0.5)
        with c2:
            e = st.number_input("Elastic modulus (GPa)", min_value=0.001, value=30.0, step=1.0)
            inertia = st.number_input("Second moment of area (m⁴)", min_value=1e-9, value=0.00008, format="%.8f")
        submitted = st.form_submit_button("Run Analysis", use_container_width=True)

    if not submitted:
        st.info("Enter analysis inputs and run the preliminary solver.")
        return

    try:
        result = analyse_simply_supported_beam(
            SimplySupportedBeamInput(
                span_m=float(span),
                udl_kn_m=float(udl),
                elastic_modulus_gpa=float(e),
                second_moment_m4=float(inertia),
            )
        )
    except ValueError as exc:
        st.error(str(exc))
        return

    st.subheader("Analysis results")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Left reaction", f"{result.reaction_left_kn:.2f} kN")
    k2.metric("Right reaction", f"{result.reaction_right_kn:.2f} kN")
    k3.metric("Max moment", f"{result.maximum_moment_kn_m:.2f} kN·m")
    k4.metric("Max deflection", f"{result.maximum_deflection_mm:.2f} mm")

    rows = [
        {"Result": "Left reaction", "Value": result.reaction_left_kn, "Unit": "kN"},
        {"Result": "Right reaction", "Value": result.reaction_right_kn, "Unit": "kN"},
        {"Result": "Maximum shear", "Value": result.maximum_shear_kn, "Unit": "kN"},
        {"Result": "Maximum moment", "Value": result.maximum_moment_kn_m, "Unit": "kN·m"},
        {"Result": "Maximum deflection", "Value": result.maximum_deflection_mm, "Unit": "mm"},
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    chart = px.bar(pd.DataFrame(rows), x="Result", y="Value", text="Value", title="Analysis result magnitudes")
    chart.update_layout(xaxis_title="Result", yaxis_title="Numerical value")
    st.plotly_chart(chart, use_container_width=True)

    st.info(
        "Engineering scope: linear elastic, simply supported beam, uniformly distributed load. "
        "The kernel does not currently cover frames, plates, shells, nonlinear behaviour, dynamics, "
        "mesh convergence, load combinations or code-based member design."
    )


__all__ = ["render"]
