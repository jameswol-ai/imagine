from sqlalchemy.orm import Session
from typing import Optional

def create_organization(db: Session, name: str, description: Optional[str] = None):
    # TODO: replace with real DB model create
    org = {"id": 1, "name": name, "description": description}
    return org

def get_organization(db: Session, org_id: int):
    # TODO: fetch from DB
    if org_id == 1:
        return {"id": 1, "name": "Default Org", "description": "Seed org"}
    return None
