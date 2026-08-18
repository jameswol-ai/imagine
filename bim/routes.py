from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db_dependency
from . import schemas, service

router = APIRouter(prefix="/buildings", tags=["buildings"])

@router.post("/", response_model=schemas.BuildingOut)
def create_building(payload: schemas.BuildingCreate, db: Session = Depends(get_db_dependency)):
    return service.create_building(db, payload.project_id, payload.name, payload.address)

@router.get("/project/{project_id}", response_model=list[schemas.BuildingOut])
def list_buildings(project_id: int, db: Session = Depends(get_db_dependency)):
    return service.list_buildings(db, project_id)