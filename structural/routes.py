from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db_dependency
from . import schemas, service

router = APIRouter(prefix="/beam-design", tags=["beam_design"])

@router.post("/", response_model=schemas.BeamDesignOut)
def create_beam(payload: schemas.BeamDesignCreate, db: Session = Depends(get_db_dependency)):
    return service.create_beam(db, payload.project_id, payload.material, payload.span_length, payload.load_capacity)

@router.get("/project/{project_id}", response_model=list[schemas.BeamDesignOut])
def list_beams(project_id: int, db: Session = Depends(get_db_dependency)):
    return service.list_beams(db, project_id)