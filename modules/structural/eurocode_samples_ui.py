"""Interactive worked-sample navigator for EN 1990 through EN 1999."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from modules.structural.eurocode_samples import SAMPLES, sample_for


def render() -> None:
    st.title("Eurocode Worked Samples")
    st.caption("Illustrative calculations and design workflows for all ten Eurocode families")
    st.warning("These are teaching and preliminary screening examples, not certified design calculations. Verify the adopted edition, National Annex, project inputs and complete clauses before use.")

    overview = pd.DataFrame([
        {"Code": s.code, "Sample": s.title, "Inputs": len(s.inputs), "Outputs": len(s.outputs)}
        for s in SAMPLES
    ])
    st.dataframe(overview, use_container_width=True, hide_index=True)

    selected = st.selectbox("Eurocode family", [s.code for s in SAMPLES], key="worked_sample_code")
    sample = sample_for(selected)
    if sample is None:
        st.error("Sample not found.")
        return

    st.markdown(f"### {sample.code} · {sample.title}")
    left, right = st.columns(2)
    with left:
        st.markdown("#### Sample inputs")
        st.dataframe(pd.DataFrame(sample.inputs, columns=["Parameter", "Value"]), use_container_width=True, hide_index=True)
    with right:
        st.markdown("#### Sample outputs")
        st.dataframe(pd.DataFrame(sample.outputs, columns=["Result", "Value"]), use_container_width=True, hide_index=True)

    st.info(sample.note)

    st.markdown("### Complete Eurocode family map")
    st.write("EN 1990 Basis → EN 1991 Actions → EN 1992 Concrete → EN 1993 Steel → EN 1994 Composite → EN 1995 Timber → EN 1996 Masonry → EN 1997 Geotechnical → EN 1998 Seismic → EN 1999 Aluminium")

    st.download_button(
        "Download worked-sample register",
        overview.to_csv(index=False).encode("utf-8"),
        file_name="imagine_eurocode_worked_samples.csv",
        mime="text/csv",
        use_container_width=True,
    )


render_module = render
__all__ = ["render", "render_module"]
