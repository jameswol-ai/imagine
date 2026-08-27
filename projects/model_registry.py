"""
IMAGINE Projects SQLAlchemy model registry.

All models participating in the Projects relationship graph are
imported here before any Projects service performs an ORM query.

This prevents SQLAlchemy from encountering unresolved string
relationship targets such as "Approval" and "Revision".
"""

from __future__ import annotations


# ============================================================
# CORE DATABASE MODELS
# ============================================================

from database.models.organization import Organization  # noqa: F401
from database.models.user import User  # noqa: F401


# ============================================================
# PROJECT DOMAIN MODELS
# ============================================================

# Relationship targets must be imported before Project.
from projects.approvals.models import Approval  # noqa: F401
from projects.revisions.models import Revision  # noqa: F401

# Project is deliberately imported last.
from projects.projects.models import Project  # noqa: F401


__all__ = [
    "Organization",
    "User",
    "Approval",
    "Revision",
    "Project",
]