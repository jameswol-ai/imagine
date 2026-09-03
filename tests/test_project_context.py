from modules.platform.project_context import (
    MODULE_ORDER,
    ProjectContext,
    context_from_project,
    context_from_projects,
    project_from_context,
)


def test_project_context_initialises_all_disciplines():
    context = ProjectContext(project_id="p-1", project_name="Test Project")

    assert tuple(context.module_status) == MODULE_ORDER
    assert tuple(context.outputs) == MODULE_ORDER


def test_project_context_tracks_outputs_and_handoffs():
    context = ProjectContext(project_id="p-1", project_name="Test Project")
    output_id = context.add_output(
        "Architecture",
        "floor_plan",
        {"gross_floor_area_m2": 1250.0},
    )
    context.set_status("Architecture", "complete", 100.0)

    assert context.outputs_for("Architecture", "floor_plan")[0]["id"] == output_id
    assert context.module_status["Architecture"].output_count == 1
    assert context.module_status["Architecture"].progress == 100.0

    handoff = context.handoff("Architecture", "Structural Engineering", "floor_plan")
    assert handoff["project_id"] == "p-1"
    assert handoff["target_module"] == "Structural Engineering"
    assert len(handoff["outputs"]) == 1


def test_project_record_round_trip():
    project = {
        "id": "p-2",
        "name": "Warehouse",
        "status": "active",
        "description": "Industrial warehouse",
        "client": "Example Client",
        "location": "Juba",
        "currency": "USD",
        "sector": "Industrial",
    }
    context = context_from_project(project)
    restored = project_from_context(context)

    assert restored["id"] == "p-2"
    assert restored["name"] == "Warehouse"
    assert restored["sector"] == "Industrial"


def test_context_selection_is_project_specific():
    projects = [
        {"id": "p-1", "name": "One"},
        {"id": "p-2", "name": "Two"},
    ]

    context = context_from_projects(projects, "p-2")
    assert context is not None
    assert context.project_name == "Two"
    assert context_from_projects(projects, "missing") is None
