"""BIM quantity schedules derived from registered elements."""
import pandas as pd
import streamlit as st
from .core import records

def render()->None:
 st.title("BIM Quantities & Schedules"); st.caption("Aggregate registered BIM component quantities for schedules and downstream BOQ workflows.")
 elements=records("bim_elements")
 if not elements: st.info("Register BIM elements first."); return
 df=pd.DataFrame(elements)
 a,b,c=st.columns(3); a.metric("Element records",len(df)); b.metric("Categories",df.category.nunique()); c.metric("Quantity lines",len(df.groupby(["category","type_name","unit"])))
 schedule=df.groupby(["category","type_name","unit"],dropna=False)["quantity"].sum().reset_index().sort_values("category")
 st.subheader("Quantity Schedule"); st.dataframe(schedule,hide_index=True,use_container_width=True)
 st.subheader("Category Summary"); st.bar_chart(df.groupby("category")["quantity"].sum())
 st.download_button("Export Quantity Schedule CSV",schedule.to_csv(index=False),"imagine_bim_quantities.csv","text/csv",use_container_width=True)
