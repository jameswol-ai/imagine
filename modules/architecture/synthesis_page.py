"""
IMAGINE Platform — Architecture Synthesis UI Component
Path: modules/architecture/synthesis_page.py
App: imagine
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from modules.architecture.synthesis import ArchitectureSynthesisEngine, STATE_KEY
from modules.utils.crud import CRUDService


class ArchitectureSynthesisPage:
    """UI Renderer for the Architecture Synthesis Engine module."""

    @classmethod
    def render(cls) -> None:
        st.title("🏛️ Architecture Generative Synthesis")
        st.caption(
            "Algorithmic spatial layout generator, Floor Area Ratio (FAR) solver, and procedural floorplan synthesis."
        )

        tab_synthesis, tab_saved = st.tabs(["⚡ Layout Generator", "📚 Saved Layout Concepts"])

        with tab_synthesis:
            col_ctrl, col_view = st.columns([1, 2])

            with col_ctrl:
                st.subheader("Parametric Inputs")
                layout_title = st.text_input("Concept Title", value="Tower Block — Concept A")
                typology = st.selectbox(
                    "Building Typology",
                    ["Commercial Office", "Residential", "Mixed-Use", "Educational"],
                )

                st.markdown("---")
                st.write("**Site & Envelope Boundaries**")
                site_w = st.number_input("Site Width (m)", value=40.0, step=5.0, min_value=10.0)
                site_l = st.number_input("Site Length (m)", value=60.0, step=5.0, min_value=10.0)
                floors = st.slider("Number of Floors", min_value=1, max_value=40, value=8)
                target_far = st.slider("Target Floor Area Ratio (FAR)", min_value=0.5, max_value=12.0, value=3.5, step=0.5)

                run_btn = st.button("🚀 Synthesize Architecture", type="primary", use_container_width=True)

            with col_view:
                st.subheader("Generative Floorplan & Massing")

                if run_btn or "last_synthesis" not in st.session_state:
                    res = ArchitectureSynthesisEngine.synthesize_program(
                        site_width=site_w,
                        site_length=site_l,
                        total_floors=floors,
                        target_far=target_far,
                        building_typology=typology,
                    )
                    st.session_state["last_synthesis"] = res
                else:
                    res = st.session_state["last_synthesis"]

                if not res.get("success", False):
                    st.error(res.get("error", "An error occurred during generative synthesis."))
                else:
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Site Area", f"{res['site_area_m2']} m²")
                    m2.metric("Gross Floor Area (GFA)", f"{res['total_gfa_m2']} m²")
                    m3.metric("Achieved FAR", f"{res['achieved_far']} / {target_far}")
                    m4.metric("Footprint", f"{res['footprint_area_m2']} m²")

                    boxes = res["layout_boxes"]
                    fig = go.Figure()

                    fig.add_shape(
                        type="rect",
                        x0=0,
                        y0=0,
                        x1=site_w,
                        y1=site_l,
                        line=dict(color="#A0AEC0", width=2, dash="dot"),
                        fillcolor="rgba(0,0,0,0)",
                        name="Site Boundary",
                    )

                    colors = ["#3182CE", "#38A169", "#DD6B20", "#805AD5", "#E53E3E"]
                    for idx, box in enumerate(boxes):
                        c = colors[idx % len(colors)]
                        fig.add_shape(
                            type="rect",
                            x0=box["x0"],
                            y0=box["y0"],
                            x1=box["x1"],
                            y1=box["y1"],
                            line=dict(color=c, width=2),
                            fillcolor=c,
                            opacity=0.45,
                        )
                        fig.add_annotation(
                            x=(box["x0"] + box["x1"]) / 2,
                            y=(box["y0"] + box["y1"]) / 2,
                            text=f"<b>{box['zone']}</b><br>{box['area_m2']} m²",
                            showarrow=False,
                            font=dict(color="#FFFFFF", size=12),
                        )

                    fig.update_layout(
                        height=420,
                        xaxis=dict(range=[-2, site_w + 2], title="Width (m)", showgrid=True),
                        yaxis=dict(range=[-2, site_l + 2], title="Length (m)", showgrid=True),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#CBD5E0"),
                        margin=dict(l=10, r=10, t=10, b=10),
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    if st.button("💾 Save Synthesis Concept"):
                        record = {
                            "id": f"SYN-{len(CRUDService.get_all(STATE_KEY)) + 1:03d}",
                            "title": layout_title,
                            "typology": typology,
                            "gfa_m2": res["total_gfa_m2"],
                            "far": res["achieved_far"],
                            "floors": floors,
                        }
                        CRUDService.create(STATE_KEY, record)
                        st.success(f"Saved concept `{layout_title}`!")

        with tab_saved:
            st.subheader("Saved Architecture Concepts")
            saved_records = CRUDService.get_all(STATE_KEY)
            if saved_records:
                st.dataframe(pd.DataFrame(saved_records), use_container_width=True, hide_index=True)
            else:
                st.info("No architectural synthesis concepts saved yet.")
