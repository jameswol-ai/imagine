# create a default organization and admin user, assign admin role
from sqlalchemy.orm import Session
from database.models import Organization, User, Role
from core.authentication.service import create_user, get_user_by_email
from database.connection import SessionLocal

DEFAULT_ORG = {"name": "Default Org", "description": "Seed organization"}
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "ChangeMe123!"

def seed(session: Session):
    org = session.query(Organization).filter_by(name=DEFAULT_ORG["name"]).first()
    if not org:
        org = Organization(name=DEFAULT_ORG["name"], description=DEFAULT_ORG["description"])
        session.add(org)
        session.commit()
        session.refresh(org)

    admin = get_user_by_email(session, ADMIN_EMAIL)
    if not admin:
        admin = create_user(session, email=ADMIN_EMAIL, password=ADMIN_PASSWORD, full_name="Platform Admin")
    # attach user to organization if not already
    if org not in admin.organizations:
        admin.organizations.append(org)
        session.add(admin)
        session.commit()

    # assign Admin role
    admin_role = session.query(Role).filter_by(name="Admin").first()
    if admin_role and admin_role not in admin.roles:
        admin.roles.append(admin_role)
        session.add(admin)
        session.commit()

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed(db)
        print("Seeded organization and admin user")
    finally:
        db.close()
