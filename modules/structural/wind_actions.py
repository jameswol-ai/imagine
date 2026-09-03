"""Preliminary wind pressure and line-load workspace."""
from __future__ import annotations
import pandas as pd
import streamlit as st


def render() -> None:
    st.title("Wind Actions")
    st.caption("Preliminary wind pressure workflow. This workspace exposes assumptions rather than hiding them.")
    c1, c2 = st.columns(2)
    with c1:
        vb = st.number_input("Basic wind velocity vb (m/s)", min_value=1.0, value=25.0, step=1.0)
        rho = st.number_input("Air density rho (kg/m³)", min_value=0.5, value=1.25, step=0.05)
        ce = st.number_input("Exposure coefficient ce", min_value=0.1, value=1.0, step=0.05)
    with c2:
        cdir = st.number_input("Direction coefficient cdir", min_value=0.1, value=1.0, step=0.05)
        cseason = st.number_input("Season coefficient cseason", min_value=0.1, value=1.0, step=0.05)
        cp = st.number_input("Pressure coefficient cp", min_value=-3.0, max_value=3.0, value=0.8, step=0.05)
        tributary = st.number_input("Tributary width (m)", min_value=0.1, value=3.0, step=0.1)
    vb_eff = vb * cdir * cseason
    qp = 0.5 * rho * vb_eff**2 / 1000.0
    pressure = qp * ce * cp
    line = pressure * tributary
    a, b, c = st.columns(3)
    a.metric("Velocity", f"{vb_eff:.2f} m/s")
    b.metric("Velocity pressure", f"{qp:.3f} kN/m²")
    c.metric("Surface pressure", f"{pressure:.3f} kN/m²")
    st.dataframe(pd.DataFrame([["Wind pressure", pressure, "kN/m²"], ["Tributary line load", line, "kN/m"], ["Direction coefficient", cdir, "-"], ["Exposure coefficient", ce, "-"]], columns=["Parameter", "Value", "Unit"]), use_container_width=True, hide_index=True)
    st.warning("Preliminary calculation only. Terrain, altitude, orography, turbulence, external/internal pressure, dynamic response and the adopted EN 1991-1-4 National Annex must be checked for final design.")


__all__ = ["render"]
