from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import date
from enum import Enum

class ProjectStatus(str, Enum):
    planning = "planning"
    active = "active"
    on_hold = "on_hold"
    completed = "completed"
    cancelled = "cancelled"

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.planning
    budget: float
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    client_id: UUID4

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    budget: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    client_id: Optional[UUID4] = None

class ProjectResponse(ProjectBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime