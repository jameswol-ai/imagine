from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.authentication import schemas, service, utils
from app.dependencies import get_db_dependency

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=schemas.UserOut)
def signup(payload: schemas.UserCreate, db: Session = Depends(get_db_dependency)):
    existing = service.get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = service.create_user(db, email=payload.email, password=payload.password, full_name=payload.full_name)
    return user

@router.post("/login", response_model=schemas.Token)
def login(payload: schemas.UserCreate, db: Session = Depends(get_db_dependency)):
    user = service.authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = utils.create_access_token(subject=str(user.id))
    return {"access_token": token, "token_type": "bearer"}
