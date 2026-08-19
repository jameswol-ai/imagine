"""
IMAGINE
Site Planning Service

Provides the asynchronous Site Planning domain service used by
the API and a synchronous adapter used by Streamlit and other
synchronous callers.
"""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Awaitable, Callable
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import AsyncSessionLocal

from .models import SitePlan
from .repository import SitePlanRepository
from .schemas import SitePlanCreate, SitePlanUpdate


class SitePlanService:
    """
    Application service for Site Planning.

    The primary service API is asynchronous.

    Synchronous adapters are provided separately for Streamlit:

        list_sync()
        create_sync()
        update_sync()
        delete_sync()
        summary_sync()
    """

    def __init__(self, session: AsyncSession):
        self.repo = SitePlanRepository(session)

    # ========================================================
    # ASYNC API
    # ========================================================

    async def list(
        self,
        project_id: UUID | None = None,
        active_only: bool = False,
    ) -> list[SitePlan]:
        """
        List site plans.

        Parameters
        ----------
        project_id:
            Optional project filter.

        active_only:
            When True, return only active site plans.
        """

        return await self.repo.list(
            project_id=project_id,
            active_only=active_only,
        )

    async def get(
        self,
        site_plan_id: UUID,
    ) -> SitePlan | None:
        """Return a site plan by ID."""

        return await self.repo.get(
            site_plan_id
        )

    async def create(
        self,
        payload: SitePlanCreate,
    ) -> SitePlan:
        """
        Create a site plan.

        Business rules are validated before persistence.
        """

        existing = await self.repo.get_by_code(
            payload.site_code
        )

        if existing:
            raise ValueError(
                "Site plan code already exists: "
                f"{payload.site_code}"
            )

        values = payload.model_dump()

        self._validate_area_allocation(
            values
        )

        site_plan = SitePlan(
            **values
        )

        return await self.repo.create(
            site_plan
        )

    async def update(
        self,
        site_plan_id: UUID,
        payload: SitePlanUpdate,
    ) -> SitePlan:
        """
        Update an existing site plan.

        Area allocation is validated against the merged
        existing/new values.
        """

        obj = await self.repo.get(
            site_plan_id
        )

        if not obj:
            raise LookupError(
                "Site plan not found"
            )

        values = payload.model_dump(
            exclude_unset=True
        )

        # ----------------------------------------------------
        # Validate unique site code
        # ----------------------------------------------------

        if "site_code" in values:

            existing = await self.repo.get_by_code(
                values["site_code"]
            )

            if (
                existing
                and existing.id != obj.id
            ):
                raise ValueError(
                    "Site plan code already exists: "
                    f"{values['site_code']}"
                )

        # ----------------------------------------------------
        # Merge existing allocation values with changes
        # ----------------------------------------------------

        merged = {
            key: getattr(
                obj,
                key,
            )
            for key in (
                "site_area_m2",
                "building_footprint_m2",
                "road_area_m2",
                "parking_area_m2",
                "landscape_area_m2",
            )
        }

        merged.update(
            values
        )

        self._validate_area_allocation(
            merged
        )

        return await self.repo.update(
            obj,
            values,
        )

    async def delete(
        self,
        site_plan_id: UUID,
    ) -> None:
        """Delete a site plan."""

        obj = await self.repo.get(
            site_plan_id
        )

        if not obj:
            raise LookupError(
                "Site plan not found"
            )

        await self.repo.delete(
            obj
        )

    async def summary(
        self,
    ) -> dict[str, Any]:
        """Return Site Planning summary statistics."""

        return await self.repo.summary()

    # ========================================================
    # SYNCHRONOUS EXECUTION BRIDGE
    # ========================================================

    @staticmethod
    def _run_sync(
        operation: Callable[
            [AsyncSession],
            Awaitable[Any],
        ],
    ) -> Any:
        """
        Execute an asynchronous database operation from
        synchronous code.

        This is primarily intended for Streamlit.

        A fresh AsyncSession is created for every operation.

        Successful operations are committed.

        Failed operations are rolled back.

        If Streamlit or another synchronous caller happens to
        execute while an asyncio event loop is already running,
        the coroutine is executed in a separate worker thread
        instead of attempting to nest asyncio.run().
        """

        async def runner() -> Any:

            async with AsyncSessionLocal() as session:

                try:

                    result = await operation(
                        session
                    )

                    await session.commit()

                    return result

                except Exception:

                    await session.rollback()

                    raise

        # ----------------------------------------------------
        # Normal synchronous execution
        # ----------------------------------------------------

        try:

            asyncio.get_running_loop()

        except RuntimeError:

            return asyncio.run(
                runner()
            )

        # ----------------------------------------------------
        # An event loop is already running.
        #
        # Execute the complete async operation in a separate
        # thread with its own event loop.
        # ----------------------------------------------------

        with ThreadPoolExecutor(
            max_workers=1
        ) as executor:

            future = executor.submit(
                asyncio.run,
                runner(),
            )

            return future.result()

    # ========================================================
    # PAYLOAD CONVERSION
    # ========================================================

    @staticmethod
    def _coerce_create_payload(
        payload: SitePlanCreate | dict[str, Any],
    ) -> SitePlanCreate:
        """
        Convert a dictionary into SitePlanCreate.

        Existing SitePlanCreate objects are returned unchanged.
        """

        if isinstance(
            payload,
            SitePlanCreate,
        ):
            return payload

        return SitePlanCreate.model_validate(
            payload
        )

    @staticmethod
    def _coerce_update_payload(
        payload: SitePlanUpdate | dict[str, Any],
    ) -> SitePlanUpdate:
        """
        Convert a dictionary into SitePlanUpdate.

        Existing SitePlanUpdate objects are returned unchanged.
        """

        if isinstance(
            payload,
            SitePlanUpdate,
        ):
            return payload

        return SitePlanUpdate.model_validate(
            payload
        )

    # ========================================================
    # STREAMLIT SYNC ADAPTERS
    # ========================================================

    def list_sync(
        self,
        project_id: UUID | None = None,
        active_only: bool = False,
    ) -> list[SitePlan]:
        """
        Synchronous adapter for SitePlanService.list().

        Intended for Streamlit and other synchronous callers.
        """

        return self._run_sync(
            lambda session:
                SitePlanService(
                    session
                ).list(
                    project_id=project_id,
                    active_only=active_only,
                )
        )

    def create_sync(
        self,
        payload: SitePlanCreate | dict[str, Any],
    ) -> SitePlan:
        """
        Synchronous adapter for SitePlanService.create().
        """

        validated_payload = (
            self._coerce_create_payload(
                payload
            )
        )

        return self._run_sync(
            lambda session:
                SitePlanService(
                    session
                ).create(
                    validated_payload
                )
        )

    def update_sync(
        self,
        site_plan_id: UUID,
        payload: SitePlanUpdate | dict[str, Any],
    ) -> SitePlan:
        """
        Synchronous adapter for SitePlanService.update().
        """

        validated_payload = (
            self._coerce_update_payload(
                payload
            )
        )

        return self._run_sync(
            lambda session:
                SitePlanService(
                    session
                ).update(
                    site_plan_id,
                    validated_payload,
                )
        )

    def delete_sync(
        self,
        site_plan_id: UUID,
    ) -> None:
        """
        Synchronous adapter for SitePlanService.delete().
        """

        return self._run_sync(
            lambda session:
                SitePlanService(
                    session
                ).delete(
                    site_plan_id
                )
        )

    def summary_sync(
        self,
    ) -> dict[str, Any]:
        """
        Synchronous adapter for SitePlanService.summary().
        """

        return self._run_sync(
            lambda session:
                SitePlanService(
                    session
                ).summary()
        )

    # ========================================================
    # BUSINESS VALIDATION
    # ========================================================

    @staticmethod
    def _validate_area_allocation(
        values: dict[str, Any],
    ) -> None:
        """
        Ensure allocated site areas do not exceed total site area.

        The following allocations are checked:

            building footprint
            roads
            parking
            landscaping
        """

        site_area = values[
            "site_area_m2"
        ]

        allocated_area = sum(
            values.get(
                key,
                0,
            )
            or 0
            for key in (
                "building_footprint_m2",
                "road_area_m2",
                "parking_area_m2",
                "landscape_area_m2",
            )
        )

        if allocated_area > site_area:

            raise ValueError(
                "Building, road, parking and "
                "landscape areas cannot exceed "
                "site area"
            )