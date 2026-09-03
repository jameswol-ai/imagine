"""Central SQLAlchemy model registry for the Projects domain."""
from __future__ import annotations

from database.models.organization import Organization  # noqa: F401
from database.models.user import User  # noqa: F401
from projects.approvals.models import Approval  # noqa: F401
from projects.revisions.models import Revision  # noqa: F401
from projects.workflows.models import Workflow  # noqa: F401
from projects.projects.models import Project  # noqa: F401

__all__ = ["Organization", "User", "Approval", "Revision", "Workflow", "Project"]
