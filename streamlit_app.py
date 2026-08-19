"""
IMAGINE — Generative Architecture & Civil Engine
Main Application Router and Page Wrapper
Path: streamlit_app.py
App: imagine
"""

import importlib
from dataclasses import dataclass
import streamlit as st

# ==============================================================================
# PAGE CONFIGURATION & GLASSMORPHIC STYLING
# ==============================================================================
st.set_page_config(
    page_title="IMAGINE — Generative Architecture & Civil Engine",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* Glassmorphic Sidebar Frame */
    div[data-testid="stSidebar"] {
        background: rgba(25, 30, 45, 0.65);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* Enterprise Brand Header */
    .brand-title {
        font-size: 1.6rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #FFFFFF;
        margin-bottom: 0px;
    }
    .brand-subtitle {
        font-size: 0.8rem;
        color: #A0AEC0;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }

    /* User Profile Card */
    .user-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 0.75rem 1rem;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 1.25rem;
    }
    .user-card p {
        margin: 0;
        font-size: 0.82rem;
        color: #CBD5E0;
    }
    .user-card strong {
        color: #FFFFFF;
    }

    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        background: rgba(66, 153, 225, 0.2);
        color: #63B3ED;
        border: 1px solid rgba(99, 179, 237, 0.3);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# MODULE METADATA DEFINITION & REGISTRY
# ==============================================================================
@dataclass
class EurocodeMeta:
    code: str
    title: str
    ref: str
    desc: str
    icon: str
    renderer_path: str
    renderer_name: str


EUROCODE_REGISTRY = {
    "EN 1990": EurocodeMeta(
        code="EN 1990",
        title="Basis of Structural Design",
        ref="EN 1990:2002",
        desc="Basis of structural design, reliability classes, and ULS/SLS load combinations.",
        icon="⚖️",
        renderer_path="structural.eurocode.en1990.ui",
        renderer_name="render_en1990",
    ),
    "EN 1991": EurocodeMeta(
        code="EN 1991",
        title="Actions on Structures",
        ref="EN 1991-1-1",
        desc="Densities, self-weight, imposed loads, snow, wind, and thermal actions.",
        icon="🌬️",
        renderer_path="structural.eurocode.en1991.ui",
        renderer_name="render_en1991",
    ),
    "EN 1992": EurocodeMeta(
        code="EN 1992",
        title="Design of Concrete Structures",
        ref="EN 1992-1-1",
        desc="Reinforced and prestressed concrete design for flexure, shear, axial load, and SLS.",
        icon="🧱",
        renderer_path="structural.eurocode.en1992.ui",
        renderer_name="render_en1992",
    ),
    "EN 1993": EurocodeMeta(
        code="EN 1993",
        title="Design of Steel Structures",
        ref="EN 1993-1-1",
        desc="Cross-section classification, member flexural/lateral-torsional buckling, and connections.",
        icon="⚙️",
        renderer_path="structural.eurocode.en1993.ui",
        renderer_name="render_en1993",
    ),
    "EN 1994": EurocodeMeta(
        code="EN 1994",
        title="Design of Composite Structures",
        ref="EN 1994-1-1",
        desc="Composite steel-concrete beams, slabs, shear connector capacity, and interaction.",
        icon="🔗",
        renderer_path="structural.eurocode.en1994.ui",
        renderer_name="render_en1994",
    ),
    "EN 1995": EurocodeMeta(
        code="EN 1995",
        title="Design of Timber Structures",
        ref="EN 1995-1-1",
        desc="Solid timber, glulam, and engineered wood member verification and modification factors.",
        icon="🪵",
        renderer_path="structural.eurocode.en1995.ui",
        renderer_name="render_en1995",
    ),
    "EN 1996": EurocodeMeta(
        code="EN 1996",
        title="Design of Masonry Structures",
        ref="EN 1996-1-1",
        desc="Unreinforced and reinforced masonry wall axial compression, out-of-plane flexure, and shear.",
        icon="🏛️",
        renderer_path="structural.eurocode.en1996.ui",
        renderer_name="render_en1996",
    ),
    "EN 1997": EurocodeMeta(
        code="EN 1997",
        title="Geotechnical Design",
        ref="EN 1997-1",
        desc="Shallow foundations, deep pile foundations, retaining structures, and slope stability.",
        icon="⛏️",
        renderer_path="structural.eurocode.en1997.ui",
        renderer_name="render_en1997",
    ),
    "EN 1998": EurocodeMeta(
        code="EN 1998",
        title="Design for Earthquake Resistance",
        ref="EN 1998-1",
        desc="Seismic hazard response spectra, ductility classes, dynamic analysis, and detailing.",
        icon="〰️",
        renderer_path="structural.eurocode.en1998.ui",
        renderer_name="render_en1998",
    ),
}


# ==============================================================================
# DYNAMIC PAGE WRAPPER & FALLBACK RENDERER
# ==============================================================================
def render_fallback_placeholder(meta: EurocodeMeta) -> None:
    """Renders a standard placeholder UI when a module is not yet exposed or implemented."""
    st.info(f"**{meta.code}: {meta.title} ({meta.ref})** module is currently being configured.")
    st.write(
        "This structural analysis module will include ULS/SLS limit state verifications, "
        "interactive parameter adjustments, and standard compliance checks."
    )
    col1, col2, col3 = st.columns(3)
    col1.metric("Status", "In Development")
    col2.metric("Standard Ref", meta.ref)
    col3.metric("Target Module", meta.code)


def page_wrapper(meta: EurocodeMeta) -> None:
    """Safely dynamic import and rendering wrapper for structural modules."""
    st.subheader(f"{meta.icon} {meta.code} — {meta.title}")
    st.caption(f"Ref: **{meta.ref}** | {meta.desc}")
    st.divider()

    try:
        # Dynamically import module (e.g. structural.eurocode.en1990.ui)
        module = importlib.import_module(meta.renderer_path)

        # Check if expected callable exists (e.g. render_en1990)
        if hasattr(module, meta.renderer_name):
            renderer_func = getattr(module, meta.renderer_name)
            renderer_func()
        else:
            st.warning(
                f"⚠️ Module `{meta.renderer_path}` was imported successfully, but does not expose "
                f"the expected callable `{meta.renderer_name}()`."
            )
            render_fallback_placeholder(meta)

    except ModuleNotFoundError:
        st.info(f"ℹ️ Module file `{meta.renderer_path.replace('.', '/')}.py` was not found.")
        render_fallback_placeholder(meta)

    except Exception as e:
        st.error(f"❌ Execution error encountered inside `{meta.code}` ({meta.renderer_path}):")
        st.exception(e)


# ==============================================================================
# WORKSPACE MODULE PLACEHOLDERS
# ==============================================================================
def render_architecture_ai() -> None:
    """Generative Architecture AI Workspace."""
    st.title("🏛️ Generative Architecture AI Engine")
    st.caption("AI-assisted floor plan generation, spatial optimization, and building envelope design.")
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Spatial Parameters")
        st.number_input("Total Floor Area (m²)", min_value=50, max_value=10000, value=450, step=25)
        st.selectbox("Building Typology", ["Residential Villa", "Commercial Office", "Multi-Family Housing", "Mixed-Use"])
        st.slider("Target Efficiency Ratio", 0.60, 0.95, 0.82, step=0.01)

    with col2:
        st.subheader("Generative Output State")
        st.info("Generative Layout Engine ready. Set constraints and click generate.")
        st.button("⚡ Generate Spatial Layouts", type="primary")


def render_project_overview() -> None:
    """Project Overview Dashboard."""
    st.title("📊 Project Overview & Management")
    st.caption("Active structural models, saved calculations, and export management.")
    st.divider()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Active Eurocodes", "9 Modules")
    m2.metric("Calculations Run", "24")
    m3.metric("Global Annex", "Recommended (CEN)")
    m4.metric("Engine Version", "v1.0.0 Enterprise")


# ==============================================================================
# MAIN APPLICATION CONTROLLER
# ==============================================================================
def main() -> None:
    # Sidebar Header & User Profile
    with st.sidebar:
        st.markdown("<div class='brand-title'>IMAGINE</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='brand-subtitle'>Generative Architecture & Civil Engine</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class='user-card'>
                <p>User: <strong>admin</strong></p>
                <p>Role: <strong>Principal Engineer</strong></p>
                <p><span class='status-badge'>IMAGINE 1.0.0 Enterprise</span></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Primary Workspace Router
        workspace = st.radio(
            "Select Workspace",
            options=[
                "Eurocode Structural Suite",
                "Architecture AI",
                "Project Overview",
            ],
            index=0,
            key="main_workspace_nav",
        )
        st.divider()

    # Workspace Navigation Logic
    if workspace == "Eurocode Structural Suite":
        with st.sidebar:
            st.subheader("Eurocode Standards")
            selected_code = st.radio(
                "Select Standard",
                options=list(EUROCODE_REGISTRY.keys()),
                format_func=lambda code: f"{EUROCODE_REGISTRY[code].icon} {code}: {EUROCODE_REGISTRY[code].title}",
                index=0,  # Defaults to EN 1990
                key="eurocode_selected_code",
            )

        active_meta = EUROCODE_REGISTRY[selected_code]
        page_wrapper(active_meta)

    elif workspace == "Architecture AI":
        render_architecture_ai()

    elif workspace == "Project Overview":
        render_project_overview()


if __name__ == "__main__":
    main()
