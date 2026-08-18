from sqlalchemy.orm import Session
from .models import BeamDesign

def create_beam(db: Session, project_id: int, material: str, span_length: float, load_capacity: float = None):
    beam = BeamDesign(project_id=project_id, material=material, span_length=span_length, load_capacity=load_capacity)
    db.add(beam)
    db.commit()
    db.refresh(beam)
    return beam

def list_beams(db: Session, project_id: int):
    return db.query(BeamDesign).filter(BeamDesign.project_id == project_id).all()