# IMAGINE/database/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from . import Base
from .associations import user_roles_table, organization_users_table

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # relationships
    roles = relationship("Role", secondary=user_roles_table, back_populates="users")
    organizations = relationship("Organization", secondary=organization_users_table, back_populates="users")
    audit_records = relationship("AuditRecord", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="creator", cascade="all, delete-orphan")
