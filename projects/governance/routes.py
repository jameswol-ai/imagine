"""Governance API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db_dependency

router = APIRouter(prefix="/governance", tags=["Governance"])


@router.get("/health")
def governance_health(
    db: Session = Depends(get_db_dependency),
) -> dict[str, str]:
    """Return a lightweight governance route health check."""
    del db
    return {"status": "ok"}
