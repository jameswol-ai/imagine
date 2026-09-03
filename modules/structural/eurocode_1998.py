"""Streamlit workspace for preliminary EN 1998 seismic screening."""
from __future__ import annotations
import pandas as pd
import streamlit as st
from modules.structural.ec8 import SeismicInput, base_shear_kn, distribute_storey_forces_kn

def render() -> None:
    st.title("EN 1998 Seismic Design")
    st.caption("Preliminary equivalent-lateral-force screening. Spectrum definition, ductility, torsion, irregularity, drift, P-delta and detailed member design require project-specific verification.")
    a,b=st.columns(2)
    with a:
        mass=st.number_input("Seismic mass (tonnes)",min_value=1.0,value=1200.0,step=50.0)
        ag=st.number_input("Design ground acceleration ag (m/s²)",min_value=0.01,value=2.0,step=0.1)
        s=st.number_input("Soil factor S",min_value=0.5,value=1.2,step=0.05)
        q=st.number_input("Behaviour factor q",min_value=1.0,value=3.0,step=0.1)
        t1=st.number_input("Fundamental period T1 (s)",min_value=0.05,value=0.6,step=0.05)
        run=st.button("Calculate seismic screening",type="primary",use_container_width=True)
    with b:
        if run:
            try:
                inp=SeismicInput(mass_tonnes=mass,ag_ms2=ag,s=s,q=q,t1_s=t1)
                v=base_shear_kn(inp); st.session_state["ec8_result"]=(inp,v,distribute_storey_forces_kn(v,[1,2,3,4]))
            except ValueError as exc: st.error(str(exc)); return
        data=st.session_state.get("ec8_result")
        if data:
            inp,v,forces=data; st.metric("Base shear",f"{v:.1f} kN")
            st.dataframe(pd.DataFrame({"Storey":[1,2,3,4],"Lateral force (kN)":forces}),use_container_width=True,hide_index=True)
        else: st.info("Enter seismic parameters and calculate.")
__all__=["render"]
