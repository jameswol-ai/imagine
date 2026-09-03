from architecture.assistant.engine import ArchitectureAssistant, ArchitectureBrief


def test_architecture_assessment_is_deterministic() -> None:
    assistant = ArchitectureAssistant()
    brief = ArchitectureBrief(
        site_area_m2=5000,
        site_width_m=50,
        site_depth_m=100,
        target_occupants=250,
    )
    first = assistant.assess(brief)
    second = assistant.assess(brief)
    assert first == second
    assert first.buildable_footprint_m2 > 0
    assert first.program_gross_area_m2 > first.program_net_area_m2


def test_architecture_assistant_answers_site_question() -> None:
    assistant = ArchitectureAssistant()
    assessment = assistant.assess(ArchitectureBrief())
    response = assistant.respond("How much site can I build on?", assessment)
    assert "Screening site envelope" in response


def test_architecture_assistant_flags_high_occupancy() -> None:
    assistant = ArchitectureAssistant()
    assessment = assistant.assess(ArchitectureBrief(target_occupants=750))
    assert any(item.category == "Life Safety" for item in assessment.recommendations)
