"""Data-driven Eurocode Suite for the IMAGINE structural workbench.

The suite combines the Eurocode metadata catalog with a non-copyrighted
engineering knowledge layer. Normative text is intentionally not reproduced.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from modules.structural.eurocode import render as render_load_combinations
from modules.structural.eurocode_data import EUROCODE_FAMILY, all_parts, family_codes, parts_for
from modules.structural.eurocode_knowledge import CHECKS, PARAMETERS, FAMILIES, checks_for, search_catalog


IMPLEMENTED_WORKSPACES = {
    "Load Combinations", "Wind Actions", "Structural Analysis", "Beam Design",
    "Column Design", "Slab Design", "Foundation Design", "Retaining Walls",
    "Punching Shear", "Steel Members", "Steel Connections", "Section Shapes",
    "RC Detailing", "Roof Design", "Building Materials", "Seismic Actions",
}


def _unique_parts(parts):
    seen = set()
    result = []
    for part in parts:
        if part.code in seen:
            continue
        seen.add(part.code)
        result.append(part)
    return result


def _open_workspace(label: str) -> None:
    st.session_state.active_route = label
    st.session_state.workspace = label
    st.rerun()


def _family_frame() -> pd.DataFrame:
    rows = []
    for code in family_codes():
        data = EUROCODE_FAMILY[code]
        parts = _unique_parts(parts_for(code))
        knowledge = FAMILIES.get(code, {})
        rows.append({
            "Family": code,
            "Title": data["title"],
            "Parts": len(parts),
            "Topics": len(data["topics"]),
            "Design checks": len(knowledge.get("checks", ())),
        })
    return pd.DataFrame(rows)


def _part_frame(parts) -> pd.DataFrame:
    return pd.DataFrame([
        {"Code": p.code, "Title": p.title, "Topics": ", ".join(p.topics), "Linked workspaces": ", ".join(p.linked_tools)}
        for p in _unique_parts(parts)
    ])


def _render_part(part) -> None:
    st.markdown(f"### {part.code} · {part.title}")
    st.caption(part.scope)
    c1, c2, c3 = st.columns(3)
    c1.metric("Design topics", len(part.topics))
    c2.metric("Input groups", len(part.inputs))
    c3.metric("Output groups", len(part.outputs))
    left, right = st.columns(2)
    with left:
        st.markdown("#### Topics")
        st.dataframe(pd.DataFrame({"Topic": list(part.topics)}), use_container_width=True, hide_index=True)
        st.markdown("#### Typical inputs")
        st.dataframe(pd.DataFrame({"Input": list(part.inputs)}), use_container_width=True, hide_index=True)
    with right:
        st.markdown("#### Typical outputs")
        st.dataframe(pd.DataFrame({"Output": list(part.outputs)}), use_container_width=True, hide_index=True)
        st.markdown("#### IMAGINE workspaces")
        for tool in part.linked_tools:
            status = "Implemented" if tool in IMPLEMENTED_WORKSPACES else "Integration target"
            a, b = st.columns([3, 1])
            a.write(tool)
            b.caption(status)
            if tool in IMPLEMENTED_WORKSPACES and st.button(f"Open {tool}", key=f"ec_open_{part.code}_{tool}"):
                _open_workspace(tool)


def _render_knowledge() -> None:
    st.subheader("Engineering knowledge map")
    st.caption("Structured design-check schemas. Parameters remain project and National-Annex controlled.")
    family = st.selectbox("Knowledge family", family_codes(), key="ec_knowledge_family")
    checks = checks_for(family)
    if not checks:
        st.info("No detailed check schema is catalogued for this family yet.")
        return
    rows = [{"ID": c.id, "Check": c.name, "Status": c.status, "Tools": ", ".join(c.tools)} for c in checks]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    selected_id = st.selectbox("Open design check", [c.id for c in checks], key=f"ec_check_{family.replace(' ', '_')}")
    check = next(c for c in checks if c.id == selected_id)
    st.markdown(f"### {check.name}")
    st.write(check.purpose)
    a, b = st.columns(2)
    with a:
        st.markdown("**Inputs**")
        st.dataframe(pd.DataFrame({"Input": list(check.inputs)}), use_container_width=True, hide_index=True)
    with b:
        st.markdown("**Outputs**")
        st.dataframe(pd.DataFrame({"Output": list(check.outputs)}), use_container_width=True, hide_index=True)
    st.markdown("**Linked workspaces**")
    for tool in check.tools:
        if tool in IMPLEMENTED_WORKSPACES and st.button(f"Open {tool}", key=f"ec_check_tool_{selected_id}_{tool}"):
            _open_workspace(tool)
        else:
            st.write(tool)


def _render_parameters() -> None:
    frame = pd.DataFrame([
        {"Parameter": p.key, "Label": p.label, "Unit": p.unit, "Source / control": p.source, "Required": "Yes" if p.required else "No", "Project controlled": "Yes" if p.project_controlled else "No"}
        for p in PARAMETERS
    ])
    st.subheader("Parameter register")
    st.caption("This is a parameter schema, not a universal default-value table. Values must be populated from the adopted standard, National Annex and project documents.")
    st.dataframe(frame, use_container_width=True, hide_index=True)
    st.download_button("Download parameter register", frame.to_csv(index=False), "eurocode_parameter_register.csv", "text/csv")


def render() -> None:
    st.title("Eurocode Suite")
    st.caption("EN 1990–EN 1999 knowledge navigator, design-check map and connected structural workspaces.")
    try:
        families = family_codes()
        parts = _unique_parts(all_parts())
    except Exception as exc:
        st.error(f"Eurocode catalog could not be loaded: {exc}")
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Eurocode families", len(families))
    c2.metric("Catalog parts", len(parts))
    c3.metric("Design checks", len(CHECKS))
    c4.metric("Parameters", len(PARAMETERS))
    st.info("Use this suite as a design-basis and navigation layer. The adopted edition, National Annex, project specification and verified engineering calculations remain authoritative.")

    tabs = st.tabs(["Overview", "Family Explorer", "Part Explorer", "Design Checks", "Parameters", "Search", "Coverage", "Calculator"])
    with tabs[0]:
        st.subheader("Eurocode family coverage")
        st.dataframe(_family_frame(), use_container_width=True, hide_index=True)
        st.markdown("#### Connected engineering workflow")
        st.write("Design basis → actions → combinations → analysis → member resistance → connections → foundations → detailing → verification → documentation.")
        st.markdown("#### Current calculation engines")
        st.dataframe(pd.DataFrame({"Workspace": sorted(IMPLEMENTED_WORKSPACES)}), use_container_width=True, hide_index=True)

    with tabs[1]:
        selected_family = st.selectbox("Eurocode family", families, key="eurocode_suite_family")
        data = EUROCODE_FAMILY[selected_family]
        st.markdown(f"### {selected_family} · {data['title']}")
        st.write("Primary topics: " + ", ".join(data["topics"]))
        family_parts = _unique_parts(parts_for(selected_family))
        st.dataframe(_part_frame(family_parts), use_container_width=True, hide_index=True)
        if family_parts:
            selected_code = st.selectbox("Open part", [p.code for p in family_parts], key=f"eurocode_suite_part_{selected_family.replace(' ', '_')}")
            _render_part(next(p for p in family_parts if p.code == selected_code))

    with tabs[2]:
        selected_code = st.selectbox("Eurocode part", [p.code for p in parts], key="eurocode_suite_part")
        _render_part(next(p for p in parts if p.code == selected_code))

    with tabs[3]:
        _render_knowledge()

    with tabs[4]:
        _render_parameters()

    with tabs[5]:
        query = st.text_input("Search Eurocode catalog", placeholder="wind, fire, buckling, foundations, fatigue")
        if query.strip():
            matches = search_catalog(query)
            st.metric("Design-check matches", len(matches))
            if matches:
                st.dataframe(pd.DataFrame([{"ID": c.id, "Family": c.family, "Check": c.name, "Tools": ", ".join(c.tools)} for c in matches]), use_container_width=True, hide_index=True)
                selected_id = st.selectbox("Open result", [c.id for c in matches], key="eurocode_suite_search_result")
                check = next(c for c in matches if c.id == selected_id)
                st.markdown(f"### {check.name}")
                st.write(check.purpose)
            else:
                st.warning("No design-check entries matched that search.")
        else:
            st.caption("Search across design checks, families, inputs, outputs and linked workspaces.")

    with tabs[6]:
        rows = []
        for p in parts:
            rows.append({"Code": p.code, "Title": p.title, "Topics": len(p.topics), "Inputs": len(p.inputs), "Outputs": len(p.outputs), "Linked tools": len(p.linked_tools), "Implemented links": sum(t in IMPLEMENTED_WORKSPACES for t in p.linked_tools)})
        coverage = pd.DataFrame(rows)
        st.dataframe(coverage, use_container_width=True, hide_index=True)
        st.bar_chart(coverage.set_index("Code")["Implemented links"], use_container_width=True)

    with tabs[7]:
        render_load_combinations()

    st.warning("Preliminary engineering knowledge and calculation layer. Do not treat it as a substitute for the adopted Eurocode, National Annex, project-specific actions, material certificates, geotechnical information, specialist fire/seismic provisions, or independent professional verification.")


__all__ = ["IMPLEMENTED_WORKSPACES", "render"]
