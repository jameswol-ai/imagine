from typing import Generator
from database.connection import get_db

def get_db_dependency() -> Generator:
    db = get_db()
    try:
        yield db
    finally:
        db.close()
