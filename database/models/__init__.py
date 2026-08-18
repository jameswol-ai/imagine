# IMAGINE/database/models/__init__.py
# Expose a single Base and import models so Alembic can discover metadata.

from sqlalchemy.ext.declarative import declarative_base

# Shared Base for all models
Base = declarative_base()

# Import models here so Alembic autogenerate can find them
# Add additional model imports as you create them
from .user import User  # noqa: F401
