from fastapi import FastAPI
from core.authentication.routes import router as auth_router

app = FastAPI(
    title="IMAGINE Platform",
    description="Architecture, Engineering, Construction & AI Integration",
    version="0.1.0"
)

app.include_router(auth_router)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "IMAGINE is running"}
