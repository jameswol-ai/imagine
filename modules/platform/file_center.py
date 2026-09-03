"""Persistent project file center for the IMAGINE Streamlit workspace.

The file center uses the application database when available, so uploads survive
Streamlit reruns and deployments. If the database is unavailable, it falls back
to the current session and clearly reports that limitation.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from io import BytesIO
import hashlib
from typing import Any

import pandas as pd
import streamlit as st


@dataclass
class ProjectFile:
    id: str
    name: str
    size_bytes: int
    file_type: str
    uploaded_at: str
    project: str
    category: str
    data: bytes
    checksum: str = ""


def _human_size(value: int) -> str:
    size = float(max(0, value))
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{value} B"


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


def _database_session():
    """Return a database session when persistent storage is available."""
    try:
        from database.bootstrap import ensure_schema
        from database.connection import SessionLocal

        ensure_schema()
        return SessionLocal()
    except Exception:
        return None


def _row_to_file(row: Any) -> ProjectFile:
    uploaded = row.uploaded_at
    if isinstance(uploaded, datetime):
        if uploaded.tzinfo is None:
            uploaded = uploaded.replace(tzinfo=timezone.utc)
        uploaded_text = uploaded.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    else:
        uploaded_text = str(uploaded)
    return ProjectFile(
        id=str(row.id),
        name=row.name,
        size_bytes=int(row.size_bytes),
        file_type=row.file_type,
        uploaded_at=uploaded_text,
        project=row.project,
        category=row.category,
        data=bytes(row.content),
        checksum=row.checksum,
    )


def _session_records() -> list[ProjectFile]:
    return st.session_state.setdefault("project_files", [])


def _load_records() -> tuple[list[ProjectFile], bool]:
    db = _database_session()
    if db is None:
        return list(_session_records()), False
    try:
        from database.models.project_file import ProjectFileRecord
        rows = db.query(ProjectFileRecord).order_by(ProjectFileRecord.uploaded_at.desc()).all()
        return [_row_to_file(row) for row in rows], True
    except Exception:
        return list(_session_records()), False
    finally:
        db.close()


def _add_uploads(files: list[Any], project: str, category: str) -> tuple[int, int, bool]:
    """Persist uploads and return ``(added, skipped_duplicates, persistent)``."""
    db = _database_session()
    if db is None:
        records = _session_records()
        existing = {hashlib.sha256(item.data).hexdigest() for item in records}
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        added = skipped = 0
        for uploaded in files:
            payload = uploaded.getvalue()
            checksum = hashlib.sha256(payload).hexdigest()
            if checksum in existing:
                skipped += 1
                continue
            records.append(
                ProjectFile(
                    id=checksum[:36],
                    name=uploaded.name,
                    size_bytes=len(payload),
                    file_type=(uploaded.name.rsplit(".", 1)[-1].upper() if "." in uploaded.name else "FILE"),
                    uploaded_at=now,
                    project=project.strip() or "Unassigned",
                    category=category if category != "Auto" else _category_for(uploaded.name),
                    data=payload,
                    checksum=checksum,
                )
            )
            existing.add(checksum)
            added += 1
        return added, skipped, False

    try:
        from database.models.project_file import ProjectFileRecord
        added = skipped = 0
        for uploaded in files:
            payload = uploaded.getvalue()
            checksum = hashlib.sha256(payload).hexdigest()
            if db.query(ProjectFileRecord).filter(ProjectFileRecord.checksum == checksum).first():
                skipped += 1
                continue
            db.add(ProjectFileRecord(
                name=uploaded.name,
                size_bytes=len(payload),
                file_type=(uploaded.name.rsplit(".", 1)[-1].upper() if "." in uploaded.name else "FILE"),
                project=project.strip() or "Unassigned",
                category=category if category != "Auto" else _category_for(uploaded.name),
                checksum=checksum,
                content=payload,
            ))
            added += 1
        db.commit()
        return added, skipped, True
    except Exception:
        db.rollback()
        return 0, len(files), False
    finally:
        db.close()


def _preview(file: ProjectFile) -> None:
    suffix = file.name.rsplit(".", 1)[-1].lower() if "." in file.name else ""
    if suffix in {"txt", "md", "json", "csv"}:
        try:
            if suffix == "csv":
                st.dataframe(pd.read_csv(BytesIO(file.data)), use_container_width=True, hide_index=True)
            else:
                text = file.data.decode("utf-8", errors="replace")
                st.code(text[:12000], language="json" if suffix == "json" else None)
        except Exception as exc:
            st.warning(f"Preview unavailable: {type(exc).__name__}: {exc}")
    elif suffix in {"png", "jpg", "jpeg"}:
        st.image(file.data, use_container_width=True)
    else:
        st.info("Preview is not rendered for this file type. Download it to open it in the appropriate application.")


def _delete_file(file: ProjectFile) -> bool:
    db = _database_session()
    if db is None:
        records = _session_records()
        before = len(records)
        records[:] = [item for item in records if item.id != file.id]
        return len(records) != before
    try:
        from database.models.project_file import ProjectFileRecord
        row = db.get(ProjectFileRecord, file.id)
        if row is None:
            return False
        db.delete(row)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
    finally:
        db.close()


def render() -> None:
    st.subheader("Project File Center")
    st.caption("Persistent project document, drawing, BIM and data workspace.")

    records, persistent = _load_records()
    if persistent:
        st.success("Persistent database storage is active.")
    else:
        st.warning("Database storage is unavailable. Files are currently held only in this Streamlit session.")

    upload_tab, library_tab, preview_tab = st.tabs(["Upload", "Library", "Preview"])

    with upload_tab:
        project = st.text_input("Project", value=st.session_state.get("selected_project_name") or "Unassigned", key="file_project")
        category = st.selectbox("Category", ["Auto", "Documents", "Drawings", "BIM", "Data", "Images", "Other"], key="file_category")
        uploads = st.file_uploader(
            "Add project files",
            type=["pdf", "doc", "docx", "txt", "md", "csv", "xls", "xlsx", "ifc", "dwg", "dxf", "rvt", "json", "png", "jpg", "jpeg"],
            accept_multiple_files=True,
            key="project_file_uploader",
            help="Files are stored in the application database when database storage is available.",
        )
        if uploads and st.button("Save files", type="primary", use_container_width=True):
            added, skipped, stored = _add_uploads(uploads, project, category)
            if stored:
                st.success(f"Saved {added} file(s) to persistent storage. {skipped} duplicate(s) skipped.")
            elif added:
                st.warning(f"Saved {added} file(s) to the current session. Database storage was unavailable.")
            else:
                st.info(f"No new files saved. {skipped} duplicate or unavailable file(s).")
            st.rerun()

    with library_tab:
        if not records:
            st.info("No files have been added to this workspace yet.")
        else:
            categories = sorted({item.category for item in records})
            filter_category = st.selectbox("Category filter", ["All categories", *categories], key="file_category_filter")
            query = st.text_input("Filter files", placeholder="Search by filename, project or category", key="file_query")
            filtered = [item for item in records if
                        (filter_category == "All categories" or item.category == filter_category)
                        and (not query or query.casefold() in f"{item.name} {item.project} {item.category}".casefold())]
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
                            st.download_button("Download", item.data, item.name, key=f"download_file_{item.id}", use_container_width=True)
                        with delete_col:
                            if st.button("Remove", key=f"delete_file_{item.id}", use_container_width=True):
                                if _delete_file(item):
                                    st.rerun()
                                st.error("File could not be removed.")

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
            options = {f"{item.name} | {item.project} | {item.id[:8]}": item for item in records}
            selected_label = st.selectbox("Select file", list(options), key="file_preview_id")
            selected = options[selected_label]
            st.markdown(f"### {selected.name}")
            st.caption(f"{selected.category} · {selected.file_type} · {_human_size(selected.size_bytes)} · {selected.project}")
            _preview(selected)
            st.download_button("Download selected file", selected.data, selected.name, key="download_selected_file")

    if records:
        metadata = pd.DataFrame([
            {"File ID": item.id, "File": item.name, "Type": item.file_type, "Category": item.category,
             "Project": item.project, "Size": _human_size(item.size_bytes), "Uploaded": item.uploaded_at,
             "Checksum": item.checksum}
            for item in records
        ])
        st.download_button("Export file manifest", metadata.to_csv(index=False).encode("utf-8"), "imagine_file_manifest.csv", "text/csv", key="export_file_manifest")


__all__ = ["ProjectFile", "render", "_category_for", "_human_size", "_upload_key"]
