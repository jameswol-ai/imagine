from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db_dependency
from . import schemas, service

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/", response_model=schemas.ProjectOut)
def create_project(payload: schemas.ProjectCreate, db: Session = Depends(get_db_dependency), user_id: int = 1):
    # TODO: replace user_id with authenticated user
    project = service.create_project(db, payload.name, payload.description, owner_id=user_id)
    return project

@router.get("/{project_id}", response_model=schemas.ProjectOut)
def read_project(project_id: int, db: Session = Depends(get_db_dependency)):
    project = service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project

@router.get("/", response_model=list[schemas.ProjectOut])
def list_projects(db: Session = Depends(get_db_dependency)):
    return service.list_projects(db)