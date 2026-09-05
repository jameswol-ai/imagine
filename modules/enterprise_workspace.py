"""Functional workspaces for enterprise routes that are not specialist solvers yet.

These workspaces are deliberately useful rather than empty placeholders. They
provide route-specific inputs, deterministic screening calculations, validation,
record persistence in session state, and CSV/JSON export. Specialist engines
can replace an individual workspace later without changing the application
shell or route contract.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import pandas as pd
import streamlit as st


@dataclass(frozen=True, slots=True)
class Field:
    name: str
    label: str
    kind: str = "text"
    default: Any = ""
    options: tuple[str, ...] = ()
    help: str = ""


@dataclass(frozen=True, slots=True)
class Profile:
    purpose: str
    fields: tuple[Field, ...]


COMMON = (
    Field("name", "Record name", "text", ""),
    Field("description", "Description", "textarea", ""),
)


PROFILES: dict[str, Profile] = {
    "IMAGINE Architect": Profile(
        "Architecture copilot workspace for briefs, constraints and concept-generation inputs.",
        COMMON + (Field("building_type", "Building type", "text", "Commercial"), Field("site_area", "Site area", "number", 2500.0, help="m2"), Field("floors", "Storeys", "number", 12.0), Field("brief", "Design brief", "textarea", "")),
    ),
    "IMAGINE Engineer": Profile(
        "Engineering copilot workspace for structured analysis requests and assumptions.",
        COMMON + (Field("discipline", "Discipline", "select", "Structural", ("Structural", "Civil", "Geotechnical", "MEP")), Field("design_stage", "Design stage", "select", "Concept", ("Concept", "Preliminary", "Detailed", "Review")), Field("question", "Engineering question", "textarea", "")),
    ),
    "IMAGINE MEP": Profile(
        "MEP copilot workspace for system selection, load assumptions and design questions.",
        COMMON + (Field("system", "System", "select", "HVAC", ("HVAC", "Electrical", "Plumbing", "Firefighting", "Energy")), Field("floor_area", "Served floor area", "number", 1000.0, help="m2"), Field("question", "MEP design question", "textarea", "")),
    ),
    "IMAGINE QS": Profile(
        "Quantity-surveying copilot workspace for cost, BOQ and procurement questions.",
        COMMON + (Field("currency", "Currency", "text", "USD"), Field("project_value", "Project value", "number", 1000000.0), Field("question", "QS question", "textarea", "")),
    ),
    "IMAGINE PM": Profile(
        "Project-management copilot workspace for programme, cost, risk and quality questions.",
        COMMON + (Field("stage", "Project stage", "select", "Construction", ("Concept", "Design", "Tender", "Construction", "Closeout")), Field("budget", "Approved budget", "number", 1000000.0), Field("question", "PM question", "textarea", "")),
    ),
    "Energy": Profile(
        "Digital-twin energy workspace for baseline consumption and intensity screening.",
        COMMON + (Field("floor_area", "Floor area", "number", 1000.0, help="m2"), Field("annual_energy", "Annual energy", "number", 250000.0, help="kWh/year"), Field("occupancy", "Average occupancy", "number", 100.0)),
    ),
    "Uganda": Profile("Uganda project context workspace for jurisdiction, approvals and design-basis records.", COMMON + (Field("jurisdiction", "Jurisdiction", "text", "Uganda"), Field("project_type", "Project type", "select", "Building", ("Building", "Infrastructure", "Industrial", "Agricultural")), Field("approval", "Primary approval", "text", "Development permission"))),
    "Kenya": Profile("Kenya project context workspace for jurisdiction, approvals and design-basis records.", COMMON + (Field("jurisdiction", "Jurisdiction", "text", "Kenya"), Field("project_type", "Project type", "select", "Building", ("Building", "Infrastructure", "Industrial", "Agricultural")), Field("approval", "Primary approval", "text", "Development permission"))),
    "Tanzania": Profile("Tanzania project context workspace for jurisdiction, approvals and design-basis records.", COMMON + (Field("jurisdiction", "Jurisdiction", "text", "Tanzania"), Field("project_type", "Project type", "select", "Building", ("Building", "Infrastructure", "Industrial", "Agricultural")), Field("approval", "Primary approval", "text", "Development permission"))),
    "Rwanda": Profile("Rwanda project context workspace for jurisdiction, approvals and design-basis records.", COMMON + (Field("jurisdiction", "Jurisdiction", "text", "Rwanda"), Field("project_type", "Project type", "select", "Building", ("Building", "Infrastructure", "Industrial", "Agricultural")), Field("approval", "Primary approval", "text", "Development permission"))),
    "South Sudan": Profile("South Sudan project context workspace for jurisdiction, approvals and design-basis records.", COMMON + (Field("jurisdiction", "Jurisdiction", "text", "South Sudan"), Field("project_type", "Project type", "select", "Building", ("Building", "Infrastructure", "Industrial", "Agricultural")), Field("approval", "Primary approval", "text", "Development permission"))),
    "Codes": Profile("Engineering code register for recording the applicable code family, edition and National Annex.", COMMON + (Field("code_family", "Code family", "text", "EN 1990"), Field("edition", "Edition", "text", "Current adopted edition"), Field("national_annex", "National Annex", "text", "Project-specific"))),
    "Zoning Laws": Profile("Planning-control register for recording land-use, density, height and setback constraints.", COMMON + (Field("land_use", "Land use", "text", "Mixed use"), Field("plot_ratio", "Maximum plot ratio", "number", 2.0), Field("site_coverage", "Maximum site coverage", "number", 50.0, help="%"), Field("height_limit", "Height limit", "number", 30.0, help="m"))),
    "Microsoft": Profile("Microsoft integration workspace for documenting the intended data exchange and service boundary.", COMMON + (Field("service", "Service", "select", "Microsoft 365", ("Microsoft 365", "SharePoint", "OneDrive", "Azure")), Field("format", "Exchange format", "select", "JSON", ("JSON", "CSV", "XLSX", "IFC")), Field("endpoint", "Endpoint or workspace", "text", ""))),
    "AutoCAD": Profile("AutoCAD integration workspace for drawing-file and exchange metadata.", COMMON + (Field("format", "Drawing format", "select", "DWG", ("DWG", "DXF", "PDF")), Field("drawing_no", "Drawing number", "text", ""), Field("revision", "Revision", "text", "A"))),
    "Revit": Profile("Revit integration workspace for BIM exchange and model coordination metadata.", COMMON + (Field("model", "Model name", "text", ""), Field("discipline", "Discipline", "select", "Architecture", ("Architecture", "Structure", "MEP")), Field("exchange", "Exchange format", "select", "IFC", ("IFC", "RVT", "NWC")))),
    "Archicad": Profile("Archicad integration workspace for BIM model exchange metadata.", COMMON + (Field("model", "Model name", "text", ""), Field("exchange", "Exchange format", "select", "IFC", ("IFC", "PLN", "BCF")), Field("revision", "Revision", "text", "A"))),
    "Tekla": Profile("Tekla integration workspace for structural fabrication-model exchange metadata.", COMMON + (Field("model", "Model name", "text", ""), Field("exchange", "Exchange format", "select", "IFC", ("IFC", "DSTV", "STEP")), Field("revision", "Revision", "text", "A"))),
    "IfcOpenShell": Profile("IfcOpenShell processing workspace for IFC validation and extraction jobs.", COMMON + (Field("file", "IFC file", "text", ""), Field("operation", "Operation", "select", "Validate", ("Validate", "Extract", "Convert", "Inspect")), Field("schema", "IFC schema", "select", "IFC4", ("IFC2X3", "IFC4", "IFC4X3")))),
    "ArcGIS": Profile("ArcGIS integration workspace for GIS layer and coordinate-system metadata.", COMMON + (Field("layer", "Layer name", "text", "Site boundary"), Field("geometry", "Geometry", "select", "Polygon", ("Point", "Line", "Polygon")), Field("crs", "Coordinate reference system", "text", "WGS 84"))),
    "Azure": Profile("Azure integration workspace for documenting cloud service boundaries and deployment metadata.", COMMON + (Field("service", "Azure service", "select", "Storage", ("Storage", "Functions", "Database", "AI", "IoT")), Field("resource", "Resource name", "text", ""), Field("environment", "Environment", "select", "Development", ("Development", "Staging", "Production")))),
    "Mapbox": Profile("Mapbox integration workspace for map layers, tokens and visualization metadata without storing secrets.", COMMON + (Field("map", "Map name", "text", "Site map"), Field("style", "Map style", "text", "Standard"), Field("layer", "Primary layer", "text", "Site boundary"))),
}


def _profile(route: str) -> Profile:
    return PROFILES.get(route, Profile("Enterprise route workspace for structured records, validation and controlled export.", COMMON + (Field("value", "Value", "number", 0.0),)))


def _field(field: Field) -> Any:
    if field.kind == "textarea":
        return st.text_area(field.label, value=str(field.default), help=field.help)
    if field.kind == "select":
        options = list(field.options)
        index = options.index(field.default) if field.default in options else 0
        return st.selectbox(field.label, options, index=index, help=field.help)
    if field.kind == "number":
        return st.number_input(field.label, value=float(field.default), step=1.0, help=field.help)
    return st.text_input(field.label, value=str(field.default), help=field.help)


def _analysis(route: str, values: dict[str, Any]) -> dict[str, Any]:
    if route == "Energy":
        area = max(float(values["floor_area"]), 1e-9)
        return {"energy_intensity_kwh_m2_year": float(values["annual_energy"]) / area}
    if route == "IMAGINE Architect":
        area = max(float(values["site_area"]), 0.0)
        floors = max(float(values["floors"]), 0.0)
        return {"indicative_gross_floor_area_m2": area * floors}
    if route == "IMAGINE QS":
        return {"budget_per_m2": None}
    if route == "Zoning Laws":
        return {"maximum_floor_area_factor_m2_per_m2": max(float(values["plot_ratio"]), 0.0), "site_coverage_percent": max(0.0, min(100.0, float(values["site_coverage"]))), "height_limit_m": max(float(values["height_limit"]), 0.0)}
    return {"status": "validated"}


def _records_key(route: str) -> str:
    return "enterprise_records_" + route


def _save(route: str, payload: dict[str, Any]) -> None:
    payload = dict(payload)
    payload["saved_at"] = datetime.now(timezone.utc).isoformat()
    st.session_state.setdefault(_records_key(route), []).append(payload)
    st.session_state["enterprise_last_record"] = payload


def render() -> None:
    route = str(st.session_state.get("active_route", "Enterprise Workspace"))
    profile = _profile(route)
    st.subheader(f"{route} Workspace")
    st.caption(profile.purpose)

    with st.form(f"enterprise_workspace_{route}", clear_on_submit=False):
        values = {field.name: _field(field) for field in profile.fields}
        submitted = st.form_submit_button("Validate and Save", use_container_width=True)

    if submitted:
        errors: list[str] = []
        if not str(values.get("name", route)).strip():
            errors.append("Record name is required.")
        for name, value in values.items():
            if name not in {"name", "description", "brief", "question"} and isinstance(value, (int, float)) and value < 0:
                errors.append(f"{name} cannot be negative.")
        if errors:
            for error in errors:
                st.error(error)
        else:
            payload = {"route": route, "inputs": values, "analysis": _analysis(route, values)}
            _save(route, payload)
            st.success("Record validated and saved.")

    records = st.session_state.get(_records_key(route), [])
    if records:
        st.write("Saved records")
        st.dataframe(pd.json_normalize(records), use_container_width=True)
        st.download_button("Download CSV", pd.json_normalize(records).to_csv(index=False).encode("utf-8"), file_name=f"{route.lower().replace(' ', '_')}.csv", mime="text/csv", use_container_width=True)
        st.download_button("Download JSON", json.dumps(records, indent=2).encode("utf-8"), file_name=f"{route.lower().replace(' ', '_')}.json", mime="application/json", use_container_width=True)

    last = st.session_state.get("enterprise_last_record")
    if last and last.get("route") == route:
        st.write("Latest analysis")
        st.json(last["analysis"])


render_module = render

__all__ = ["Field", "Profile", "PROFILES", "render", "render_module"]
