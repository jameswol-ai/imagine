from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.notifications import schemas, service
from app.dependencies import get_db_dependency

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.post("/")
def notify(payload: schemas.NotificationCreate, db: Session = Depends(get_db_dependency)):
    rec = service.create_notification(db, payload.to, payload.subject, payload.body, payload.send_email, payload.send_in_app)
    return rec
