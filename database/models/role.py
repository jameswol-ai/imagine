# IMAGINE/database/models/role.py
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import relationship
from . import Base
from .associations import role_permissions_table, user_roles_table

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # relationships
    permissions = relationship("Permission", secondary=role_permissions_table, back_populates="roles")
    users = relationship("User", secondary=user_roles_table, back_populates="roles")
