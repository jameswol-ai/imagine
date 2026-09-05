from __future__ import annotations


def test_sample_project_contract() -> None:
    from projects.sample_project import EUROCODES, PROJECT, SAMPLE_CHECKS

    assert PROJECT["name"] == "IMAGINE Innovation Hub"
    assert PROJECT["storeys"] == 12
    assert len(EUROCODES) == 10
    assert len(SAMPLE_CHECKS) == 10
    assert {row[0] for row in EUROCODES} == {f"EN 199{i}" for i in range(10)}


def test_eurocode_worked_samples_cover_all_families() -> None:
    from modules.structural.eurocode_samples import SAMPLES

    assert len(SAMPLES) == 10
    assert {sample.code for sample in SAMPLES} == {f"EN 199{i}" for i in range(10)}
    for sample in SAMPLES:
        assert sample.title
        assert sample.inputs
        assert sample.outputs
        assert sample.note


def test_eurocode_sample_calculations_are_deterministic() -> None:
    from modules.structural.eurocode_samples import build_samples

    first = build_samples()
    second = build_samples()
    assert first == second
    assert dict(first[0].outputs)["Illustrative Ed"] == "9.90 kN/m2"
    assert dict(first[7].outputs)["A"] == "3.50 m2"
