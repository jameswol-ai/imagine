"""IMAGINE project approval service."""

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
        status="pending",
    )
    db.add(approval)
    db.commit()
    db.refresh(approval)
    return approval


def list_approvals(db: Session, project_id: UUID):
    return (
        db.query(Approval)
        .filter(Approval.project_id == project_id)
        .order_by(Approval.id.desc())
        .all()
    )


def update_approval(
    db: Session,
    approval_id: int,
    status: str,
    comment: Optional[str] = None,
):
    approval = db.get(Approval, approval_id)
    if approval is None:
        return None

    approval.status = status
    approval.comment = comment
    db.commit()
    db.refresh(approval)
    return approval


def delete_approval(db: Session, approval_id: int) -> bool:
    approval = db.get(Approval, approval_id)
    if approval is None:
        return False

    db.delete(approval)
    db.commit()
    return True
