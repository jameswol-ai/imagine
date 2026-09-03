"""Streamlit workspace for preliminary EN 1997 geotechnical screening."""
from __future__ import annotations
import pandas as pd
import streamlit as st
from modules.structural.ec7 import Soil, ultimate_bearing_capacity_kpa

def render() -> None:
    st.title("EN 1997 Geotechnical Design")
    st.caption("Preliminary bearing-capacity screening. Settlement, groundwater, layered soils, sliding, uplift and full limit-state design require project geotechnical verification.")
    a,b=st.columns(2)
    with a:
        gamma=st.number_input("Soil unit weight (kN/m³)",min_value=10.0,value=18.0,step=0.5)
        cohesion=st.number_input("c' (kPa)",min_value=0.0,value=10.0,step=1.0)
        phi=st.number_input("phi' (degrees)",min_value=0.0,max_value=60.0,value=30.0,step=1.0)
        width=st.number_input("Foundation width B (m)",min_value=0.3,value=2.0,step=0.1)
        depth=st.number_input("Foundation embedment D (m)",min_value=0.0,value=1.0,step=0.1)
        run=st.button("Calculate bearing screening",type="primary",use_container_width=True)
    with b:
        if run:
            try: st.session_state["ec7_result"]=ultimate_bearing_capacity_kpa(Soil(gamma,cohesion,phi,200),width,depth)
            except (ValueError,TypeError) as exc: st.error(str(exc)); return
        r=st.session_state.get("ec7_result")
        if r is not None:
            st.metric("Ultimate bearing capacity",f"{r:.1f} kPa")
            st.dataframe(pd.DataFrame([["Ultimate bearing",r,"kPa"]],columns=["Check","Value","Unit"]),use_container_width=True,hide_index=True)
        else: st.info("Enter soil and footing parameters and calculate.")
__all__=["render"]
