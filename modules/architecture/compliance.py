import streamlit as st
import pandas as pd

def render():
    st.subheader("Compliance Checking")
    code = st.selectbox("Select Code", ["Uganda National Building Code", "Kenya Building Code", "Tanzania Building Standards"])
    st.file_uploader("Upload floor plan (DXF/PDF)", type=["dxf", "pdf"])
    if st.button("Run Compliance Check"):
        results = pd.DataFrame({
            "Rule": ["Fire escape distance", "Parking ratio", "Daylight factor"],
            "Required": ["< 30m", "1:100 m²", "> 2%"],
            "Actual": ["25m", "1:120 m²", "2.5%"],
            "Status": ["Pass", "Warning", "Pass"],
        })
        st.dataframe(results)
        st.success("Compliance check complete (mock).")