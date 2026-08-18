from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.settings import settings
from app.dependencies import lifespan
from projects.projects.routes import router as projects_router
from core.authentication.routes import router as auth_router
# Import all routers from other modules...

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(projects_router, prefix=settings.API_V1_PREFIX)
# ... include all other routers

@app.get("/")
async def root():
    return {"message": "IMAGINE API", "version": "1.0.0"}