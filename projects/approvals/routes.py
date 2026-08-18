from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db_dependency
from . import schemas, service

router = APIRouter(prefix="/approvals", tags=["approvals"])

@router.post("/", response_model=schemas.ApprovalOut)
def create_approval(payload: schemas.ApprovalCreate, db: Session = Depends(get_db_dependency)):
    return service.create_approval(db, payload.project_id, payload.approver_id, payload.comment)

@router.get("/project/{project_id}", response_model=list[schemas.ApprovalOut])
def list_project_approvals(project_id: int, db: Session = Depends(get_db_dependency)):
    return service.list_approvals(db, project_id)