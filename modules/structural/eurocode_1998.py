"""Streamlit workspace for preliminary EN 1998 seismic screening."""
from __future__ import annotations
import pandas as pd
import streamlit as st
from modules.structural.ec8 import SeismicInput, base_shear_kn, distribute_storey_forces_kn

def render() -> None:
    st.title("EN 1998 Seismic Design")
    st.caption("Preliminary equivalent-static seismic screening. Verify the project hazard, soil class, National Annex, regularity, drift and full structural analysis.")
    a,b=st.columns(2)
    with a:
        coefficient=st.number_input("Seismic coefficient",min_value=0.0,value=0.30,step=0.01)
        mass=st.number_input("Total seismic mass (tonnes)",min_value=0.0,value=1200.0,step=50.0)
        q=st.number_input("Behaviour factor q",min_value=0.1,value=3.0,step=0.1)
        importance=st.number_input("Importance factor gammaI",min_value=0.1,value=1.0,step=0.05)
        masses_text=st.text_input("Storey masses (t), comma separated",value="300,300,300,300")
        heights_text=st.text_input("Storey heights (m), comma separated",value="3,6,9,12")
        run=st.button("Calculate seismic screening",type="primary",use_container_width=True)
    with b:
        if run:
            try:
                inp=SeismicInput(coefficient,mass,q,importance)
                masses=[float(x.strip()) for x in masses_text.split(",") if x.strip()]
                heights=[float(x.strip()) for x in heights_text.split(",") if x.strip()]
                v=base_shear_kn(inp); forces=distribute_storey_forces_kn(v,masses,heights)
                st.session_state["ec8_result"]=(v,forces)
            except (ValueError,TypeError) as exc: st.error(str(exc)); return
        data=st.session_state.get("ec8_result")
        if data:
            v,forces=data; st.metric("Base shear",f"{v:.1f} kN")
            st.dataframe(pd.DataFrame({"Storey":list(range(1,len(forces)+1)),"Lateral force (kN)":forces}),use_container_width=True,hide_index=True)
        else: st.info("Enter seismic parameters and calculate.")
__all__=["render"]
