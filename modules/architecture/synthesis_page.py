import streamlit as st
from modules.architecture.synthesis import ArchitectureSynthesisEngine

def render():
    st.header("📐 Architecture - Synthesis")

    # Demo inputs
    inputs = {"site": "Demo Site", "zoning": "Mixed-use"}
    engine = ArchitectureSynthesisEngine()
    result = engine.run(inputs)

    st.subheader("Generative Layout Result")
    st.json(result)