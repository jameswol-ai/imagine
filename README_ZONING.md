# IMAGINE Architecture: Zoning

Production-oriented first Architecture module.

## Includes

- SQLAlchemy zoning model
- Pydantic v2 schemas
- Repository
- Service layer
- FastAPI CRUD routes
- Seed data
- Streamlit CRUD UI
- Unit tests
- PostgreSQL migration SQL

## Database

Apply:

`database/migrations/sql/001_create_zoning_rules.sql`

after the existing `projects` table has been created.

The repository currently contains only a minimal `alembic.ini` placeholder, so this module does not invent an Alembic revision chain.

## Streamlit

Add:

`from architecture.zoning.ui import render_zoning`

Then replace the existing Architecture/Zoning tab body with:

`render_zoning()`

Keep all other Architecture tabs unchanged.

## Seed

Call:

`await seed_zoning(db)`

from the application's database seeding/startup workflow.

The seed records use `project_id = NULL`, making them reusable zoning templates.

## Tests

Run:

`pytest -q tests/unit/test_zoning_schemas.py tests/unit/test_zoning_service.py tests/unit/test_zoning_repository.py`

The tests are deliberately independent of a live PostgreSQL instance.
