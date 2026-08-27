from sqlalchemy.orm import Session
from .models import Approval


def create_approval(
    db: Session,
    project_id: int,
    approver_id: int,
    comment: str = None,
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
    project_id: int,
):
    return (
        db.query(Approval)
        .filter(
            Approval.project_id == project_id
        )
        .all()
    )