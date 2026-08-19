"""
IMAGINE
Application Health Checks
"""

from __future__ import annotations

import importlib
import traceback
from dataclasses import dataclass
from typing import Any


@dataclass
class ModuleHealth:
    """Health information for one application module."""

    name: str
    status: str
    path: str | None = None
    error: str | None = None
    traceback_text: str | None = None


def check_module(
    module_name: str,
) -> ModuleHealth:
    """Safely import and inspect a module."""

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


def run_startup_health_check() -> list[ModuleHealth]:
    """
    Check the core IMAGINE application modules.

    Generative Design is intentionally included because it is
    currently one of the primary application workflows.
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


def health_summary(
    results: list[ModuleHealth],
) -> dict[str, Any]:

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


__all__ = [
    "ModuleHealth",
    "check_module",
    "health_summary",
    "run_startup_health_check",
]