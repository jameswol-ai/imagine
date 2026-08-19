"""
IMAGINE Architecture
Room Programming Streamlit UI
"""

from __future__ import annotations

import asyncio
from uuid import UUID

import pandas as pd
import streamlit as st

from database.connection import AsyncSessionLocal

from architecture.floor_planning.models import FloorPlan

from .models import RoomType
from .schemas import (
    RoomProgramCreate,
    RoomProgramUpdate,
)
from .service import (
    RoomProgramConflictError,
    RoomProgramConstraintError,
    RoomProgramNotFoundError,
    RoomProgramService,
)


def _run(coro):
    return asyncio.run(coro)


def _with_db(operation):
    async def runner():
        async with AsyncSessionLocal() as db:
            result = await operation(db)
            await db.commit()
            return result

    return _run(runner())


def _list_floor_plans():
    async def operation(db):
        result = await db.execute(
            __import__("sqlalchemy").select(FloorPlan)
            .where(FloorPlan.active.is_(True))
            .order_by(FloorPlan.name)
        )
        return list(result.scalars().all())

    return _with_db(operation)


def _list_rooms(floor_plan_id):
    return _with_db(
        lambda db: RoomProgramService.list(
            db,
            floor_plan_id=floor_plan_id,
            active_only=False,
            limit=500,
        )
    )


def _create_room(payload):
    return _with_db(
        lambda db: RoomProgramService.create(
            db,
            payload,
        )
    )


def _update_room(room_id, payload):
    return _with_db(
        lambda db: RoomProgramService.update(
            db,
            room_id,
            payload,
        )
    )


def _delete_room(room_id):
    return _with_db(
        lambda db: RoomProgramService.delete(
            db,
            room_id,
        )
    )


def _summary(floor_plan_id):
    return _with_db(
        lambda db: RoomProgramService.summary(
            db,
            floor_plan_id,
        )
    )


def render_room_programming():
    """
    Render the production Room Programming interface.

    The visual role remains the same as the original
    Architecture > Room Programming tab.
    """

    st.subheader("Room Programming")

    try:
        floor_plans = _list_floor_plans()
    except Exception as exc:
        st.error(
            f"Unable to load floor plans: {exc}"
        )
        return

    if not floor_plans:
        st.warning(
            "No active floor plans are available. "
            "Create a floor plan before programming rooms."
        )
        return

    floor_plan_labels = {
        f"{plan.plan_code} · {plan.name}": plan
        for plan in floor_plans
    }

    selected_label = st.selectbox(
        "Select Floor Plan",
        list(floor_plan_labels),
        key="room_programming_floor_plan",
    )

    selected_floor_plan = floor_plan_labels[
        selected_label
    ]

    floor_plan_id = selected_floor_plan.id

    try:
        rooms = _list_rooms(
            floor_plan_id
        )
        summary = _summary(
            floor_plan_id
        )
    except Exception as exc:
        st.error(
            f"Unable to load room program: {exc}"
        )
        return

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Floor Area",
        f"{float(summary.floor_area_m2):,.1f} m²",
    )

    c2.metric(
        "Programmed Area",
        f"{float(summary.total_programmed_area_m2):,.1f} m²",
    )

    c3.metric(
        "Remaining Area",
        f"{float(summary.remaining_floor_area_m2):,.1f} m²",
    )

    c4.metric(
        "Occupancy",
        f"{summary.total_occupancy:,}",
    )

    if summary.overall_compliant:
        st.success(
            "Room program is compliant."
        )
    else:
        st.warning(
            "Room program requires review."
        )

    if rooms:
        rows = [
            {
                "ID": str(room.id),
                "Code": room.room_code,
                "Room": room.name,
                "Type": room.room_type.value.title(),
                "Qty": room.quantity,
                "Area (m²)": float(room.area_m2),
                "Min Area (m²)": float(
                    room.minimum_area_m2
                ),
                "Max Area (m²)": float(
                    room.maximum_area_m2
                ),
                "Occupancy": room.occupancy,
                "Level": room.floor_level or "",
                "Active": room.active,
            }
            for room in rooms
        ]

        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info(
            "No rooms programmed for this floor plan."
        )

    with st.expander(
        "➕ Add Room",
        expanded=not bool(rooms),
    ):
        with st.form(
            "room_programming_create_form",
            clear_on_submit=True,
        ):
            c1, c2, c3 = st.columns(3)

            room_code = c1.text_input(
                "Room Code",
                placeholder="OFF-101",
            )

            name = c2.text_input(
                "Room Name",
                placeholder="Office 101",
            )

            room_type = c3.selectbox(
                "Room Type",
                list(RoomType),
                format_func=lambda item:
                item.value.replace(
                    "_", " "
                ).title(),
            )

            c1, c2, c3, c4 = st.columns(4)

            quantity = c1.number_input(
                "Quantity",
                min_value=1,
                value=1,
                step=1,
            )

            area = c2.number_input(
                "Area (m²)",
                min_value=0.01,
                value=20.0,
                step=1.0,
            )

            minimum_area = c3.number_input(
                "Minimum Area (m²)",
                min_value=0.0,
                value=0.0,
                step=1.0,
            )

            maximum_area = c4.number_input(
                "Maximum Area (m²)",
                min_value=0.0,
                value=0.0,
                step=1.0,
            )

            c1, c2, c3 = st.columns(3)

            occupancy = c1.number_input(
                "Occupancy",
                min_value=0,
                value=0,
                step=1,
            )

            occupancy_factor = c2.number_input(
                "m² / Person",
                min_value=0.0,
                value=0.0,
                step=0.5,
            )

            floor_level = c3.text_input(
                "Floor / Level",
                placeholder="Level 1",
            )

            description = st.text_area(
                "Description"
            )

            adjacency_notes = st.text_area(
                "Adjacency Requirements",
                placeholder=(
                    "Adjacent to lobby and corridor."
                ),
            )

            submitted = st.form_submit_button(
                "Create Room",
                type="primary",
            )

            if submitted:

                try:
                    _create_room(
                        RoomProgramCreate(
                            floor_plan_id=floor_plan_id,
                            room_code=room_code,
                            name=name,
                            room_type=room_type.value,
                            quantity=quantity,
                            area_m2=area,
                            minimum_area_m2=minimum_area,
                            maximum_area_m2=maximum_area,
                            occupancy=occupancy,
                            occupancy_factor_m2_per_person=(
                                occupancy_factor
                            ),
                            floor_level=(
                                floor_level.strip()
                                or None
                            ),
                            description=(
                                description.strip()
                                or None
                            ),
                            adjacency_notes=(
                                adjacency_notes.strip()
                                or None
                            ),
                        )
                    )

                    st.success(
                        "Room created successfully."
                    )

                    st.rerun()

                except (
                    RoomProgramConflictError,
                    RoomProgramConstraintError,
                    ValueError,
                ) as exc:
                    st.error(str(exc))

                except Exception as exc:
                    st.error(
                        f"Unable to create room: {exc}"
                    )

    if not rooms:
        return

    st.subheader("Manage Room Program")

    labels = {
        f"{room.room_code} · {room.name}": room
        for room in rooms
    }

    selected_room_label = st.selectbox(
        "Select room",
        list(labels),
        key="room_programming_selected_room",
    )

    selected_room = labels[
        selected_room_label
    ]

    with st.form(
        "room_programming_edit_form"
    ):
        c1, c2 = st.columns(2)

        edit_code = c1.text_input(
            "Room Code",
            value=selected_room.room_code,
        )

        edit_name = c2.text_input(
            "Room Name",
            value=selected_room.name,
        )

        room_types = list(RoomType)

        edit_type = st.selectbox(
            "Room Type",
            room_types,
            index=room_types.index(
                selected_room.room_type
            ),
            format_func=lambda item:
            item.value.replace(
                "_", " "
            ).title(),
        )

        c1, c2, c3, c4 = st.columns(4)

        edit_quantity = c1.number_input(
            "Quantity",
            min_value=1,
            value=selected_room.quantity,
            step=1,
        )

        edit_area = c2.number_input(
            "Area (m²)",
            min_value=0.01,
            value=float(
                selected_room.area_m2
            ),
            step=1.0,
        )

        edit_minimum = c3.number_input(
            "Minimum Area (m²)",
            min_value=0.0,
            value=float(
                selected_room.minimum_area_m2
            ),
            step=1.0,
        )

        edit_maximum = c4.number_input(
            "Maximum Area (m²)",
            min_value=0.0,
            value=float(
                selected_room.maximum_area_m2
            ),
            step=1.0,
        )

        c1, c2, c3 = st.columns(3)

        edit_occupancy = c1.number_input(
            "Occupancy",
            min_value=0,
            value=selected_room.occupancy,
            step=1,
        )

        edit_factor = c2.number_input(
            "m² / Person",
            min_value=0.0,
            value=float(
                selected_room.occupancy_factor_m2_per_person
            ),
            step=0.5,
        )

        edit_level = c3.text_input(
            "Floor / Level",
            value=selected_room.floor_level or "",
        )

        edit_description = st.text_area(
            "Description",
            value=selected_room.description or "",
        )

        edit_adjacency = st.text_area(
            "Adjacency Requirements",
            value=selected_room.adjacency_notes or "",
        )

        edit_active = st.checkbox(
            "Active",
            value=selected_room.active,
        )

        save, delete = st.columns(2)

        save_clicked = save.form_submit_button(
            "Save Changes",
            type="primary",
        )

        delete_clicked = delete.form_submit_button(
            "Delete Room"
        )

    if save_clicked:

        try:
            _update_room(
                selected_room.id,
                RoomProgramUpdate(
                    room_code=edit_code,
                    name=edit_name,
                    room_type=edit_type.value,
                    quantity=edit_quantity,
                    area_m2=edit_area,
                    minimum_area_m2=edit_minimum,
                    maximum_area_m2=edit_maximum,
                    occupancy=edit_occupancy,
                    occupancy_factor_m2_per_person=(
                        edit_factor
                    ),
                    floor_level=(
                        edit_level.strip()
                        or None
                    ),
                    description=(
                        edit_description.strip()
                        or None
                    ),
                    adjacency_notes=(
                        edit_adjacency.strip()
                        or None
                    ),
                    active=edit_active,
                ),
            )

            st.success(
                "Room updated successfully."
            )

            st.rerun()

        except (
            RoomProgramNotFoundError,
            RoomProgramConflictError,
            RoomProgramConstraintError,
            ValueError,
        ) as exc:
            st.error(str(exc))

        except Exception as exc:
            st.error(
                f"Unable to update room: {exc}"
            )

    if delete_clicked:

        try:
            _delete_room(
                selected_room.id
            )

            st.success(
                "Room deleted successfully."
            )

            st.rerun()

        except RoomProgramNotFoundError as exc:
            st.error(str(exc))

        except Exception as exc:
            st.error(
                f"Unable to delete room: {exc}"
            )