from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db_dependency
from . import schemas, service

router = APIRouter(prefix="/generative-design", tags=["generative_design"])

@router.post("/", response_model=schemas.GenerativeDesignOut)
def create_design(payload: schemas.GenerativeDesignCreate, db: Session = Depends(get_db_dependency)):
    return service.create_design(db, payload.project_id, payload.algorithm, payload.parameters)

@router.get("/project/{project_id}", response_model=list[schemas.GenerativeDesignOut])
def list_designs(project_id: int, db: Session = Depends(get_db_dependency)):
    return service.list_designs(db, project_id)