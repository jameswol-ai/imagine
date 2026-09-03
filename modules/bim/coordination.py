"""BIM coordination and clash register."""
import pandas as pd
import streamlit as st
from .core import records, save

def render()->None:
 st.title("BIM Coordination & Clash Detection"); st.caption("Rule-based coordination register for documenting model conflicts before formal federated-model checking.")
 data=records("bim_clashes")
 if not data:
  data=[{"id":"CLASH-001","discipline_a":"Architecture","element_a":"ELM-001","discipline_b":"MEP","element_b":"MEP-001","type":"Clearance","severity":"Medium","status":"Open","resolution":"Review coordination"}]; st.session_state["bim_clashes"]=data
 df=pd.DataFrame(data); a,b,c,d=st.columns(4); a.metric("Issues",len(df)); b.metric("Open",int((df.status=="Open").sum())); c.metric("High",int((df.severity=="High").sum())); d.metric("Resolved",int((df.status=="Resolved").sum()))
 st.dataframe(df,hide_index=True,use_container_width=True)
 with st.form("clash_form"):
  ca,cb=st.columns(2)
  with ca: da=st.selectbox("Discipline A",["Architecture","Structural","MEP","Civil"]); ea=st.text_input("Element A"); db=st.selectbox("Discipline B",["MEP","Architecture","Structural","Civil"]); eb=st.text_input("Element B")
  with cb: typ=st.selectbox("Clash Type",["Geometry","Clearance","System","Data","Access"]); sev=st.selectbox("Severity",["Low","Medium","High","Critical"]); resolution=st.text_area("Resolution")
  if st.form_submit_button("Register Clash",type="primary"):
   save("bim_clashes",{"id":f"CLASH-{len(data)+1:03d}","discipline_a":da,"element_a":ea,"discipline_b":db,"element_b":eb,"type":typ,"severity":sev,"status":"Open","resolution":resolution}); st.rerun()
 st.info("Automated geometric clash detection against native IFC/Revit/Tekla geometry requires a model parser or federated coordination engine. This register provides the workflow layer now.")
