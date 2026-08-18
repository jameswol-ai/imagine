from sqlalchemy import Column, String, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship
from database.models.base import BaseModel
from sqlalchemy.dialects.postgresql import UUID
import enum

class ProjectStatus(str, enum.Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Project(BaseModel):
    __tablename__ = "projects"
    name = Column(String, index=True)
    description = Column(String)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PLANNING)
    budget = Column(Float)
    start_date = Column(String)
    end_date = Column(String)
    client_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    # Many-to-many with users (project team)
    # Use separate association table if needed

    client = relationship("Organization", foreign_keys=[client_id])
    approvals = relationship("Approval", back_populates="project")
    revisions = relationship("Revision", back_populates="project")