from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db_dependency
from . import schemas, service

router = APIRouter(prefix="/revisions", tags=["revisions"])

@router.post("/", response_model=schemas.RevisionOut)
def create_revision(payload: schemas.RevisionCreate, db: Session = Depends(get_db_dependency)):
    return service.create_revision(db, payload.project_id, payload.description, payload.created_by)

@router.get("/project/{project_id}", response_model=list[schemas.RevisionOut])
def list_project_revisions(project_id: int, db: Session = Depends(get_db_dependency)):
    return service.list_revisions(db, project_id)