"""Architecture API router."""

from fastapi import APIRouter

from architecture.zoning.routes import router as zoning_router


router = APIRouter(
    prefix="/architecture",
    tags=["architecture"],
)

router.include_router(zoning_router)
