from sqlalchemy.orm import Session
from .models import Workflow

def create_workflow(db: Session, project_id: int, step: str, assigned_to: int = None):
    wf = Workflow(project_id=project_id, step=step, assigned_to=assigned_to)
    db.add(wf)
    db.commit()
    db.refresh(wf)
    return wf

def list_workflows(db: Session, project_id: int):
    return db.query(Workflow).filter(Workflow.project_id == project_id).all()