# create default roles and permissions
from sqlalchemy.orm import Session
from database.models import Role, Permission
from database.connection import SessionLocal

DEFAULT_ROLES = [
    {"name": "Admin", "description": "Full access"},
    {"name": "Architect", "description": "Architect role"},
    {"name": "Engineer", "description": "Engineer role"},
    {"name": "QuantitySurveyor", "description": "QS role"},
]

DEFAULT_PERMISSIONS = [
    {"name": "projects.view", "description": "View projects"},
    {"name": "projects.edit", "description": "Edit projects"},
    {"name": "bim.view", "description": "View BIM models"},
    {"name": "bim.edit", "description": "Edit BIM models"},
]

def seed(session: Session):
    for p in DEFAULT_PERMISSIONS:
        exists = session.query(Permission).filter_by(name=p["name"]).first()
        if not exists:
            session.add(Permission(name=p["name"], description=p.get("description")))
    session.commit()

    for r in DEFAULT_ROLES:
        exists = session.query(Role).filter_by(name=r["name"]).first()
        if not exists:
            session.add(Role(name=r["name"], description=r.get("description")))
    session.commit()

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed(db)
        print("Seeded roles and permissions")
    finally:
        db.close()
