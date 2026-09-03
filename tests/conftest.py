from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Make the repository root importable when pytest is invoked from any working directory.
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.main import app
from database.connection import SessionLocal, engine
from database.models import Base


@pytest.fixture(scope="session")
def test_db_path(tmp_path_factory):
    return tmp_path_factory.mktemp("data") / "test_imagine.db"


@pytest.fixture(scope="session")
def setup_database(tmp_path_factory):
    db_file = tmp_path_factory.mktemp("db") / "test_imagine.db"
    db_url = f"sqlite:///{db_file}"
    os.environ["DATABASE_URL"] = db_url

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
