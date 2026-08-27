# modules/dashboard/dashboard.py
import streamlit as st
def render():
    st.header("📊 Executive Dashboard")
    st.info("Overview dashboard placeholder.")
    st.table(st.session_state.projects_data)
