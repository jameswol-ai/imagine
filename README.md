# IMAGINE

Integrated AEC Engine for architecture, structural engineering, BIM, MEP, costing, construction, documents, AI, analytics, regional compliance, integrations and digital-twin workflows.

## Application

The primary Streamlit entrypoint is `streamlit_app.py`.

The application uses a searchable enterprise module registry instead of a long static sidebar list. Modules are lazy-loaded so an isolated renderer failure does not take down the application.

## Module execution model

There are two supported renderer levels:

1. Specialist renderer: a module has its own domain models, services, calculations and Streamlit UI.
2. Functional workspace: a registered module that is still being upgraded has a domain-aware input form, deterministic preliminary calculation where applicable, validation, database persistence, session fallback and CSV/JSON export.

The functional workspace is an execution layer, not a substitute for certified engineering design software. Engineering results must be independently reviewed and checked against the applicable project code, National Annex, design assumptions and professional requirements before use on a live project.

## Database

The application uses SQLAlchemy through `database.connection`. The shared `ModuleWorkspaceRecord` model provides portable persistence for enterprise workspaces, while specialist modules can use their own normalized domain tables.

`database.bootstrap.ensure_schema()` creates missing metadata tables for development and controlled first-run deployments.

## UI policy

The application UI is emoji-free. `modules.ui_sanitizer` provides a central runtime safeguard for specialist renderers that still contain legacy emoji glyphs.

The sidebar remains compact and searchable. The Streamlit default page navigation is disabled through `.streamlit/config.toml`.

## Testing

The repository includes registry validation, Streamlit shell contract tests, module renderer contract tests, database model tests and functional workspace calculation tests.

Run locally with:

```bash
python -m compileall .
pytest -q
```

## Deployment

Streamlit Community Cloud can deploy the repository using `streamlit_app.py` as the application entrypoint. Runtime configuration is stored in `.streamlit/config.toml`; secrets should be supplied through the deployment environment and never committed.

## Development roadmap

The functional workspace keeps every registered route executable while specialist implementations are completed incrementally. The next implementation layers should replace the functional workspace with certified domain services for structural Eurocodes, BIM coordination, MEP sizing, cost management, construction controls, document workflows, regional rules and external integrations.
