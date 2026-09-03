from modules.construction.progress_tracking import ProgressTrackingService
from modules.construction.rfis import RFI, RFIEngine
from modules.construction.snagging import SnaggingService


def test_progress_statuses() -> None:
    assert ProgressTrackingService.schedule_status(0) == "On Track"
    assert ProgressTrackingService.schedule_status(-5) == "Minor Delay"
    assert ProgressTrackingService.schedule_status(-11) == "Critical Delay"


def test_rfi_counts_open_and_overdue() -> None:
    result = RFIEngine().run([RFI("RFI-1", "Question", "Open", "High", "2000-01-01"), RFI("RFI-2", "Answer", "Answered", "Normal", "2000-01-01")])
    assert result["count"] == 2
    assert result["open"] == 1
    assert result["overdue"] == 1


def test_snag_lifecycle() -> None:
    snag = SnaggingService.create_snag("Room 1", "Door adjustment", "High")
    assert snag["status"] == "Open"
    closed = SnaggingService.close_snag(snag, "Engineer")
    assert closed["status"] == "Closed"
    assert closed["closed_by"] == "Engineer"
