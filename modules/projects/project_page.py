import streamlit as st
def render():
    st.header("📂 Project Hub")
    st.info("Project directory placeholder.")
    st.table(st.session_state.projects_data)
