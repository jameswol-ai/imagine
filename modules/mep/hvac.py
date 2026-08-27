import streamlit as st

class HVACAnalysisEngine:
    def __init__(self):
        pass

    def run(self, inputs=None):
        return {"hvac": "Demo HVAC analysis", "inputs": inputs or {}}

def render():
    st.header("⚡ MEP - HVAC")
    engine = HVACAnalysisEngine()
    result = engine.run({"system": "Chiller"})
    st.table(st.session_state.hvac_data)
    st.json(result)