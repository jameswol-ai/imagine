"""
IMAGINE Architecture
Floor Planning Service

This layer owns the planning rules.

Floor Planning is intentionally dependent on:
    Site Planning
    Zoning
"""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from architecture.site_planning.models import SitePlan
from architecture.zoning.models import ZoningRule

from .models import FloorPlan
from .repository import FloorPlanRepository
from .schemas import (
    FloorPlanConstraintResult,
    FloorPlanCreate,
    FloorPlanUpdate,
)


class FloorPlanService:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

        self.repository = FloorPlanRepository(
            session
        )

    async def list(
        self,
        project_id: UUID | None = None,
        site_plan_id: UUID | None = None,
        zoning_id: UUID | None = None,
        active_only: bool = False,
    ):
        return await self.repository.list(
            project_id=project_id,
            site_plan_id=site_plan_id,
            zoning_id=zoning_id,
            active_only=active_only,
        )

    async def get(
        self,
        floor_plan_id: UUID,
    ):
        return await self.repository.get(
            floor_plan_id
        )

    async def create(
        self,
        payload: FloorPlanCreate,
    ) -> FloorPlan:

        existing = await self.repository.get_by_code(
            payload.plan_code
        )

        if existing:
            raise ValueError(
                f"Floor plan code already exists: "
                f"{payload.plan_code}"
            )

        site = await self._get_site(
            payload.site_plan_id
        )

        zoning = await self._get_zoning(
            payload.zoning_id
        )

        values = payload.model_dump()

        self._calculate_gfa(values)

        self._validate_constraints(
            values=values,
            site=site,
            zoning=zoning,
        )

        floor_plan = FloorPlan(
            **values
        )

        return await self.repository.create(
            floor_plan
        )

    async def update(
        self,
        floor_plan_id: UUID,
        payload: FloorPlanUpdate,
    ) -> FloorPlan:

        floor_plan = await self.repository.get(
            floor_plan_id
        )

        if not floor_plan:
            raise LookupError(
                "Floor plan not found"
            )

        values = payload.model_dump(
            exclude_unset=True
        )

        if "plan_code" in values:

            existing = await self.repository.get_by_code(
                values["plan_code"]
            )

            if (
                existing
                and existing.id != floor_plan.id
            ):
                raise ValueError(
                    f"Floor plan code already exists: "
                    f"{values['plan_code']}"
                )

        site_plan_id = values.get(
            "site_plan_id",
            floor_plan.site_plan_id,
        )

        zoning_id = values.get(
            "zoning_id",
            floor_plan.zoning_id,
        )

        site = await self._get_site(
            site_plan_id
        )

        zoning = await self._get_zoning(
            zoning_id
        )

        merged = {
            "site_area_m2": floor_plan.floor_area_m2,
            "floor_area_m2": floor_plan.floor_area_m2,
            "building_footprint_m2": (
                floor_plan.building_footprint_m2
            ),
            "gross_floor_area_m2": (
                floor_plan.gross_floor_area_m2
            ),
            "number_of_floors": (
                floor_plan.number_of_floors
            ),
            "front_setback_m": (
                floor_plan.front_setback_m
            ),
            "rear_setback_m": (
                floor_plan.rear_setback_m
            ),
            "side_setback_m": (
                floor_plan.side_setback_m
            ),
        }

        merged.update(values)

        self._calculate_gfa(
            merged
        )

        self._validate_constraints(
            values=merged,
            site=site,
            zoning=zoning,
        )

        return await self.repository.update(
            floor_plan,
            values,
        )

    async def delete(
        self,
        floor_plan_id: UUID,
    ) -> None:

        floor_plan = await self.repository.get(
            floor_plan_id
        )

        if not floor_plan:
            raise LookupError(
                "Floor plan not found"
            )

        await self.repository.delete(
            floor_plan
        )

    async def validate_constraints(
        self,
        floor_plan_id: UUID,
    ) -> FloorPlanConstraintResult:

        floor_plan = await self.repository.get(
            floor_plan_id
        )

        if not floor_plan:
            raise LookupError(
                "Floor plan not found"
            )

        site = await self._get_site(
            floor_plan.site_plan_id
        )

        zoning = await self._get_zoning(
            floor_plan.zoning_id
        )

        values = {
            "building_footprint_m2": (
                floor_plan.building_footprint_m2
            ),
            "gross_floor_area_m2": (
                floor_plan.gross_floor_area_m2
            ),
            "floor_area_m2": (
                floor_plan.floor_area_m2
            ),
            "number_of_floors": (
                floor_plan.number_of_floors
            ),
            "front_setback_m": (
                floor_plan.front_setback_m
            ),
            "rear_setback_m": (
                floor_plan.rear_setback_m
            ),
            "side_setback_m": (
                floor_plan.side_setback_m
            ),
        }

        return self._build_constraint_result(
            floor_plan,
            site,
            zoning,
            values,
        )

    async def _get_site(
        self,
        site_plan_id: UUID,
    ) -> SitePlan:

        site = await self.session.get(
            SitePlan,
            site_plan_id,
        )

        if not site:
            raise LookupError(
                "Site Plan not found"
            )

        return site

    async def _get_zoning(
        self,
        zoning_id: UUID,
    ) -> ZoningRule:

        zoning = await self.session.get(
            ZoningRule,
            zoning_id,
        )

        if not zoning:
            raise LookupError(
                "Zoning record not found"
            )

        return zoning

    @staticmethod
    def _calculate_gfa(
        values: dict,
    ) -> None:

        if (
            "number_of_floors" in values
            and "floor_area_m2" in values
        ):
            values["gross_floor_area_m2"] = (
                Decimal(
                    str(values["number_of_floors"])
                )
                * Decimal(
                    str(values["floor_area_m2"])
                )
            )

    @staticmethod
    def _zoning_value(
        zoning,
        *names,
        default=Decimal("0"),
    ):
        for name in names:
            if hasattr(zoning, name):
                value = getattr(zoning, name)

                if value is not None:
                    return Decimal(str(value))

        return default

    def _validate_constraints(
        self,
        values: dict,
        site: SitePlan,
        zoning: ZoningRule,
    ) -> None:

        result = self._calculate_constraints(
            site=site,
            zoning=zoning,
            values=values,
        )

        if not result["overall_compliant"]:
            raise ValueError(
                "Floor plan violates planning constraints: "
                + "; ".join(result["violations"])
            )

    def _calculate_constraints(
        self,
        site: SitePlan,
        zoning: ZoningRule,
        values: dict,
    ):

        site_area = Decimal(
            str(site.site_area_m2)
        )

        maximum_coverage = self._zoning_value(
            zoning,
            "site_coverage_pct",
            "coverage_percent",
            "max_coverage_percent",
            "coverage",
        )

        maximum_far = self._zoning_value(
            zoning,
            "far",
            "max_far",
            "floor_area_ratio",
        )

        required_front = self._zoning_value(
            zoning,
            "front_setback_m",
            "front_setback",
            "setback_m",
        )

        required_rear = self._zoning_value(
            zoning,
            "rear_setback_m",
            "rear_setback",
            "setback_m",
        )

        required_side = self._zoning_value(
            zoning,
            "side_setback_m",
            "side_setback",
            "setback_m",
        )

        maximum_footprint = (
            site_area
            * maximum_coverage
            / Decimal("100")
        )

        maximum_gfa = (
            site_area
            * maximum_far
        )

        proposed_footprint = Decimal(
            str(values["building_footprint_m2"])
        )

        proposed_gfa = Decimal(
            str(values["gross_floor_area_m2"])
        )

        proposed_coverage = (
            proposed_footprint
            / site_area
            * Decimal("100")
        )

        proposed_far = (
            proposed_gfa
            / site_area
        )

        front = Decimal(
            str(values["front_setback_m"])
        )

        rear = Decimal(
            str(values["rear_setback_m"])
        )

        side = Decimal(
            str(values["side_setback_m"])
        )

        violations: list[str] = []

        site_area_ok = (
            proposed_footprint <= site_area
        )

        if not site_area_ok:
            violations.append(
                "Building footprint exceeds site area."
            )

        coverage_ok = (
            proposed_footprint
            <= maximum_footprint
        )

        if not coverage_ok:
            violations.append(
                "Building footprint exceeds "
                "maximum permitted site coverage."
            )

        far_ok = (
            proposed_far <= maximum_far
        )

        if not far_ok:
            violations.append(
                "Proposed FAR exceeds the zoning limit."
            )

        gfa_ok = (
            proposed_gfa <= maximum_gfa
        )

        if not gfa_ok:
            violations.append(
                "Gross floor area exceeds "
                "maximum permitted GFA."
            )

        setbacks_ok = (
            front >= required_front
            and rear >= required_rear
            and side >= required_side
        )

        if front < required_front:
            violations.append(
                "Front setback is below the zoning requirement."
            )

        if rear < required_rear:
            violations.append(
                "Rear setback is below the zoning requirement."
            )

        if side < required_side:
            violations.append(
                "Side setback is below the zoning requirement."
            )

        overall = all(
            (
                site_area_ok,
                coverage_ok,
                far_ok,
                gfa_ok,
                setbacks_ok,
            )
        )

        return {
            "site_area_m2": site_area,
            "maximum_coverage_percent": maximum_coverage,
            "maximum_footprint_m2": maximum_footprint,
            "proposed_footprint_m2": proposed_footprint,
            "proposed_coverage_percent": proposed_coverage,
            "maximum_far": maximum_far,
            "proposed_far": proposed_far,
            "maximum_gfa_m2": maximum_gfa,
            "proposed_gfa_m2": proposed_gfa,
            "required_front_setback_m": required_front,
            "required_rear_setback_m": required_rear,
            "required_side_setback_m": required_side,
            "proposed_front_setback_m": front,
            "proposed_rear_setback_m": rear,
            "proposed_side_setback_m": side,
            "setbacks_compliant": setbacks_ok,
            "site_area_compliant": site_area_ok,
            "coverage_compliant": coverage_ok,
            "far_compliant": far_ok,
            "gfa_compliant": gfa_ok,
            "overall_compliant": overall,
            "violations": violations,
        }

    def _build_constraint_result(
        self,
        floor_plan,
        site,
        zoning,
        values,
    ):

        result = self._calculate_constraints(
            site=site,
            zoning=zoning,
            values=values,
        )

        return FloorPlanConstraintResult(
            floor_plan_id=floor_plan.id,
            **result,
        )