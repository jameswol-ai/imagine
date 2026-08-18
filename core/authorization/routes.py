from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.authorization import schemas, service
from app.dependencies import get_db_dependency

router = APIRouter(prefix="/authz", tags=["authorization"])

@router.post("/check", response_model=schemas.CheckPermissionResponse)
def check_permission(payload: schemas.CheckPermissionRequest, db: Session = Depends(get_db_dependency)):
    allowed = service.user_has_permission(db, payload.user_id, payload.permission, payload.resource)
    return {"allowed": allowed, "reasons": None if allowed else ["No matching permission found"]}
