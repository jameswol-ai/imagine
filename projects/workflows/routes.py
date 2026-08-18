from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db_dependency
from . import schemas, service

router = APIRouter(prefix="/workflows", tags=["workflows"])

@router.post("/", response_model=schemas.WorkflowOut)
def create_workflow(payload: schemas.WorkflowCreate, db: Session = Depends(get_db_dependency)):
    return service.create_workflow(db, payload.project_id, payload.step, payload.assigned_to)

@router.get("/project/{project_id}", response_model=list[schemas.WorkflowOut])
def list_project_workflows(project_id: int, db: Session = Depends(get_db_dependency)):
    return service.list_workflows(db, project_id)