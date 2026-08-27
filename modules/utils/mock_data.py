import streamlit as st

def init_session_state():
    """Initialize all mock data keys in session_state if missing."""

    # Dashboard / Projects
    if "projects_data" not in st.session_state:
        st.session_state.projects_data = []

    # Architecture
    if "synthesis_data" not in st.session_state:
        st.session_state.synthesis_data = []
    if "zoning_data" not in st.session_state:
        st.session_state.zoning_data = []
    if "room_programming_data" not in st.session_state:
        st.session_state.room_programming_data = []

    # BIM
    if "buildings_data" not in st.session_state:
        st.session_state.buildings_data = []
    if "storeys_data" not in st.session_state:
        st.session_state.storeys_data = []
    if "spaces_data" not in st.session_state:
        st.session_state.spaces_data = []
    if "ifc_export_data" not in st.session_state:
        st.session_state.ifc_export_data = []

    # Structural
    if "eurocode_data" not in st.session_state:
        st.session_state.eurocode_data = []
    if "beam_data" not in st.session_state:
        st.session_state.beam_data = []
    if "column_data" not in st.session_state:
        st.session_state.column_data = []
    if "slab_data" not in st.session_state:
        st.session_state.slab_data = []
    if "foundation_data" not in st.session_state:
        st.session_state.foundation_data = []
    if "retaining_walls_data" not in st.session_state:
        st.session_state.retaining_walls_data = []
    if "steel_connections_data" not in st.session_state:
        st.session_state.steel_connections_data = []

    # MEP
    if "mep_analysis_data" not in st.session_state:
        st.session_state.mep_analysis_data = []
    if "hvac_data" not in st.session_state:
        st.session_state.hvac_data = []
    if "electrical_data" not in st.session_state:
        st.session_state.electrical_data = []
    if "plumbing_data" not in st.session_state:
        st.session_state.plumbing_data = []
    if "energy_simulation_data" not in st.session_state:
        st.session_state.energy_simulation_data = []

    # Costing
    if "boq_data" not in st.session_state:
        st.session_state.boq_data = []
    if "procurement_data" not in st.session_state:
        st.session_state.procurement_data = []
    if "forex_data" not in st.session_state:
        st.session_state.forex_data = []
    if "escalation_data" not in st.session_state:
        st.session_state.escalation_data = []
    if "risk_analysis_data" not in st.session_state:
        st.session_state.risk_analysis_data = []

    # Governance
    if "approvals_data" not in st.session_state:
        st.session_state.approvals_data = []

    # Construction
    if "rfis_data" not in st.session_state:
        st.session_state.rfis_data = []
    if "submittals_data" not in st.session_state:
        st.session_state.submittals_data = []
    if "site_diary_data" not in st.session_state:
        st.session_state.site_diary_data = []
    if "progress_tracking_data" not in st.session_state:
        st.session_state.progress_tracking_data = []
    if "snagging_data" not in st.session_state:
        st.session_state.snagging_data = []

    # Documents
    if "documents_data" not in st.session_state:
        st.session_state.documents_data = []
    if "revisions_data" not in st.session_state:
        st.session_state.revisions_data = []
    if "drawing_register_data" not in st.session_state:
        st.session_state.drawing_register_data = []
    if "specifications_data" not in st.session_state:
        st.session_state.specifications_data = []
    if "transmittals_data" not in st.session_state:
        st.session_state.transmittals_data = []

    # Analytics
    if "portfolio_data" not in st.session_state:
        st.session_state.portfolio_data = []
    if "reporting_data" not in st.session_state:
        st.session_state.reporting_data = []
    if "forecasting_data" not in st.session_state:
        st.session_state.forecasting_data = []
    if "kpis_data" not in st.session_state:
        st.session_state.kpis_data = []

    # Digital Twin
    if "assets_data" not in st.session_state:
        st.session_state.assets_data = []
    if "sensors_data" not in st.session_state:
        st.session_state.sensors_data = []
    if "telemetry_data" not in st.session_state:
        st.session_state.telemetry_data = []
    if "maintenance_data" not in st.session_state:
        st.session_state.maintenance_data = []
    if "predictive_ai_data" not in st.session_state:
        st.session_state.predictive_ai_data = []

    # AI Assistant
    if "architect_ai_data" not in st.session_state:
        st.session_state.architect_ai_data = []
    if "engineer_ai_data" not in st.session_state:
        st.session_state.engineer_ai_data = []
    if "mep_ai_data" not in st.session_state:
        st.session_state.mep_ai_data = []
    if "qs_ai_data" not in st.session_state:
        st.session_state.qs_ai_data = []
    if "pm_ai_data" not in st.session_state:
        st.session_state.pm_ai_data = []