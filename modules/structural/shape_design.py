"""Streamlit structural section-shape workspace."""
from __future__ import annotations
import pandas as pd
import streamlit as st
from modules.structural.section_shapes import CircularSection, RectangularSection, section_catalogue

def render() -> None:
    st.title("Structural Section Shapes")
    st.caption("Section-property calculator and shape catalogue for preliminary beam, column and member sizing.")
    shape = st.selectbox("Shape", ["Rectangular", "Circular", "Catalogue"])
    if shape == "Rectangular":
        b = st.number_input("Width b (mm)", min_value=50.0, value=300.0, step=10.0)
        h = st.number_input("Depth h (mm)", min_value=50.0, value=500.0, step=10.0)
        s = RectangularSection(b, h)
        st.dataframe(pd.DataFrame([["Area", s.area_mm2, "mm²"], ["Ix", s.ix_mm4, "mm⁴"], ["Iy", s.iy_mm4, "mm⁴"], ["rx", s.rx_mm, "mm"], ["ry", s.ry_mm, "mm"], ["Zx", s.z_x_mm3, "mm³"], ["Zy", s.z_y_mm3, "mm³"]], columns=["Property", "Value", "Unit"]), use_container_width=True, hide_index=True)
    elif shape == "Circular":
        d = st.number_input("Diameter D (mm)", min_value=50.0, value=400.0, step=10.0)
        s = CircularSection(d)
        st.dataframe(pd.DataFrame([["Area", s.area_mm2, "mm²"], ["I", s.i_mm4, "mm⁴"], ["r", s.r_mm, "mm"], ["Z", s.z_mm3, "mm³"]], columns=["Property", "Value", "Unit"]), use_container_width=True, hide_index=True)
    else:
        st.dataframe(pd.DataFrame(section_catalogue()), use_container_width=True, hide_index=True)

__all__ = ["render"]
