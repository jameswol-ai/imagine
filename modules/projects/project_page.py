# modules/projects/project_page.py
import streamlit as st
from modules.utils.crud import crud_table

def render():
    st.title("📁 Project Directory")
    if st.button("🔄 Refresh"):
        st.rerun()
    crud_table(
        data_key="projects_data",
        item_name="project",
        endpoint="projects",
        display_fields=["name", "status", "budget", "progress"],
        edit_fields={"name": "text", "status": "text", "budget": "number", "progress": "number"},
        add_fields={"name": "text", "status": "text", "budget": "number", "progress": "number"}
    )