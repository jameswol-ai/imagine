"""
IMAGINE database model registry.

All models share the declarative Base defined in
database.connection.
"""

from database.connection import Base

from .user import User
from .organization import Organization
from .role import Role
from .permission import Permission
from .audit import AuditRecord
from .notification import Notification

from .associations import (
    role_permissions_table,
    user_roles_table,
    organization_users_table,
)


__all__ = [
    "Base",
    "User",
    "Organization",
    "Role",
    "Permission",
    "AuditRecord",
    "Notification",
    "role_permissions_table",
    "user_roles_table",
    "organization_users_table",
]