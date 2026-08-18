from sqlalchemy.orm import Session
from .models import Project

def create_project(db: Session, name: str, description: str, owner_id: int) -> Project:
    project = Project(name=name, description=description, owner_id=owner_id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

def get_project(db: Session, project_id: int) -> Project | None:
    return db.query(Project).filter(Project.id == project_id).first()

def list_projects(db: Session):
    return db.query(Project).all()