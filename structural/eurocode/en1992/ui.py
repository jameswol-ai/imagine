"""
Consuming Global State in EN 1992
Path: structural/eurocode/en1992/ui.py
App: imagine
"""

import streamlit as st
from structural.eurocode.config import get_active_factors, get_unit_labels


def render_en1992() -> None:
    # Retrieve global settings dynamically
    factors = get_active_factors()
    units = get_unit_labels()

    gamma_c = factors["gamma_c"]
    gamma_s = factors["gamma_s"]

    st.write(
        f"Active Safety Factors ({st.session_state.national_annex}): "
        f"**γc = {gamma_c:.2f}**, **γs = {gamma_s:.2f}**"
    )

    # Inputs automatically format labels using global units dict
    col1, col2 = st.columns(2)
    with col1:
        m_ed = st.number_input(
            f"Design Bending Moment M_Ed ({units['moment']})",
            min_value=0.0,
            value=175.0,
        )
    with col2:
        width_b = st.number_input(
            f"Section Width b ({units['section_dim']})",
            min_value=100,
            value=300,
        )
