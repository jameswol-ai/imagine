from typing import List
from sqlalchemy.orm import Session

def user_has_permission(db: Session, user_id: int, permission: str, resource: str = None) -> bool:
    # TODO: implement real permission lookup using roles/permissions tables
    # Placeholder logic: allow everything for user_id == 1 (admin)
    if user_id == 1:
        return True
    # otherwise deny by default
    return False
