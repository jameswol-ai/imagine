"""Preliminary equivalent-static seismic action workspace."""
from __future__ import annotations
import pandas as pd
import streamlit as st
from modules.structural.ec8 import SeismicInput, distribute_storey_forces_kn


def render() -> None:
    st.title("Seismic Actions")
    st.caption("Preliminary EN 1998 equivalent-static base shear and storey-force distribution.")
    c1, c2 = st.columns(2)
    with c1:
        coefficient = st.number_input("Seismic coefficient", min_value=0.0, value=0.12, step=0.01)
        q = st.number_input("Behaviour factor q", min_value=1.0, value=3.0, step=0.1)
        importance = st.number_input("Importance factor", min_value=0.1, value=1.0, step=0.1)
    with c2:
        masses_text = st.text_input("Storey masses (t), comma separated", value="100,100,100")
        heights_text = st.text_input("Storey heights (m), comma separated", value="3,6,9")
    try:
        masses = [float(x.strip()) for x in masses_text.split(",") if x.strip()]
        heights = [float(x.strip()) for x in heights_text.split(",") if x.strip()]
        if len(masses) != len(heights) or not masses:
            raise ValueError("Mass and height lists must have the same non-zero length.")
        seismic = SeismicInput(coefficient=coefficient, mass=sum(masses), q=q, importance=importance)
        base_shear = seismic.design_base_shear_kn()
        forces = distribute_storey_forces_kn(base_shear, masses, heights)
        table = pd.DataFrame({"Storey": range(1, len(masses) + 1), "Mass (t)": masses, "Height (m)": heights, "Force (kN)": forces})
        a, b = st.columns(2)
        a.metric("Design base shear", f"{base_shear:.1f} kN")
        b.metric("Storeys", len(masses))
        st.dataframe(table, use_container_width=True, hide_index=True)
    except (ValueError, TypeError, ZeroDivisionError) as exc:
        st.error(str(exc))
    st.warning("Preliminary seismic screening only. Confirm hazard parameters, soil class, spectrum, ductility class, accidental torsion, second-order effects and the adopted EN 1998 National Annex before design use.")


__all__ = ["render"]
