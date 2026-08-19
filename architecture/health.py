"""
IMAGINE
Application Health Checks

Provides safe, isolated import checks for application modules.
"""

from __future__ import annotations

import importlib
import traceback
from dataclasses import dataclass
from typing import Any


# ============================================================
# DATA MODEL
# ============================================================


@dataclass
class ModuleHealth:
    """Health information for one application module."""

    name: str
    status: str
    path: str | None = None
    error: str | None = None
    traceback_text: str | None = None


# ============================================================
# MODULE CHECK
# ============================================================


def check_module(
    module_name: str,
) -> ModuleHealth:
    """
    Safely import one module.

    Returns a ModuleHealth object instead of allowing an
    import exception to crash the caller.
    """

    try:
        module = importlib.import_module(
            module_name
        )

        return ModuleHealth(
            name=module_name,
            status="ok",
            path=getattr(
                module,
                "__file__",
                None,
            ),
        )

    except Exception as exc:

        return ModuleHealth(
            name=module_name,
            status="error",
            error=str(exc),
            traceback_text=traceback.format_exc(),
        )


# ============================================================
# STARTUP HEALTH CHECK
# ============================================================


def run_startup_health_check() -> list[ModuleHealth]:
    """
    Check the core Generative Design dependency chain.

    The order is intentional:

        schemas
            ↓
        constraints
            ↓
        generator
            ↓
        service
            ↓
        ui
    """

    modules = [
        "architecture.generative_design.schemas",
        "architecture.generative_design.constraints",
        "architecture.generative_design.generator",
        "architecture.generative_design.service",
        "architecture.generative_design.ui",
    ]

    return [
        check_module(module)
        for module in modules
    ]


# ============================================================
# SUMMARY
# ============================================================


def health_summary(
    results: list[ModuleHealth],
) -> dict[str, Any]:
    """Return aggregate health information."""

    total = len(results)

    healthy = sum(
        result.status == "ok"
        for result in results
    )

    failed = total - healthy

    return {
        "total": total,
        "healthy": healthy,
        "failed": failed,
        "status": (
            "healthy"
            if failed == 0
            else "degraded"
        ),
    }


# ============================================================
# PUBLIC API
# ============================================================


__all__ = [
    "ModuleHealth",
    "check_module",
    "health_summary",
    "run_startup_health_check",
]