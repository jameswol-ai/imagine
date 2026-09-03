"""Preliminary EN 1993 steel member design workspace."""
from __future__ import annotations
import math
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from modules.structural.ec3 import SteelSection, preliminary_slenderness

def render() -> None:
    st.title("Steel Members")
    st.caption("Preliminary EN 1993 member screening for axial compression/tension. Final design requires section classification, buckling curves, effective lengths, lateral torsional buckling, interactions and National Annex verification.")
    a,b=st.columns(2)
    with a:
        section=st.selectbox("Section shape",["I / H section","RHS / SHS","CHS","Custom section"])
        area=st.number_input("Gross area (mm²)",min_value=100.0,value=6500.0,step=250.0)
        fy=st.number_input("Yield strength fy (MPa)",min_value=200.0,value=355.0,step=5.0)
        iy=st.number_input("Iy (mm⁴)",min_value=1e4,value=8.0e7,step=1e6)
        iz=st.number_input("Iz (mm⁴)",min_value=1e4,value=2.5e7,step=1e6)
        length=st.number_input("Unbraced/member length (m)",min_value=0.25,value=4.0,step=0.25)
        ned=st.number_input("N_Ed (kN)",min_value=0.0,value=300.0,step=25.0)
        run=st.button("Calculate steel member",type="primary",use_container_width=True)
    with b:
        if run:
            try:
                r=preliminary_slenderness(SteelSection(area,fy,iy,iz,length)); util=ned/r.gross_yield_resistance_kn if r.gross_yield_resistance_kn else float("inf")
                st.session_state["steel_member_result"]=(r,util,section)
            except ValueError as exc: st.error(str(exc)); return
        data=st.session_state.get("steel_member_result")
        if not data: st.info("Enter member properties and calculate."); return
        r,util,section=data
        c1,c2,c3=st.columns(3); c1.metric("Npl,Rd",f"{r.gross_yield_resistance_kn:.0f} kN"); c2.metric("Axial utilisation",f"{util:.2f}"); c3.metric("Governing slenderness",f"{r.governing_slenderness:.0f}")
        st.dataframe(pd.DataFrame([["Shape",section,""],["ry",r.radius_y_mm,"mm"],["rz",r.radius_z_mm,"mm"],["lambda y",r.slenderness_y,"ratio"],["lambda z",r.slenderness_z,"ratio"]],columns=["Parameter","Value","Unit"]),use_container_width=True,hide_index=True)
        fig=go.Figure(go.Bar(x=["Axial yield"],y=[util])); fig.update_layout(height=240,yaxis_title="Utilisation",margin=dict(l=10,r=10,t=20,b=10)); st.plotly_chart(fig,use_container_width=True)
        if util<=1: st.success("Gross-section axial screening passes.")
        else: st.warning("Axial demand exceeds gross-section yield resistance.")
__all__=["render"]
