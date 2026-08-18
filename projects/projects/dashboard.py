from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Iterable, Mapping, Sequence


ACTIVE_STATUSES = {"active"}
COMPLETED_STATUSES = {"completed"}
OPEN_RFI_STATUSES = {
    "open",
    "pending",
    "submitted",
    "in_progress",
}


@dataclass(frozen=True)
class ProjectDashboardMetrics:
    total_projects: int = 0
    active_projects: int = 0
    planning_projects: int = 0
    on_hold_projects: int = 0
    completed_projects: int = 0

    total_budget: float = 0.0
    average_progress: float = 0.0

    open_rfis: int = 0
    total_rfis: int = 0

    activity_count: int = 0
    recent_activity: list[dict[str, Any]] = field(default_factory=list)

    project_progress: list[dict[str, Any]] = field(default_factory=list)


def _value(
    item: Any,
    key: str,
    default: Any = None,
) -> Any:
    """
    Read a value from either a SQLAlchemy model or a dictionary.
    """
    if isinstance(item, Mapping):
        return item.get(key, default)

    return getattr(item, key, default)


def _normalise_status(value: Any) -> str:
    if value is None:
        return ""

    raw = getattr(value, "value", value)

    return str(raw).strip().lower()


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default

        return float(value)

    except (TypeError, ValueError):
        return default


def _project_name(project: Any) -> str:
    return str(
        _value(
            project,
            "name",
            _value(project, "Name", "Unnamed Project"),
        )
    )


def _project_status(project: Any) -> str:
    return _normalise_status(
        _value(
            project,
            "status",
            _value(project, "Status", ""),
        )
    )


def _project_budget(project: Any) -> float:
    """
    Project budget is stored in the Projects module.

    Legacy session-state data used 'Budget (M USD)'.
    Database projects use 'budget'.
    """
    database_value = _value(project, "budget")

    if database_value is not None:
        return _safe_float(database_value)

    legacy_value = _value(project, "Budget (M USD)", 0)

    return _safe_float(legacy_value) * 1_000_000


def _project_progress(project: Any) -> float:
    """
    Return project completion percentage.

    Legacy prototype data uses 'Progress %'.
    Database projects use 'progress'.
    """
    database_value = _value(project, "progress")

    if database_value is not None:
        return max(0.0, min(100.0, _safe_float(database_value)))

    legacy_value = _value(project, "Progress %", 0)

    return max(0.0, min(100.0, _safe_float(legacy_value)))


def aggregate_project_metrics(
    projects: Iterable[Any],
    rfis: Iterable[Any] | None = None,
    activities: Iterable[Any] | None = None,
) -> ProjectDashboardMetrics:
    """
    Aggregate project-domain information for the Dashboard.

    This function intentionally contains no Streamlit code.
    It can therefore be unit tested independently.
    """

    project_list = list(projects)

    total_projects = len(project_list)

    active_projects = 0
    planning_projects = 0
    on_hold_projects = 0
    completed_projects = 0

    total_budget = 0.0
    progress_values: list[float] = []

    project_progress: list[dict[str, Any]] = []

    for project in project_list:
        status = _project_status(project)
        budget = _project_budget(project)
        progress = _project_progress(project)

        total_budget += budget
        progress_values.append(progress)

        if status in ACTIVE_STATUSES:
            active_projects += 1
        elif status == "planning":
            planning_projects += 1
        elif status == "on_hold":
            on_hold_projects += 1
        elif status in COMPLETED_STATUSES:
            completed_projects += 1

        project_progress.append(
            {
                "ID": _value(project, "id", _value(project, "ID")),
                "Name": _project_name(project),
                "Status": status.replace("_", " ").title(),
                "Budget (USD)": budget,
                "Progress %": progress,
            }
        )

    average_progress = (
        sum(progress_values) / len(progress_values)
        if progress_values
        else 0.0
    )

    rfi_list = list(rfis or [])

    total_rfis = len(rfi_list)

    open_rfis = sum(
        1
        for rfi in rfi_list
        if _normalise_status(_value(rfi, "status")) in OPEN_RFI_STATUSES
    )

    activity_list = list(activities or [])

    activity_list.sort(
        key=lambda item: _activity_datetime(item),
        reverse=True,
    )

    return ProjectDashboardMetrics(
        total_projects=total_projects,
        active_projects=active_projects,
        planning_projects=planning_projects,
        on_hold_projects=on_hold_projects,
        completed_projects=completed_projects,
        total_budget=total_budget,
        average_progress=average_progress,
        open_rfis=open_rfis,
        total_rfis=total_rfis,
        activity_count=len(activity_list),
        recent_activity=[
            _activity_to_dict(activity)
            for activity in activity_list[:10]
        ],
        project_progress=project_progress,
    )


def _activity_datetime(activity: Any) -> datetime:
    value = _value(activity, "created_at")

    if isinstance(value, datetime):
        return value

    return datetime.min


def _activity_to_dict(activity: Any) -> dict[str, Any]:
    created_at = _value(activity, "created_at")

    project = _value(activity, "project")
    project_name = (
        _value(project, "name")
        if project is not None
        else None
    )

    description = _value(activity, "description")

    if description:
        action = description
    else:
        action = activity.__class__.__name__.replace("_", " ")

    return {
        "Time": created_at,
        "Project": project_name or "Project",
        "Action": action,
        "Type": activity.__class__.__name__,
    }


def dashboard_dataframe(metrics: ProjectDashboardMetrics):
    """
    Convert project health data into a DataFrame for Plotly/Streamlit.
    """
    import pandas as pd

    return pd.DataFrame(metrics.project_progress)


def dashboard_summary(metrics: ProjectDashboardMetrics) -> dict[str, Any]:
    """
    Serialize Dashboard metrics into a simple dictionary.

    Useful for APIs, tests, logging, and future dashboard endpoints.
    """
    return {
        "total_projects": metrics.total_projects,
        "active_projects": metrics.active_projects,
        "planning_projects": metrics.planning_projects,
        "on_hold_projects": metrics.on_hold_projects,
        "completed_projects": metrics.completed_projects,
        "total_budget": metrics.total_budget,
        "average_progress": metrics.average_progress,
        "open_rfis": metrics.open_rfis,
        "total_rfis": metrics.total_rfis,
        "activity_count": metrics.activity_count,
    }