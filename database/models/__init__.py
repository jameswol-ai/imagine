"""IMAGINE database models.

All models share the canonical SQLAlchemy Base from database.connection.
"""

from database.connection import Base

from .user import User
from .organization import Organization
from .role import Role
from .permission import Permission
from .audit import AuditRecord
from .notification import Notification
from .module_workspace import ModuleWorkspaceRecord
from .project_file import ProjectFileRecord
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
    "ModuleWorkspaceRecord",
    "ProjectFileRecord",
    "role_permissions_table",
    "user_roles_table",
    "organization_users_table",
]
