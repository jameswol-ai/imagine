from fastapi import APIRouter
from architecture.site_planning.routes import router as site_planning_router
router = APIRouter(prefix="/architecture", tags=["Architecture"])
router.include_router(site_planning_router)
