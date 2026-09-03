"""Structural engineering command dashboard."""
from __future__ import annotations
import pandas as pd
import streamlit as st
from modules.enterprise_registry import MODULE_SPECS


def render() -> None:
    st.title("Structural Engineering Dashboard")
    st.caption("Central command center for structural design, actions, materials, codes and analysis.")
    specs = [s for s in MODULE_SPECS if s.section == "STRUCTURAL"]
    ready = [s for s in specs if s.implemented]
    a,b,c,d = st.columns(4)
    a.metric("Workspaces", len(specs)); b.metric("Ready", len(ready)); c.metric("Eurocodes", 10); d.metric("Design tools", sum(x in {"Beam Design","Column Design","Slab Design","Foundation Design","Retaining Walls","Punching Shear","Steel Members","Steel Connections","Stairs Design","Openings Design","Railings & Balustrades"} for x in ready))
    groups = {
        "Basis & Actions": ["Structural Design Handbook","Load Combinations","Wind Actions","Seismic Actions","Eurocode Suite","EN 1990","EN 1991","EN 1998"],
        "Concrete": ["Building Materials","EN 1992","Beam Design","Column Design","Slab Design","Foundation Design","Punching Shear","RC Detailing"],
        "Steel": ["EN 1993","Steel Members","Steel Connections","Section Shapes"],
        "Other Materials": ["EN 1994","EN 1995","EN 1996","EN 1999"],
        "Building Components": ["Roof Design","Stairs Design","Openings Design","Railings & Balustrades"],
        "Analysis": ["Structural Analysis","Finite Element Analysis"],
    }
    rows=[]
    for group, labels in groups.items():
        found=[s for s in specs if s.label in labels]
        rows.append({"Area":group,"Ready":sum(s.implemented for s in found),"Workspaces":len(found)})
    left,right=st.columns([1,1.6])
    with left: st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
    with right:
        df=pd.DataFrame(rows); st.bar_chart(df.set_index("Area")["Ready"])
    st.subheader("Design workflow")
    st.info("Actions → EN 1990/1991 → material/code basis → member design → foundations/geotechnics → analysis → detailing → review.")
    st.warning("Engineering outputs are preliminary unless explicitly validated against the adopted Eurocode edition, National Annex, project specification and professional design review.")

__all__=["render"]
