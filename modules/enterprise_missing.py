"""Route-aware enterprise workspaces for IMAGINE registry entries.

These workspaces provide usable data capture, validation, metrics, charts and
export for routes that do not yet have a specialist engine. They are deliberately
transparent: they do not claim to be certified engineering calculations or live
third-party integrations.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import pandas as pd
import streamlit as st

from modules.enterprise_runtime import _load_records, _save_record


REGIONAL_ROUTES = {"Uganda", "Kenya", "Tanzania", "Rwanda", "South Sudan", "Codes", "Zoning Laws"}
INTEGRATION_ROUTES = {"Microsoft", "AutoCAD", "Revit", "Archicad", "Tekla", "IfcOpenShell", "ArcGIS", "Azure", "Mapbox"}

PROFILES: dict[str, dict[str, Any]] = {
    "Finite Element Analysis": {"description": "Analysis-case register for model inputs, mesh strategy and result review.", "fields": ["Model", "Analysis type", "Mesh", "Result status"]},
    "Elements": {"description": "BIM element register for classification, quantities and coordination status.", "fields": ["Element", "Category", "Level", "Status"]},
    "COBie": {"description": "COBie handover data capture and readiness register.", "fields": ["Asset", "Component", "Type", "Handover status"]},
    "BIM Digital Twin": {"description": "BIM-to-operations handover workspace for digital-twin records.", "fields": ["Asset", "System", "Location", "Twin status"]},
    "Energy": {"description": "Digital-twin energy record workspace for consumption and performance data.", "fields": ["Asset", "Period", "Energy kWh", "Performance"]},
    "Uganda": {"description": "Uganda project-reference workspace for jurisdictional assumptions and approvals.", "fields": ["Requirement", "Authority", "Reference", "Status"]},
    "Kenya": {"description": "Kenya project-reference workspace for jurisdictional assumptions and approvals.", "fields": ["Requirement", "Authority", "Reference", "Status"]},
    "Tanzania": {"description": "Tanzania project-reference workspace for jurisdictional assumptions and approvals.", "fields": ["Requirement", "Authority", "Reference", "Status"]},
    "Rwanda": {"description": "Rwanda project-reference workspace for jurisdictional assumptions and approvals.", "fields": ["Requirement", "Authority", "Reference", "Status"]},
    "South Sudan": {"description": "South Sudan project-reference workspace for jurisdictional assumptions and approvals.", "fields": ["Requirement", "Authority", "Reference", "Status"]},
    "Codes": {"description": "Regional code-reference register. Verify the governing edition and authority before design use.", "fields": ["Code", "Edition", "Jurisdiction", "Reference"]},
    "Zoning Laws": {"description": "Planning and zoning reference register for project assumptions.", "fields": ["Rule", "Jurisdiction", "Source", "Status"]},
    "Microsoft": {"description": "Microsoft integration configuration and data-exchange readiness workspace.", "fields": ["Connection", "Service", "Environment", "Status"]},
    "AutoCAD": {"description": "CAD integration readiness and drawing-exchange register.", "fields": ["Connection", "Drawing set", "Format", "Status"]},
    "Revit": {"description": "Revit integration readiness and model-exchange register.", "fields": ["Connection", "Model", "Version", "Status"]},
    "Archicad": {"description": "Archicad integration readiness and model-exchange register.", "fields": ["Connection", "Model", "Version", "Status"]},
    "Tekla": {"description": "Tekla integration readiness and structural-model exchange register.", "fields": ["Connection", "Model", "Version", "Status"]},
    "IfcOpenShell": {"description": "IFC processing configuration and exchange workspace.", "fields": ["Connection", "IFC file", "Schema", "Status"]},
    "ArcGIS": {"description": "GIS integration readiness and spatial-data register.", "fields": ["Connection", "Layer", "Coordinate system", "Status"]},
    "Azure": {"description": "Cloud integration configuration and deployment-readiness workspace.", "fields": ["Connection", "Resource", "Environment", "Status"]},
    "Mapbox": {"description": "Mapping integration readiness and map-layer register.", "fields": ["Connection", "Map", "Layer", "Status"]},
}


def _route() -> str:
    return str(st.session_state.get("active_route", "Enterprise Module"))


def _profile(route: str) -> dict[str, Any]:
    return PROFILES.get(route, {"description": "Functional enterprise workspace for this registered route.", "fields": ["Record", "Category", "Reference", "Status"]})


def _normalise_records(records: list[dict[str, Any]]) -> pd.DataFrame:
    if not records:
        return pd.DataFrame()
    frame = pd.DataFrame(records).copy()
    if "updated_at" in frame.columns:
        frame["updated_at"] = pd.to_datetime(frame["updated_at"], errors="coerce", utc=True).dt.strftime("%Y-%m-%d %H:%M UTC")
    return frame


def _warning(route: str) -> None:
    if route in REGIONAL_ROUTES:
        st.warning("Reference workspace only. Confirm current legislation, authority requirements and project-specific applicability before relying on an entry for design or approval.")
    elif route in INTEGRATION_ROUTES:
        st.info("Configuration workspace only. A real connector is not claimed until credentials, API contracts and an end-to-end exchange are configured.")
    elif route in {"Finite Element Analysis", "Energy"}:
        st.warning("Design-assistance workspace. Results are not a substitute for a validated engineering model or professional review.")


def render() -> None:
    route = _route()
    profile = _profile(route)
    records, persistent = _load_records(route)

    st.title(route)
    st.caption(profile["description"])
    _warning(route)

    overview, entry, analysis, export = st.tabs(["Overview", "Data Entry", "Analysis", "Export"])
    with overview:
        frame = _normalise_records(records)
        total = len(frame)
        status_count = int(frame["Status"].isin(["Complete", "Active"] ).sum()) if "Status" in frame.columns else 0
        review_count = int(frame["Status"].isin(["Review", "Draft"] ).sum()) if "Status" in frame.columns else 0
        a, b, c, d = st.columns(4)
        a.metric("Records", total)
        b.metric("Ready / Active", status_count)
        c.metric("Review / Draft", review_count)
        d.metric("Storage", "Database" if persistent else "Session")
        if not frame.empty:
            st.dataframe(frame, use_container_width=True, hide_index=True)
        else:
            st.info("No records have been entered yet. Use Data Entry to create the first record.")

    with entry:
        fields = profile["fields"]
        with st.form(f"route_form_{route}", clear_on_submit=True):
            values: dict[str, Any] = {}
            for field in fields:
                if field in {"Energy kWh", "Performance"}:
                    values[field] = st.number_input(field, min_value=0.0, value=0.0, step=1.0)
                elif field in {"Status", "Result status", "Handover status", "Twin status"}:
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
        frame = _normalise_records(records)
        if frame.empty:
            st.info("Add records to populate workspace analysis.")
        else:
            if "Status" in frame.columns:
                counts = frame["Status"].value_counts()
                st.subheader("Status distribution")
                st.bar_chart(counts)
            elif "Energy kWh" in frame.columns:
                numeric = pd.to_numeric(frame["Energy kWh"], errors="coerce").fillna(0)
                st.metric("Total energy", f"{numeric.sum():,.1f} kWh")
                st.bar_chart(numeric)
            else:
                st.subheader("Workspace statistics")
                st.dataframe(frame.describe(include="all").transpose(), use_container_width=True)

    with export:
        if records:
            frame = _normalise_records(records)
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            safe_name = "".join(ch.lower() if ch.isalnum() else "_" for ch in route).strip("_")
            st.download_button("Download CSV", frame.to_csv(index=False).encode("utf-8"), file_name=f"{safe_name}_{stamp}.csv", mime="text/csv", use_container_width=True)
            st.download_button("Download JSON", json.dumps(records, indent=2, ensure_ascii=False, default=str).encode("utf-8"), file_name=f"{safe_name}_{stamp}.json", mime="application/json", use_container_width=True)
        else:
            st.info("Add records before exporting.")


render_module = render
__all__ = ["PROFILES", "render", "render_module"]
