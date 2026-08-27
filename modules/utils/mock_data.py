import streamlit as st

def init_session_state():
    """Initialize all mock data keys in session_state if missing."""
    if "projects_data" not in st.session_state:
        st.session_state.projects_data = []

    if "buildings_data" not in st.session_state:
        st.session_state.buildings_data = []

    if "approvals_data" not in st.session_state:
        st.session_state.approvals_data = []

    # Add other mock datasets as needed
    if "storeys_data" not in st.session_state:
        st.session_state.storeys_data = []

    if "spaces_data" not in st.session_state:
        st.session_state.spaces_data = []