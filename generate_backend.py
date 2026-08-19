# generate_backend.py
import os
import shutil

BASE_DIR = "IMAGINE"

# Define field definitions for each submodule
# Format: { module: { submodule: [ (field, type, kwargs), ... ] } }
FIELD_DEFS = {
    "architecture": {
        "generative_design": [
            ("name", "String", {"nullable": True}),
            ("iterations", "Integer", {"default": 50}),
            ("objective", "String", {"default": "balance"}),
            ("population", "Integer", {"default": 100}),
            ("results", "JSON", {"nullable": True}),
        ],
        "zoning": [
            ("zone_type", "String", {"nullable": False}),
            ("max_height", "Float", {"nullable": False}),
            ("coverage", "Float", {"nullable": False}),
            ("setback", "Float", {"nullable": False}),
            ("description", "String", {"nullable": True}),
        ],
        "site_planning": [
            ("area", "Float", {"nullable": False}),
            ("slope", "Float", {"nullable": False}),
            ("soil_type", "String", {"nullable": False}),
            ("orientation", "String", {"nullable": False}),
            ("layout_data", "JSON", {"nullable": True}),
        ],
        "floor_planning": [
            ("building_type", "String", {"nullable": False}),
            ("floors", "Integer", {"nullable": False}),
            ("plan_data", "JSON", {"nullable": True}),
        ],
        "room_programming": [
            ("room_name", "String", {"nullable": False}),
            ("area", "Float", {"nullable": False}),
            ("quantity", "Integer", {"nullable": False}),
            ("adjacency", "String", {"nullable": True}),
        ],
        "compliance": [
            ("code", "String", {"nullable": False}),
            ("rule", "String", {"nullable": False}),
            ("required", "String", {"nullable": False}),
            ("actual", "String", {"nullable": False}),
            ("status", "String", {"nullable": False}),
            ("comments", "String", {"nullable": True}),
        ],
    },
    "structural": {
        "eurocode": [
            ("part", "String", {"nullable": False}),
            ("parameters", "JSON", {"nullable": True}),
        ],
        "beam_design": [
            ("beam_id", "String", {"nullable": False}),
            ("span", "Float", {"nullable": False}),
            ("load", "Float", {"nullable": False}),
            ("material", "String", {"nullable": False}),
            ("status", "String", {"nullable": False}),
            ("design_data", "JSON", {"nullable": True}),
        ],
        "column_design": [
            ("column_id", "String", {"nullable": False}),
            ("axial_load", "Float", {"nullable": False}),
            ("section", "String", {"nullable": False}),
            ("reinforcement_ratio", "Float", {"nullable": False}),
            ("design_data", "JSON", {"nullable": True}),
        ],
        "slab_design": [
            ("slab_id", "String", {"nullable": False}),
            ("thickness", "Float", {"nullable": False}),
            ("span", "Float", {"nullable": False}),
            ("load", "Float", {"nullable": False}),
            ("design_data", "JSON", {"nullable": True}),
        ],
        "foundation_design": [
            ("foundation_type", "String", {"nullable": False}),
            ("capacity", "Float", {"nullable": False}),
            ("depth", "Float", {"nullable": False}),
            ("design_data", "JSON", {"nullable": True}),
        ],
        "retaining_walls": [
            ("wall_id", "String", {"nullable": False}),
            ("height", "Float", {"nullable": False}),
            ("thickness", "Float", {"nullable": False}),
            ("stability", "String", {"nullable": False}),
        ],
        "steel_connections": [
            ("connection_type", "String", {"nullable": False}),
            ("bolts", "String", {"nullable": False}),
            ("capacity", "Float", {"nullable": False}),
            ("design_data", "JSON", {"nullable": True}),
        ],
        "finite_element_analysis": [
            ("analysis_type", "String", {"nullable": False}),
            ("results", "JSON", {"nullable": True}),
            ("status", "String", {"nullable": False}),
        ],
    },
    "bim": {
        "buildings": [
            ("name", "String", {"nullable": False}),
            ("storeys", "Integer", {"nullable": False}),
            ("area", "Float", {"nullable": False}),
            ("ifc_version", "String", {"nullable": True}),
            ("description", "String", {"nullable": True}),
        ],
        "storeys": [
            ("level", "String", {"nullable": False}),
            ("height", "Float", {"nullable": False}),
            ("area", "Float", {"nullable": False}),
        ],
        "spaces": [
            ("name", "String", {"nullable": False}),
            ("area", "Float", {"nullable": False}),
            ("height", "Float", {"nullable": False}),
            ("space_type", "String", {"nullable": False}),
        ],
        "elements": [
            ("name", "String", {"nullable": False}),
            ("material", "String", {"nullable": False}),
            ("quantity", "Float", {"nullable": False}),
            ("unit", "String", {"nullable": False}),
            ("element_type", "String", {"nullable": True}),
        ],
        "ifc": [
            ("filename", "String", {"nullable": False}),
            ("version", "String", {"nullable": False}),
            ("file_path", "String", {"nullable": False}),
        ],
        "cobie": [
            ("asset_name", "String", {"nullable": False}),
            ("serial_number", "String", {"nullable": False}),
            ("manufacturer", "String", {"nullable": False}),
            ("warranty_years", "Integer", {"nullable": False}),
        ],
        "digital_twin": [
            ("sensor_data", "JSON", {"nullable": True}),
            ("energy_usage", "Float", {"nullable": True}),
            ("occupancy", "Integer", {"nullable": True}),
            ("temperature", "Float", {"nullable": True}),
            ("humidity", "Float", {"nullable": True}),
        ],
    },
}

# Additional top-level modules (projects, mep, costing, etc.) will use generic fields
# but you can extend the FIELD_DEFS similarly.

# -------------------------------------------------------------------
# Helper functions to generate model, schema, service, routes
# -------------------------------------------------------------------
def generate_model(module_name, fields):
    """Generate SQLAlchemy model class with given fields."""
    imports = [
        "from sqlalchemy import Column, String, Integer, Float, JSON, ForeignKey",
        "from sqlalchemy.orm import relationship",
        "from database.models.base import BaseModel",
        "from sqlalchemy.dialects.postgresql import UUID",
    ]
    cols = []
    for field, ftype, kwargs in fields:
        col_line = f"    {field} = Column({ftype}"
        if kwargs:
            opts = ", ".join(f"{k}={v}" for k, v in kwargs.items())
            col_line += f", {opts}"
        col_line += ")"
        cols.append(col_line)
    # Add foreign key to project (optional)
    cols.append("    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=True)")

    body = f"""
from sqlalchemy import Column, String, Integer, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from database.models.base import BaseModel
from sqlalchemy.dialects.postgresql import UUID

class {module_name.capitalize()}(BaseModel):
    __tablename__ = "{module_name}"
{chr(10).join(cols)}
"""
    return body

def generate_schema(module_name, fields):
    """Generate Pydantic schemas."""
    # Fields for base
    base_fields = []
    for field, ftype, kwargs in fields:
        # Determine optional/required
        optional = kwargs.get("nullable", False) or kwargs.get("default") is not None
        type_map = {
            "String": "str",
            "Integer": "int",
            "Float": "float",
            "JSON": "dict",
        }
        py_type = type_map.get(ftype, "str")
        if optional:
            base_fields.append(f"    {field}: Optional[{py_type}] = None")
        else:
            base_fields.append(f"    {field}: {py_type}")
    # Add project_id as optional
    base_fields.append("    project_id: Optional[UUID4] = None")

    base_body = f"""
from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime

class {module_name.capitalize()}Base(BaseModel):
{chr(10).join(base_fields)}
"""
    create_body = f"""
class {module_name.capitalize()}Create({module_name.capitalize()}Base):
    pass
"""
    update_body = f"""
class {module_name.capitalize()}Update(BaseModel):
{chr(10).join([f"    {f}: Optional[{type_map.get(t, 'str')}] = None" for f, t, _ in fields])}
    project_id: Optional[UUID4] = None
"""
    response_body = f"""
class {module_name.capitalize()}Response({module_name.capitalize()}Base):
    id: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None
"""
    return base_body + create_body + update_body + response_body

def generate_service(module_name):
    """Generate service class with CRUD methods."""
    return f"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models import {module_name.capitalize()}
from .schemas import {module_name.capitalize()}Create, {module_name.capitalize()}Update

class {module_name.capitalize()}Service:
    @staticmethod
    async def get(db: AsyncSession, id: str):
        return await db.get({module_name.capitalize()}, id)

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100):
        result = await db.execute(select({module_name.capitalize()}).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def create(db: AsyncSession, data: {module_name.capitalize()}Create):
        instance = {module_name.capitalize()}(**data.model_dump())
        db.add(instance)
        await db.commit()
        await db.refresh(instance)
        return instance

    @staticmethod
    async def update(db: AsyncSession, id: str, data: {module_name.capitalize()}Update):
        instance = await db.get({module_name.capitalize()}, id)
        if not instance:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(instance, key, value)
        await db.commit()
        await db.refresh(instance)
        return instance

    @staticmethod
    async def delete(db: AsyncSession, id: str):
        instance = await db.get({module_name.capitalize()}, id)
        if instance:
            await db.delete(instance)
            await db.commit()
            return True
        return False
"""

def generate_routes(module_name):
    """Generate FastAPI routes."""
    return f"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from .schemas import {module_name.capitalize()}Create, {module_name.capitalize()}Update, {module_name.capitalize()}Response
from .service import {module_name.capitalize()}Service
from database.connection import get_db
from core.authorization.dependencies import require_permission

router = APIRouter(prefix="/{module_name}", tags=["{module_name}"])

@router.get("/", response_model=List[{module_name.capitalize()}Response])
async def list_items(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), _=Depends(require_permission("view_{module_name}"))):
    return await {module_name.capitalize()}Service.get_all(db, skip, limit)

@router.get("/{{id}}", response_model={module_name.capitalize()}Response)
async def get_item(id: str, db: AsyncSession = Depends(get_db), _=Depends(require_permission("view_{module_name}"))):
    item = await {module_name.capitalize()}Service.get(db, id)
    if not item:
        raise HTTPException(404, "Not found")
    return item

@router.post("/", response_model={module_name.capitalize()}Response, status_code=201)
async def create_item(data: {module_name.capitalize()}Create, db: AsyncSession = Depends(get_db), _=Depends(require_permission("edit_{module_name}"))):
    return await {module_name.capitalize()}Service.create(db, data)

@router.put("/{{id}}", response_model={module_name.capitalize()}Response)
async def update_item(id: str, data: {module_name.capitalize()}Update, db: AsyncSession = Depends(get_db), _=Depends(require_permission("edit_{module_name}"))):
    item = await {module_name.capitalize()}Service.update(db, id, data)
    if not item:
        raise HTTPException(404, "Not found")
    return item

@router.delete("/{{id}}", status_code=204)
async def delete_item(id: str, db: AsyncSession = Depends(get_db), _=Depends(require_permission("edit_{module_name}"))):
    deleted = await {module_name.capitalize()}Service.delete(db, id)
    if not deleted:
        raise HTTPException(404, "Not found")
    return
"""

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)

def generate_module_files(base, module_name, fields):
    """Generate all files for a submodule."""
    # Create __init__.py
    create_file(os.path.join(base, module_name, "__init__.py"), "")
    # models.py
    create_file(os.path.join(base, module_name, "models.py"), generate_model(module_name, fields))
    # schemas.py
    create_file(os.path.join(base, module_name, "schemas.py"), generate_schema(module_name, fields))
    # service.py
    create_file(os.path.join(base, module_name, "service.py"), generate_service(module_name))
    # routes.py
    create_file(os.path.join(base, module_name, "routes.py"), generate_routes(module_name))

# -------------------------------------------------------------------
# Main generation
# -------------------------------------------------------------------
def generate_backend():
    os.makedirs(BASE_DIR, exist_ok=True)

    # Generate modules with specific fields
    for module, submodules in FIELD_DEFS.items():
        for sub, fields in submodules.items():
            base_path = os.path.join(BASE_DIR, module)
            generate_module_files(base_path, sub, fields)

    # Generate other core modules (generic)
    generic_modules = [
        ("projects", ["projects", "approvals", "revisions", "workflows", "governance"]),
        ("mep", ["mechanical", "electrical", "plumbing"]),
        ("costing", ["boq", "quantity_takeoff", "procurement", "forex", "inflation", "risk_analysis", "cashflow"]),
        ("construction", ["planning", "scheduling", "rfis", "submittals", "variations", "snagging", "progress_tracking", "site_diaries"]),
        ("documents", ["drawing_management", "specifications", "contracts", "reports", "version_control", "archives"]),
        ("ai", ["imagine_architect", "imagine_engineer", "imagine_mep", "imagine_qs", "imagine_pm", "vector_store", "rag", "prompt_library"]),
        ("analytics", ["dashboards", "kpis", "portfolio", "forecasting", "reporting"]),
        ("regional", ["uganda", "kenya", "tanzania", "rwanda", "south_sudan", "codes", "zoning_laws"]),
        ("integrations", ["microsoft", "autocad", "revit", "archicad", "tekla", "ifcopenshell", "arcgis", "azure", "mapbox"]),
        ("digital_twin", ["assets", "sensors", "telemetry", "energy", "maintenance", "predictive_ai"]),
    ]

    for module, sublist in generic_modules:
        for sub in sublist:
            # Use a generic field set (only name)
            fields = [("name", "String", {"nullable": True})]
            base_path = os.path.join(BASE_DIR, module)
            generate_module_files(base_path, sub, fields)

    # Create app, database, core folders (using previous script content)
    # ... (include the app/ and database/ files from earlier)
    # I'll add them here for completeness.
    app_files = {
        "app/main.py": """from fastapi import FastAPI\nfrom fastapi.middleware.cors import CORSMiddleware\nfrom app.settings import settings\nfrom app.dependencies import lifespan\n\napp = FastAPI(title=settings.APP_NAME, version="1.0.0", lifespan=lifespan)\napp.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])\n\n@app.get("/")\nasync def root():\n    return {"message": "IMAGINE API"}""",
        "app/config.py": "from .settings import settings\n\nclass AppConfig:\n    API_PREFIX = settings.API_V1_PREFIX\n    PROJECT_NAME = settings.APP_NAME\n    DEBUG = settings.DEBUG\n\nconfig = AppConfig()",
        "app/settings.py": """from pydantic_settings import BaseSettings\n\nclass Settings(BaseSettings):\n    APP_NAME: str = "IMAGINE"\n    DEBUG: bool = False\n    API_V1_PREFIX: str = "/api/v1"\n    SECRET_KEY: str = "your-secret-key"\n    ALGORITHM: str = "HS256"\n    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7\n    DB_USER: str = "postgres"\n    DB_PASSWORD: str = "postgres"\n    DB_HOST: str = "localhost"\n    DB_PORT: int = 5432\n    DB_NAME: str = "imagine"\n\n    @property\n    def DATABASE_URL(self) -> str:\n        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"\n\n    class Config:\n        env_file = ".env"\n\nsettings = Settings()""",
        "app/dependencies.py": "from contextlib import asynccontextmanager\nfrom fastapi import FastAPI\nfrom database.connection import engine\n\n@asynccontextmanager\nasync def lifespan(app: FastAPI):\n    yield\n    await engine.dispose()",
    }
    for path, content in app_files.items():
        create_file(os.path.join(BASE_DIR, path), content)

    # Database files (simplified)
    db_files = {
        "database/connection.py": """from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker\nfrom sqlalchemy.orm import declarative_base\nfrom app.settings import settings\n\nengine = create_async_engine(settings.DATABASE_URL, echo=True)\nAsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)\n\nasync def get_db() -> AsyncSession:\n    async with AsyncSessionLocal() as session:\n        yield session\n\nBase = declarative_base()""",
        "database/models/base.py": """from sqlalchemy import Column, DateTime, String, func\nfrom sqlalchemy.dialects.postgresql import UUID\nfrom database.connection import Base\nimport uuid\n\nclass BaseModel(Base):\n    __abstract__ = True\n    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)\n    created_at = Column(DateTime, server_default=func.now())\n    updated_at = Column(DateTime, onupdate=func.now())\n    created_by = Column(String, nullable=True)\n    updated_by = Column(String, nullable=True)""",
        "database/models/__init__.py": "",
        "database/repositories/base.py": """from sqlalchemy.ext.asyncio import AsyncSession\nfrom sqlalchemy import select\n\nclass BaseRepository:\n    def __init__(self, model):\n        self.model = model\n\n    async def get(self, db: AsyncSession, id: str):\n        return await db.get(self.model, id)\n\n    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100):\n        result = await db.execute(select(self.model).offset(skip).limit(limit))\n        return result.scalars().all()""",
        "database/repositories/__init__.py": "",
        "database/seeders/__init__.py": "",
        "database/migrations/alembic.ini": "[alembic]\nscript_location = migrations\nprepend_sys_path = .\nversion_path_separator = os\nsqlalchemy.url = postgresql+asyncpg://postgres:postgres@localhost/imagine",
        "database/migrations/env.py": """from logging.config import fileConfig\nfrom sqlalchemy.ext.asyncio import create_async_engine\nfrom alembic import context\nfrom database.connection import Base\nfrom app.settings import settings\nimport asyncio\n\nconfig = context.config\nfileConfig(config.config_file_name)\ntarget_metadata = Base.metadata\n\ndef run_migrations_offline():\n    context.configure(url=settings.DATABASE_URL, target_metadata=target_metadata, literal_binds=True)\n    with context.begin_transaction():\n        context.run_migrations()\n\nasync def run_migrations_online():\n    connectable = create_async_engine(settings.DATABASE_URL)\n    async with connectable.connect() as connection:\n        await connection.run_sync(do_run_migrations)\n\ndef do_run_migrations(connection):\n    context.configure(connection=connection, target_metadata=target_metadata)\n    with context.begin_transaction():\n        context.run_migrations()\n\nif context.is_offline_mode():\n    run_migrations_offline()\nelse:\n    asyncio.run(run_migrations_online())""",
        "database/migrations/versions/.keep": "",
    }
    for path, content in db_files.items():
        create_file(os.path.join(BASE_DIR, path), content)

    # Core modules (authentication, authorization, organizations, users, roles, permissions, audit, notifications)
    core_modules = ["authentication", "authorization", "organizations", "users", "roles", "permissions", "audit", "notifications"]
    for mod in core_modules:
        base_path = os.path.join(BASE_DIR, "core", mod)
        os.makedirs(base_path, exist_ok=True)
        create_file(os.path.join(base_path, "__init__.py"), "")
        # Generic fields for core (can be expanded later)
        fields = [("name", "String", {"nullable": True})]
        create_file(os.path.join(base_path, "models.py"), generate_model(mod, fields))
        create_file(os.path.join(base_path, "schemas.py"), generate_schema(mod, fields))
        create_file(os.path.join(base_path, "service.py"), generate_service(mod))
        create_file(os.path.join(base_path, "routes.py"), generate_routes(mod))

    # Top-level folders
    for folder in ["tests", "deployment/docker", "deployment/kubernetes", "deployment/github_actions", "deployment/azure",
                   "docs/architecture", "docs/api", "docs/database", "docs/engineering", "docs/user_manuals"]:
        os.makedirs(os.path.join(BASE_DIR, folder), exist_ok=True)
        create_file(os.path.join(BASE_DIR, folder, "__init__.py"), "")

    # Requirements, Docker, etc.
    create_file(os.path.join(BASE_DIR, "requirements.txt"), """fastapi\nuvicorn[standard]\nsqlalchemy\nasyncpg\nalembic\npython-jose[cryptography]\npasslib[bcrypt]\npython-multipart\npydantic-settings""")
    create_file(os.path.join(BASE_DIR, "Dockerfile"), """FROM python:3.11-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\nCOPY . .\nCMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]""")
    create_file(os.path.join(BASE_DIR, ".env.example"), """DB_USER=postgres\nDB_PASSWORD=postgres\nDB_HOST=localhost\nDB_PORT=5432\nDB_NAME=imagine\nSECRET_KEY=change_this_in_production""")
    create_file(os.path.join(BASE_DIR, "docker-compose.yml"), """version: '3.8'\nservices:\n  db:\n    image: postgres:15\n    environment:\n      POSTGRES_USER: postgres\n      POSTGRES_PASSWORD: postgres\n      POSTGRES_DB: imagine\n    ports:\n      - "5432:5432"\n    volumes:\n      - postgres_data:/var/lib/postgresql/data\n  app:\n    build: .\n    ports:\n      - "8000:8000"\n    depends_on:\n      - db\n    environment:\n      DB_HOST: db\n      DB_USER: postgres\n      DB_PASSWORD: postgres\n      DB_NAME: imagine\n    volumes:\n      - .:/app\nvolumes:\n  postgres_data:""")

    print(f"✅ Backend generated in '{BASE_DIR}' with real fields for Architecture, Structural, BIM.")

if __name__ == "__main__":
    generate_backend()
