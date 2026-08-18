import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from app.main import app
from database.connection import engine, SessionLocal
from database.models import Base
from sqlalchemy.orm import sessionmaker

# Use a temporary SQLite DB for tests
TEST_DB = "sqlite:///./test_imagine.db"

@pytest.fixture(scope="session")
def test_db_path(tmp_path_factory):
    return tmp_path_factory.mktemp("data")

@pytest.fixture(scope="session")
def setup_database(tmp_path_factory):
    # create a fresh sqlite file in tmp
    db_file = tmp_path_factory.mktemp("db") / "test_imagine.db"
    db_url = f"sqlite:///{db_file}"
    os.environ["DATABASE_URL"] = db_url

    # re-import engine/session if necessary or create tables directly
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
