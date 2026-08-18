from sqlalchemy import Column, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from database.models.base import BaseModel
from sqlalchemy.dialects.postgresql import UUID

role_permissions = Table(
    "role_permissions",
    BaseModel.metadata,
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id")),
    Column("permission_id", UUID(as_uuid=True), ForeignKey("permissions.id")),
)

class Role(BaseModel):
    __tablename__ = "roles"
    name = Column(String, unique=True)
    description = Column(String)

    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    users = relationship("User", secondary="user_roles", back_populates="roles")