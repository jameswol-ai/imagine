from sqlalchemy import Column, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from database.models.base import BaseModel
from sqlalchemy.dialects.postgresql import UUID
import uuid

# Association tables for many-to-many
user_roles = Table(
    "user_roles",
    BaseModel.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id")),
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id")),
)

class User(BaseModel):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))

    roles = relationship("Role", secondary=user_roles, back_populates="users")
    organization = relationship("Organization", back_populates="users")