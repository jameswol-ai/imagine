# modules/architecture/synthesis.py
import streamlit as st

try:
    from modules.costing.boq import BoQEngine
except ImportError:
    BoQEngine = None

def render():
    st.title("📐 Architecture")
    st.info("Architecture synthesis module.")
    if BoQEngine:
        st.write("BoQ Engine loaded.")
    else:
        st.warning("BoQ Engine not available.")