from pydantic import BaseModel, UUID4, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class ZoningType(str, Enum):
    residential = "residential"
    commercial = "commercial"
    mixed_use = "mixed_use"
    industrial = "industrial"

class ComplianceStatus(str, Enum):
    pass_ = "pass"
    warning = "warning"
    fail = "fail"

# ---------- Generative Design ----------
class GenerativeDesignBase(BaseModel):
    project_id: UUID4
    name: str
    iterations: int = 50
    objective: str = "balance"
    population: int = 100
    results: Optional[Dict[str, Any]] = None

class GenerativeDesignCreate(GenerativeDesignBase):
    pass

class GenerativeDesignUpdate(BaseModel):
    name: Optional[str] = None
    iterations: Optional[int] = None
    objective: Optional[str] = None
    population: Optional[int] = None
    results: Optional[Dict[str, Any]] = None

class GenerativeDesignResponse(GenerativeDesignBase):
    id: UUID4
    created_at: datetime
    updated_at: Optional[datetime]

# ---------- Zoning ----------
class ZoningBase(BaseModel):
    project_id: UUID4
    zone_type: ZoningType
    max_height: float
    coverage: float
    setback: float
    description: Optional[str] = None

class ZoningCreate(ZoningBase): pass
class ZoningUpdate(BaseModel):
    zone_type: Optional[ZoningType] = None
    max_height: Optional[float] = None
    coverage: Optional[float] = None
    setback: Optional[float] = None
    description: Optional[str] = None

class ZoningResponse(ZoningBase):
    id: UUID4
    created_at: datetime
    updated_at: Optional[datetime]

# ---------- Site Plan ----------
class SitePlanBase(BaseModel):
    project_id: UUID4
    area: float
    slope: float
    soil_type: str
    orientation: str
    layout_data: Optional[Dict[str, Any]] = None

class SitePlanCreate(SitePlanBase): pass
class SitePlanUpdate(BaseModel):
    area: Optional[float] = None
    slope: Optional[float] = None
    soil_type: Optional[str] = None
    orientation: Optional[str] = None
    layout_data: Optional[Dict[str, Any]] = None

class SitePlanResponse(SitePlanBase):
    id: UUID4
    created_at: datetime
    updated_at: Optional[datetime]

# ---------- Floor Plan ----------
class FloorPlanBase(BaseModel):
    project_id: UUID4
    building_type: str
    floors: int
    plan_data: Optional[Dict[str, Any]] = None

class FloorPlanCreate(FloorPlanBase): pass
class FloorPlanUpdate(BaseModel):
    building_type: Optional[str] = None
    floors: Optional[int] = None
    plan_data: Optional[Dict[str, Any]] = None

class FloorPlanResponse(FloorPlanBase):
    id: UUID4
    created_at: datetime
    updated_at: Optional[datetime]

# ---------- Room Program ----------
class RoomProgramBase(BaseModel):
    project_id: UUID4
    room_name: str
    area: float
    quantity: int
    adjacency: Optional[str] = None

class RoomProgramCreate(RoomProgramBase): pass
class RoomProgramUpdate(BaseModel):
    room_name: Optional[str] = None
    area: Optional[float] = None
    quantity: Optional[int] = None
    adjacency: Optional[str] = None

class RoomProgramResponse(RoomProgramBase):
    id: UUID4
    created_at: datetime
    updated_at: Optional[datetime]

# ---------- Compliance Check ----------
class ComplianceCheckBase(BaseModel):
    project_id: UUID4
    code: str
    rule: str
    required: str
    actual: str
    status: ComplianceStatus
    comments: Optional[str] = None

class ComplianceCheckCreate(ComplianceCheckBase): pass
class ComplianceCheckUpdate(BaseModel):
    code: Optional[str] = None
    rule: Optional[str] = None
    required: Optional[str] = None
    actual: Optional[str] = None
    status: Optional[ComplianceStatus] = None
    comments: Optional[str] = None

class ComplianceCheckResponse(ComplianceCheckBase):
    id: UUID4
    created_at: datetime
    updated_at: Optional[datetime]