"""
Updated Router Integration
Path: structural/eurocode/router.py
App: imagine
"""

import streamlit as st
from structural.eurocode.config import render_global_settings_sidebar


def render_eurocode_router() -> None:
    # Render Global Eurocode Sidebar Controls (National Annex & Units)
    render_global_settings_sidebar()

    # Sidebar Navigation Controls
    with st.sidebar:
        st.subheader("Eurocode Module")
        selected_code = st.radio(
            "Select Standard",
            options=[
                "EN 1990",
                "EN 1991",
                "EN 1992",
                "EN 1993",
                "EN 1994",
                "EN 1995",
                "EN 1996",
                "EN 1997",
                "EN 1998",
            ],
            index=2,
        )

    st.caption(
        f"Active National Annex: **{st.session_state.national_annex}** | "
        f"Unit System: **{st.session_state.unit_system}**"
    )
    st.divider()

    # Execute active module renderer...
