# IMAGINE/database/models/audit.py

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, func
from sqlalchemy.orm import relationship

from . import Base


class AuditRecord(Base):
    __tablename__ = "audit_records"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    action = Column(
        String(255),
        nullable=False,
    )

    resource = Column(
        String(255),
        nullable=True,
    )

    # "metadata" is reserved by SQLAlchemy's Declarative API.
    #
    # Keep the database column name as "metadata" for compatibility,
    # but expose it through the Python ORM as "metadata_json".
    metadata_json = Column(
        "metadata",
        JSON,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="audit_records",
    )