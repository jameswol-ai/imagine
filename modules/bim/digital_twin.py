"""BIM to Digital Twin asset handoff."""
import pandas as pd
import streamlit as st
from .core import records, save

def render()->None:
 st.title("BIM → Digital Twin"); st.caption("Convert BIM components into operational asset records ready for sensors, telemetry and maintenance workflows.")
 elements=records("bim_elements"); assets=records("digital_twin_assets")
 if not assets and elements:
  assets=[{"id":f"ASSET-{i+1:03d}","element_id":e.get("id",""),"asset_name":e.get("name",""),"category":e.get("category",""),"location":f"{e.get('building_id','')} / {e.get('storey_id','')}","sensor_count":0,"maintenance_status":"Not commissioned"} for i,e in enumerate(elements)]; st.session_state["digital_twin_assets"]=assets
 df=pd.DataFrame(assets); a,b,c=st.columns(3); a.metric("Twin Assets",len(df)); b.metric("With Sensors",int((df.sensor_count>0).sum()) if not df.empty else 0); c.metric("Commissioned",int((df.maintenance_status=="Commissioned").sum()) if not df.empty else 0)
 if not df.empty: st.dataframe(df,hide_index=True,use_container_width=True)
 with st.form("twin_asset_form"):
  name=st.text_input("Asset Name"); category=st.selectbox("Asset Category",["Structure","Envelope","HVAC","Electrical","Plumbing","Fire Safety","Vertical Transport","Other"]); location=st.text_input("Location"); sensors=st.number_input("Sensor Count",min_value=0,value=0)
  if st.form_submit_button("Create Twin Asset",type="primary"):
   save("digital_twin_assets",{"id":f"ASSET-{len(assets)+1:03d}","element_id":"","asset_name":name or "New Asset","category":category,"location":location,"sensor_count":int(sensors),"maintenance_status":"Not commissioned"}); st.rerun()
