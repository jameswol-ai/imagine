from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.permissions import schemas, service
from app.dependencies import get_db_dependency

router = APIRouter(prefix="/permissions", tags=["permissions"])

@router.post("/", response_model=schemas.PermissionOut)
def create_permission(payload: schemas.PermissionCreate, db: Session = Depends(get_db_dependency)):
    return service.create_permission(db, payload.name, payload.description)

@router.get("/", response_model=list[schemas.PermissionOut])
def get_permissions(db: Session = Depends(get_db_dependency)):
    return service.list_permissions(db)
