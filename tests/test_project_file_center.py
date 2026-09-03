"""Tests for the IMAGINE project file-center domain logic."""
from __future__ import annotations

import hashlib

from modules.platform.file_center import ProjectFile, _category_for, _human_size, _upload_key


def test_file_categories_cover_common_aec_formats() -> None:
    assert _category_for("model.ifc") == "BIM"
    assert _category_for("plan.dwg") == "Drawings"
    assert _category_for("schedule.xlsx") == "Data"
    assert _category_for("report.pdf") == "Documents"
    assert _category_for("photo.jpg") == "Images"
    assert _category_for("unknown.bin") == "Other"


def test_human_size_is_readable() -> None:
    assert _human_size(0) == "0 B"
    assert _human_size(1024) == "1.0 KB"
    assert _human_size(1024 * 1024) == "1.0 MB"


def test_upload_key_uses_content_hash_not_only_filename_and_size() -> None:
    first = b"abc"
    second = b"abd"
    assert _upload_key("same.txt", first) != _upload_key("same.txt", second)
    assert _upload_key("same.txt", first) == (
        "same.txt",
        len(first),
        hashlib.sha256(first).hexdigest(),
    )


def test_project_file_has_stable_file_id() -> None:
    item = ProjectFile(
        name="model.ifc",
        size_bytes=3,
        file_type="IFC",
        uploaded_at="2026-09-03 00:00 UTC",
        project="Demo",
        category="BIM",
        data=b"abc",
    )
    assert item.file_id
    assert len(item.file_id) == 64
    assert item.file_id == hashlib.sha256(b"model.ifc|3|abc").hexdigest()
