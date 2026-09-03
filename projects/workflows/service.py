from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from projects.model_registry import Project

from .models import Workflow


VALID_STATUSES = ("pending", "in_progress", "completed", "blocked", "cancelled")


def _project_uuid(value: str | UUID) -> UUID:
    return value if isinstance(value, UUID) else UUID(str(value))


def create_workflow(db: Session, project_id: str | UUID, step: str, assigned_to: int | None = None):
    project_id = _project_uuid(project_id)
    if db.get(Project, project_id) is None:
        raise ValueError("Project does not exist.")
    workflow = Workflow(project_id=project_id, step=step.strip(), assigned_to=assigned_to)
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    return workflow


def list_workflows(db: Session, project_id: str | UUID):
    return db.query(Workflow).filter(Workflow.project_id == _project_uuid(project_id)).order_by(Workflow.id).all()


def update_workflow(db: Session, workflow_id: int, *, step: str | None = None, status: str | None = None, assigned_to: int | None = None):
    workflow = db.get(Workflow, int(workflow_id))
    if workflow is None:
        return None
    if step is not None:
        workflow.step = step.strip()
    if status is not None:
        if status not in VALID_STATUSES:
            raise ValueError(f"Invalid workflow status: {status}")
        workflow.status = status
    workflow.assigned_to = assigned_to
    db.commit()
    db.refresh(workflow)
    return workflow


def delete_workflow(db: Session, workflow_id: int) -> bool:
    workflow = db.get(Workflow, int(workflow_id))
    if workflow is None:
        return False
    db.delete(workflow)
    db.commit()
    return True
