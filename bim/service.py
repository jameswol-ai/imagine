from sqlalchemy.orm import Session
from .models import Building

def create_building(db: Session, project_id: int, name: str, address: str = None):
    b = Building(project_id=project_id, name=name, address=address)
    db.add(b)
    db.commit()
    db.refresh(b)
    return b

def list_buildings(db: Session, project_id: int):
    return db.query(Building).filter(Building.project_id == project_id).all()