"""
IMAGINE Projects SQLAlchemy model registry.

The Projects models contain cross-module SQLAlchemy relationships.
All relationship targets are imported here before Project is used
by any service/query.
"""

from __future__ import annotations

# Core database models referenced by Projects.
from database.models.organization import Organization  # noqa: F401
from database.models.user import User  # noqa: F401

# Projects relationship targets.
#
# Approval and Revision must be imported before Project so that
# SQLAlchemy can resolve Project.approvals and Project.revisions
# when mapper configuration occurs.
from projects.approvals.models import Approval  # noqa: F401
from projects.revisions.models import Revision  # noqa: F401

# Import Project last.
from projects.projects.models import Project  # noqa: F401


__all__ = [
    "Organization",
    "User",
    "Approval",
    "Revision",
    "Project",
]