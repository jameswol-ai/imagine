"""BIM type and assembly registry."""
import pandas as pd
import streamlit as st
from .core import records, save, delete
KEY="bim_assemblies"

def render()->None:
 data=records(KEY); st.title("BIM Types & Assemblies"); st.caption("Group reusable component types into coordinated assemblies and systems.")
 if not data:
  data=[{"id":"ASM-001","code":"WALL-EXT-200","name":"External Wall Assembly","category":"Envelope","components":"Blockwork; insulation; finish","unit":"m²","status":"Approved"}]; st.session_state[KEY]=data
 df=pd.DataFrame(data); a,b,c=st.columns(3); a.metric("Assemblies",len(df)); b.metric("Categories",df.category.nunique()); c.metric("Approved",int((df.status=="Approved").sum()))
 st.dataframe(df,hide_index=True,use_container_width=True)
 with st.form("assembly_form"):
  code=st.text_input("Assembly Code"); name=st.text_input("Name"); category=st.selectbox("Category",["Structure","Envelope","Interior","MEP","Site"]); components=st.text_input("Components",help="Separate components with semicolons"); unit=st.text_input("Unit","item")
  if st.form_submit_button("Add Assembly",type="primary"):
   save(KEY,{"id":f"ASM-{len(data)+1:03d}","code":code or f"ASM-{len(data)+1:03d}","name":name or "New Assembly","category":category,"components":components,"unit":unit,"status":"Draft"}); st.rerun()
 if data:
  x=st.selectbox("Delete assembly",[r["id"] for r in data])
  if st.button("Delete selected assembly"): delete(KEY,x); st.rerun()
