"""Shared structural design-basis and handoff contract for IMAGINE.

The contract is deliberately metadata/data oriented. It stores project decisions,
actions and design outputs without reproducing normative Eurocode text. Values
must be verified against the adopted edition and project-specific National Annex.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

import pandas as pd
import streamlit as st

from structural.eurocode.config import NATIONAL_ANNEX_DEFAULTS


PIPELINE_STAGES = (
    "Design Basis",
    "Actions",
    "Combinations",
    "Analysis",
    "Member Design",
    "Detailing",
    "Schedules",
    "BIM / BOQ",
)


@dataclass
class DesignBasis:
    project_id: str = "IMAGINE-DEMO"
    project_name: str = "Untitled Project"
    jurisdiction: str = "Recommended (CEN)"
    eurocode_edition: str = "Current adopted edition"
    units: str = "Metric (kN, m, MPa)"
    design_situation: str = "Persistent / transient"
    consequence_class: str = "CC2"
    reliability_class: str = "RC2"
    exposure_class: str = "Project controlled"
    fire_design_required: bool = False
    seismic_design_required: bool = False
    notes: str = ""
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class DesignRecord:
    record_id: str
    category: str
    name: str
    value: float | str | bool | None
    unit: str = ""
    source: str = "Project input"
    status: str = "Draft"
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def _state() -> dict[str, Any]:
    if "imagine_design_basis" not in st.session_state:
        st.session_state.imagine_design_basis = DesignBasis()
    if "imagine_design_records" not in st.session_state:
        st.session_state.imagine_design_records = []
    if "imagine_pipeline_status" not in st.session_state:
        st.session_state.imagine_pipeline_status = {stage: "Not started" for stage in PIPELINE_STAGES}
    return {
        "basis": st.session_state.imagine_design_basis,
        "records": st.session_state.imagine_design_records,
        "pipeline": st.session_state.imagine_pipeline_status,
    }


def get_design_basis() -> DesignBasis:
    return _state()["basis"]


def set_design_basis(**changes: Any) -> DesignBasis:
    basis = get_design_basis()
    for key, value in changes.items():
        if hasattr(basis, key):
            setattr(basis, key, value)
    basis.updated_at = datetime.now(timezone.utc).isoformat()
    st.session_state.imagine_design_basis = basis
    return basis


def add_design_record(category: str, name: str, value: Any, unit: str = "", source: str = "Project input", status: str = "Draft") -> DesignRecord:
    record = DesignRecord(
        record_id=f"{category.lower().replace(' ', '-')}-{len(st.session_state.imagine_design_records) + 1:04d}",
        category=category,
        name=name,
        value=value,
        unit=unit,
        source=source,
        status=status,
    )
    st.session_state.imagine_design_records.append(record)
    return record


def records_for(category: str | None = None) -> list[DesignRecord]:
    records = list(_state()["records"])
    return [r for r in records if category is None or r.category == category]


def update_pipeline(stage: str, status: str) -> None:
    if stage not in PIPELINE_STAGES:
        raise KeyError(stage)
    _state()["pipeline"][stage] = status


def pipeline_frame() -> pd.DataFrame:
    return pd.DataFrame([
        {"Stage": stage, "Status": _state()["pipeline"].get(stage, "Not started"), "Records": len(records_for(stage))}
        for stage in PIPELINE_STAGES
    ])


def export_contract() -> dict[str, Any]:
    state = _state()
    return {
        "design_basis": asdict(state["basis"]),
        "records": [asdict(record) for record in state["records"]],
        "pipeline": dict(state["pipeline"]),
    }


def _basis_ui() -> None:
    basis = get_design_basis()
    st.subheader("Project design basis")
    st.caption("Project-controlled design basis. Confirm the adopted edition and National Annex before engineering use.")
    c1, c2 = st.columns(2)
    with c1:
        project_id = st.text_input("Project ID", basis.project_id)
        project_name = st.text_input("Project name", basis.project_name)
        jurisdiction = st.selectbox("National Annex / jurisdiction", list(NATIONAL_ANNEX_DEFAULTS), index=max(0, list(NATIONAL_ANNEX_DEFAULTS).index(basis.jurisdiction) if basis.jurisdiction in NATIONAL_ANNEX_DEFAULTS else 0))
        edition = st.text_input("Eurocode edition / source", basis.eurocode_edition)
        units = st.selectbox("Unit system", ["Metric (kN, m, MPa)", "Imperial (kips, ft, ksi)"], index=0 if "Metric" in basis.units else 1)
    with c2:
        situation = st.selectbox("Design situation", ["Persistent / transient", "Accidental", "Seismic", "Fire", "Execution"], index=0 if basis.design_situation not in {"Accidental", "Seismic", "Fire", "Execution"} else ["Persistent / transient", "Accidental", "Seismic", "Fire", "Execution"].index(basis.design_situation))
        consequence = st.selectbox("Consequence class", ["CC1", "CC2", "CC3"], index=["CC1", "CC2", "CC3"].index(basis.consequence_class) if basis.consequence_class in {"CC1", "CC2", "CC3"} else 1)
        reliability = st.selectbox("Reliability class", ["RC1", "RC2", "RC3"], index=["RC1", "RC2", "RC3"].index(basis.reliability_class) if basis.reliability_class in {"RC1", "RC2", "RC3"} else 1)
        exposure = st.text_input("Exposure / durability class", basis.exposure_class)
        fire = st.checkbox("Fire design required", basis.fire_design_required)
        seismic = st.checkbox("Seismic design required", basis.seismic_design_required)
    notes = st.text_area("Design-basis notes", basis.notes)
    if st.button("Save design basis", type="primary", key="save_design_basis"):
        set_design_basis(project_id=project_id, project_name=project_name, jurisdiction=jurisdiction, eurocode_edition=edition, units=units, design_situation=situation, consequence_class=consequence, reliability_class=reliability, exposure_class=exposure, fire_design_required=fire, seismic_design_required=seismic, notes=notes)
        update_pipeline("Design Basis", "Configured")
        st.success("Design basis saved to the shared project context.")

    factors = NATIONAL_ANNEX_DEFAULTS[jurisdiction]
    st.markdown("#### Active factor set")
    st.dataframe(pd.DataFrame([{"Parameter": k, "Value": v} for k, v in factors.items()]), use_container_width=True, hide_index=True)
    st.warning("The factor table is a configurable application reference, not a replacement for the project-specific National Annex. Verify every applicable parameter.")


def _actions_ui() -> None:
    st.subheader("Actions and handoffs")
    st.caption("Capture project actions here, then use the dedicated action and combination workspaces for verified calculations.")
    with st.form("shared_action_form"):
        category = st.selectbox("Action category", ["Permanent", "Variable", "Wind", "Snow", "Seismic", "Thermal", "Accidental", "Execution"])
        name = st.text_input("Action name", placeholder="Floor imposed load")
        value = st.number_input("Representative value", value=0.0)
        unit = st.text_input("Unit", "kN")
        source = st.text_input("Source / basis", "Project input")
        submitted = st.form_submit_button("Add action")
    if submitted and name.strip():
        add_design_record("Actions", name.strip(), value, unit, source, "Draft")
        update_pipeline("Actions", "Configured")
        st.success(f"Action '{name.strip()}' added to the shared context.")
    actions = records_for("Actions")
    if actions:
        st.dataframe(pd.DataFrame([asdict(r) for r in actions]), use_container_width=True, hide_index=True)
    else:
        st.info("No project actions have been captured yet.")


def _pipeline_ui() -> None:
    st.subheader("Design pipeline")
    frame = pipeline_frame()
    st.dataframe(frame, use_container_width=True, hide_index=True)
    done = sum(frame["Status"].isin(["Configured", "Complete", "Verified"]))
    st.progress(done / len(PIPELINE_STAGES), text=f"Pipeline readiness: {done}/{len(PIPELINE_STAGES)} stages configured")
    st.markdown("**Handoff contract:** project basis → actions → combinations → analysis effects → member resistances → detailing → schedules → BIM/BOQ.")
    st.download_button("Export shared design contract", pd.Series(export_contract()).to_json(), "imagine_design_contract.json", "application/json")


def render() -> None:
    _state()
    st.title("Structural Design Basis & Data Flow")
    st.caption("Shared project context connecting Eurocode basis, actions, calculations and downstream deliverables.")
    tabs = st.tabs(["Design Basis", "Actions", "Pipeline", "Records"])
    with tabs[0]:
        _basis_ui()
    with tabs[1]:
        _actions_ui()
    with tabs[2]:
        _pipeline_ui()
    with tabs[3]:
        records = _state()["records"]
        if records:
            st.dataframe(pd.DataFrame([asdict(r) for r in records]), use_container_width=True, hide_index=True)
        else:
            st.info("Shared design records will appear here as modules contribute project data.")
    st.warning("Preliminary engineering data-flow layer. Calculations must be performed and independently verified using the adopted Eurocodes, National Annex, project specifications and professional engineering judgement.")


__all__ = [
    "DesignBasis", "DesignRecord", "PIPELINE_STAGES", "add_design_record", "export_contract",
    "get_design_basis", "pipeline_frame", "records_for", "render", "set_design_basis", "update_pipeline",
]
