# IMAGINE/database/models/base.py

import uuid

from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID

from database.connection import Base


class BaseModel(Base):
    __abstract__ = True

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime,
        onupdate=func.now(),
    )

    created_by = Column(
        String,
        nullable=True,
    )

    updated_by = Column(
        String,
        nullable=True,
    )