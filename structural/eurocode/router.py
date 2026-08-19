"""
Main Eurocode Structural Design Navigation Router Module
Path: structural/eurocode/router.py
App: imagine
"""

import streamlit as st

# Import implemented Eurocode renderers
try:
    from structural.eurocode.en1995.ui import render_en1995
except ImportError:
    render_en1995 = None

try:
    from structural.eurocode.en1996.ui import render_en1996
except ImportError:
    render_en1996 = None


def render_placeholder(eurocode_code: str, eurocode_name: str, standard_ref: str) -> None:
    """Renders a standard placeholder UI for modules under active development."""
    st.info(f"**{eurocode_code}: {eurocode_name} ({standard_ref})** module is being configured.")
    st.write(
        "This structural analysis module will include ULS/SLS limit state verifications, "
        "interactive parameter adjustments, and full standard compliance checks."
    )
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Status", "In Development")
    col2.metric("Standard", standard_ref)
    col3.metric("Target Module", eurocode_code)


def render_eurocode_router() -> None:
    """Main routing controller for Eurocode Structural Analysis Suite in imagine."""

    # Top Header & Category Overview
    st.markdown("## 🏗️ Structural Eurocode Suite")
    st.caption("Harmonized European standards for structural design and verification (EN 1990 - EN 1998)")

    # Eurocode Definitions
    eurocodes = {
        "EN 1990": {
            "title": "Basis of Structural Design",
            "ref": "EN 1990",
            "desc": "Load combinations, safety factors (γ, ψ), partial factor methodology, and ULS/SLS principles.",
            "icon": "⚖️",
            "renderer": lambda: render_placeholder("EN 1990", "Basis of Structural Design", "EN 1990"),
        },
        "EN 1991": {
            "title": "Actions on Structures",
            "ref": "EN 1991",
            "desc": "Self-weight, imposed loads, snow loads, wind actions, thermal actions, and accidental loads.",
            "icon": "🌬️",
            "renderer": lambda: render_placeholder("EN 1991", "Actions on Structures", "EN 1991"),
        },
        "EN 1992": {
            "title": "Design of Concrete Structures",
            "ref": "EN 1992",
            "desc": "Reinforced and prestressed concrete design for flexure, shear, axial load, and serviceability.",
            "icon": "🧱",
            "renderer": lambda: render_placeholder("EN 1992", "Design of Concrete Structures", "EN 1992"),
        },
        "EN 1993": {
            "title": "Design of Steel Structures",
            "ref": "EN 1993",
            "desc": "Member cross-section classification, flexural buckling, lateral-torsional buckling, and connections.",
            "icon": "⚙️",
            "renderer": lambda: render_placeholder("EN 1993", "Design of Steel Structures", "EN 1993"),
        },
        "EN 1994": {
            "title": "Design of Composite Structures",
            "ref": "EN 1994",
            "desc": "Composite steel-concrete beams, columns, and slabs with shear connection design.",
            "icon": "🔗",
            "renderer": lambda: render_placeholder("EN 1994", "Design of Composite Structures", "EN 1994"),
        },
        "EN 1995": {
            "title": "Design of Timber Structures",
            "ref": "EN 1995",
            "desc": "Solid timber, glulam, and engineered wood member verification, kmod adjustments, and creep.",
            "icon": "🪵",
            "renderer": render_en1995 if render_en1995 else lambda: render_placeholder("EN 1995", "Design of Timber Structures", "EN 1995-1-1"),
        },
        "EN 1996": {
            "title": "Design of Masonry Structures",
            "ref": "EN 1996",
            "desc": "Unreinforced and reinforced masonry wall axial compression, out-of-plane flexure, and shear.",
            "icon": "🏛️",
            "renderer": render_en1996 if render_en1996 else lambda: render_placeholder("EN 1996", "Design of Masonry Structures", "EN 1996-1-1"),
        },
        "EN 1997": {
            "title": "Geotechnical Design",
            "ref": "EN 1997",
            "desc": "Shallow foundations, deep pile foundations, retaining walls, and slope stability analysis.",
            "icon": "⛏️",
            "renderer": lambda: render_placeholder("EN 1997", "Geotechnical Design", "EN 1997"),
        },
        "EN 1998": {
            "title": "Earthquake Resistance Design",
            "ref": "EN 1998",
            "desc": "Seismic hazard response spectra, ductility classes, dynamic analysis, and seismic detailing.",
            "icon": "〰️",
            "renderer": lambda: render_placeholder("EN 1998", "Earthquake Resistance Design", "EN 1998"),
        },
    }

    # Sidebar Navigation Controls
    with st.sidebar:
        st.subheader("Eurocode Module")
        selected_code = st.radio(
            "Select Standard",
            options=list(eurocodes.keys()),
            format_func=lambda code: f"{eurocodes[code]['icon']} {code}: {eurocodes[code]['title']}",
            index=5,  # Default to EN 1995 Timber
        )

    active_module = eurocodes[selected_code]

    # Active Sub-Header Card
    st.subheader(f"{active_module['icon']} {selected_code} — {active_module['title']}")
    st.caption(f"Ref: **{active_module['ref']}** | {active_module['desc']}")
    st.divider()

    # Route Execution
    active_module["renderer"]()


if __name__ == "__main__":
    st.set_page_config(
        page_title="imagine - Eurocode Suite",
        page_icon="📐",
        layout="wide",
    )
    render_eurocode_router()
