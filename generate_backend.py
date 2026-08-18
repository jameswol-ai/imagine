# generate_backend.py
import os
import shutil

BASE_DIR = "IMAGINE"

# Define all sub-packages and files
MODULES = {
    "core": {
        "authentication": ["models", "schemas", "service", "routes"],
        "authorization": ["models", "schemas", "service", "routes"],
        "organizations": ["models", "schemas", "service", "routes"],
        "users": ["models", "schemas", "service", "routes"],
        "roles": ["models", "schemas", "service", "routes"],
        "permissions": ["models", "schemas", "service", "routes"],
        "audit": ["models", "schemas", "service", "routes"],
        "notifications": ["models", "schemas", "service", "routes"],
    },
    "projects": {
        "projects": ["models", "schemas", "service", "routes"],
        "approvals": ["models", "schemas", "service", "routes"],
        "revisions": ["models", "schemas", "service", "routes"],
        "workflows": ["models", "schemas", "service", "routes"],
        "governance": ["models", "schemas", "service", "routes"],
    },
    "bim": {
        "buildings": ["models", "schemas", "service", "routes"],
        "storeys": ["models", "schemas", "service", "routes"],
        "spaces": ["models", "schemas", "service", "routes"],
        "elements": ["models", "schemas", "service", "routes"],
        "ifc": ["models", "schemas", "service", "routes"],
        "cobie": ["models", "schemas", "service", "routes"],
        "digital_twin": ["models", "schemas", "service", "routes"],
    },
    "architecture": {
        "generative_design": ["models", "schemas", "service", "routes"],
        "zoning": ["models", "schemas", "service", "routes"],
        "site_planning": ["models", "schemas", "service", "routes"],
        "floor_planning": ["models", "schemas", "service", "routes"],
        "room_programming": ["models", "schemas", "service", "routes"],
        "compliance": ["models", "schemas", "service", "routes"],
    },
    "structural": {
        "eurocode": ["models", "schemas", "service", "routes"],
        "beam_design": ["models", "schemas", "service", "routes"],
        "column_design": ["models", "schemas", "service", "routes"],
        "slab_design": ["models", "schemas", "service", "routes"],
        "foundation_design": ["models", "schemas", "service", "routes"],
        "retaining_walls": ["models", "schemas", "service", "routes"],
        "steel_connections": ["models", "schemas", "service", "routes"],
        "finite_element_analysis": ["models", "schemas", "service", "routes"],
    },
    "mep": {
        "mechanical": ["models", "schemas", "service", "routes"],
        "electrical": ["models", "schemas", "service", "routes"],
        "plumbing": ["models", "schemas", "service", "routes"],
    },
    "costing": {
        "boq": ["models", "schemas", "service", "routes"],
        "quantity_takeoff": ["models", "schemas", "service", "routes"],
        "procurement": ["models", "schemas", "service", "routes"],
        "forex": ["models", "schemas", "service", "routes"],
        "inflation": ["models", "schemas", "service", "routes"],
        "risk_analysis": ["models", "schemas", "service", "routes"],
        "cashflow": ["models", "schemas", "service", "routes"],
    },
    "construction": {
        "planning": ["models", "schemas", "service", "routes"],
        "scheduling": ["models", "schemas", "service", "routes"],
        "rfis": ["models", "schemas", "service", "routes"],
        "submittals": ["models", "schemas", "service", "routes"],
        "variations": ["models", "schemas", "service", "routes"],
        "snagging": ["models", "schemas", "service", "routes"],
        "progress_tracking": ["models", "schemas", "service", "routes"],
        "site_diaries": ["models", "schemas", "service", "routes"],
    },
    "documents": {
        "drawing_management": ["models", "schemas", "service", "routes"],
        "specifications": ["models", "schemas", "service", "routes"],
        "contracts": ["models", "schemas", "service", "routes"],
        "reports": ["models", "schemas", "service", "routes"],
        "version_control": ["models", "schemas", "service", "routes"],
        "archives": ["models", "schemas", "service", "routes"],
    },
    "ai": {
        "imagine_architect": ["models", "schemas", "service", "routes"],
        "imagine_engineer": ["models", "schemas", "service", "routes"],
        "imagine_mep": ["models", "schemas", "service", "routes"],
        "imagine_qs": ["models", "schemas", "service", "routes"],
        "imagine_pm": ["models", "schemas", "service", "routes"],
        "vector_store": ["models", "schemas", "service", "routes"],
        "rag": ["models", "schemas", "service", "routes"],
        "prompt_library": ["models", "schemas", "service", "routes"],
    },
    "analytics": {
        "dashboards": ["models", "schemas", "service", "routes"],
        "kpis": ["models", "schemas", "service", "routes"],
        "portfolio": ["models", "schemas", "service", "routes"],
        "forecasting": ["models", "schemas", "service", "routes"],
        "reporting": ["models", "schemas", "service", "routes"],
    },
    "regional": {
        "uganda": ["models", "schemas", "service", "routes"],
        "kenya": ["models", "schemas", "service", "routes"],
        "tanzania": ["models", "schemas", "service", "routes"],
        "rwanda": ["models", "schemas", "service", "routes"],
        "south_sudan": ["models", "schemas", "service", "routes"],
        "codes": ["models", "schemas", "service", "routes"],
        "zoning_laws": ["models", "schemas", "service", "routes"],
    },
    "integrations": {
        "microsoft": ["models", "schemas", "service", "routes"],
        "autocad": ["models", "schemas", "service", "routes"],
        "revit": ["models", "schemas", "service", "routes"],
        "archicad": ["models", "schemas", "service", "routes"],
        "tekla": ["models", "schemas", "service", "routes"],
        "ifcopenshell": ["models", "schemas", "service", "routes"],
        "arcgis": ["models", "schemas", "service", "routes"],
        "azure": ["models", "schemas", "service", "routes"],
        "mapbox": ["models", "schemas", "service", "routes"],
    },
    "digital_twin": {
        "assets": ["models", "schemas", "service", "routes"],
        "sensors": ["models", "schemas", "service", "routes"],
        "telemetry": ["models", "schemas", "service", "routes"],
        "energy": ["models", "schemas", "service", "routes"],
        "maintenance": ["models", "schemas", "service", "routes"],
        "predictive_ai": ["models", "schemas", "service", "routes"],
    },
}

# Additional top-level folders
TOP_FOLDERS = [
    "app",
    "database",
    "tests",
    "deployment/docker",
    "deployment/kubernetes",
    "deployment/github_actions",
    "deployment/azure",
    "docs/architecture",
    "docs/api",
    "docs/database",
    "docs/engineering",
    "docs/user_manuals",
]

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)

def generate_module_files(base, module_name, files):
    # Create __init__.py
    create_file(os.path.join(base, module_name, "__init__.py"), "")
    for file in files:
        file_path = os.path.join(base, module_name, f"{file}.py")
        # Generate boilerplate content based on file type
        if file == "models":
            content = f"""from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from database.models.base import BaseModel

class {module_name.capitalize()}(BaseModel):
    __tablename__ = "{module_name}"
    # Add your fields here
    name = Column(String, nullable=True)
    # ... other fields
"""
        elif file == "schemas":
            content = f"""from pydantic import BaseModel, UUID4
from typing import Optional

class {module_name.capitalize()}Base(BaseModel):
    name: Optional[str] = None

class {module_name.capitalize()}Create({module_name.capitalize()}Base):
    pass

class {module_name.capitalize()}Update(BaseModel):
    name: Optional[str] = None

class {module_name.capitalize()}Response({module_name.capitalize()}Base):
    id: UUID4
"""
        elif file == "service":
            content = f"""from sqlalchemy.ext.asyncio import AsyncSession
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
        elif file == "routes":
            content = f"""from fastapi import APIRouter, Depends, HTTPException, status
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
        create_file(file_path, content)

def generate_backend():
    # Create base dir
    os.makedirs(BASE_DIR, exist_ok=True)

    # Create top-level app files
    app_files = {
        "app/main.py": """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.settings import settings
from app.dependencies import lifespan
# Import routers here

app = FastAPI(title=settings.APP_NAME, version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/")
async def root():
    return {"message": "IMAGINE API"}

# Include routers later
""",
        "app/config.py": """from .settings import settings

class AppConfig:
    API_PREFIX = settings.API_V1_PREFIX
    PROJECT_NAME = settings.APP_NAME
    DEBUG = settings.DEBUG

config = AppConfig()
""",
        "app/settings.py": """from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "IMAGINE"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "imagine"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"

settings = Settings()
""",
        "app/dependencies.py": """from contextlib import asynccontextmanager
from fastapi import FastAPI
from database.connection import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown
    await engine.dispose()
""",
    }
    for path, content in app_files.items():
        create_file(os.path.join(BASE_DIR, path), content)

    # Create database files
    db_files = {
        "database/connection.py": """from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.settings import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

Base = declarative_base()
""",
        "database/models/base.py": """from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from database.connection import Base
import uuid

class BaseModel(Base):
    __abstract__ = True
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
""",
        "database/models/__init__.py": "",
        "database/repositories/base.py": """from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class BaseRepository:
    def __init__(self, model):
        self.model = model

    async def get(self, db: AsyncSession, id: str):
        return await db.get(self.model, id)

    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100):
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()
""",
        "database/repositories/__init__.py": "",
        "database/seeders/__init__.py": "",
        "database/migrations/alembic.ini": """[alembic]
script_location = migrations
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = postgresql+asyncpg://postgres:postgres@localhost/imagine
""",
        "database/migrations/env.py": """from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from database.connection import Base
from app.settings import settings
import asyncio

config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata

def run_migrations_offline():
    context.configure(url=settings.DATABASE_URL, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    connectable = create_async_engine(settings.DATABASE_URL)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
""",
        "database/migrations/versions/.keep": "",
    }
    for path, content in db_files.items():
        create_file(os.path.join(BASE_DIR, path), content)

    # Generate module files
    for module, submodules in MODULES.items():
        base_path = os.path.join(BASE_DIR, module)
        for sub, files in submodules.items():
            generate_module_files(base_path, sub, files)

    # Create top-level folders
    for folder in TOP_FOLDERS:
        os.makedirs(os.path.join(BASE_DIR, folder), exist_ok=True)
        # Create __init__.py in each
        init_path = os.path.join(BASE_DIR, folder, "__init__.py")
        if not os.path.exists(init_path):
            create_file(init_path, "")

    # Additional files: requirements.txt, Dockerfile, .env.example
    create_file(os.path.join(BASE_DIR, "requirements.txt"), """fastapi
uvicorn[standard]
sqlalchemy
asyncpg
alembic
python-jose[cryptography]
passlib[bcrypt]
python-multipart
pydantic-settings
""")
    create_file(os.path.join(BASE_DIR, "Dockerfile"), """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
""")
    create_file(os.path.join(BASE_DIR, ".env.example"), """DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=imagine
SECRET_KEY=change_this_in_production
""")
    create_file(os.path.join(BASE_DIR, "docker-compose.yml"), """version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: imagine
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
  app:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      DB_HOST: db
      DB_USER: postgres
      DB_PASSWORD: postgres
      DB_NAME: imagine
    volumes:
      - .:/app
volumes:
  postgres_data:
""")

    print(f"✅ Backend generated in '{BASE_DIR}'")

if __name__ == "__main__":
    generate_backend()