"""Project file center for the IMAGINE Streamlit workspace.

This is a session-safe presentation layer for project files. It keeps file
metadata visible, supports preview/download for common text and tabular files,
and avoids writing arbitrary uploads to the application package.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
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


def _human_size(value: int) -> str:
    size = float(value)
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


def _add_uploads(files: list[Any], project: str, category: str) -> None:
    records = _records()
    existing = {(item.name, item.size_bytes) for item in records}
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    for uploaded in files:
        payload = uploaded.getvalue()
        key = (uploaded.name, len(payload))
        if key in existing:
            continue
        records.append(
            ProjectFile(
                name=uploaded.name,
                size_bytes=len(payload),
                file_type=(uploaded.name.rsplit(".", 1)[-1].upper() if "." in uploaded.name else "FILE"),
                uploaded_at=now,
                project=project,
                category=category if category != "Auto" else _category_for(uploaded.name),
                data=payload,
            )
        )


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
        st.info("Preview is not rendered for this file type. Use Download to open it in the appropriate desktop application.")


def render() -> None:
    st.subheader("Project File Center")
    st.caption("A structured workspace for uploading, reviewing, filtering and exporting project files.")

    upload_tab, library_tab, preview_tab = st.tabs(["Upload", "Library", "Preview"])

    with upload_tab:
        project = st.text_input("Project", value=st.session_state.get("selected_project_name") or "Unassigned")
        category = st.selectbox("Category", ["Auto", "Documents", "Drawings", "BIM", "Data", "Images", "Other"])
        uploads = st.file_uploader(
            "Add project files",
            type=["pdf", "doc", "docx", "txt", "md", "csv", "xls", "xlsx", "ifc", "dwg", "dxf", "rvt", "json", "png", "jpg", "jpeg"],
            accept_multiple_files=True,
            help="Files are held in the current Streamlit session unless a persistent storage connector is configured.",
        )
        if uploads:
            _add_uploads(uploads, project, category)
            st.success(f"{len(uploads)} file(s) processed into the workspace library.")

    with library_tab:
        records = _records()
        if not records:
            st.info("No files have been added to this workspace yet.")
        else:
            categories = sorted({item.category for item in records})
            filter_category = st.selectbox("Category filter", ["All categories", *categories], key="file_category_filter")
            query = st.text_input("Filter files", placeholder="Search by filename or project", key="file_query")
            filtered = [
                item for item in records
                if (filter_category == "All categories" or item.category == filter_category)
                and (not query or query.casefold() in f"{item.name} {item.project} {item.category}".casefold())
            ]
            st.caption(f"{len(filtered)} file(s) shown")
            for index, item in enumerate(filtered):
                with st.container(border=True):
                    left, mid, right = st.columns([2.8, 1.4, 1.2])
                    with left:
                        st.markdown(f"**{item.name}**")
                        st.caption(f"{item.category} · {item.file_type} · {item.project} · {item.uploaded_at}")
                    with mid:
                        st.metric("Size", _human_size(item.size_bytes))
                    with right:
                        st.download_button("Download", item.data, item.name, key=f"download_file_{index}", use_container_width=True)

            table = pd.DataFrame([
                {"File": item.name, "Type": item.file_type, "Category": item.category, "Project": item.project, "Size": _human_size(item.size_bytes), "Uploaded": item.uploaded_at}
                for item in filtered
            ])
            with st.expander("Table view", expanded=False):
                st.dataframe(table, use_container_width=True, hide_index=True)

    with preview_tab:
        records = _records()
        if not records:
            st.info("Add a file first to enable preview.")
        else:
            names = [item.name for item in records]
            selected_name = st.selectbox("Select file", names, key="file_preview_name")
            selected = next(item for item in records if item.name == selected_name)
            st.markdown(f"### {selected.name}")
            st.caption(f"{selected.category} · {selected.file_type} · {_human_size(selected.size_bytes)} · {selected.project}")
            _preview(selected)
            st.download_button("Download selected file", selected.data, selected.name, key="download_selected_file")

    if _records():
        metadata = pd.DataFrame([{k: v for k, v in asdict(item).items() if k != "data"} for item in _records()])
        st.download_button("Export file manifest", metadata.to_csv(index=False).encode("utf-8"), "imagine_file_manifest.csv", "text/csv")


__all__ = ["ProjectFile", "render"]
