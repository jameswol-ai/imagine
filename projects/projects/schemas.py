from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, UUID4


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

    budget: float = 0.0

    progress: float = 0.0

    start_date: Optional[date] = None
    end_date: Optional[date] = None

    client_id: Optional[UUID4] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

    status: Optional[ProjectStatus] = None

    budget: Optional[float] = None

    progress: Optional[float] = None

    start_date: Optional[date] = None
    end_date: Optional[date] = None

    client_id: Optional[UUID4] = None


class ProjectResponse(ProjectBase):
    id: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None