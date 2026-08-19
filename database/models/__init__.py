# IMAGINE/database/models/__init__.py
#
# Shared SQLAlchemy Base and model imports.
#
# This module is also used by Alembic so that all models are
# registered with the same SQLAlchemy metadata collection.

from sqlalchemy.orm import declarative_base


Base = declarative_base()


# ------------------------------------------------------------------
# Model imports
# ------------------------------------------------------------------
#
# Import models after Base is created so SQLAlchemy registers them
# against this shared declarative registry.
#

from .user import User  # noqa: E402,F401
from .organization import Organization  # noqa: E402,F401
from .role import Role  # noqa: E402,F401
from .permission import Permission  # noqa: E402,F401
from .audit import AuditRecord  # noqa: E402,F401
from .notification import Notification  # noqa: E402,F401
from .associations import (  # noqa: E402,F401
    role_permissions_table,
    user_roles_table,
    organization_users_table,
)