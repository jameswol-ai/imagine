import streamlit as st

class AssetEngine:
    def __init__(self):
        pass

    def run(self, inputs=None):
        return {"assets": "Demo asset management", "inputs": inputs or {}}

def render():
    st.header("📡 Digital Twin - Assets")
    engine = AssetEngine()
    result = engine.run({"asset": "Chiller"})
    st.table(st.session_state.assets_data)
    st.json(result)