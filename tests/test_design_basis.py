from __future__ import annotations

from dataclasses import asdict

from modules.structural.design_basis import (
    PIPELINE_STAGES,
    DesignBasis,
    DesignRecord,
    export_contract,
    pipeline_frame,
    update_pipeline,
)


def test_design_basis_defaults_are_serializable():
    basis = DesignBasis()
    data = asdict(basis)
    assert data["project_id"]
    assert data["jurisdiction"] == "Recommended (CEN)"
    assert data["units"] == "Metric (kN, m, MPa)"


def test_pipeline_contains_expected_handoffs():
    assert PIPELINE_STAGES == (
        "Design Basis", "Actions", "Combinations", "Analysis",
        "Member Design", "Detailing", "Schedules", "BIM / BOQ",
    )
    frame = pipeline_frame()
    assert list(frame["Stage"]) == list(PIPELINE_STAGES)
    assert set(frame["Status"]) == {"Not started"}


def test_contract_exports_basis_records_and_pipeline():
    contract = export_contract()
    assert set(contract) == {"design_basis", "records", "pipeline"}
    assert contract["records"] == []
    assert list(contract["pipeline"]) == list(PIPELINE_STAGES)


def test_design_record_shape():
    record = DesignRecord("a-1", "Actions", "Wind", 1.2, "kN", "Project input")
    data = asdict(record)
    assert data["category"] == "Actions"
    assert data["value"] == 1.2


def test_invalid_pipeline_stage_is_rejected():
    try:
        update_pipeline("Not a stage", "Configured")
    except KeyError:
        pass
    else:
        raise AssertionError("Expected invalid pipeline stage to raise KeyError")
