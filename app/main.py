from fastapi import FastAPI
from app import config, settings, dependencies

app = FastAPI(
    title="IMAGINE Platform",
    description="Architecture, Engineering, Construction & AI Integration",
    version="0.1.0"
)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "IMAGINE is running"}

@app.get("/")
def root():
    return {"message": "Welcome to IMAGINE!"}

@app.get("/projects")
def list_projects():
    # placeholder: replace with database.repositories.projects.list()
    return {"projects": ["Project Alpha", "Project Beta"]}
