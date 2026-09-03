"""IMAGINE project revision service."""

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


def list_revisions(db: Session, project_id: UUID):
    return (
        db.query(Revision)
        .filter(Revision.project_id == project_id)
        .order_by(Revision.id.desc())
        .all()
    )


def update_revision(
    db: Session,
    revision_id: int,
    description: str,
):
    revision = db.get(Revision, revision_id)
    if revision is None:
        return None

    revision.description = description
    db.commit()
    db.refresh(revision)
    return revision


def delete_revision(db: Session, revision_id: int) -> bool:
    revision = db.get(Revision, revision_id)
    if revision is None:
        return False

    db.delete(revision)
    db.commit()
    return True
