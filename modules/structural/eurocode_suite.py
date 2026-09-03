"""Data-driven Eurocode Suite for the IMAGINE structural workbench.

The suite consumes ``modules.structural.eurocode_data`` as its source of
structured knowledge. It deliberately presents metadata, design topics,
inputs, outputs and links to IMAGINE workspaces instead of reproducing
copyrighted standards text.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from modules.structural.eurocode_data import EUROCODE_FAMILY, all_parts, family_codes, parts_for


IMPLEMENTED_WORKSPACES = {
    "Load Combinations",
    "Wind Actions",
    "Structural Analysis",
    "Beam Design",
    "Column Design",
    "Slab Design",
    "Foundation Design",
    "Retaining Walls",
    "Punching Shear",
    "Steel Members",
    "Steel Connections",
    "Section Shapes",
    "RC Detailing",
    "Roof Design",
    "Building Materials",
}


def _unique_parts(parts):
    """Return parts in source order without duplicate identifiers."""
    seen = set()
    result = []
    for part in parts:
        if part.code in seen:
            continue
        seen.add(part.code)
        result.append(part)
    return result


def _open_workspace(label: str) -> None:
    """Route the user back through the application shell to a workspace."""
    st.session_state.active_route = label
    st.session_state.workspace = label
    st.rerun()


def _family_frame() -> pd.DataFrame:
    rows = []
    for code in family_codes():
        family = EUROCODE_FAMILY[code]
        parts = _unique_parts(parts_for(code))
        rows.append(
            {
                "Family": code,
                "Title": family["title"],
                "Parts": len(parts),
                "Topics": len(family["topics"]),
            }
        )
    return pd.DataFrame(rows)


def _part_frame(parts) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Code": p.code,
                "Title": p.title,
                "Topics": ", ".join(p.topics),
                "Linked workspaces": ", ".join(p.linked_tools),
            }
            for p in _unique_parts(parts)
        ]
    )


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
            status = "Implemented" if tool in IMPLEMENTED_WORKSPACES else "Linked / integration target"
            a, b = st.columns([3, 1])
            a.write(tool)
            b.caption(status)
            if tool in IMPLEMENTED_WORKSPACES and st.button(f"Open {tool}", key=f"ec_open_{part.code}_{tool}"):
                _open_workspace(tool)


def render() -> None:
    st.title("Eurocode Suite")
    st.caption(
        "Structured EN 1990–EN 1999 knowledge navigator with design topics, input/output maps and linked IMAGINE workspaces."
    )

    try:
        families = family_codes()
        parts = _unique_parts(all_parts())
    except Exception as exc:
        st.error(f"Eurocode catalog could not be loaded: {exc}")
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Eurocode families", len(families))
    c2.metric("Catalog parts", len(parts))
    c3.metric("Design topics", len(set(t for p in parts for t in p.topics)))
    c4.metric("Linked workspaces", len(set(t for p in parts for t in p.linked_tools)))

    st.info(
        "Use the catalog as a navigation and design-basis layer. The adopted edition, National Annex, project specification and verified engineering calculations remain authoritative."
    )

    tabs = st.tabs(["Overview", "Family Explorer", "Part Explorer", "Search", "Coverage"])

    with tabs[0]:
        st.subheader("Eurocode family coverage")
        st.dataframe(_family_frame(), use_container_width=True, hide_index=True)
        st.markdown("#### Engineering workflow")
        st.write(
            "Design basis → actions → combinations → analysis → member resistance → "
            "connections → foundations → detailing → verification → documentation."
        )

    with tabs[1]:
        selected_family = st.selectbox("Eurocode family", families, key="eurocode_suite_family")
        family = EUROCODE_FAMILY[selected_family]
        st.markdown(f"### {selected_family} · {family['title']}")
        st.write("Primary topics: " + ", ".join(family["topics"]))
        family_parts = _unique_parts(parts_for(selected_family))
        st.dataframe(_part_frame(family_parts), use_container_width=True, hide_index=True)
        if family_parts:
            selected_code = st.selectbox(
                "Open part",
                [p.code for p in family_parts],
                key=f"eurocode_suite_part_{selected_family.replace(' ', '_')}",
            )
            _render_part(next(p for p in family_parts if p.code == selected_code))

    with tabs[2]:
        selected_code = st.selectbox("Eurocode part", [p.code for p in parts], key="eurocode_suite_part")
        selected = next(p for p in parts if p.code == selected_code)
        _render_part(selected)

    with tabs[3]:
        query = st.text_input("Search Eurocode catalog", placeholder="e.g. wind, fire, buckling, foundations, fatigue")
        if query.strip():
            q = query.casefold()
            matches = [
                p
                for p in parts
                if q in " ".join([p.code, p.title, p.scope, *p.topics, *p.inputs, *p.outputs, *p.linked_tools]).casefold()
            ]
            st.metric("Matches", len(matches))
            if matches:
                st.dataframe(_part_frame(matches), use_container_width=True, hide_index=True)
                selected_search_code = st.selectbox("Open search result", [p.code for p in matches], key="eurocode_suite_search_result")
                _render_part(next(p for p in matches if p.code == selected_search_code))
            else:
                st.warning("No catalog entries matched that search.")
        else:
            st.caption("Search across codes, scopes, topics, inputs, outputs and linked workspaces.")

    with tabs[4]:
        rows = []
        for p in parts:
            rows.append(
                {
                    "Code": p.code,
                    "Title": p.title,
                    "Topics": len(p.topics),
                    "Inputs": len(p.inputs),
                    "Outputs": len(p.outputs),
                    "Linked tools": len(p.linked_tools),
                    "Implemented links": sum(tool in IMPLEMENTED_WORKSPACES for tool in p.linked_tools),
                }
            )
        coverage = pd.DataFrame(rows)
        st.dataframe(coverage, use_container_width=True, hide_index=True)
        st.markdown("#### Implementation signal")
        st.bar_chart(coverage.set_index("Code")["Implemented links"], use_container_width=True)

    st.warning(
        "Preliminary engineering knowledge layer. Do not treat this catalog as a substitute for the adopted Eurocode, National Annex, project-specific actions, material certificates, geotechnical information, specialist fire/seismic provisions, or independent professional verification."
    )


__all__ = ["IMPLEMENTED_WORKSPACES", "render"]
