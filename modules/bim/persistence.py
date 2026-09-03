"""Project-scoped persistence for the BIM hierarchy.

The UI can continue to operate without a configured database, but whenever an
active project is selected and the schema is available, BIM records are loaded
from and written to SQLAlchemy models instead of session-only demo storage.
"""
from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select

from database.bootstrap import ensure_schema
from database.connection import SessionLocal
from bim.models import Building, Storey, Space, Element


MODEL_BY_KEY = {
    "bim_buildings": Building,
    "bim_storeys": Storey,
    "bim_spaces": Space,
    "bim_elements": Element,
}


def _uuid(value: str | UUID | None) -> UUID | None:
    if value is None or str(value).strip() == "":
        return None
    return value if isinstance(value, UUID) else UUID(str(value))


def available() -> bool:
    try:
        ensure_schema()
        return True
    except Exception:
        return False


def load(key: str, project_id: str | UUID | None = None) -> list[dict[str, Any]]:
    """Load project-scoped BIM records as UI-friendly dictionaries."""
    model = MODEL_BY_KEY.get(key)
    if model is None:
        return []

    pid = _uuid(project_id)
    if pid is None:
        return []

    try:
        with SessionLocal() as db:
            if model is Building:
                rows = db.scalars(select(Building).where(Building.project_id == pid)).all()
            elif model is Storey:
                rows = db.scalars(
                    select(Storey)
                    .join(Building, Storey.building_id == Building.id)
                    .where(Building.project_id == pid)
                ).all()
            elif model is Space:
                rows = db.scalars(
                    select(Space)
                    .join(Building, Space.building_id == Building.id)
                    .where(Building.project_id == pid)
                ).all()
            else:
                rows = db.scalars(
                    select(Element)
                    .join(Building, Element.building_id == Building.id)
                    .where(Building.project_id == pid)
                ).all()
            return [_to_dict(row) for row in rows]
    except Exception:
        return []


def create(key: str, record: dict[str, Any], project_id: str | UUID) -> dict[str, Any]:
    """Persist one BIM record and return its serialized representation."""
    model = MODEL_BY_KEY.get(key)
    pid = _uuid(project_id)
    if model is None or pid is None:
        raise ValueError("A supported BIM key and active project UUID are required")

    with SessionLocal() as db:
        if model is Building:
            row = Building(
                project_id=pid,
                code=record.get("building_code") or record.get("code"),
                name=record.get("name") or "Building",
                storeys=record.get("levels_count", record.get("storeys", 0)),
                area=record.get("gross_area_m2", record.get("area", 0.0)),
                height=record.get("height_m", record.get("height", 0.0)),
                typology=record.get("typology"),
                status=record.get("status", "Concept Design"),
                ifc_version=record.get("ifc_version", "IFC4"),
                description=record.get("description"),
            )
        elif model is Storey:
            building_id = _uuid(record.get("building_id"))
            _require_building(db, building_id, pid)
            row = Storey(
                building_id=building_id,
                code=record.get("storey_code") or record.get("code"),
                level=record.get("name") or record.get("level") or "Level",
                elevation=record.get("elevation_m", record.get("elevation", 0.0)),
                height=record.get("height_m", record.get("height", 0.0)),
                area=record.get("area", 0.0),
                description=record.get("description"),
            )
        elif model is Space:
            building_id = _uuid(record.get("building_id"))
            storey_id = _uuid(record.get("storey_id"))
            _require_building(db, building_id, pid)
            _require_storey(db, storey_id, building_id)
            row = Space(
                building_id=building_id,
                storey_id=storey_id,
                code=record.get("space_code") or record.get("code"),
                name=record.get("name") or "Space",
                area=record.get("net_area_m2", record.get("area", 0.0)),
                height=record.get("height", 0.0),
                space_type=record.get("usage_type") or record.get("space_type"),
                capacity=record.get("capacity", 0),
            )
        else:
            building_id = _uuid(record.get("building_id"))
            storey_id = _uuid(record.get("storey_id"))
            _require_building(db, building_id, pid)
            if storey_id:
                _require_storey(db, storey_id, building_id)
            row = Element(
                building_id=building_id,
                storey_id=storey_id,
                code=record.get("code"),
                name=record.get("name") or "Element",
                material=record.get("material"),
                quantity=record.get("quantity", 1.0),
                unit=record.get("unit", "item"),
                element_type=record.get("category") or record.get("element_type"),
                type_name=record.get("type_name"),
                status=record.get("status", "Design"),
                guid=record.get("guid"),
            )

        db.add(row)
        db.commit()
        db.refresh(row)
        return _to_dict(row)


def _require_building(db, building_id: UUID | None, project_id: UUID) -> None:
    if building_id is None:
        raise ValueError("building_id is required")
    row = db.scalar(select(Building).where(Building.id == building_id, Building.project_id == project_id))
    if row is None:
        raise ValueError("Building does not belong to the active project")


def _require_storey(db, storey_id: UUID | None, building_id: UUID | None) -> None:
    if storey_id is None or building_id is None:
        raise ValueError("storey_id and building_id are required")
    row = db.scalar(select(Storey).where(Storey.id == storey_id, Storey.building_id == building_id))
    if row is None:
        raise ValueError("Storey does not belong to the selected building")


def _to_dict(row: Any) -> dict[str, Any]:
    if isinstance(row, Building):
        return {
            "id": str(row.id), "building_code": row.code or "", "name": row.name,
            "typology": row.typology or "", "gross_area_m2": row.area or 0.0,
            "levels_count": row.storeys or 0, "height_m": row.height or 0.0,
            "status": row.status or "Concept Design", "project_id": str(row.project_id),
        }
    if isinstance(row, Storey):
        return {
            "id": str(row.id), "storey_code": row.code or "", "building_id": str(row.building_id),
            "name": row.level, "elevation_m": row.elevation or 0.0,
            "height_m": row.height or 0.0, "description": row.description or "",
        }
    if isinstance(row, Space):
        return {
            "id": str(row.id), "space_code": row.code or "", "name": row.name,
            "building_id": str(row.building_id), "storey_id": str(row.storey_id),
            "level": "", "usage_type": row.space_type or "", "net_area_m2": row.area or 0.0,
            "capacity": row.capacity or 0,
        }
    return {
        "id": str(row.id), "building_id": str(row.building_id),
        "storey_id": str(row.storey_id) if row.storey_id else "",
        "category": row.element_type or "", "name": row.name,
        "type_name": row.type_name or row.element_type or "", "quantity": row.quantity or 0.0,
        "unit": row.unit or "item", "status": row.status or "Design", "guid": row.guid or "",
    }


__all__ = ["available", "load", "create"]
