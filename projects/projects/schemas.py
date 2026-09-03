from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProjectStatus(str, Enum):
    planning = "planning"
    active = "active"
    on_hold = "on_hold"
    completed = "completed"
    cancelled = "cancelled"


class ProjectBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.planning
    budget: float = Field(default=0.0, ge=0.0)
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    # organizations.id is Integer in the canonical database model.
    client_id: Optional[int] = Field(default=None, ge=1)


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    budget: Optional[float] = Field(default=None, ge=0.0)
    progress: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    client_id: Optional[int] = Field(default=None, ge=1)


class ProjectResponse(ProjectBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
