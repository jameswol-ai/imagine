from pydantic import BaseModel
from typing import Optional

class GenerativeDesignCreate(BaseModel):
    project_id: int
    algorithm: str
    parameters: Optional[str] = None

class GenerativeDesignOut(BaseModel):
    id: int
    project_id: int
    algorithm: str
    result_summary: Optional[str]

    class Config:
        orm_mode = True