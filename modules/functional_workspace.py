"""Functional fallback workspaces for enterprise IMAGINE modules.

This layer gives every registered route a domain-aware data model, validation,
lightweight engineering/business calculations, persistence and export without
forcing every specialist solver to load at application startup.

Specialist modules should continue to replace these workspaces as their domain
engines mature. The workspace is intentionally deterministic and dependency-light.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import pandas as pd
import streamlit as st


@dataclass(frozen=True, slots=True)
class FieldSpec:
    name: str
    label: str
    kind: str = "number"
    default: Any = 0.0
    options: tuple[str, ...] = ()
    help: str = ""


@dataclass(frozen=True, slots=True)
class ModuleProfile:
    route: str
    purpose: str
    fields: tuple[FieldSpec, ...]
    result_label: str = "Calculated result"


COMMON = (
    FieldSpec("name", "Record name", "text", ""),
    FieldSpec("description", "Description", "textarea", ""),
)


PROFILES: dict[str, ModuleProfile] = {
    "EN 1990": ModuleProfile(
        "EN 1990",
        "Basis of structural design and persistent load-combination records.",
        COMMON + (
            FieldSpec("gk", "Permanent action Gk", "number", 100.0, help="kN"),
            FieldSpec("qk", "Variable action Qk", "number", 50.0, help="kN"),
            FieldSpec("gamma_g", "Partial factor gammaG", "number", 1.35),
            FieldSpec("gamma_q", "Partial factor gammaQ", "number", 1.50),
        ),
        "ULS design action",
    ),
    "EN 1991": ModuleProfile(
        "EN 1991",
        "Actions on structures and representative load records.",
        COMMON + (
            FieldSpec("area", "Loaded area", "number", 100.0, help="m2"),
            FieldSpec("imposed", "Imposed load", "number", 2.5, help="kN/m2"),
            FieldSpec("snow", "Snow load", "number", 0.75, help="kN/m2"),
            FieldSpec("wind", "Wind pressure", "number", 0.8, help="kN/m2"),
        ),
        "Total characteristic action",
    ),
    "EN 1992": ModuleProfile(
        "EN 1992",
        "Reinforced concrete design input register.",
        COMMON + (
            FieldSpec("b", "Section width", "number", 300.0, help="mm"),
            FieldSpec("h", "Section depth", "number", 500.0, help="mm"),
            FieldSpec("fck", "Concrete strength fck", "number", 30.0, help="MPa"),
            FieldSpec("fyk", "Rebar yield strength fyk", "number", 500.0, help="MPa"),
            FieldSpec("med", "Design bending moment", "number", 80.0, help="kNm"),
        ),
        "Section bending demand index",
    ),
    "EN 1993": ModuleProfile(
        "EN 1993",
        "Structural steel member design input register.",
        COMMON + (
            FieldSpec("area", "Steel area", "number", 3000.0, help="mm2"),
            FieldSpec("fy", "Yield strength fy", "number", 355.0, help="MPa"),
            FieldSpec("ned", "Axial design force NEd", "number", 500.0, help="kN"),
            FieldSpec("med", "Bending design moment MEd", "number", 40.0, help="kNm"),
            FieldSpec("wel", "Elastic section modulus Wel", "number", 150000.0, help="mm3"),
        ),
        "Steel utilisation estimate",
    ),
    "EN 1994": ModuleProfile(
        "EN 1994",
        "Composite steel and concrete design input register.",
        COMMON + (
            FieldSpec("steel_area", "Steel area", "number", 3000.0, help="mm2"),
            FieldSpec("fy", "Steel yield strength", "number", 355.0, help="MPa"),
            FieldSpec("concrete_area", "Concrete effective area", "number", 100000.0, help="mm2"),
            FieldSpec("fck", "Concrete strength", "number", 30.0, help="MPa"),
        ),
        "Composite resistance estimate",
    ),
    "EN 1995": ModuleProfile(
        "EN 1995",
        "Timber member design input register.",
        COMMON + (
            FieldSpec("width", "Timber width", "number", 100.0, help="mm"),
            FieldSpec("depth", "Timber depth", "number", 300.0, help="mm"),
            FieldSpec("fm", "Bending strength fm", "number", 24.0, help="MPa"),
            FieldSpec("med", "Design moment", "number", 8.0, help="kNm"),
        ),
        "Timber bending utilisation estimate",
    ),
    "EN 1996": ModuleProfile(
        "EN 1996",
        "Masonry wall design input register.",
        COMMON + (
            FieldSpec("thickness", "Wall thickness", "number", 200.0, help="mm"),
            FieldSpec("height", "Wall height", "number", 3.0, help="m"),
            FieldSpec("length", "Wall length", "number", 5.0, help="m"),
            FieldSpec("fk", "Masonry characteristic strength", "number", 5.0, help="MPa"),
            FieldSpec("ned", "Design axial load", "number", 150.0, help="kN"),
        ),
        "Masonry axial utilisation estimate",
    ),
    "EN 1997": ModuleProfile(
        "EN 1997",
        "Geotechnical design input register.",
        COMMON + (
            FieldSpec("width", "Foundation width", "number", 2.0, help="m"),
            FieldSpec("length", "Foundation length", "number", 2.0, help="m"),
            FieldSpec("bearing", "Allowable bearing pressure", "number", 200.0, help="kPa"),
            FieldSpec("load", "Design vertical load", "number", 500.0, help="kN"),
        ),
        "Bearing pressure utilisation",
    ),
    "EN 1998": ModuleProfile(
        "EN 1998",
        "Seismic design input register.",
        COMMON + (
            FieldSpec("ag", "Reference ground acceleration", "number", 0.20, help="g"),
            FieldSpec("soil", "Soil factor S", "number", 1.15),
            FieldSpec("mass", "Seismic mass", "number", 1000.0, help="tonnes"),
            FieldSpec("importance", "Importance factor gammaI", "number", 1.0),
        ),
        "Base shear proxy",
    ),
    "Finite Element Analysis": ModuleProfile(
        "Finite Element Analysis",
        "Small linear-analysis case register for preliminary engineering studies.",
        COMMON + (
            FieldSpec("nodes", "Node count", "number", 10.0),
            FieldSpec("elements", "Element count", "number", 12.0),
            FieldSpec("load", "Applied load", "number", 100.0, help="kN"),
            FieldSpec("stiffness", "Representative stiffness", "number", 10000.0, help="kN/m"),
        ),
        "Linear displacement proxy",
    ),
    "Elements": ModuleProfile(
        "Elements",
        "BIM element register for model coordination.",
        COMMON + (
            FieldSpec("category", "Category", "select", "Wall", ("Wall", "Floor", "Roof", "Door", "Window", "Column", "Beam", "Equipment")),
            FieldSpec("level", "Storey", "text", "Level 1"),
            FieldSpec("count", "Quantity", "number", 1.0),
        ),
        "Element quantity",
    ),
    "COBie": ModuleProfile(
        "COBie",
        "Facilities handover and asset information register.",
        COMMON + (
            FieldSpec("asset_type", "Asset type", "text", "Mechanical Equipment"),
            FieldSpec("manufacturer", "Manufacturer", "text", ""),
            FieldSpec("serial", "Serial number", "text", ""),
            FieldSpec("warranty_months", "Warranty period", "number", 12.0, help="months"),
        ),
        "Warranty period",
    ),
    "BIM Digital Twin": ModuleProfile(
        "BIM Digital Twin",
        "Digital twin object register linking BIM identity to operational data.",
        COMMON + (
            FieldSpec("asset_id", "Asset identifier", "text", ""),
            FieldSpec("status", "Operational status", "select", "Active", ("Active", "Inactive", "Maintenance", "Decommissioned")),
            FieldSpec("health", "Health score", "number", 100.0),
        ),
        "Twin health score",
    ),
    "Transformers": ModuleProfile(
        "Transformers",
        "Electrical transformer sizing register.",
        COMMON + (
            FieldSpec("load", "Connected load", "number", 500.0, help="kVA"),
            FieldSpec("utilisation", "Target utilisation", "number", 0.80),
            FieldSpec("pf", "Power factor", "number", 0.90),
        ),
        "Recommended transformer rating",
    ),
    "Generators": ModuleProfile(
        "Generators",
        "Generator sizing register.",
        COMMON + (
            FieldSpec("load", "Essential load", "number", 300.0, help="kW"),
            FieldSpec("pf", "Power factor", "number", 0.80),
            FieldSpec("margin", "Design margin", "number", 0.20),
        ),
        "Recommended generator rating",
    ),
    "Cable Sizing": ModuleProfile(
        "Cable Sizing",
        "Preliminary cable sizing register using current and allowable current density.",
        COMMON + (
            FieldSpec("power", "Three-phase load", "number", 100.0, help="kW"),
            FieldSpec("voltage", "Line voltage", "number", 400.0, help="V"),
            FieldSpec("pf", "Power factor", "number", 0.90),
            FieldSpec("density", "Allowable current density", "number", 3.0, help="A/mm2"),
        ),
        "Minimum conductor area",
    ),
    "Solar PV": ModuleProfile(
        "Solar PV",
        "Preliminary PV capacity register.",
        COMMON + (
            FieldSpec("daily_energy", "Daily energy demand", "number", 1000.0, help="kWh/day"),
            FieldSpec("sun_hours", "Peak sun hours", "number", 5.0, help="h/day"),
            FieldSpec("system_eff", "System efficiency", "number", 0.80),
        ),
        "Required PV capacity",
    ),
    "Stormwater": ModuleProfile(
        "Stormwater",
        "Rational-method preliminary drainage case register.",
        COMMON + (
            FieldSpec("area", "Catchment area", "number", 1.0, help="ha"),
            FieldSpec("runoff", "Runoff coefficient", "number", 0.70),
            FieldSpec("rainfall", "Rainfall intensity", "number", 100.0, help="mm/h"),
        ),
        "Peak runoff",
    ),
    "Sewer Networks": ModuleProfile(
        "Sewer Networks",
        "Preliminary sewer flow register.",
        COMMON + (
            FieldSpec("population", "Design population", "number", 1000.0),
            FieldSpec("demand", "Water demand", "number", 120.0, help="L/person/day"),
            FieldSpec("return", "Return factor", "number", 0.80),
        ),
        "Average wastewater flow",
    ),
    "Firefighting": ModuleProfile(
        "Firefighting",
        "Fire-water demand register.",
        COMMON + (
            FieldSpec("flow", "Design flow", "number", 20.0, help="L/s"),
            FieldSpec("duration", "Required duration", "number", 60.0, help="min"),
        ),
        "Fire-water storage volume",
    ),
    "Cashflow": ModuleProfile(
        "Cashflow",
        "Project cashflow forecast register.",
        COMMON + (
            FieldSpec("contract", "Contract value", "number", 1000000.0),
            FieldSpec("spent", "Spent to date", "number", 250000.0),
            FieldSpec("forecast", "Forecast remaining spend", "number", 700000.0),
        ),
        "Forecast variance",
    ),
    "Planning": ModuleProfile(
        "Planning",
        "Construction planning activity register.",
        COMMON + (
            FieldSpec("planned_days", "Planned duration", "number", 30.0, help="days"),
            FieldSpec("progress", "Progress", "number", 0.0, help="%"),
            FieldSpec("actual_days", "Actual elapsed duration", "number", 0.0, help="days"),
        ),
        "Schedule performance",
    ),
    "Scheduling": ModuleProfile(
        "Scheduling",
        "Construction scheduling activity register.",
        COMMON + (
            FieldSpec("duration", "Activity duration", "number", 10.0, help="days"),
            FieldSpec("predecessors", "Predecessor count", "number", 0.0),
            FieldSpec("float", "Available float", "number", 2.0, help="days"),
        ),
        "Schedule float",
    ),
    "Variations": ModuleProfile(
        "Variations",
        "Contract variation register.",
        COMMON + (
            FieldSpec("original", "Original contract value", "number", 1000000.0),
            FieldSpec("variation", "Variation amount", "number", 0.0),
            FieldSpec("approved", "Approval status", "select", "Pending", ("Pending", "Approved", "Rejected")),
        ),
        "Revised contract value",
    ),
    "Reports": ModuleProfile(
        "Reports",
        "Report definition register for controlled project reporting.",
        COMMON + (
            FieldSpec("report_type", "Report type", "select", "Progress", ("Progress", "Cost", "Design", "Quality", "Risk", "Executive")),
            FieldSpec("period", "Reporting period", "text", "Current period"),
        ),
        "Report status",
    ),
    "Archives": ModuleProfile(
        "Archives",
        "Controlled archive register for superseded project records.",
        COMMON + (
            FieldSpec("document_id", "Document identifier", "text", ""),
            FieldSpec("revision", "Revision", "text", "A"),
            FieldSpec("reason", "Archive reason", "text", "Superseded"),
        ),
        "Archive status",
    ),
    "Vector Store": ModuleProfile(
        "Vector Store",
        "Knowledge-index record register for future retrieval pipelines.",
        COMMON + (
            FieldSpec("source", "Source document", "text", ""),
            FieldSpec("chunk_count", "Chunk count", "number", 1.0),
        ),
        "Indexed chunks",
    ),
    "RAG": ModuleProfile(
        "RAG",
        "Retrieval configuration register for engineering knowledge workflows.",
        COMMON + (
            FieldSpec("query", "Query", "text", ""),
            FieldSpec("top_k", "Top K results", "number", 5.0),
        ),
        "Retrieval configuration",
    ),
    "Prompt Library": ModuleProfile(
        "Prompt Library",
        "Versioned prompt template register for engineering AI workflows.",
        COMMON + (
            FieldSpec("prompt", "Prompt template", "textarea", ""),
            FieldSpec("version", "Version", "text", "1.0"),
        ),
        "Prompt status",
    ),
}


def _profile(route: str) -> ModuleProfile:
    if route in PROFILES:
        return PROFILES[route]
    return ModuleProfile(
        route,
        "Enterprise workspace for controlled records and module-specific metadata.",
        COMMON + (FieldSpec("value", "Value", "number", 0.0),),
    )


def _render_field(field: FieldSpec) -> Any:
    if field.kind == "text":
        return st.text_input(field.label, value=str(field.default), help=field.help)
    if field.kind == "textarea":
        return st.text_area(field.label, value=str(field.default), help=field.help)
    if field.kind == "select":
        return st.selectbox(field.label, options=list(field.options), index=list(field.options).index(field.default), help=field.help)
    return st.number_input(field.label, value=float(field.default), step=1.0, help=field.help)


def _calculate(route: str, values: dict[str, Any]) -> tuple[float | None, str]:
    try:
        if route == "EN 1990":
            return 1.35 * values["gk"] + 1.50 * values["qk"], "kN"
        if route == "EN 1991":
            return values["area"] * (values["imposed"] + values["snow"] + values["wind"]), "kN"
        if route == "EN 1992":
            capacity = values["b"] * values["h"] * max(values["fck"], 1.0) / 1e6
            return values["med"] / max(capacity, 1e-9), "utilisation proxy"
        if route == "EN 1993":
            axial = values["ned"] * 1000.0 / max(values["area"] * values["fy"], 1e-9)
            bending = values["med"] * 1e6 / max(values["wel"] * values["fy"], 1e-9)
            return axial + bending, "utilisation proxy"
        if route == "EN 1994":
            return (values["steel_area"] * values["fy"] + values["concrete_area"] * values["fck"]) / 1000.0, "kN resistance proxy"
        if route == "EN 1995":
            w = values["width"] * values["depth"] ** 2 / 6.0
            return values["med"] * 1e6 / max(w * values["fm"], 1e-9), "utilisation proxy"
        if route == "EN 1996":
            area = values["thickness"] * values["length"] * 1000.0
            return values["ned"] * 1000.0 / max(area * values["fk"], 1e-9), "utilisation proxy"
        if route == "EN 1997":
            pressure = values["load"] / max(values["width"] * values["length"], 1e-9)
            return pressure / max(values["bearing"], 1e-9), "bearing utilisation"
        if route == "EN 1998":
            return values["ag"] * values["soil"] * values["importance"] * values["mass"] * 9.81, "kN base-shear proxy"
        if route == "Finite Element Analysis":
            return values["load"] / max(values["stiffness"], 1e-9), "m displacement proxy"
        if route == "Transformers":
            return values["load"] / max(values["utilisation"], 1e-9), "kVA"
        if route == "Generators":
            return values["load"] * (1.0 + values["margin"]) / max(values["pf"], 1e-9), "kVA"
        if route == "Cable Sizing":
            current = values["power"] * 1000.0 / (3 ** 0.5 * values["voltage"] * max(values["pf"], 1e-9))
            return current / max(values["density"], 1e-9), "mm2"
        if route == "Solar PV":
            return values["daily_energy"] / max(values["sun_hours"] * values["system_eff"], 1e-9), "kWp"
        if route == "Stormwater":
            return 0.00278 * values["runoff"] * values["rainfall"] * values["area"] * 10.0, "m3/s"
        if route == "Sewer Networks":
            return values["population"] * values["demand"] * values["return"] / 86400.0, "L/s"
        if route == "Firefighting":
            return values["flow"] * values["duration"] * 60.0 / 1000.0, "m3"
        if route == "Cashflow":
            return values["contract"] - values["spent"] - values["forecast"], "currency variance"
        if route == "Planning":
            expected = min(max(values["planned_days"] * values["progress"] / 100.0, 0.0), values["planned_days"])
            return values["actual_days"] - expected, "days variance"
        if route == "Scheduling":
            return values["float"], "days float"
        if route == "Variations":
            return values["original"] + values["variation"], "revised contract value"
        if route == "Elements":
            return values["count"], "elements"
        if route == "COBie":
            return values["warranty_months"], "months"
        if route == "BIM Digital Twin":
            return max(0.0, min(100.0, values["health"])), "% health"
        if route == "Vector Store":
            return values["chunk_count"], "chunks"
        if route == "RAG":
            return values["top_k"], "retrieval count"
        return None, ""
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return None, ""


def _save(route: str, values: dict[str, Any], result: float | None, unit: str) -> None:
    now = datetime.now(timezone.utc)
    payload = dict(values)
    payload["result"] = result
    payload["unit"] = unit
    try:
        from database.bootstrap import ensure_schema
        from database.connection import SessionLocal
        from database.models.module_workspace import ModuleWorkspaceRecord

        ensure_schema()
        name = str(values.get("name") or route)
        description = str(values.get("description") or "")
        with SessionLocal() as db:
            db.add(ModuleWorkspaceRecord(
                module_route=route,
                name=name,
                description=description,
                value=float(result or 0.0),
                metadata_json=payload,
                created_at=now,
                updated_at=now,
            ))
            db.commit()
        st.session_state[f"functional_last_{route}"] = {"payload": payload, "persistent": True}
    except Exception:
        key = f"functional_records_{route}"
        st.session_state.setdefault(key, [])
        st.session_state[key].append({"payload": payload, "saved_at": now.isoformat()})
        st.session_state[f"functional_last_{route}"] = {"payload": payload, "persistent": False}


def render_module() -> None:
    """Render the domain-aware workspace for the active route."""
    route = str(st.session_state.get("active_route", "Enterprise Module"))
    profile = _profile(route)

    st.subheader(f"{route} Workspace")
    st.caption(profile.purpose)

    with st.form(f"functional_form_{route}", clear_on_submit=False):
        values: dict[str, Any] = {}
        for field in profile.fields:
            values[field.name] = _render_field(field)
        submitted = st.form_submit_button("Validate and Save", use_container_width=True)

    result, unit = _calculate(route, values)
    if result is not None:
        st.metric(profile.result_label, f"{result:,.4g} {unit}")

    last = st.session_state.get(f"functional_last_{route}")
    if submitted:
        errors: list[str] = []
        if "name" in values and not str(values["name"]).strip():
            errors.append("Record name is required.")
        numeric = [v for k, v in values.items() if k not in {"name", "description", "prompt"} and isinstance(v, (int, float))]
        if any(v < 0 for v in numeric):
            errors.append("Numeric inputs cannot be negative.")
        if errors:
            for error in errors:
                st.error(error)
        else:
            _save(route, values, result, unit)
            st.success("Record validated and saved.")
            last = st.session_state.get(f"functional_last_{route}")

    if last:
        st.write("Latest record")
        st.json(last["payload"])

    records = st.session_state.get(f"functional_records_{route}", [])
    if records:
        frame = pd.DataFrame(records)
        st.download_button(
            "Download session records",
            frame.to_csv(index=False).encode("utf-8"),
            file_name=f"{route.lower().replace(' ', '_')}_records.csv",
            mime="text/csv",
            use_container_width=True,
        )


__all__ = ["FieldSpec", "ModuleProfile", "PROFILES", "render_module"]
