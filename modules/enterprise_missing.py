"""Functional route-specific workspaces for registry entries without specialist engines.

These workspaces are intentionally lightweight. They provide usable data capture,
validation, metrics, tables and export while deeper discipline engines are added.
They never pretend to be a certified design calculation or external integration.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import pandas as pd
import streamlit as st

from modules.enterprise_runtime import _load_records, _save_record


PROFILES: dict[str, dict[str, Any]] = {
    "Finite Element Analysis": {"description": "Analysis case workspace for model inputs and result records.", "fields": ["Model", "Analysis type", "Mesh", "Result status"]},
    "Elements": {"description": "BIM element register for classification, quantities and coordination status.", "fields": ["Element", "Category", "Level", "Status"]},
    "COBie": {"description": "COBie handover data capture and readiness register.", "fields": ["Asset", "Component", "Type", "Handover status"]},
    "BIM Digital Twin": {"description": "BIM-to-operations handover workspace for twin records.", "fields": ["Asset", "System", "Location", "Twin status"]},
    "Energy": {"description": "Digital-twin energy record workspace for consumption and performance data.", "fields": ["Asset", "Period", "Energy kWh", "Performance"]},
    "Uganda": {"description": "Uganda project-reference workspace for jurisdictional assumptions and approvals.", "fields": ["Requirement", "Authority", "Reference", "Status"]},
    "Kenya": {"description": "Kenya project-reference workspace for jurisdictional assumptions and approvals.", "fields": ["Requirement", "Authority", "Reference", "Status"]},
    "Tanzania": {"description": "Tanzania project-reference workspace for jurisdictional assumptions and approvals.", "fields": ["Requirement", "Authority", "Reference", "Status"]},
    "Rwanda": {"description": "Rwanda project-reference workspace for jurisdictional assumptions and approvals.", "fields": ["Requirement", "Authority", "Reference", "Status"]},
    "South Sudan": {"description": "South Sudan project-reference workspace for jurisdictional assumptions and approvals.", "fields": ["Requirement", "Authority", "Reference", "Status"]},
    "Codes": {"description": "Regional code-reference register. Verify the governing edition and authority before design use.", "fields": ["Code", "Edition", "Jurisdiction", "Reference"]},
    "Zoning Laws": {"description": "Planning and zoning reference register for project assumptions.", "fields": ["Rule", "Jurisdiction", "Source", "Status"]},
    "Microsoft": {"description": "Integration configuration and data-exchange readiness workspace.", "fields": ["Connection", "Service", "Environment", "Status"]},
    "AutoCAD": {"description": "CAD integration readiness and drawing-exchange register.", "fields": ["Connection", "Drawing set", "Format", "Status"]},
    "Revit": {"description": "Revit integration readiness and model-exchange register.", "fields": ["Connection", "Model", "Version", "Status"]},
    "Archicad": {"description": "Archicad integration readiness and model-exchange register.", "fields": ["Connection", "Model", "Version", "Status"]},
    "Tekla": {"description": "Tekla integration readiness and structural-model exchange register.", "fields": ["Connection", "Model", "Version", "Status"]},
    "IfcOpenShell": {"description": "IFC processing configuration and exchange workspace.", "fields": ["Connection", "IFC file", "Schema", "Status"]},
    "ArcGIS": {"description": "GIS integration readiness and spatial-data register.", "fields": ["Connection", "Layer", "Coordinate system", "Status"]},
    "Azure": {"description": "Cloud integration configuration and deployment readiness workspace.", "fields": ["Connection", "Resource", "Environment", "Status"]},
    "Mapbox": {"description": "Mapping integration readiness and map-layer register.", "fields": ["Connection", "Map", "Layer", "Status"]},
}


def _route() -> str:
    return str(st.session_state.get("active_route", "Enterprise Module"))


def _profile(route: str) -> dict[str, Any]:
    return PROFILES.get(route, {
        "description": "Functional enterprise workspace for this registered route.",
        "fields": ["Record", "Category", "Reference", "Status"],
    })


def _session_records(route: str) -> list[dict[str, Any]]:
    key = f"enterprise_workspace_{route}"
    if key not in st.session_state:
        st.session_state[key] = []
    return st.session_state[key]


def render() -> None:
    route = _route()
    profile = _profile(route)
    records, persistent = _load_records(route)

    st.subheader(f"{route} Workspace")
    st.caption(profile["description"])

    if route in {"Uganda", "Kenya", "Tanzania", "Rwanda", "South Sudan", "Codes", "Zoning Laws"}:
        st.warning("Reference workspace only. Confirm current legislation, authority requirements and project-specific applicability before relying on an entry for design or approval.")
    elif route in {"Microsoft", "AutoCAD", "Revit", "Archicad", "Tekla", "IfcOpenShell", "ArcGIS", "Azure", "Mapbox"}:
        st.info("Configuration workspace only. A real connector is not claimed until credentials, API contracts and an end-to-end exchange are configured.")
    elif route in {"Finite Element Analysis", "Energy"}:
        st.warning("Design-assistance workspace. Results are not a substitute for a validated engineering model or professional review.")

    overview, entry, analysis, export = st.tabs(["Overview", "Data Entry", "Analysis", "Export"])
    with overview:
        a, b, c = st.columns(3)
        a.metric("Records", len(records))
        b.metric("Storage", "Database" if persistent else "Session fallback")
        c.metric("Updated", records[0].get("updated_at", "None") if records else "None")
        if records:
            st.dataframe(pd.DataFrame(records), use_container_width=True, hide_index=True)
        else:
            st.info("No records have been entered yet.")

    with entry:
        fields = profile["fields"]
        with st.form(f"route_form_{route}", clear_on_submit=True):
            values: dict[str, Any] = {}
            for index, field in enumerate(fields):
                if field in {"Energy kWh", "Performance"}:
                    values[field] = st.number_input(field, min_value=0.0, value=0.0, step=1.0)
                elif field == "Status":
                    values[field] = st.selectbox(field, ["Draft", "Active", "Review", "Complete", "Blocked"])
                else:
                    values[field] = st.text_input(field)
            notes = st.text_area("Notes")
            submitted = st.form_submit_button("Save Record", use_container_width=True)
        if submitted:
            primary = next((str(values[f]).strip() for f in fields if str(values.get(f, "")).strip()), "")
            if not primary:
                st.error("Enter at least one identifying field before saving.")
            else:
                _save_record(route, primary, notes.strip(), 0.0, {"fields": values})
                st.success("Record saved successfully.")
                st.rerun()

    with analysis:
        frame = pd.DataFrame(records)
        if frame.empty:
            st.info("Add records to populate workspace analysis.")
        else:
            st.metric("Record count", len(frame))
            if "Status" in frame.columns:
                st.bar_chart(frame["Status"].value_counts())
            elif "Energy kWh" in frame.columns:
                numeric = pd.to_numeric(frame["Energy kWh"], errors="coerce").fillna(0)
                st.metric("Total energy", f"{numeric.sum():,.1f} kWh")
                st.bar_chart(numeric)
            else:
                st.dataframe(frame.describe(include="all").transpose(), use_container_width=True)

    with export:
        if records:
            frame = pd.DataFrame(records)
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            st.download_button("Download CSV", frame.to_csv(index=False).encode("utf-8"), file_name=f"{route.lower().replace(' ', '_')}_{stamp}.csv", mime="text/csv", use_container_width=True)
            st.download_button("Download JSON", json.dumps(records, indent=2, ensure_ascii=False).encode("utf-8"), file_name=f"{route.lower().replace(' ', '_')}_{stamp}.json", mime="application/json", use_container_width=True)
        else:
            st.info("Add records before exporting.")


render_module = render
__all__ = ["PROFILES", "render", "render_module"]
