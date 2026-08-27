"""
IMAGINE Platform — Master Session State Initializer
Path: modules/utils/mock_data.py
App: imagine
"""

import streamlit as st


def init_session_state() -> None:
    """Ensures all global state arrays exist across all platform modules."""
    schema = {
        "projects": [],
        "architecture_layouts": [],
        "zoning_plans": [],
        "room_programs": [],
        "bim_buildings": [],
        "bim_storeys": [],
        "bim_spaces": [],
        "structural_calcs": [],
        "mep_analyses": [],
        "boq_items": [],
        "procurement_orders": [],
        "forex_rates": [],
        "rfis": [],
        "submittals": [],
        "site_diaries": [],
        "documents": [],
        "digital_twin_sensors": [],
        "telemetry_logs": [],
        "approvals": [],
    }

    for key, default_val in schema.items():
        if key not in st.session_state:
            st.session_state[key] = default_val
