"""Persistent project file center for the IMAGINE Streamlit workspace."""
from __future__ import annotations

from dataclasses import dataclass
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
    return {"pdf":"Documents","docx":"Documents","doc":"Documents","xlsx":"Data","xls":"Data","csv":"Data","ifc":"BIM","rvt":"BIM","dwg":"Drawings","dxf":"Drawings","png":"Images","jpg":"Images","jpeg":"Images","json":"Data","txt":"Documents","md":"Documents"}.get(suffix, "Other")


def _upload_key(name: str, payload: bytes) -> tuple[str, int, str]:
    return name, len(payload), hashlib.sha256(payload).hexdigest()


def _database_session():
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
        if uploaded.tzinfo is None: uploaded = uploaded.replace(tzinfo=timezone.utc)
        uploaded_text = uploaded.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    else: uploaded_text = str(uploaded)
    return ProjectFile(str(row.id), row.name, int(row.size_bytes), row.file_type, uploaded_text, row.project, row.category, bytes(row.content), row.checksum)


def _session_records() -> list[ProjectFile]:
    return st.session_state.setdefault("project_files", [])


def _load_records() -> tuple[list[ProjectFile], bool]:
    db = _database_session()
    if db is None: return list(_session_records()), False
    try:
        from database.models.project_file import ProjectFileRecord
        rows = db.query(ProjectFileRecord).order_by(ProjectFileRecord.uploaded_at.desc()).all()
        return [_row_to_file(r) for r in rows], True
    except Exception:
        return list(_session_records()), False
    finally: db.close()


def _add_uploads(files: list[Any], project: str, category: str) -> tuple[int, int, bool]:
    db = _database_session()
    if db is None:
        records = _session_records(); existing = {x.checksum for x in records}; added = skipped = 0
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        for uploaded in files:
            payload = uploaded.getvalue(); checksum = hashlib.sha256(payload).hexdigest()
            if checksum in existing: skipped += 1; continue
            records.append(ProjectFile(checksum[:36], uploaded.name, len(payload), uploaded.name.rsplit(".",1)[-1].upper() if "." in uploaded.name else "FILE", now, project.strip() or "Unassigned", category if category != "Auto" else _category_for(uploaded.name), payload, checksum)); existing.add(checksum); added += 1
        return added, skipped, False
    try:
        from database.models.project_file import ProjectFileRecord
        added = skipped = 0
        for uploaded in files:
            payload = uploaded.getvalue(); checksum = hashlib.sha256(payload).hexdigest()
            if db.query(ProjectFileRecord).filter(ProjectFileRecord.checksum == checksum).first(): skipped += 1; continue
            db.add(ProjectFileRecord(name=uploaded.name, size_bytes=len(payload), file_type=uploaded.name.rsplit(".",1)[-1].upper() if "." in uploaded.name else "FILE", project=project.strip() or "Unassigned", category=category if category != "Auto" else _category_for(uploaded.name), checksum=checksum, content=payload)); added += 1
        db.commit(); return added, skipped, True
    except Exception:
        db.rollback(); return 0, len(files), False
    finally: db.close()


def _preview(file: ProjectFile) -> None:
    suffix = file.name.rsplit(".",1)[-1].lower() if "." in file.name else ""
    if suffix == "csv":
        try: st.dataframe(pd.read_csv(BytesIO(file.data)), use_container_width=True, hide_index=True)
        except Exception as exc: st.warning(f"Preview unavailable: {type(exc).__name__}: {exc}")
    elif suffix in {"txt","md","json"}:
        st.code(file.data.decode("utf-8", errors="replace")[:20000], language="json" if suffix == "json" else None)
    elif suffix in {"png","jpg","jpeg"}: st.image(file.data, use_container_width=True)
    else: st.info("This file type is stored safely but does not have an in-app renderer yet. Use Download to open it in its native application.")


def _delete_file(file: ProjectFile) -> bool:
    db = _database_session()
    if db is None:
        records = _session_records(); before = len(records); records[:] = [x for x in records if x.id != file.id]; return len(records) != before
    try:
        from database.models.project_file import ProjectFileRecord
        row = db.get(ProjectFileRecord, file.id)
        if row is None: return False
        db.delete(row); db.commit(); return True
    except Exception:
        db.rollback(); return False
    finally: db.close()


def render() -> None:
    st.subheader("Project File Center")
    st.caption("A visual document hub for project files, drawings, BIM models, data and images.")
    records, persistent = _load_records()
    total_bytes = sum(x.size_bytes for x in records)
    categories = sorted({x.category for x in records})
    projects = sorted({x.project for x in records})
    a,b,c,d = st.columns(4)
    a.metric("Files", len(records)); b.metric("Storage", _human_size(total_bytes)); c.metric("Categories", len(categories)); d.metric("Projects", len(projects))
    if persistent: st.success("Persistent database storage is active.")
    else: st.warning("Database storage is unavailable. Files are currently held only in this Streamlit session.")

    upload_tab, library_tab, preview_tab = st.tabs(["Upload", "Library", "Preview"])
    with upload_tab:
        project = st.text_input("Project", value=st.session_state.get("selected_project_name") or "Unassigned", key="file_project")
        category = st.selectbox("Category", ["Auto","Documents","Drawings","BIM","Data","Images","Other"], key="file_category")
        uploads = st.file_uploader("Add project files", type=["pdf","doc","docx","txt","md","csv","xls","xlsx","ifc","dwg","dxf","rvt","json","png","jpg","jpeg"], accept_multiple_files=True, key="project_file_uploader")
        if uploads and st.button("Save files", type="primary", use_container_width=True):
            added, skipped, stored = _add_uploads(uploads, project, category)
            (st.success if stored else st.warning)(f"Saved {added} file(s). {skipped} duplicate(s) skipped.")
            st.rerun()

    with library_tab:
        if not records: st.info("No files have been added yet.")
        else:
            c1,c2,c3 = st.columns([1,1,1.4])
            with c1: filter_category = st.selectbox("Category", ["All categories", *categories], key="file_category_filter")
            with c2: filter_project = st.selectbox("Project", ["All projects", *projects], key="file_project_filter")
            with c3: query = st.text_input("Search", placeholder="Filename, type, project...", key="file_query")
            view = st.radio("Presentation", ["Cards", "Table"], horizontal=True, key="file_view_mode")
            filtered = [x for x in records if (filter_category == "All categories" or x.category == filter_category) and (filter_project == "All projects" or x.project == filter_project) and (not query or query.casefold() in f"{x.name} {x.file_type} {x.project} {x.category}".casefold())]
            st.caption(f"Showing {len(filtered)} of {len(records)} files")
            if view == "Cards":
                cols = st.columns(3)
                for i, item in enumerate(filtered):
                    with cols[i % 3]:
                        with st.container(border=True):
                            st.markdown(f"**{item.name}**")
                            st.caption(f"{item.file_type} · {item.category}")
                            st.write(f"Project: **{item.project}**")
                            st.write(f"Size: {_human_size(item.size_bytes)}")
                            st.caption(item.uploaded_at)
                            st.download_button("Download", item.data, item.name, key=f"download_file_{item.id}", use_container_width=True)
                            if st.button("Remove", key=f"delete_file_{item.id}", use_container_width=True):
                                if _delete_file(item): st.rerun()
            else:
                table = pd.DataFrame([{"File":x.name,"Type":x.file_type,"Category":x.category,"Project":x.project,"Size":_human_size(x.size_bytes),"Uploaded":x.uploaded_at} for x in filtered])
                st.dataframe(table, use_container_width=True, hide_index=True)
            if filtered:
                st.download_button("Export visible file manifest", pd.DataFrame([{"File ID":x.id,"File":x.name,"Type":x.file_type,"Category":x.category,"Project":x.project,"Size":_human_size(x.size_bytes),"Uploaded":x.uploaded_at,"Checksum":x.checksum} for x in filtered]).to_csv(index=False).encode(), "imagine_file_manifest.csv", "text/csv", key="export_file_manifest")

    with preview_tab:
        if not records: st.info("Add a file first to enable preview.")
        else:
            options = {f"{x.name} | {x.project} | {x.id[:8]}": x for x in records}
            selected = options[st.selectbox("Select file", list(options), key="file_preview_id")]
            st.markdown(f"### {selected.name}")
            st.caption(f"{selected.category} · {selected.file_type} · {_human_size(selected.size_bytes)} · {selected.project}")
            _preview(selected)
            st.download_button("Download selected file", selected.data, selected.name, key="download_selected_file")


__all__ = ["ProjectFile", "render", "_category_for", "_human_size", "_upload_key"]
