"""
IMAGINE Platform — Main Router & Navigation System
Path: app.py
App: imagine
"""

import importlib
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="IMAGINE — Civil & Structural Eurocode Suite",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Global Session State Initialization
if "national_annex" not in st.session_state:
    st.session_state["national_annex"] = "UK National Annex (BS EN)"
if "project_name" not in st.session_state:
    st.session_state["project_name"] = "Commercial Development Tower A"


# 3. Module Navigation Routing Directory
NAV_MAP = {
    "🧱 EN 1992: Concrete Structures": {
        "RC Column Design": "modules.structural.column_design",
        "RC Slab Design": "modules.structural.slab_design",
        "Pad Footing Design": "modules.structural.foundation_design",
        "Punching Shear Verification": "modules.structural.punching_shear",
    },
    "⚖️ EN 1990 & 1991: Loads & Actions": {
        "EN 1990 Basis of Structural Design": "modules.structural.en1990_basis",
        "EN 1991 Wind & Imposed Actions": "modules.structural.en1991_actions",
    },
    "🔩 EN 1993 & 1994: Steel & Composite": {
        "EN 1993 Steel Beam & Column Design": "modules.structural.en1993_steel",
        "EN 1994 Composite Slab & Beam": "modules.structural.en1994_composite",
    },
    "🪵 EN 1995 & 1996: Timber & Masonry": {
        "EN 1995 Timber Joist & Post Design": "modules.structural.en1995_timber",
        "EN 1996 Masonry Wall Verification": "modules.structural.en1996_masonry",
    },
    "🌍 EN 1997 & 1998: Geotech & Seismic": {
        "EN 1997 Retaining Wall & Foundation": "modules.structural.retaining_wall",
        "EN 1998 Seismic Analysis & Ductility": "modules.structural.en1998_seismic",
    },
}


def load_module(module_path: str):
    """Dynamically imports and executes the module's render() function."""
    try:
        mod = importlib.import_module(module_path)
        if hasattr(mod, "render"):
            mod.render()
        else:
            st.error(f"Module `{module_path}` does not define a `render()` function.")
    except ModuleNotFoundError:
        st.warning(f"🔨 Module `{module_path}` is currently under development.")
        st.info("Ensure the corresponding Python file exists inside your `modules/` directory.")


def render_sidebar() -> str:
    """Renders the top branding, global settings, and returns the selected route."""
    with st.sidebar:
        st.title("🏗️ IMAGINE")
        st.caption("Eurocode Structural Engineering & Generative Design Engine")
        st.divider()

        # Global Project & National Annex Selection
        st.markdown("### 🌐 Global Design Context")
        st.session_state["project_name"] = st.text_input("Project Name", value=st.session_state["project_name"])
        st.session_state["national_annex"] = st.selectbox(
            "National Annex (NA)",
            [
                "UK National Annex (BS EN)",
                "Recommended EN Values (Standard)",
                "German National Annex (DIN EN)",
                "Irish National Annex (IS EN)",
                "French National Annex (NF EN)"
            ],
            index=0
        )

        st.divider()
        st.markdown("### 🧭 Navigation")

        # Category and Module Pickers
        category = st.selectbox("Eurocode Standard Category", list(NAV_MAP.keys()))
        selected_route = st.radio("Select Design Module", list(NAV_MAP[category].keys()))

        st.divider()
        st.caption(f"Active NA: **{st.session_state['national_annex'].split()[0]}**")
        st.caption("App: `imagine` v1.0.0 | EN 1990 - EN 1998")

        return NAV_MAP[category][selected_route]


def main():
    selected_module_path = render_sidebar()
    load_module(selected_module_path)


if __name__ == "__main__":
    main()