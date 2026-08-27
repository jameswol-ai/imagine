import streamlit as st

def init_session_state():
    """Initialize all mock data keys in session_state if missing, with demo content."""

    # Projects
    if "projects_data" not in st.session_state:
        st.session_state.projects_data = [
            {"name": "City Mall", "status": "Design", "budget": 5_000_000},
            {"name": "Tech Park", "status": "Construction", "budget": 12_500_000},
        ]

    # BIM
    if "buildings_data" not in st.session_state:
        st.session_state.buildings_data = [
            {"name": "Block A", "address": "Downtown"},
            {"name": "Block B", "address": "Uptown"},
        ]
    if "storeys_data" not in st.session_state:
        st.session_state.storeys_data = [
            {"building": "Block A", "level": "Ground"},
            {"building": "Block A", "level": "First"},
        ]
    if "spaces_data" not in st.session_state:
        st.session_state.spaces_data = [
            {"storey": "Ground", "space": "Lobby"},
            {"storey": "First", "space": "Office"},
        ]

    # Structural
    if "beam_data" not in st.session_state:
        st.session_state.beam_data = [
            {"id": "B1", "span": 6.0, "material": "RC"},
            {"id": "B2", "span": 8.0, "material": "Steel"},
        ]

    # MEP
    if "hvac_data" not in st.session_state:
        st.session_state.hvac_data = [
            {"system": "Chiller", "capacity": "200 kW"},
            {"system": "Split AC", "capacity": "20 kW"},
        ]
    if "electrical_data" not in st.session_state:
        st.session_state.electrical_data = [
            {"panel": "Main", "load": "500 kVA"},
            {"panel": "Sub", "load": "200 kVA"},
        ]

    # Costing
    if "boq_data" not in st.session_state:
        st.session_state.boq_data = [
            {"item": "Concrete", "qty": 100, "unit": "m³"},
            {"item": "Steel", "qty": 50, "unit": "tons"},
        ]

    # Governance
    if "approvals_data" not in st.session_state:
        st.session_state.approvals_data = [
            {"stage": "Planning", "status": "Approved"},
            {"stage": "Construction", "status": "Pending"},
        ]

    # Construction
    if "rfis_data" not in st.session_state:
        st.session_state.rfis_data = [
            {"id": "RFI-001", "subject": "Beam detail clarification"},
            {"id": "RFI-002", "subject": "HVAC duct routing"},
        ]

    # Documents
    if "documents_data" not in st.session_state:
        st.session_state.documents_data = [
            {"doc": "General Arrangement", "rev": "A"},
            {"doc": "Electrical Layout", "rev": "B"},
        ]

    # Analytics
    if "kpis_data" not in st.session_state:
        st.session_state.kpis_data = [
            {"metric": "Cost Variance", "value": "-5%"},
            {"metric": "Schedule Performance", "value": "1.1"},
        ]

    # Digital Twin
    if "assets_data" not in st.session_state:
        st.session_state.assets_data = [
            {"asset": "Chiller", "status": "Operational"},
            {"asset": "Elevator", "status": "Maintenance"},
        ]

    # AI Assistant
    if "architect_ai_data" not in st.session_state:
        st.session_state.architect_ai_data = [
            {"query": "Optimize zoning", "response": "Suggested mixed-use layout"},
        ]