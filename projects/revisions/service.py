from sqlalchemy.orm import Session
from .models import Revision

def create_revision(db: Session, project_id: int, description: str, created_by: int):
    rev = Revision(project_id=project_id, description=description, created_by=created_by)
    db.add(rev)
    db.commit()
    db.refresh(rev)
    return rev

def list_revisions(db: Session, project_id: int):
    return db.query(Revision).filter(Revision.project_id == project_id).all()