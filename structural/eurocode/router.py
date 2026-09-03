"""Eurocode navigation router.

The application-level registry normally opens ``modules.structural.eurocode_suite``.
This router remains available for the legacy structural/eurocode entry point and
uses the same catalog-driven suite so the two entry paths do not diverge.
"""
from __future__ import annotations

import streamlit as st

from modules.structural.eurocode_suite import render as render_suite
from structural.eurocode.config import render_global_settings_sidebar


def render_eurocode_router() -> None:
    render_global_settings_sidebar()
    with st.sidebar:
        st.subheader("Eurocode Navigation")
        st.caption("EN 1990 to EN 1999")
        st.info("Use the Family Explorer and Part Explorer in the main Eurocode Suite.")

    st.caption(
        f"Active National Annex: **{st.session_state.get('national_annex', 'Recommended (CEN)')}** | "
        f"Unit System: **{st.session_state.get('unit_system', 'Metric')}**"
    )
    render_suite()


__all__ = ["render_eurocode_router"]
