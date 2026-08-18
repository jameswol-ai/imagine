from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from database.models.base import BaseModel

class Permission(BaseModel):
    __tablename__ = "permissions"
    name = Column(String, unique=True)
    codename = Column(String, unique=True)  # e.g., "view_project", "edit_project"

    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")