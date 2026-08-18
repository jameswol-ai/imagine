from sqlalchemy.orm import Session
from .models import GenerativeDesign

def create_design(db: Session, project_id: int, algorithm: str, parameters: str = None):
    design = GenerativeDesign(project_id=project_id, algorithm=algorithm, parameters=parameters)
    db.add(design)
    db.commit()
    db.refresh(design)
    return design

def list_designs(db: Session, project_id: int):
    return db.query(GenerativeDesign).filter(GenerativeDesign.project_id == project_id).all()