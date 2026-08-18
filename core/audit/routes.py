from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.audit import service
from app.dependencies import get_db_dependency

router = APIRouter(prefix="/audit", tags=["audit"])

@router.post("/log")
def log(payload: dict, db: Session = Depends(get_db_dependency)):
    # payload expected to contain user_id and action
    user_id = payload.get("user_id")
    action = payload.get("action")
    resource = payload.get("resource")
    metadata = payload.get("metadata")
    rec = service.log_event(db, user_id, action, resource, metadata)
    return rec
