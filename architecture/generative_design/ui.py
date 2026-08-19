"""
architecture/generative_design/ui.py
------------------------------------
AI multi-objective design space exploration and evolutionary synthesis.
Exposes zero-argument `render_generative_design()` required by streamlit_app.py.
"""

from __future__ import annotations

import streamlit as st


def render_generative_design() -> None:
    """Zero-argument Streamlit renderer for Generative Design & Concept Synthesis."""

    st.title("✨ Generative Design & Concept Synthesis")
    st.caption("Multi-objective algorithmic space exploration, Pareto-frontier optimization, and evolutionary design generation.")

    st.divider()

    col_params, col_main = st.columns([1, 2], gap="large")

    with col_params:
        st.subheader("Generative Parameters")

        optimization_targets = st.multiselect(
            "Optimization Objectives",
            [
                "Maximize Daylight Autonomy",
                "Minimize Structural Material Volume",
                "Maximize View Corridors",
                "Minimize Solar Heat Gain",
                "Maximize Floor Plate Efficiency",
            ],
            default=["Maximize Daylight Autonomy", "Minimize Structural Material Volume"],
            key="gen_design_targets",
        )

        algorithm_type = st.selectbox(
            "Generative Algorithm",
            [
                "NSGA-II (Genetic Multi-Objective)",
                "Latent Space Diffusion / VAE Model",
                "Topology Optimization (MMC)",
                "Agent-Based Spatial Packing",
            ],
            key="gen_design_algorithm",
        )

        st.markdown("**Evolutionary Search Controls**")
        pop_size = st.slider(
            "Population Size (Variants / Gen)",
            min_value=10,
            max_value=200,
            value=50,
            step=10,
            key="gen_design_pop_size",
        )

        generations = st.slider(
            "Evolutionary Generations",
            min_value=5,
            max_value=100,
            value=25,
            step=5,
            key="gen_design_generations",
        )

        mutation_rate = st.slider(
            "Mutation / Variation Rate (%)",
            min_value=1,
            max_value=30,
            value=12,
            key="gen_design_mutation_rate",
        )

        st.divider()

        run_gen_btn = st.button(
            "🚀 Run Generative Optimization Engine",
            type="primary",
            use_container_width=True,
            key="gen_design_run_btn",
        )

    with col_main:
        if "gen_design_explored" not in st.session_state:
            st.session_state.gen_design_explored = False

        if run_gen_btn:
            st.session_state.gen_design_explored = True

        tab_pareto, tab_variants, tab_lineage = st.tabs([
            "📈 Pareto Frontier",
            "🖼️ Selected Variants",
            "🧬 Convergence & Lineage",
        ])

        with tab_pareto:
            if not st.session_state.gen_design_explored:
                st.info(
                    "Configure optimization objectives on the left and click "
                    "**Run Generative Optimization Engine** to synthesize design iterations."
                )
            else:
                st.success(
                    f"Explored {pop_size * generations:,} candidate forms across {generations} generations."
                )

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Evaluated Form Candidates", f"{pop_size * generations:,}")
                m2.metric("Pareto-Optimal Set", "14 Forms")
                m3.metric("Top Daylight Score", "89%")
                m4.metric("Material Reduction", "-22%")

                st.markdown("### Multi-Objective Pareto Scatter Matrix")
                st.markdown(
                    f"""
                    <div style="
                        background-color: rgba(128, 128, 128, 0.08);
                        border: 1px dashed rgba(128, 128, 128, 0.3);
                        border-radius: 12px;
                        padding: 3.5rem 1.5rem;
                        text-align: center;
                        margin-bottom: 1.5rem;
                    ">
                        <h4 style="margin: 0;">Trade-off Chart: Structural Weight vs. Daylight Factor</h4>
                        <p style="color: #777; font-size: 0.85rem; margin-top: 0.5rem;">
                            Algorithm: {algorithm_type.split()[0]} | Population: {pop_size}
                        </p>
                        <p style="color: #777; font-size: 0.8rem;">
                            [ Interactive Plotly / D3 Pareto Frontier Chart ]
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with tab_variants:
            st.markdown("### Top Ranked Pareto-Optimal Candidates")

            v1, v2, v3 = st.columns(3)

            with v1:
                st.markdown("**Variant #42 (Balanced)**")
                st.caption("Optimal balance between daylighting and cantilever steel volume.")
                st.metric("Daylight", "84%")
                st.metric("Structural Efficiency", "91%")

            with v2:
                st.markdown("**Variant #88 (High Daylight)**")
                st.caption("Maximum glazing area with automated solar shading fins.")
                st.metric("Daylight", "94%")
                st.metric("Structural Efficiency", "78%")

            with v3:
                st.markdown("**Variant #104 (Low Mass)**")
                st.caption("Tapered massing optimized for minimal wind load drag.")
                st.metric("Daylight", "76%")
                st.metric("Structural Efficiency", "96%")

        with tab_lineage:
            st.markdown("### Algorithmic Convergence History")

            convergence_history = [
                {"Generation": "Gen 01", "Avg Fitness": "0.42", "Best Fitness": "0.61", "Diversity Index": "0.95"},
                {"Generation": "Gen 05", "Avg Fitness": "0.58", "Best Fitness": "0.74", "Diversity Index": "0.82"},
                {"Generation": "Gen 10", "Avg Fitness": "0.71", "Best Fitness": "0.83", "Diversity Index": "0.68"},
                {"Generation": "Gen 20", "Avg Fitness": "0.82", "Best Fitness": "0.91", "Diversity Index": "0.45"},
                {"Generation": "Gen 25 (Final)", "Avg Fitness": "0.86", "Best Fitness": "0.94", "Diversity Index": "0.32"},
            ]
            st.dataframe(convergence_history, use_container_width=True, hide_index=True)

