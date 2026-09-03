"""Shared runtime for registered IMAGINE enterprise modules.

This runtime gives every registered module a usable workspace while its
specialist implementation is being connected. It deliberately avoids emojis
and keeps transient workspace data in Streamlit session state.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import pandas as pd
import streamlit as st


def _active_route() -> str:
    return str(st.session_state.get("active_route", "Enterprise Module"))


def _workspace_key(route: str) -> str:
    return f"enterprise_workspace_{route}"


def _records(route: str) -> list[dict[str, Any]]:
    key = _workspace_key(route)
    if key not in st.session_state:
        st.session_state[key] = []
    return st.session_state[key]


def render_module() -> None:
    """Render a functional generic workspace for a registered module."""
    route = _active_route()
    records = _records(route)

    st.subheader(f"{route} Workspace")
    st.caption("Enterprise module workspace")

    overview, data_entry, export = st.tabs(["Overview", "Data Entry", "Export"])

    with overview:
        a, b, c = st.columns(3)
        a.metric("Records", len(records))
        b.metric("Workspace", "Ready")
        c.metric("Last Update", records[-1]["updated_at"] if records else "None")

        if records:
            st.dataframe(pd.DataFrame(records), use_container_width=True, hide_index=True)
        else:
            st.info("No records have been entered in this workspace yet.")

    with data_entry:
        with st.form(f"enterprise_form_{route}", clear_on_submit=True):
            name = st.text_input("Record name")
            description = st.text_area("Description")
            value = st.number_input("Value", value=0.0, step=1.0)
            metadata_text = st.text_area(
                "Additional metadata (JSON)",
                value="{}",
                help="Enter a JSON object for module-specific temporary data.",
            )
            submitted = st.form_submit_button("Save Record", use_container_width=True)

        if submitted:
            try:
                metadata = json.loads(metadata_text or "{}")
                if not isinstance(metadata, dict):
                    raise ValueError("Metadata must be a JSON object.")
                if not name.strip():
                    raise ValueError("Record name is required.")
                timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
                records.append(
                    {
                        "name": name.strip(),
                        "description": description.strip(),
                        "value": float(value),
                        "metadata": json.dumps(metadata, ensure_ascii=False),
                        "updated_at": timestamp,
                    }
                )
                st.success("Record saved to the current workspace.")
                st.rerun()
            except (ValueError, json.JSONDecodeError) as exc:
                st.error(str(exc))

        if records and st.button("Clear Workspace Records", use_container_width=True):
            st.session_state[_workspace_key(route)] = []
            st.rerun()

    with export:
        if records:
            frame = pd.DataFrame(records)
            st.download_button(
                "Download CSV",
                frame.to_csv(index=False).encode("utf-8"),
                file_name=f"{route.lower().replace(' ', '_')}.csv",
                mime="text/csv",
                use_container_width=True,
            )
            st.download_button(
                "Download JSON",
                json.dumps(records, indent=2, ensure_ascii=False).encode("utf-8"),
                file_name=f"{route.lower().replace(' ', '_')}.json",
                mime="application/json",
                use_container_width=True,
            )
        else:
            st.info("Enter records before exporting workspace data.")


__all__ = ["render_module"]
