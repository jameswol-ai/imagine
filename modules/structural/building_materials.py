"""Building materials library for preliminary structural design studies."""
from __future__ import annotations

import pandas as pd
import streamlit as st

MATERIAL_LIBRARY = [
    {"Material":"Concrete C25/30","Family":"Concrete","Density kg/m³":2400,"Characteristic strength MPa":25,"Elastic modulus GPa":31,"Reference":"EN 1992 / project specification"},
    {"Material":"Concrete C30/37","Family":"Concrete","Density kg/m³":2400,"Characteristic strength MPa":30,"Elastic modulus GPa":33,"Reference":"EN 1992 / project specification"},
    {"Material":"Concrete C35/45","Family":"Concrete","Density kg/m³":2400,"Characteristic strength MPa":35,"Elastic modulus GPa":34,"Reference":"EN 1992 / project specification"},
    {"Material":"Reinforcement B500","Family":"Reinforcing steel","Density kg/m³":7850,"Characteristic strength MPa":500,"Elastic modulus GPa":200,"Reference":"EN 1992 / product standard"},
    {"Material":"Steel S235","Family":"Structural steel","Density kg/m³":7850,"Characteristic strength MPa":235,"Elastic modulus GPa":210,"Reference":"EN 1993 / product standard"},
    {"Material":"Steel S275","Family":"Structural steel","Density kg/m³":7850,"Characteristic strength MPa":275,"Elastic modulus GPa":210,"Reference":"EN 1993 / product standard"},
    {"Material":"Steel S355","Family":"Structural steel","Density kg/m³":7850,"Characteristic strength MPa":355,"Elastic modulus GPa":210,"Reference":"EN 1993 / product standard"},
    {"Material":"Timber C16","Family":"Solid timber","Density kg/m³":370,"Characteristic strength MPa":16,"Elastic modulus GPa":8,"Reference":"EN 1995 / product declaration"},
    {"Material":"Timber C24","Family":"Solid timber","Density kg/m³":420,"Characteristic strength MPa":24,"Elastic modulus GPa":11,"Reference":"EN 1995 / product declaration"},
    {"Material":"Aluminium 6061-T6","Family":"Aluminium","Density kg/m³":2700,"Characteristic strength MPa":240,"Elastic modulus GPa":69,"Reference":"EN 1999 / alloy certificate"},
]


def render() -> None:
    st.subheader("Building Materials Library")
    st.caption("Searchable material reference for preliminary structural studies. Values are indicative and must be confirmed against the adopted material/product standard and project specification.")
    df = pd.DataFrame(MATERIAL_LIBRARY)
    c1,c2 = st.columns([1,1])
    with c1: family = st.selectbox("Material family", ["All families", *sorted(df["Family"].unique())])
    with c2: query = st.text_input("Search materials", placeholder="C30, S355, timber, aluminium...")
    shown = df if family == "All families" else df[df["Family"] == family]
    if query: shown = shown[shown.apply(lambda row: query.casefold() in " ".join(map(str,row.values)).casefold(), axis=1)]
    st.dataframe(shown, use_container_width=True, hide_index=True)
    if not shown.empty:
        selected = st.selectbox("Material detail", shown["Material"].tolist())
        row = shown[shown["Material"] == selected].iloc[0]
        a,b,c,d = st.columns(4)
        a.metric("Density", f'{row["Density kg/m³"]:.0f} kg/m³'); b.metric("Strength", f'{row["Characteristic strength MPa"]:.0f} MPa'); c.metric("Elastic modulus", f'{row["Elastic modulus GPa"]:.0f} GPa'); d.metric("Family", row["Family"])
        st.info(f"Reference: {row['Reference']}")
    st.download_button("Export material library", df.to_csv(index=False).encode("utf-8"), "imagine_material_library.csv", "text/csv")
    st.warning("Indicative reference values only. Do not use this library as a substitute for certified product data, the adopted Eurocode, National Annex, exposure/durability specification or engineer-approved material schedule.")


__all__ = ["MATERIAL_LIBRARY", "render"]
