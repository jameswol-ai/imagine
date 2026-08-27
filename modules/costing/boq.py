# modules/costing/boq.py
"""
Bill of Quantities Engine
"""

import streamlit as st

class BoQEngine:
    """Mock BoQ engine – replace with real logic later."""
    
    def __init__(self):
        self.data = st.session_state.get("boq_data", [])
    
    def get_items(self):
        return self.data
    
    def add_item(self, item):
        self.data.append(item)
        st.session_state["boq_data"] = self.data
    
    def update_item(self, index, item):
        if 0 <= index < len(self.data):
            self.data[index] = item
            st.session_state["boq_data"] = self.data
    
    def delete_item(self, index):
        if 0 <= index < len(self.data):
            del self.data[index]
            st.session_state["boq_data"] = self.data

def render():
    """Render the BoQ page – placeholder."""
    st.subheader("Bill of Quantities")
    st.info("BoQ management coming soon.")