"""
IMAGINE Project Approvals service.

Uses the central Projects model registry so Approval, Revision,
Project, User, and Organization relationship targets are all
registered before SQLAlchemy mapper configuration.
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from projects.model_registry import Approval


def create_approval(
    db: Session,
    project_id: UUID,
    approver_id: int,
    comment: Optional[str] = None,
):
    approval = Approval(
        project_id=project_id,
        approver_id=approver_id,
        comment=comment,
    )

    db.add(approval)
    db.commit()
    db.refresh(approval)

    return approval


def list_approvals(
    db: Session,
    project_id: UUID,
):
    return (
        db.query(Approval)
        .filter(
            Approval.project_id == project_id
        )
        .all()
    )