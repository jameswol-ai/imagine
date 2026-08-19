from __future__ import annotations

import asyncio
import traceback
from typing import Any, Awaitable, Callable

import streamlit as st

from database.connection import AsyncSessionLocal

# ============================================================
# PROJECT MODEL REGISTRATION
# ============================================================
#
# IMPORTANT:
# This import must happen before ProjectService executes any
# SQLAlchemy query.
#
# The registry imports:
#   Organization
#   User
#   Approval
#   Revision
#   Project
#
# in the required dependency order.
# ============================================================

from projects.model_registry import Project  # noqa: F401

# ============================================================
# PROJECT SERVICE
# ============================================================

from projects.projects.service import ProjectService

# ============================================================
# PROJECT SCHEMAS
# ============================================================

from projects.projects.schemas import (
    ProjectCreate,
    ProjectUpdate,
)