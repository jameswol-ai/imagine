"""Streamlit workspace for preliminary EN 1993 steel member screening."""
from __future__ import annotations
import pandas as pd
import streamlit as st
from modules.structural.ec3 import SteelSection, preliminary_slenderness

def render() -> None:
    st.title("EN 1993 Steel Design")
    st.caption("Preliminary gross-yield and member slenderness screening. Section classification, buckling, interaction, fatigue and connections require full project design verification.")
    a,b=st.columns(2)
    with a:
        area=st.number_input("Area (mm²)",min_value=100.0,value=6500.0,step=250.0)
        fy=st.number_input("fy (MPa)",min_value=200.0,value=355.0,step=5.0)
        iy=st.number_input("Iy (mm⁴)",min_value=1e4,value=8e7,step=1e6)
        iz=st.number_input("Iz (mm⁴)",min_value=1e4,value=2.5e7,step=1e6)
        length=st.number_input("Member length (m)",min_value=0.5,value=4.0,step=0.25)
        run=st.button("Calculate steel screening",type="primary",use_container_width=True)
    with b:
        if run:
            try: st.session_state["ec3_result"]=preliminary_slenderness(SteelSection(area,fy,iy,iz,length))
            except ValueError as exc: st.error(str(exc)); return
        r=st.session_state.get("ec3_result")
        if r:
            c1,c2=st.columns(2); c1.metric("Yield resistance",f"{r.gross_yield_resistance_kn:.0f} kN"); c2.metric("Governing slenderness",f"{r.governing_slenderness:.0f}")
            st.dataframe(pd.DataFrame([["ry",r.radius_y_mm,"mm"],["rz",r.radius_z_mm,"mm"],["lambda y",r.slenderness_y,"ratio"],["lambda z",r.slenderness_z,"ratio"]],columns=["Parameter","Value","Unit"]),use_container_width=True,hide_index=True)
        else: st.info("Enter steel section properties and calculate a screening result.")
__all__=["render"]
