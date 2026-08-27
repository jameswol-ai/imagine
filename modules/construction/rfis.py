import streamlit as st

class RFIEngine:
    def __init__(self):
        pass

    def run(self, inputs=None):
        return {"rfi": "Demo RFI handling", "inputs": inputs or {}}

def render():
    st.header("🏗️ Construction - RFIs")
    engine = RFIEngine()
    result = engine.run({"id": "RFI-001"})
    st.table(st.session_state.rfis_data)
    st.json(result)