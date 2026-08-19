"""
IMAGINE Projects SQLAlchemy model registry.

Importing this module guarantees that all Projects-related
relationship targets are registered with the shared SQLAlchemy
declarative registry before any ORM query is executed.
"""

from __future__ import annotations

# Core database relationship targets.
from database.models import Organization, User  # noqa: F401

# Projects relationship targets.
from projects.approvals.models import Approval  # noqa: F401
from projects.revisions.models import Revision  # noqa: F401

# Root Projects model must be imported after its relationship
# targets are available.
from projects.projects.models import Project  # noqa: F401


__all__ = [
    "Organization",
    "User",
    "Approval",
    "Revision",
    "Project",
]