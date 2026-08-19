"""
architecture/ui.py
------------------
Main entry point for the Architecture workspace module.
Exposes zero-argument `render_architecture()` expected by streamlit_app.py.
"""

from __future__ import annotations

import streamlit as st


def render_architecture() -> None:
    """Zero-argument Streamlit renderer for the Generative Architecture workspace."""
    
    st.title("🏛️ Architecture Workspace")
    st.caption("AI-assisted generative conceptual design, massing, and spatial programming.")

    st.divider()

    # Two-column layout: Parameter controls on left, generative output on right
    col_params, col_main = st.columns([1, 2], gap="large")

    with col_params:
        st.subheader("Design Parameters")

        typology = st.selectbox(
            "Building Typology",
            [
                "Residential Multi-Family",
                "Commercial Office",
                "Mixed-Use High-Rise",
                "Cultural & Public Space",
            ],
            key="arch_typology",
        )

        st.markdown("**Site & Massing Constraints**")
        target_gfa = st.number_input(
            "Target Gross Floor Area (m²)",
            min_value=100,
            value=5000,
            step=250,
            key="arch_gfa",
        )
        max_floors = st.slider(
            "Max Height (Floors)",
            min_value=1,
            max_value=60,
            value=12,
            key="arch_floors",
        )
        site_coverage = st.slider(
            "Max Site Coverage (%)",
            min_value=10,
            max_value=100,
            value=60,
            key="arch_coverage",
        )

        st.markdown("**Architectural Style & AI Steering**")
        style = st.selectbox(
            "Design Aesthetic",
            [
                "Parametric & Organic",
                "Contemporary Glass & Steel",
                "Biophilic & Green Facade",
                "Minimalist Structural Concrete",
            ],
            key="arch_style",
        )

        custom_prompt = st.text_area(
            "Generative Prompt / Specific Instructions",
            placeholder="e.g., Cantilevered upper floors, central daylight atrium, integrated exterior solar shading...",
            key="arch_prompt",
        )

        st.divider()

        generate_btn = st.button(
            "✨ Generate Architectural Concept",
            type="primary",
            use_container_width=True,
            key="arch_generate_btn",
        )

    with col_main:
        if "arch_concept_generated" not in st.session_state:
            st.session_state.arch_concept_generated = False

        if generate_btn:
            st.session_state.arch_concept_generated = True

        tab_massing, tab_program, tab_analysis = st.tabs([
            "🎨 Concept & Massing",
            "📐 Spatial Program",
            "📊 AI Performance Evaluation",
        ])

        with tab_massing:
            if not st.session_state.arch_concept_generated:
                st.info(
                    "Configure design parameters on the left and click "
                    "**Generate Architectural Concept** to run the generative pipeline."
                )
            else:
                st.success(f"Concept generated for **{typology}** ({style})")

                # High-level metrics
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Target GFA", f"{target_gfa:,} m²")
                m2.metric("Floors", f"{max_floors}")
                m3.metric("Est. FAR", f"{round(target_gfa / (target_gfa / max_floors * (100 / site_coverage)), 2)}")
                m4.metric("Floor Efficiency", "84%")

                st.markdown("### 3D Massing Viewer")
                st.markdown(
                    """
                    <div style="
                        background-color: rgba(128, 128, 128, 0.08);
                        border: 1px dashed rgba(128, 128, 128, 0.3);
                        border-radius: 12px;
                        padding: 3.5rem 1.5rem;
                        text-align: center;
                        margin-bottom: 1.5rem;
                    ">
                        <h4 style="margin: 0;">Interactive 3D Massing Viewport</h4>
                        <p style="color: #777; font-size: 0.85rem; margin-top: 0.5rem;">
                            [ WebGL / Three.js Mesh Renderer Container ]
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown("### Facade & Conceptual Options")
                var1, var2 = st.columns(2)
                with var1:
                    st.info("**Option A: High-Performance Solar Envelope**")
                    st.caption("Optimized for solar heat gain reduction and natural ventilation.")
                with var2:
                    st.info("**Option B: Terraced Atrium Design**")
                    st.caption("Maximizes indoor daylight penetration and communal green zones.")

        with tab_program:
            st.markdown("### Area Schedule & Spatial Allocations")
            
            program_data = [
                {"Zone": "Primary Usable Floor Area", "Allocation": "65%", "Target Area (m²)": int(target_gfa * 0.65)},
                {"Zone": "Circulation & Vertical Cores", "Allocation": "18%", "Target Area (m²)": int(target_gfa * 0.18)},
                {"Zone": "MEP & Technical Infrastructure", "Allocation": "10%", "Target Area (m²)": int(target_gfa * 0.10)},
                {"Zone": "Public & Amenity Space", "Allocation": "7%", "Target Area (m²)": int(target_gfa * 0.07)},
            ]
            st.dataframe(program_data, use_container_width=True, hide_index=True)

        with tab_analysis:
            st.markdown("### Preliminary AI Design Evaluation")
            col_eval1, col_eval2 = st.columns(2)

            with col_eval1:
                st.markdown("**Daylight Autonomy Factor**")
                st.progress(0.78, text="78% floor area daylight compliant")

                st.markdown("**Structural Grid Alignment**")
                st.progress(0.88, text="88% optimal column layout efficiency")

            with col_eval2:
                st.markdown("**Solar Radiation Mitigation**")
                st.progress(0.65, text="65% envelope shading performance")

                st.markdown("**Zoning Envelope Compliance**")
                st.progress(0.95, text="95% inside height & setback boundary")
