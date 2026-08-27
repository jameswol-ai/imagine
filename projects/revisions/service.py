"""
IMAGINE Project Revisions service.

Uses the central Projects model registry so Revision and its
Project/User relationship targets are registered before ORM use.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from projects.model_registry import Revision


def create_revision(
    db: Session,
    project_id: UUID,
    description: str,
    created_by: int,
):
    revision = Revision(
        project_id=project_id,
        description=description,
        created_by=created_by,
    )

    db.add(revision)
    db.commit()
    db.refresh(revision)

    return revision


def list_revisions(
    db: Session,
    project_id: UUID,
):
    return (
        db.query(Revision)
        .filter(
            Revision.project_id == project_id
        )
        .all()
    )