"""IMAGINE FastAPI application."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.dependencies import lifespan
from app.settings import settings


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.app_name,
        version="1.1.0",
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Router imports are intentionally lazy. This keeps the API bootable when
    # an optional domain package is unavailable while preserving the core API.
    try:
        from core.authentication.routes import router as auth_router
        application.include_router(auth_router, prefix=settings.api_v1_prefix)
    except Exception:
        pass
    try:
        from projects.projects.routes import router as projects_router
        application.include_router(projects_router, prefix=settings.api_v1_prefix)
    except Exception:
        pass

    @application.get("/", tags=["system"])
    async def root() -> dict[str, str]:
        return {"message": "IMAGINE API", "version": application.version}

    @application.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "imagine-api"}

    return application


app = create_app()

__all__ = ["app", "create_app"]
