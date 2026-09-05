from modules.structural.context import ActionCase, CombinationResult, StructuralContext


def test_action_case_rejects_negative_values():
    try:
        ActionCase("Floor load", "Variable", -1.0)
    except ValueError as exc:
        assert "negative" in str(exc)
    else:
        raise AssertionError("Negative action values must be rejected")


def test_structural_context_tracks_actions_and_combinations():
    context = StructuralContext(project_id="P-001", project_name="Test Project")
    context.add_action(ActionCase("Self weight", "Permanent", 100.0))
    context.add_action(ActionCase("Floor load", "Variable", 50.0, leading=True))

    uls = CombinationResult("ULS 1", 210.0, "ULS")
    sls = CombinationResult("SLS 1", 150.0, "SLS")
    context.set_combinations([uls, sls], governing_uls=uls, governing_sls=sls)

    assert context.pipeline["Actions"] == "Configured"
    assert context.pipeline["Combinations"] == "Complete"
    assert context.governing_uls is uls
    assert context.governing_sls is sls
    assert context.to_dict()["project_id"] == "P-001"
    assert len(context.to_dict()["actions"]) == 2


def test_context_pipeline_has_expected_handoffs():
    context = StructuralContext()
    assert list(context.pipeline) == [
        "Design Basis", "Actions", "Combinations", "Analysis",
        "Member Design", "Detailing", "Schedules", "BIM / BOQ",
    ]
