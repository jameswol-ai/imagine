from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.roles import schemas, service
from app.dependencies import get_db_dependency

router = APIRouter(prefix="/roles", tags=["roles"])

@router.post("/", response_model=schemas.RoleOut)
def create_role(payload: schemas.RoleCreate, db: Session = Depends(get_db_dependency)):
    return service.create_role(db, payload.name, payload.description)

@router.get("/", response_model=list[schemas.RoleOut])
def get_roles(db: Session = Depends(get_db_dependency)):
    return service.list_roles(db)
