"""Interactive EN 1990-style load combination workspace.

The UI reads and writes the shared structural context so later analysis and
member-design workspaces can consume the same project actions. This remains a
screening tool: the adopted National Annex and project-specific combinations
must be verified before engineering use.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from modules.structural.context import CombinationResult, get_context
from modules.structural.ec0 import LoadSet, build_sls_combinations, build_uls_combinations


def _action_value(context, category: str, fallback: float) -> float:
    values = [action.value for action in context.actions if action.category == category]
    return sum(values) if values else fallback


def render() -> None:
    context = get_context()
    st.title("Load Combinations")
    st.caption(
        "Transparent EN 1990-style ULS and SLS combination generator for preliminary structural design."
    )

    c1, c2 = st.columns(2)
    with c1:
        g = st.number_input(
            "Permanent action G (kN)", min_value=0.0,
            value=float(_action_value(context, "Permanent", 100.0)), step=5.0,
            key="structural_comb_g",
        )
        q = st.number_input(
            "Leading variable action Q (kN)", min_value=0.0,
            value=float(_action_value(context, "Variable", 50.0)), step=5.0,
            key="structural_comb_q",
        )
        qa = st.number_input(
            "Accompanying variable action (kN)", min_value=0.0,
            value=float(_action_value(context, "Accompanying", 0.0)), step=5.0,
            key="structural_comb_qa",
        )
    with c2:
        wind = st.number_input(
            "Wind W (kN)", min_value=0.0,
            value=float(_action_value(context, "Wind", 0.0)), step=5.0,
            key="structural_comb_wind",
        )
        snow = st.number_input(
            "Snow S (kN)", min_value=0.0,
            value=float(_action_value(context, "Snow", 0.0)), step=5.0,
            key="structural_comb_snow",
        )
        psi0 = st.number_input(
            "psi0", min_value=0.0, max_value=1.0, value=0.70, step=0.05,
            key="structural_comb_psi0",
        )

    actions = LoadSet(g, q, qa, wind, snow)
    uls = build_uls_combinations(actions, psi0=psi0)
    sls = build_sls_combinations(actions, psi0=psi0)

    uls_records = [CombinationResult(name, value, "ULS") for name, value in uls]
    sls_records = [CombinationResult(name, value, "SLS") for name, value in sls]
    all_records = uls_records + sls_records
    governing_uls = max(uls_records, key=lambda item: item.value) if uls_records else None
    governing_sls = max(sls_records, key=lambda item: item.value) if sls_records else None
    context.set_combinations(all_records, governing_uls, governing_sls)

    st.subheader("ULS")
    st.dataframe(
        pd.DataFrame([(item.name, item.value) for item in uls_records], columns=["Combination", "Action"]),
        use_container_width=True,
        hide_index=True,
    )
    st.subheader("SLS")
    st.dataframe(
        pd.DataFrame([(item.name, item.value) for item in sls_records], columns=["Combination", "Action"]),
        use_container_width=True,
        hide_index=True,
    )

    if governing_uls:
        st.metric("Governing ULS screening action", f"{governing_uls.value:,.2f} kN")
        st.caption(f"{governing_uls.name}")
    if governing_sls:
        st.metric("Governing SLS screening action", f"{governing_sls.value:,.2f} kN")

    st.success("Combination results are now available to downstream structural workspaces through the shared context.")
    st.info(
        "Screening defaults are not a substitute for the adopted EN 1990 National Annex, project-specific action models, or professional verification."
    )


__all__ = ["render"]
