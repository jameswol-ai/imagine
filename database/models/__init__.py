# IMAGINE/database/models/__init__.py
# Shared Base and model imports for Alembic autogenerate

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import models so Alembic can discover them
from .user import User  # noqa: F401
from .organization import Organization  # noqa: F401
from .role import Role  # noqa: F401
from .permission import Permission  # noqa: F401
from .audit import AuditRecord  # noqa: F401
from .notification import Notification  # noqa: F401
from .associations import role_permissions_table, user_roles_table, organization_users_table  # noqa: F401
