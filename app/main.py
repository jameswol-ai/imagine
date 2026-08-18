from fastapi import FastAPI
from core.authentication.routes import router as auth_router

from core.authorization.routes import router as authz_router
from core.organizations.routes import router as org_router
from core.users.routes import router as users_router
from core.roles.routes import router as roles_router
from core.permissions.routes import router as permissions_router
from core.audit.routes import router as audit_router
from core.notifications.routes import router as notifications_router

app.include_router(authz_router)
app.include_router(org_router)
app.include_router(users_router)
app.include_router(roles_router)
app.include_router(permissions_router)
app.include_router(audit_router)
app.include_router(notifications_router)



app = FastAPI(
    title="IMAGINE Platform",
    description="Architecture, Engineering, Construction & AI Integration",
    version="0.1.0"
)

app.include_router(auth_router)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "IMAGINE is running"}
