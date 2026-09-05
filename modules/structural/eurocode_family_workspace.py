"""Visible workspace used by EN 1990-EN 1999 navigation routes."""
from __future__ import annotations
import pandas as pd
import streamlit as st
from modules.structural.eurocode_data import EUROCODE_FAMILY, parts_for
from modules.structural.eurocode_samples import sample_for


def render_family(code: str) -> None:
    data = EUROCODE_FAMILY[code]
    st.title(f"{code} · {data['title']}")
    st.caption("Eurocode family workspace")
    st.warning("Preliminary learning/design-assistance workspace. Verify the adopted edition, National Annex and project-specific requirements before engineering use.")
    parts = parts_for(code)
    a,b,c=st.columns(3)
    a.metric("Parts",len(parts)); b.metric("Topics",len(data["topics"])); c.metric("Worked sample","Available" if sample_for(code) else "Catalog only")
    st.markdown("### Design topics")
    st.dataframe(pd.DataFrame({"Topic":list(data["topics"])}),use_container_width=True,hide_index=True)
    st.markdown("### Parts and design scope")
    st.dataframe(pd.DataFrame([{"Code":p.code,"Title":p.title,"Scope":p.scope,"Inputs":", ".join(p.inputs),"Outputs":", ".join(p.outputs)} for p in parts]),use_container_width=True,hide_index=True)
    sample=sample_for(code)
    if sample:
        st.markdown("### Used sample")
        left,right=st.columns(2)
        with left: st.dataframe(pd.DataFrame(sample.inputs,columns=["Input","Value"]),use_container_width=True,hide_index=True)
        with right: st.dataframe(pd.DataFrame(sample.outputs,columns=["Output","Value"]),use_container_width=True,hide_index=True)
        st.info(sample.note)
    st.markdown("### Design workflow")
    st.write("Design basis → project parameters → actions → combinations → analysis → resistance checks → detailing → verification → BIM / BOQ handoff")


def render() -> None:
    route=str(st.session_state.get("active_route", "EN 1990"))
    code=route if route in EUROCODE_FAMILY else "EN 1990"
    render_family(code)

render_module=render
__all__=["render","render_module","render_family"]
