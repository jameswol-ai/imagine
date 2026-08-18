from pydantic import BaseModel
from typing import List, Optional

class CheckPermissionRequest(BaseModel):
    user_id: int
    permission: str
    resource: Optional[str] = None

class CheckPermissionResponse(BaseModel):
    allowed: bool
    reasons: Optional[List[str]] = None
