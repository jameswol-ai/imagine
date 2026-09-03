"""BIM to costing/BOQ handoff."""
import pandas as pd
import streamlit as st
from .core import records

def render()->None:
 st.title("BIM → Costing / BOQ Handoff"); st.caption("Prepare quantity lines for downstream costing without inventing unit rates.")
 elements=records("bim_elements")
 if not elements: st.info("Register BIM elements before preparing a costing handoff."); return
 df=pd.DataFrame(elements); out=df[[c for c in ["id","category","name","type_name","quantity","unit","building_id","storey_id"] if c in df]].copy(); out["unit_rate"] = 0.0; out["amount"] = out["quantity"]*out["unit_rate"]; out["cost_status"]="Rate required"
 st.metric("Handoff Lines",len(out)); st.metric("Priced Amount",f"{out.amount.sum():,.2f}")
 edited=st.data_editor(out,hide_index=True,use_container_width=True,column_config={"unit_rate":st.column_config.NumberColumn("Unit Rate",min_value=0.0),"amount":st.column_config.NumberColumn("Amount",disabled=True)})
 edited["amount"]=edited["quantity"]*edited["unit_rate"]; edited["cost_status"]=edited["unit_rate"].apply(lambda x:"Priced" if x>0 else "Rate required")
 st.download_button("Export Costing Handoff CSV",edited.to_csv(index=False),"imagine_bim_costing_handoff.csv","text/csv",use_container_width=True)
