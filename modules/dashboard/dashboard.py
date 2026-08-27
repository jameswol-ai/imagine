import streamlit as st

def render():
    st.title("📊 Dashboard")
    st.write("Welcome to the IMAGINE Dashboard")

    # Example: show projects summary
    if "projects_data" in st.session_state:
        st.subheader("Projects Overview")
        st.table(st.session_state.projects_data)