"""Shared runtime for registered IMAGINE enterprise modules.

Every registered module has a usable workspace. Specialist modules can later
replace this renderer without changing navigation or persistence contracts.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import pandas as pd
import streamlit as st


def _active_route() -> str:
    return str(st.session_state.get("active_route", "Enterprise Module"))


def _session_records(route: str) -> list[dict[str, Any]]:
    key = f"enterprise_workspace_{route}"
    if key not in st.session_state:
        st.session_state[key] = []
    return st.session_state[key]


def _load_records(route: str) -> tuple[list[dict[str, Any]], bool]:
    """Load persistent records, falling back to session storage if unavailable."""
    try:
        from database.bootstrap import ensure_schema
        from database.connection import SessionLocal
        from database.models.module_workspace import ModuleWorkspaceRecord

        ensure_schema()
        with SessionLocal() as db:
            rows = (
                db.query(ModuleWorkspaceRecord)
                .filter(ModuleWorkspaceRecord.module_route == route)
                .order_by(ModuleWorkspaceRecord.created_at.desc())
                .all()
            )
            records = [
                {
                    "id": row.id,
                    "name": row.name,
                    "description": row.description or "",
                    "value": float(row.value or 0.0),
                    "metadata": json.dumps(row.metadata_json or {}, ensure_ascii=False),
                    "updated_at": row.updated_at.isoformat() if row.updated_at else "",
                }
                for row in rows
            ]
        return records, True
    except Exception:
        return list(_session_records(route)), False


def _save_record(route: str, name: str, description: str, value: float, metadata: dict[str, Any]) -> None:
    try:
        from database.bootstrap import ensure_schema
        from database.connection import SessionLocal
        from database.models.module_workspace import ModuleWorkspaceRecord

        ensure_schema()
        now = datetime.now(timezone.utc)
        with SessionLocal() as db:
            db.add(
                ModuleWorkspaceRecord(
                    module_route=route,
                    name=name,
                    description=description,
                    value=float(value),
                    metadata_json=metadata,
                    created_at=now,
                    updated_at=now,
                )
            )
            db.commit()
        return
    except Exception:
        records = _session_records(route)
        records.append(
            {
                "name": name,
                "description": description,
                "value": float(value),
                "metadata": json.dumps(metadata, ensure_ascii=False),
                "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
        )


def render_module() -> None:
    """Render a functional persistent workspace for a registered module."""
    route = _active_route()
    records, persistent = _load_records(route)

    st.subheader(f"{route} Workspace")
    st.caption("Enterprise module workspace")

    overview, data_entry, export = st.tabs(["Overview", "Data Entry", "Export"])

    with overview:
        a, b, c = st.columns(3)
        a.metric("Records", len(records))
        b.metric("Persistence", "Database" if persistent else "Session fallback")
        c.metric("Last Update", records[0]["updated_at"] if records else "None")

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
                help="Enter a JSON object for module-specific workspace data.",
            )
            submitted = st.form_submit_button("Save Record", use_container_width=True)

        if submitted:
            try:
                metadata = json.loads(metadata_text or "{}")
                if not isinstance(metadata, dict):
                    raise ValueError("Metadata must be a JSON object.")
                if not name.strip():
                    raise ValueError("Record name is required.")
                _save_record(route, name.strip(), description.strip(), float(value), metadata)
                st.success("Record saved successfully.")
                st.rerun()
            except (ValueError, json.JSONDecodeError) as exc:
                st.error(str(exc))

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
