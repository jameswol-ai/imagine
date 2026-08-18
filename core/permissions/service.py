from sqlalchemy.orm import Session

def create_permission(db: Session, name: str, description: str = None):
    # TODO: implement DB create
    return {"id": 1, "name": name, "description": description}

def list_permissions(db: Session):
    return [{"id": 1, "name": "projects.view", "description": "View projects"}]
