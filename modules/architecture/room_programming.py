# modules/architecture/room_programming.py
import streamlit as st
from modules.utils.crud import crud_table

def render():
    st.subheader("Room Programming")
    if st.button("🔄 Refresh Rooms"):
        st.rerun()
    crud_table(
        data_key="room_program_data",
        item_name="room",
        endpoint="architecture/room_programming",
        display_fields=["room_name", "area", "quantity", "adjacency"],
        edit_fields={"room_name": "text", "area": "number", "quantity": "number", "adjacency": "text"},
        add_fields={"room_name": "text", "area": "number", "quantity": "number", "adjacency": "text"}
    )