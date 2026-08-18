from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.organizations import schemas, service
from app.dependencies import get_db_dependency

router = APIRouter(prefix="/organizations", tags=["organizations"])

@router.post("/", response_model=schemas.OrganizationOut)
def create_org(payload: schemas.OrganizationCreate, db: Session = Depends(get_db_dependency)):
    org = service.create_organization(db, payload.name, payload.description)
    return org

@router.get("/{org_id}", response_model=schemas.OrganizationOut)
def read_org(org_id: int, db: Session = Depends(get_db_dependency)):
    org = service.get_organization(db, org_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return org
