"""Project file center for the IMAGINE Streamlit workspace.

The current implementation provides a safe session-backed project-file
workspace. It deliberately keeps uploaded bytes out of the source tree and
uses content hashes for duplicate detection and stable UI actions.

Persistent object storage/database integration can be added behind this
presentation layer without changing the Streamlit workflow.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
from io import BytesIO
from typing import Any

import pandas as pd
import streamlit as st


@dataclass
class ProjectFile:
    name: str
    size_bytes: int
    file_type: str
    uploaded_at: str
    project: str
    category: str
    data: bytes

    @property
    def file_id(self) -> str:
        """Return a deterministic identifier for this uploaded file."""
        payload = f"{self.name}|{self.size_bytes}|".encode("utf-8") + self.data
        return hashlib.sha256(payload).hexdigest()


def _human_size(value: int) -> str:
    size = float(max(0, value))
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{value} B"


def _records() -> list[ProjectFile]:
    return st.session_state.setdefault("project_files", [])


def _category_for(name: str) -> str:
    suffix = name.rsplit(".", 1)[-1].lower() if "." in name else "other"
    mapping = {
        "pdf": "Documents", "docx": "Documents", "doc": "Documents",
        "xlsx": "Data", "xls": "Data", "csv": "Data",
        "ifc": "BIM", "rvt": "BIM", "dwg": "Drawings", "dxf": "Drawings",
        "png": "Images", "jpg": "Images", "jpeg": "Images",
        "json": "Data", "txt": "Documents", "md": "Documents",
    }
    return mapping.get(suffix, "Other")


def _upload_key(name: str, payload: bytes) -> tuple[str, int, str]:
    """Build a collision-resistant key from filename, size and content."""
    return name, len(payload), hashlib.sha256(payload).hexdigest()


def _add_uploads(files: list[Any], project: str, category: str) -> tuple[int, int]:
    """Add uploads and return ``(added, skipped_duplicates)``."""
    records = _records()
    existing = {_upload_key(item.name, item.data) for item in records}
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    added = 0
    skipped = 0

    for uploaded in files:
        payload = uploaded.getvalue()
        key = _upload_key(uploaded.name, payload)
        if key in existing:
            skipped += 1
            continue
        records.append(
            ProjectFile(
                name=uploaded.name,
                size_bytes=len(payload),
                file_type=(uploaded.name.rsplit(".", 1)[-1].upper() if "." in uploaded.name else "FILE"),
                uploaded_at=now,
                project=project.strip() or "Unassigned",
                category=category if category != "Auto" else _category_for(uploaded.name),
                data=payload,
            )
        )
        existing.add(key)
        added += 1
    return added, skipped


def _preview(file: ProjectFile) -> None:
    suffix = file.name.rsplit(".", 1)[-1].lower() if "." in file.name else ""
    if suffix in {"txt", "md", "json", "csv"}:
        try:
            if suffix == "csv":
                frame = pd.read_csv(BytesIO(file.data))
                st.dataframe(frame, use_container_width=True, hide_index=True)
            else:
                text = file.data.decode("utf-8", errors="replace")
                st.code(text[:12000], language="json" if suffix == "json" else None)
        except Exception as exc:
            st.warning(f"Preview unavailable: {type(exc).__name__}: {exc}")
    elif suffix in {"png", "jpg", "jpeg"}:
        st.image(file.data, use_container_width=True)
    else:
        st.info("Preview is not rendered for this file type. Use Download to open it in the appropriate application.")


def _delete_file(file_id: str) -> bool:
    records = _records()
    before = len(records)
    records[:] = [item for item in records if item.file_id != file_id]
    return len(records) != before


def render() -> None:
    st.subheader("Project File Center")
    st.caption("Upload, organize, inspect and download project information from one workspace.")

    records = _records()
    upload_tab, library_tab, preview_tab = st.tabs(["Upload", "Library", "Preview"])

    with upload_tab:
        project = st.text_input("Project", value=st.session_state.get("selected_project_name") or "Unassigned", key="file_project")
        category = st.selectbox("Category", ["Auto", "Documents", "Drawings", "BIM", "Data", "Images", "Other"], key="file_category")
        uploads = st.file_uploader(
            "Add project files",
            type=["pdf", "doc", "docx", "txt", "md", "csv", "xls", "xlsx", "ifc", "dwg", "dxf", "rvt", "json", "png", "jpg", "jpeg"],
            accept_multiple_files=True,
            key="project_file_uploader",
            help="Uploads are held in the current Streamlit session. Persistent storage can be connected later without changing this UI contract.",
        )
        if uploads:
            added, skipped = _add_uploads(uploads, project, category)
            if added:
                st.success(f"{added} file(s) added to the workspace library.")
            if skipped:
                st.info(f"{skipped} duplicate file(s) were skipped.")

    with library_tab:
        if not records:
            st.info("No files have been added to this workspace yet.")
        else:
            categories = sorted({item.category for item in records})
            filter_category = st.selectbox("Category filter", ["All categories", *categories], key="file_category_filter")
            query = st.text_input("Filter files", placeholder="Search by filename, project or category", key="file_query")
            filtered = [
                item for item in records
                if (filter_category == "All categories" or item.category == filter_category)
                and (not query or query.casefold() in f"{item.name} {item.project} {item.category}".casefold())
            ]
            st.caption(f"{len(filtered)} of {len(records)} file(s) shown")
            for item in filtered:
                with st.container(border=True):
                    left, mid, right = st.columns([2.8, 1.2, 1.5])
                    with left:
                        st.markdown(f"**{item.name}**")
                        st.caption(f"{item.category} · {item.file_type} · {item.project} · {item.uploaded_at}")
                    with mid:
                        st.metric("Size", _human_size(item.size_bytes))
                    with right:
                        download_col, delete_col = st.columns(2)
                        with download_col:
                            st.download_button("Download", item.data, item.name, key=f"download_file_{item.file_id}", use_container_width=True)
                        with delete_col:
                            if st.button("Remove", key=f"delete_file_{item.file_id}", use_container_width=True):
                                _delete_file(item.file_id)
                                st.rerun()

            table = pd.DataFrame([
                {"File": item.name, "Type": item.file_type, "Category": item.category, "Project": item.project, "Size": _human_size(item.size_bytes), "Uploaded": item.uploaded_at}
                for item in filtered
            ])
            with st.expander("Table view", expanded=False):
                st.dataframe(table, use_container_width=True, hide_index=True)

    with preview_tab:
        if not records:
            st.info("Add a file first to enable preview.")
        else:
            selected_id = st.selectbox(
                "Select file",
                [item.file_id for item in records],
                format_func=lambda value: next(item.name for item in records if item.file_id == value),
                key="file_preview_id",
            )
            selected = next(item for item in records if item.file_id == selected_id)
            st.markdown(f"### {selected.name}")
            st.caption(f"{selected.category} · {selected.file_type} · {_human_size(selected.size_bytes)} · {selected.project}")
            _preview(selected)
            st.download_button("Download selected file", selected.data, selected.name, key="download_selected_file")

    if records:
        metadata = pd.DataFrame([{k: v for k, v in asdict(item).items() if k != "data"} | {"File ID": item.file_id} for item in records])
        st.download_button("Export file manifest", metadata.to_csv(index=False).encode("utf-8"), "imagine_file_manifest.csv", "text/csv", key="export_file_manifest")


__all__ = ["ProjectFile", "render", "_category_for", "_human_size", "_upload_key"]
