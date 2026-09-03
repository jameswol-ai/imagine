"""Preliminary reinforced-concrete detailing checks and schedules."""
from __future__ import annotations
import math
import pandas as pd
import streamlit as st


def render() -> None:
    st.title("RC Detailing")
    st.caption("Preliminary reinforcement detailing checks for spacing, cover and bar-area schedules.")
    c1, c2 = st.columns(2)
    with c1:
        width = st.number_input("Member width (mm)", min_value=100.0, value=300.0, step=25.0)
        depth = st.number_input("Member depth (mm)", min_value=100.0, value=500.0, step=25.0)
        cover = st.number_input("Nominal cover (mm)", min_value=10.0, value=30.0, step=5.0)
    with c2:
        diameter = st.number_input("Bar diameter (mm)", min_value=6.0, value=16.0, step=2.0)
        spacing = st.number_input("Bar spacing (mm)", min_value=50.0, value=200.0, step=10.0)
    count = max(2, math.floor((width - 2 * cover) / spacing) + 1)
    area_bar = math.pi * diameter**2 / 4.0
    area_total = count * area_bar
    clear_spacing = (width - 2 * cover - count * diameter) / max(count - 1, 1)
    a, b, c = st.columns(3)
    a.metric("Bars", count)
    b.metric("Steel area", f"{area_total:.0f} mm²")
    c.metric("Clear spacing", f"{clear_spacing:.0f} mm")
    table = pd.DataFrame([
        ["Section", f"{width:.0f} x {depth:.0f} mm", ""],
        ["Nominal cover", cover, "mm"],
        ["Bar arrangement", f"{count}T{diameter:.0f}", ""],
        ["Nominal spacing", spacing, "mm"],
        ["Clear spacing", clear_spacing, "mm"],
        ["Total bar area", area_total, "mm²"],
    ], columns=["Item", "Value", "Unit"])
    st.dataframe(table, use_container_width=True, hide_index=True)
    if clear_spacing <= 0:
        st.error("The selected bars do not physically fit inside the specified width and cover.")
    else:
        st.success("Preliminary geometric detailing arrangement is feasible.")
    st.warning("This is a detailing aid, not a complete EN 1992 detailing check. Verify minimum/maximum reinforcement, anchorage, laps, confinement, spacing limits, durability exposure and the adopted National Annex.")


__all__ = ["render"]
