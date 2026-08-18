from pydantic import BaseModel
from typing import Optional

class BeamDesignCreate(BaseModel):
    project_id: int
    material: str
    span_length: float
    load_capacity: Optional[float] = None

class BeamDesignOut(BaseModel):
    id: int
    project_id: int
    material: str
    span_length: float
    load_capacity: Optional[float]

    class Config:
        orm_mode = True