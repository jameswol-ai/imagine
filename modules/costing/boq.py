import streamlit as st

class BoQEngine:
    def __init__(self):
        pass

    def run(self, inputs=None):
        return {"boq": "Demo bill of quantities", "inputs": inputs or {}}

def render():
    st.header("💰 Costing - BoQ")
    engine = BoQEngine()
    result = engine.run({"item": "Concrete"})
    st.table(st.session_state.boq_data)
    st.json(result)