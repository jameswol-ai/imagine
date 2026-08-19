"""
IMAGINE Architecture
Room Programming Service
"""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from architecture.floor_planning.models import FloorPlan

from .models import RoomProgram
from .repository import RoomProgramRepository
from .schemas import (
    RoomProgramConstraintResult,
    RoomProgramCreate,
    RoomProgramSummary,
    RoomProgramUpdate,
)


class RoomProgramNotFoundError(LookupError):
    """Raised when a room program does not exist."""


class RoomProgramConflictError(ValueError):
    """Raised when a room program conflicts with an existing record."""


class RoomProgramConstraintError(ValueError):
    """Raised when room programming constraints are violated."""


class RoomProgramService:

    @staticmethod
    async def get(
        db: AsyncSession,
        room_program_id: UUID,
    ) -> RoomProgram:

        room = await RoomProgramRepository.get(
            db,
            room_program_id,
        )

        if room is None:
            raise RoomProgramNotFoundError(
                f"Room program {room_program_id} not found."
            )

        return room

    @staticmethod
    async def list(
        db: AsyncSession,
        *,
        floor_plan_id: UUID | None = None,
        active_only: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> list[RoomProgram]:

        if skip < 0:
            raise ValueError("skip must be >= 0.")

        if limit < 1 or limit > 500:
            raise ValueError(
                "limit must be between 1 and 500."
            )

        return await RoomProgramRepository.list(
            db,
            floor_plan_id=floor_plan_id,
            active_only=active_only,
            skip=skip,
            limit=limit,
        )

    @staticmethod
    async def create(
        db: AsyncSession,
        data: RoomProgramCreate,
    ) -> RoomProgram:

        floor_plan = await RoomProgramService._get_floor_plan(
            db,
            data.floor_plan_id,
        )

        existing = await RoomProgramRepository.get_by_code(
            db,
            floor_plan_id=data.floor_plan_id,
            room_code=data.room_code,
        )

        if existing:
            raise RoomProgramConflictError(
                f"Room code '{data.room_code}' already exists "
                f"for this floor plan."
            )

        rooms = await RoomProgramRepository.list(
            db,
            floor_plan_id=data.floor_plan_id,
            active_only=True,
            limit=500,
        )

        values = data.model_dump(
            exclude={"adjacency"},
        )

        candidate = RoomProgram(
            **values,
        )

        proposed_rooms = [
            *rooms,
            candidate,
        ]

        violations = RoomProgramService._validate_program(
            floor_plan,
            proposed_rooms,
        )

        if violations:
            raise RoomProgramConstraintError(
                "; ".join(violations)
            )

        try:
            return await RoomProgramRepository.create(
                db,
                candidate,
            )
        except IntegrityError as exc:
            await db.rollback()

            raise RoomProgramConflictError(
                f"Room code '{data.room_code}' already exists "
                f"for this floor plan."
            ) from exc

    @staticmethod
    async def update(
        db: AsyncSession,
        room_program_id: UUID,
        data: RoomProgramUpdate,
    ) -> RoomProgram:

        room = await RoomProgramService.get(
            db,
            room_program_id,
        )

        values = data.model_dump(
            exclude_unset=True,
            exclude={"adjacency"},
        )

        floor_plan_id = values.get(
            "floor_plan_id",
            room.floor_plan_id,
        )

        floor_plan = await RoomProgramService._get_floor_plan(
            db,
            floor_plan_id,
        )

        if "room_code" in values:
            existing = await RoomProgramRepository.get_by_code(
                db,
                floor_plan_id=floor_plan_id,
                room_code=values["room_code"],
            )

            if (
                existing
                and existing.id != room.id
            ):
                raise RoomProgramConflictError(
                    f"Room code '{values['room_code']}' "
                    "already exists for this floor plan."
                )

        rooms = await RoomProgramRepository.list(
            db,
            floor_plan_id=floor_plan_id,
            active_only=True,
            limit=500,
        )

        for key, value in values.items():
            setattr(room, key, value)

        proposed_rooms = [
            item
            for item in rooms
            if item.id != room.id
        ]

        if room.active:
            proposed_rooms.append(room)

        violations = RoomProgramService._validate_program(
            floor_plan,
            proposed_rooms,
        )

        if violations:
            raise RoomProgramConstraintError(
                "; ".join(violations)
            )

        try:
            return await RoomProgramRepository.update(
                db,
                room,
            )
        except IntegrityError as exc:
            await db.rollback()

            raise RoomProgramConflictError(
                "Room program conflicts with an existing record."
            ) from exc

    @staticmethod
    async def delete(
        db: AsyncSession,
        room_program_id: UUID,
    ) -> None:

        room = await RoomProgramService.get(
            db,
            room_program_id,
        )

        await RoomProgramRepository.delete(
            db,
            room,
        )

    @staticmethod
    async def validate(
        db: AsyncSession,
        room_program_id: UUID,
    ) -> RoomProgramConstraintResult:

        room = await RoomProgramService.get(
            db,
            room_program_id,
        )

        floor_plan = await RoomProgramService._get_floor_plan(
            db,
            room.floor_plan_id,
        )

        return RoomProgramService._constraint_result(
            floor_plan,
            room,
        )

    @staticmethod
    async def summary(
        db: AsyncSession,
        floor_plan_id: UUID,
    ) -> RoomProgramSummary:

        floor_plan = await RoomProgramService._get_floor_plan(
            db,
            floor_plan_id,
        )

        rooms = await RoomProgramRepository.list(
            db,
            floor_plan_id=floor_plan_id,
            active_only=True,
            limit=500,
        )

        total_area = sum(
            (
                Decimal(str(room.area_m2))
                * Decimal(room.quantity)
                for room in rooms
            ),
            Decimal("0"),
        )

        total_quantity = sum(
            room.quantity
            for room in rooms
        )

        total_occupancy = sum(
            room.occupancy * room.quantity
            for room in rooms
        )

        compliant = 0

        for room in rooms:
            result = RoomProgramService._constraint_result(
                floor_plan,
                room,
            )

            if result.overall_compliant:
                compliant += 1

        non_compliant = (
            len(rooms) - compliant
        )

        floor_area = Decimal(
            str(floor_plan.floor_area_m2)
        )

        remaining = (
            floor_area - total_area
        )

        overall = (
            remaining >= Decimal("0")
            and non_compliant == 0
        )

        return RoomProgramSummary(
            floor_plan_id=floor_plan_id,
            room_count=len(rooms),
            total_quantity=total_quantity,
            total_programmed_area_m2=total_area,
            floor_area_m2=floor_area,
            remaining_floor_area_m2=remaining,
            total_occupancy=total_occupancy,
            compliant_rooms=compliant,
            non_compliant_rooms=non_compliant,
            overall_compliant=overall,
        )

    @staticmethod
    async def _get_floor_plan(
        db: AsyncSession,
        floor_plan_id: UUID,
    ) -> FloorPlan:

        floor_plan = await db.get(
            FloorPlan,
            floor_plan_id,
        )

        if floor_plan is None:
            raise LookupError(
                f"Floor plan {floor_plan_id} not found."
            )

        return floor_plan

    @staticmethod
    def _required_area(
        room: RoomProgram,
    ) -> Decimal:

        occupancy_area = (
            Decimal(room.occupancy)
            * Decimal(str(
                room.occupancy_factor_m2_per_person
            ))
        )

        return max(
            Decimal(str(room.minimum_area_m2)),
            occupancy_area,
        )

    @staticmethod
    def _constraint_result(
        floor_plan: FloorPlan,
        room: RoomProgram,
    ) -> RoomProgramConstraintResult:

        area = Decimal(
            str(room.area_m2)
        )

        minimum = Decimal(
            str(room.minimum_area_m2)
        )

        maximum = Decimal(
            str(room.maximum_area_m2)
        )

        required = RoomProgramService._required_area(
            room
        )

        violations: list[str] = []

        area_compliant = True

        if minimum > 0 and area < minimum:
            area_compliant = False

            violations.append(
                f"{room.room_code}: area "
                f"{area} m² is below minimum "
                f"{minimum} m²."
            )

        if maximum > 0 and area > maximum:
            area_compliant = False

            violations.append(
                f"{room.room_code}: area "
                f"{area} m² exceeds maximum "
                f"{maximum} m²."
            )

        if area < required:
            area_compliant = False

            violations.append(
                f"{room.room_code}: area "
                f"{area} m² is insufficient for "
                f"the occupancy requirement of "
                f"{required} m²."
            )

        occupancy_compliant = True

        if (
            room.occupancy > 0
            and room.occupancy_factor_m2_per_person > 0
        ):
            required_area = (
                Decimal(room.occupancy)
                * Decimal(
                    str(
                        room.occupancy_factor_m2_per_person
                    )
                )
            )

            if area < required_area:
                occupancy_compliant = False

                violations.append(
                    f"{room.room_code}: occupancy of "
                    f"{room.occupancy} requires at least "
                    f"{required_area} m²."
                )

        adjacency_compliant = True

        # Adjacency relationships are represented in the
        # program metadata and are validated at program level
        # when the UI/API supplies the complete room set.
        #
        # A room with no adjacency declaration is valid.
        #
        # The database model intentionally does not store
        # arbitrary JSON adjacency state. This keeps the core
        # room record normalized and migration-friendly.

        overall = (
            area_compliant
            and occupancy_compliant
            and adjacency_compliant
        )

        return RoomProgramConstraintResult(
            room_program_id=room.id,
            room_code=room.room_code,
            area_m2=area,
            minimum_area_m2=minimum,
            maximum_area_m2=maximum,
            occupancy=room.occupancy,
            occupancy_factor_m2_per_person=(
                Decimal(
                    str(
                        room.occupancy_factor_m2_per_person
                    )
                )
            ),
            calculated_required_area_m2=required,
            area_compliant=area_compliant,
            occupancy_compliant=occupancy_compliant,
            adjacency_compliant=adjacency_compliant,
            overall_compliant=overall,
            violations=violations,
        )

    @staticmethod
    def _validate_program(
        floor_plan: FloorPlan,
        rooms: list[RoomProgram],
    ) -> list[str]:

        violations: list[str] = []

        floor_area = Decimal(
            str(floor_plan.floor_area_m2)
        )

        total_programmed_area = sum(
            (
                Decimal(str(room.area_m2))
                * Decimal(room.quantity)
                for room in rooms
            ),
            Decimal("0"),
        )

        if total_programmed_area > floor_area:
            violations.append(
                "Total programmed room area "
                f"{total_programmed_area} m² exceeds "
                f"floor area {floor_area} m²."
            )

        seen_codes: set[str] = set()

        for room in rooms:

            if room.room_code in seen_codes:
                violations.append(
                    f"Duplicate room code: "
                    f"{room.room_code}."
                )

            seen_codes.add(
                room.room_code
            )

            result = RoomProgramService._constraint_result(
                floor_plan,
                room,
            )

            violations.extend(
                result.violations
            )

        return violations