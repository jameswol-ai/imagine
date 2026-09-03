"""Streamlit workspace for comparing architecture design standards."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from .engine import STANDARD_PROFILES, compare_standard_requirements


def render_design_standards() -> None:
    """Render the architecture standards comparison workspace."""
    st.title("Design Standards")
    st.caption(
        "Compare reference requirements for rooms, corridors, stairs, doors and other architectural elements. "
        "Always confirm the adopted jurisdiction, occupancy classification and current edition before using a value for design."
    )

    profiles = list(STANDARD_PROFILES)
    selected = st.multiselect(
        "Standards / reference profiles",
        [p.name for p in profiles],
        default=[profiles[0].name, profiles[1].name, profiles[2].name],
        key="architecture_standards_profiles",
    )
    selected_profiles = tuple(p for p in profiles if p.name in selected)

    categories = sorted({r.category for p in selected_profiles for r in p.requirements})
    if not categories:
        st.info("Select at least one standards profile.")
        return

    category = st.selectbox("Design element", categories, key="architecture_standards_category")
    items = sorted({r.item for p in selected_profiles for r in p.requirements if r.category == category})
    item = st.selectbox("Requirement", items, key="architecture_standards_item")

    rows = compare_standard_requirements(category, item, selected_profiles)
    df = pd.DataFrame(rows)
    if df.empty:
        st.warning("No comparable requirement is currently defined for this combination.")
        return

    st.subheader("Standards comparison")
    st.dataframe(df, use_container_width=True, hide_index=True)

    numeric = df.dropna(subset=["Value"])
    if not numeric.empty and numeric["Unit"].nunique() == 1:
        chart = px.bar(numeric, x="Standard", y="Value", text="Value", title=f"{item} comparison ({numeric.iloc[0]['Unit']})")
        chart.update_layout(xaxis_title="Standard / profile", yaxis_title=f"Value ({numeric.iloc[0]['Unit']})")
        st.plotly_chart(chart, use_container_width=True)

    st.subheader("Apply to a concept")
    proposed = st.number_input(
        f"Proposed value ({df.iloc[0]['Unit']})",
        min_value=0.0,
        value=float(df["Value"].dropna().min()) if not df["Value"].dropna().empty else 0.0,
        step=1.0,
        key="architecture_standards_proposed_value",
    )
    numeric_values = [float(v) for v in df["Value"].dropna()]
    if numeric_values:
        max_reference = max(numeric_values)
        st.metric("Highest selected reference", f"{max_reference:g} {df.iloc[0]['Unit']}")
        if proposed >= max_reference:
            st.success("Proposed value meets or exceeds the selected numeric reference benchmarks.")
        else:
            st.warning("Proposed value is below at least one selected reference benchmark. Review the applicable requirement.")

    st.subheader("Standards notes")
    for profile in selected_profiles:
        st.markdown(f"**{profile.name}** · {profile.jurisdiction}: {profile.description}")
    st.info(
        "This workspace is a design-decision aid, not a legal code checker. Requirements can change with occupancy, "
        "building height, evacuation strategy, accessibility category, local amendments and authority requirements."
    )
