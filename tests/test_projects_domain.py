from uuid import UUID

from projects.projects.models import ProjectStatus
from projects.projects.schemas import ProjectCreate, ProjectUpdate
from projects.workflows.models import Workflow
from projects.workflows.schemas import WorkflowCreate
from projects.workflows.service import VALID_STATUSES


def test_project_status_and_schema_contract():
    payload = ProjectCreate(name="Demo Project", status=ProjectStatus.active, budget=1000, progress=25)
    assert payload.name == "Demo Project"
    assert payload.status.value == "active"
    update = ProjectUpdate(progress=50)
    assert update.progress == 50


def test_workflow_uses_project_uuid_contract():
    project_id = UUID("12345678-1234-5678-1234-567812345678")
    payload = WorkflowCreate(project_id=project_id, step="Design review", assigned_to=1)
    assert payload.project_id == project_id
    assert payload.step == "Design review"
    assert "in_progress" in VALID_STATUSES
    assert str(Workflow.project_id.type).upper().startswith("UUID")


def test_project_workflow_relationship_is_registered():
    from projects.model_registry import Project, Workflow as RegisteredWorkflow

    assert RegisteredWorkflow.__name__ == "Workflow"
    assert hasattr(Project, "workflows")
