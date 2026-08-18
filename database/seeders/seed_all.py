# run all seeders in order
from sqlalchemy.orm import Session
from database.connection import SessionLocal
from database.seeders.seed_roles_permissions import seed as seed_roles_permissions
from database.seeders.seed_organization_admin import seed as seed_org_admin

def run_all():
    db = SessionLocal()
    try:
        seed_roles_permissions(db)
        seed_org_admin(db)
        print("All seeders executed")
    finally:
        db.close()

if __name__ == "__main__":
    run_all()
