from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# The application creates its SQLAlchemy engine at import time. Give the test
# process an isolated SQLite database before importing application modules.
os.environ.setdefault("DATABASE_URL", "sqlite:///./imagine_ci_test.db")

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.main import app
from database.connection import SessionLocal, engine
from database.models import Base


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Load all model metadata and create the isolated test schema."""
    import projects.model_registry  # noqa: F401
    import architecture.models  # noqa: F401
    import architecture.zoning.models  # noqa: F401
    import architecture.floor_planning.models  # noqa: F401
    import bim.models  # noqa: F401
    import structural.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture()
def client(setup_database):
    with TestClient(app) as c:
        yield c
