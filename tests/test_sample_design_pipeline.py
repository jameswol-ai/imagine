from __future__ import annotations


def test_sample_design_pipeline_imports_and_exposes_renderer() -> None:
    from modules.structural.sample_design_pipeline import render

    assert callable(render)


def test_sample_design_pipeline_uses_sample_project() -> None:
    from modules.structural.sample_design_pipeline import PROJECT

    assert PROJECT["name"] == "IMAGINE Innovation Hub"
    assert PROJECT["grid_m"] == 8.0
    assert PROJECT["storeys"] == 12
