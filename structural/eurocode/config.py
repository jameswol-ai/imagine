"""
Global Eurocode Configuration & State Manager
Path: structural/eurocode/config.py
App: imagine
"""

import streamlit as st

# National Annex Coefficients & Safety Factors
NATIONAL_ANNEX_DEFAULTS = {
    "Recommended (CEN)": {
        "gamma_c": 1.50,
        "gamma_s": 1.15,
        "gamma_g_unfav": 1.35,
        "gamma_q_unfav": 1.50,
        "xi": 0.85,
    },
    "UK (BS EN)": {
        "gamma_c": 1.50,
        "gamma_s": 1.15,
        "gamma_g_unfav": 1.35,
        "gamma_q_unfav": 1.50,
        "xi": 0.92,
    },
    "Germany (DIN EN)": {
        "gamma_c": 1.50,
        "gamma_s": 1.15,
        "gamma_g_unfav": 1.35,
        "gamma_q_unfav": 1.50,
        "xi": 0.85,
    },
    "France (NF EN)": {
        "gamma_c": 1.50,
        "gamma_s": 1.15,
        "gamma_g_unfav": 1.35,
        "gamma_q_unfav": 1.50,
        "xi": 0.85,
    },
}


def init_global_eurocode_state() -> None:
    """Initializes global session state keys if not already set."""
    if "national_annex" not in st.session_state:
        st.session_state.national_annex = "Recommended (CEN)"

    if "unit_system" not in st.session_state:
        st.session_state.unit_system = "Metric (kN, m, MPa)"


def render_global_settings_sidebar() -> None:
    """Renders global controls in the sidebar for National Annex and Units."""
    init_global_eurocode_state()

    st.sidebar.markdown("---")
    st.sidebar.subheader("🌐 Global Standards & Units")

    st.session_state.national_annex = st.sidebar.selectbox(
        "National Annex",
        options=list(NATIONAL_ANNEX_DEFAULTS.keys()),
        index=list(NATIONAL_ANNEX_DEFAULTS.keys()).index(st.session_state.national_annex),
        help="Applies country-specific partial factors (γ) and combination factors (ψ/ξ).",
    )

    st.session_state.unit_system = st.sidebar.selectbox(
        "Unit System",
        options=["Metric (kN, m, MPa)", "Imperial (kips, ft, ksi)"],
        index=0 if "Metric" in st.session_state.unit_system else 1,
        help="Global unit toggle for inputs and calculated outputs.",
    )


def get_active_factors() -> dict:
    """Returns partial factors for the currently selected National Annex."""
    init_global_eurocode_state()
    return NATIONAL_ANNEX_DEFAULTS[st.session_state.national_annex]


def get_unit_labels() -> dict:
    """Returns context-aware string labels for display in input forms and results."""
    init_global_eurocode_state()
    is_metric = "Metric" in st.session_state.unit_system

    return {
        "force": "kN" if is_metric else "kips",
        "length": "m" if is_metric else "ft",
        "section_dim": "mm" if is_metric else "in",
        "stress": "MPa" if is_metric else "ksi",
        "moment": "kNm" if is_metric else "kip·ft",
        "area": "mm²" if is_metric else "in²",
    }
