from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.users import schemas, service
from app.dependencies import get_db_dependency

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{user_id}", response_model=schemas.UserOut)
def read_user(user_id: int, db: Session = Depends(get_db_dependency)):
    user = service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.patch("/{user_id}", response_model=schemas.UserOut)
def patch_user(user_id: int, payload: schemas.UserUpdate, db: Session = Depends(get_db_dependency)):
    updated = service.update_user(db, user_id, payload.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated
