# database/seeders/seed.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.settings import settings
from core.users.models import User
from core.roles.models import Role, role_permissions
from core.permissions.models import Permission
from core.organizations.models import Organization
from core.authentication.utils import get_password_hash
from database.models.base import Base
import uuid

async def seed():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        # Create tables if they don't exist (optional)
        # await conn.run_sync(Base.metadata.create_all)
        pass

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Create organization
        org = Organization(name="IMAGINE HQ")
        session.add(org)
        await session.flush()

        # Create permissions
        perms = [
            Permission(name="View Projects", codename="view_project"),
            Permission(name="Edit Projects", codename="edit_project"),
            Permission(name="Delete Projects", codename="delete_project"),
            Permission(name="Create Projects", codename="create_project"),
            # Add more as needed
        ]
        session.add_all(perms)
        await session.flush()

        # Create roles
        admin_role = Role(name="Admin", description="Full access")
        manager_role = Role(name="Manager", description="Project management")
        viewer_role = Role(name="Viewer", description="Read-only")

        # Assign permissions to admin
        admin_role.permissions = perms
        manager_role.permissions = [p for p in perms if p.codename.startswith(("view", "edit", "create"))]
        viewer_role.permissions = [p for p in perms if p.codename.startswith("view")]

        session.add_all([admin_role, manager_role, viewer_role])
        await session.flush()

        # Create users
        admin_user = User(
            email="admin@imagine.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            is_active=True,
            is_superuser=True,
            organization_id=org.id,
            roles=[admin_role]
        )
        manager_user = User(
            email="manager@imagine.com",
            hashed_password=get_password_hash("manager123"),
            full_name="Project Manager",
            is_active=True,
            organization_id=org.id,
            roles=[manager_role]
        )
        viewer_user = User(
            email="viewer@imagine.com",
            hashed_password=get_password_hash("viewer123"),
            full_name="Viewer User",
            is_active=True,
            organization_id=org.id,
            roles=[viewer_role]
        )
        session.add_all([admin_user, manager_user, viewer_user])
        await session.commit()

    print("✅ Seed data inserted.")

if __name__ == "__main__":
    asyncio.run(seed())