# modules/architecture/zoning.py
import streamlit as st
from modules.utils.crud import crud_table

def render():
    st.subheader("Zoning Analysis")
    if st.button("🔄 Refresh Zoning"):
        st.rerun()
    crud_table(
        data_key="zoning_data",
        item_name="zoning",
        endpoint="architecture/zoning",
        display_fields=["zone_type", "max_height", "coverage", "setback"],
        edit_fields={"zone_type": "text", "max_height": "number", "coverage": "number", "setback": "number"},
        add_fields={"zone_type": "text", "max_height": "number", "coverage": "number", "setback": "number"}
    )