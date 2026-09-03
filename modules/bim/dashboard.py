"""BIM command centre."""
import pandas as pd
import plotly.express as px
import streamlit as st
from .core import records

def render() -> None:
    buildings = records("bim_buildings")
    storeys = records("bim_storeys")
    spaces = records("bim_spaces")
    elements = records("bim_elements")
    assemblies = records("bim_assemblies")
    exports = records("ifc_exports")
    st.title("BIM Command Centre")
    st.caption("Connected building information model: spatial hierarchy, components, exchange, quantities and operations.")
    a,b,c,d = st.columns(4)
    a.metric("Buildings", len(buildings)); b.metric("Storeys", len(storeys)); c.metric("Spaces", len(spaces)); d.metric("Elements", len(elements))
    st.divider()
    left,right = st.columns(2)
    with left:
        st.subheader("Model coverage")
        df = pd.DataFrame({"Entity":["Buildings","Storeys","Spaces","Elements","Assemblies","IFC Exports"],"Count":[len(buildings),len(storeys),len(spaces),len(elements),len(assemblies),len(exports)]})
        st.plotly_chart(px.bar(df,x="Entity",y="Count"),use_container_width=True)
    with right:
        st.subheader("Connected workflow")
        for step in ["Project → Building → Storey → Space","Space → Element → Assembly","Model → IFC / COBie","Model → Quantities → Costing","Model → Assets → Digital Twin"]:
            st.info(step)
    st.subheader("Model health")
    checks = {"Buildings registered":bool(buildings),"Storeys linked to buildings":all(s.get("building_id") for s in storeys) if storeys else False,"Spaces linked to buildings":all(s.get("building_id") for s in spaces) if spaces else False,"Elements have type/category":all(e.get("type_name") and e.get("category") for e in elements) if elements else False}
    st.dataframe(pd.DataFrame([{"Check":k,"Status":"Ready" if v else "Needs data"} for k,v in checks.items()]),hide_index=True,use_container_width=True)
    st.caption("BIM data is project information, not a geometric replacement for a native authoring model. Exchange and quantity outputs require project validation.")
