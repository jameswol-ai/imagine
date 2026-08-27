# modules/utils/mock_data.py
import streamlit as st

def init_mock_data():
    # Projects
    if "projects_data" not in st.session_state or not st.session_state.projects_data:
        st.session_state.projects_data = [
            {"id": 1, "name": "Green Tower", "status": "Active", "budget": 12.5, "progress": 75},
            {"id": 2, "name": "Harbor Bridge", "status": "Planning", "budget": 8.3, "progress": 20},
            {"id": 3, "name": "Riverside Mall", "status": "Completed", "budget": 22.1, "progress": 100},
            {"id": 4, "name": "Solar Park", "status": "Active", "budget": 5.7, "progress": 45},
        ]
    # Buildings
    if "buildings_data" not in st.session_state or not st.session_state.buildings_data:
        st.session_state.buildings_data = [
            {"id": 1, "name": "Tower A", "storeys": 25, "area": 15000, "ifc_version": "IFC4"},
            {"id": 2, "name": "Tower B", "storeys": 18, "area": 12000, "ifc_version": "IFC4"},
            {"id": 3, "name": "Pavilion", "storeys": 3, "area": 2500, "ifc_version": "IFC2x3"},
        ]
    # ... (all the other mock data as before)

    # Alias for the main entry point
    init_session_state = init_mock_data