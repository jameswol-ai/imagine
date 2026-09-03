"""Shared Streamlit workspace primitives for IMAGINE modules.

The helpers in this module keep individual AEC workspaces visually and
semantically consistent without moving engineering calculations into the UI.
"""
from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import pandas as pd
import streamlit as st


def workspace_header(title: str, description: str, *, domain: str = "") -> None:
    st.title(title)
    if domain:
        st.caption(f"{domain} workspace")
    st.write(description)


def section(title: str, description: str | None = None) -> None:
    st.subheader(title)
    if description:
        st.caption(description)


def kpi_row(items: Iterable[tuple[str, Any, str | None]]) -> None:
    values = list(items)
    cols = st.columns(max(1, min(4, len(values))))
    for index, (label, value, help_text) in enumerate(values):
        with cols[index % len(cols)]:
            st.metric(label, value, help=help_text)


def result_table(rows: list[dict[str, Any]], *, key: str | None = None) -> None:
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, key=key)
    else:
        st.info("No results are available for the current inputs.")


def validation_summary(
    *,
    passed: int,
    warnings: int = 0,
    failures: int = 0,
    note: str | None = None,
) -> None:
    cols = st.columns(3)
    cols[0].metric("Pass", passed)
    cols[1].metric("Warnings", warnings)
    cols[2].metric("Failures", failures)
    if failures:
        st.error("One or more checks require attention before the result is used.")
    elif warnings:
        st.warning("The result contains screening warnings that require engineering review.")
    else:
        st.success("Current screening checks pass for the supplied inputs.")
    if note:
        st.caption(note)


def engineering_notice(text: str = "Preliminary engineering screening only. Verify project-specific standards, National Annex parameters, load cases, combinations and professional design requirements before issue for construction.") -> None:
    st.info(text)
