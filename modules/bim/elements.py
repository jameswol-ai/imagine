"""BIM element/component registry."""
import pandas as pd
import streamlit as st
from .core import records, save, delete, seed_if_empty, utc_now

KEY="bim_elements"
SEED=[
 {"id":"ELM-001","building_id":"BLDG-001","storey_id":"STRY-001","category":"Wall","name":"External Wall A","type_name":"External Wall 200mm","quantity":120.0,"unit":"m²","status":"Design","guid":"IMAGINE-ELM-001"},
 {"id":"ELM-002","building_id":"BLDG-001","storey_id":"STRY-001","category":"Door","name":"Main Entrance Door","type_name":"Double Glazed Door","quantity":2.0,"unit":"item","status":"Design","guid":"IMAGINE-ELM-002"},
 {"id":"ELM-003","building_id":"BLDG-001","storey_id":"STRY-002","category":"Column","name":"RC Column Grid A1","type_name":"RC 400x400 C30/37","quantity":8.0,"unit":"item","status":"Design","guid":"IMAGINE-ELM-003"},
]

def render()->None:
 data=seed_if_empty(KEY,SEED); df=pd.DataFrame(data)
 st.title("BIM Elements & Components"); st.caption("Register model components and their quantities for coordination, IFC and cost handoff.")
 a,b,c=st.columns(3); a.metric("Elements",len(df)); b.metric("Categories",df.category.nunique() if not df.empty else 0); c.metric("Quantity",f"{df.quantity.sum():,.1f}" if not df.empty else "0")
 tab1,tab2=st.tabs(["Element Register","Add Element"])
 with tab1:
  q=st.text_input("Search element, type or category")
  view=df[df.apply(lambda r: q.lower() in " ".join(map(str,r.values)).lower(),axis=1)] if q and not df.empty else df
  st.dataframe(view,hide_index=True,use_container_width=True)
  if data:
   selected=st.selectbox("Delete element",[x["id"] for x in data])
   if st.button("Delete selected element"):
    delete(KEY,selected); st.rerun()
 with tab2:
  with st.form("bim_element_form"):
   c1,c2=st.columns(2)
   with c1: name=st.text_input("Element Name"); category=st.selectbox("Category",["Wall","Door","Window","Column","Beam","Slab","Roof","Stair","Railing","Equipment","Fixture"]); type_name=st.text_input("Type Name")
   with c2: building_id=st.text_input("Building ID","BLDG-001"); storey_id=st.text_input("Storey ID","STRY-001"); qty=st.number_input("Quantity",min_value=0.0,value=1.0); unit=st.text_input("Unit","item")
   if st.form_submit_button("Register Element",type="primary"):
    n=len(data)+1; save(KEY,{"id":f"ELM-{n:03d}","building_id":building_id,"storey_id":storey_id,"category":category,"name":name or f"{category} {n}","type_name":type_name or category,"quantity":float(qty),"unit":unit,"status":"Design","guid":f"IMAGINE-ELM-{n:03d}","created_at":utc_now()}); st.rerun()
