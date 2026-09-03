"""COBie handover register built from BIM asset records."""
import pandas as pd
import streamlit as st
from .core import records, save

def render()->None:
 st.title("COBie Handover"); st.caption("Structured asset handover register for facilities operations. This is a data exchange layer, not a full COBie certification engine.")
 elements=records("bim_elements"); data=records("bim_cobie")
 if not data and elements:
  data=[{"id":f"COB-{i+1:03d}","name":e.get("name",""),"category":e.get("category",""),"type_name":e.get("type_name",""),"building_id":e.get("building_id",""),"storey_id":e.get("storey_id",""),"serial_number":"","manufacturer":"","model":"","warranty_end":"","status":"Draft"} for i,e in enumerate(elements)]; st.session_state["bim_cobie"]=data
 df=pd.DataFrame(data)
 a,b,c=st.columns(3); a.metric("Assets",len(df)); b.metric("Manufacturers",df.manufacturer.replace("",pd.NA).dropna().nunique() if not df.empty and "manufacturer" in df else 0); c.metric("Completed",int((df.status=="Complete").sum()) if not df.empty else 0)
 st.dataframe(df,hide_index=True,use_container_width=True)
 with st.form("cobie_form"):
  name=st.text_input("Asset Name"); category=st.text_input("Category","Equipment"); manufacturer=st.text_input("Manufacturer"); model=st.text_input("Model"); serial=st.text_input("Serial Number"); warranty=st.date_input("Warranty End")
  if st.form_submit_button("Add COBie Asset",type="primary"):
   save("bim_cobie",{"id":f"COB-{len(data)+1:03d}","name":name,"category":category,"type_name":model,"building_id":"","storey_id":"","serial_number":serial,"manufacturer":manufacturer,"model":model,"warranty_end":str(warranty),"status":"Draft"}); st.rerun()
 if not df.empty:
  st.download_button("Export COBie Register CSV",df.to_csv(index=False),"imagine_cobie.csv","text/csv",use_container_width=True)
