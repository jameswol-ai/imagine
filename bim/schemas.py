from pydantic import BaseModel, UUID4, Field
from typing import Optional, Dict, Any
from datetime import datetime

class BuildingBase(BaseModel):
    project_id: UUID4
    name: str
    storeys: int
    area: float
    ifc_version: Optional[str] = None
    description: Optional[str] = None

class BuildingCreate(BuildingBase): pass
class BuildingUpdate(BaseModel):
    name: Optional[str] = None
    storeys: Optional[int] = None
    area: Optional[float] = None
    ifc_version: Optional[str] = None
    description: Optional[str] = None

class BuildingResponse(BuildingBase):
    id: UUID4
    created_at: datetime
    updated_at: Optional[datetime]

class StoreyBase(BaseModel):
    building_id: UUID4
    level: str
    height: float
    area: float

class StoreyCreate(StoreyBase): pass
class StoreyUpdate(BaseModel):
    building_id: Optional[UUID4] = None
    level: Optional[str] = None
    height: Optional[float] = None
    area: Optional[float] = None

class StoreyResponse(StoreyBase):
    id: UUID4
    created_at: datetime
    updated_at: Optional[datetime]

# Similarly define Space, Element, IfcModel, CobieAsset, DigitalTwin schemas.
# To save space, I'll show a few; the rest follow the same pattern.

class SpaceBase(BaseModel):
    building_id: UUID4
    storey_id: Optional[UUID4] = None
    name: str
    area: float
    height: float
    space_type: str

class SpaceCreate(SpaceBase): pass
class SpaceUpdate(BaseModel):
    building_id: Optional[UUID4] = None
    storey_id: Optional[UUID4] = None
    name: Optional[str] = None
    area: Optional[float] = None
    height: Optional[float] = None
    space_type: Optional[str] = None

class SpaceResponse(SpaceBase):
    id: UUID4
    created_at: datetime
    updated_at: Optional[datetime]

# Element, IfcModel, CobieAsset, DigitalTwin similarly...