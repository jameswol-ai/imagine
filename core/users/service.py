from sqlalchemy.orm import Session
from typing import Optional
from database.models.user import User

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def update_user(db: Session, user_id: int, data: dict) -> Optional[User]:
    user = get_user(db, user_id)
    if not user:
        return None
    for k, v in data.items():
        setattr(user, k, v)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
