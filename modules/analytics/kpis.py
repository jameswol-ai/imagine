import streamlit as st

class KPIEngine:
    def __init__(self):
        pass

    def run(self, inputs=None):
        return {"kpis": "Demo KPI dashboard", "inputs": inputs or {}}

def render():
    st.header("📈 Analytics - KPIs")
    engine = KPIEngine()
    result = engine.run({"metric": "Cost Variance"})
    for kpi in st.session_state.kpis_data:
        st.metric(kpi["metric"], kpi["value"])
    st.json(result)