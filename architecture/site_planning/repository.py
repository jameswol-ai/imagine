"""
IMAGINE Site Planning repository.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import SitePlan


class SitePlanningRepository:
    """
    Persistence layer for Site Planning.

    The repository deliberately receives a SQLAlchemy session
    rather than creating its own connection.
    """

    def __init__(
        self,
        db: Session | None = None,
    ) -> None:

        self.db = db

    # ========================================================
    # SESSION
    # ========================================================

    def _require_db(self) -> Session:

        if self.db is None:

            raise RuntimeError(
                "SitePlanningRepository requires a database session."
            )

        return self.db

    # ========================================================
    # LIST
    # ========================================================

    def list(
        self,
    ) -> list[SitePlan]:

        db = self._require_db()

        statement = (
            select(SitePlan)
            .order_by(SitePlan.id)
        )

        return list(
            db.scalars(statement).all()
        )

    # ========================================================
    # GET
    # ========================================================

    def get(
        self,
        site_plan_id: Any,
    ) -> SitePlan | None:

        db = self._require_db()

        return db.get(
            SitePlan,
            site_plan_id,
        )

    # ========================================================
    # CREATE
    # ========================================================

    def create(
        self,
        site_plan: SitePlan,
    ) -> SitePlan:

        db = self._require_db()

        db.add(site_plan)

        db.commit()

        db.refresh(site_plan)

        return site_plan

    # ========================================================
    # UPDATE
    # ========================================================

    def update(
        self,
        site_plan: SitePlan,
        values: dict[str, Any],
    ) -> SitePlan:

        db = self._require_db()

        for key, value in values.items():

            if hasattr(site_plan, key):

                setattr(
                    site_plan,
                    key,
                    value,
                )

        db.commit()

        db.refresh(site_plan)

        return site_plan

    # ========================================================
    # DELETE
    # ========================================================

    def delete(
        self,
        site_plan: SitePlan,
    ) -> None:

        db = self._require_db()

        db.delete(site_plan)

        db.commit()