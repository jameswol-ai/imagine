from sqlalchemy.orm import Session

def create_role(db: Session, name: str, description: str = None):
    # TODO: implement DB create
    return {"id": 1, "name": name, "description": description}

def list_roles(db: Session):
    # TODO: return real roles
    return [{"id": 1, "name": "Admin", "description": "Administrator role"}]
