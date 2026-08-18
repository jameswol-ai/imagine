"""
IMAGINE Cost Engineering Module

Bill of Quantities (BoQ)
Forex Conversion
Cost Planning

Version 24.1
"""

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class BoQItem:
    section: str
    description: str
    quantity: float
    unit: str
    rate_usd: float

    @property
    def amount_usd(self) -> float:
        return round(
            self.quantity * self.rate_usd,
            2
        )


class BoQEngine:

    # ----------------------------------------
    # Regional Cost Settings
    # ----------------------------------------

    REGIONAL_FACTORS = {
        "Uganda": {
            "currency": "UGX",
            "rate_to_usd": 3700.00,
            "multiplier": 0.95,
            "risk": 0.03
        },
        "Kenya": {
            "currency": "KES",
            "rate_to_usd": 129.49,
            "multiplier": 1.00,
            "risk": 0.02
        },
        "Tanzania": {
            "currency": "TZS",
            "rate_to_usd": 2625.00,
            "multiplier": 0.98,
            "risk": 0.025
        },
        "South Sudan": {
            "currency": "SSP",
            "rate_to_usd": 4626.40,
            "multiplier": 1.35,
            "risk": 0.08
        }
    }

    # ----------------------------------------
    # Building Cost Plan
    # ----------------------------------------

    @staticmethod
    def generate_cost_plan(
        gross_floor_area: float
    ) -> Listreturn [

            BoQItem(
                section="1.0",
                description="Substructure",
                quantity=gross_floor_area,
                unit="m²",
                rate_usd=150
            ),

            BoQItem(
                section="2.0",
                description="Superstructure",
                quantity=gross_floor_area,
                unit="m²",
                rate_usd=420
            ),

            BoQItem(
                section="3.0",
                description="MEP Services",
                quantity=gross_floor_area,
                unit="m²",
                rate_usd=210
            ),

            BoQItem(
                section="4.0",
                description="Finishes",
                quantity=gross_floor_area,
                unit="m²",
                rate_usd=180
            )
        ]

    # ----------------------------------------
    # Total USD Cost
    # ----------------------------------------

    @staticmethod
    def total_cost_usd(
        items: List[BoQItem]
    ) -> float:

        return round(
            sum(
                item.amount_usd
                for item in items
            ),
            2
        )

    # ----------------------------------------
    # Country Adjustments
    # ----------------------------------------

    @classmethod
    def adjusted_project_cost(
        cls,
        total_usd: float,
        country: str
    ) -> dict:

        factor = cls.REGIONAL_FACTORS.get(
            country,
            cls.REGIONAL_FACTORS["Uganda"]
        )

        adjusted = (
            total_usd
            *
            factor["multiplier"]
            *
            (1 + factor["risk"])
        )

        return {
            "country": country,
            "currency": factor["currency"],
            "usd_cost": round(
                adjusted,
                2
            ),
            "local_cost": round(
                adjusted *
                factor["rate_to_usd"],
                2
            ),
            "exchange_rate": factor["rate_to_usd"]
        }

    # ----------------------------------------
    # Cost Summary
    # ----------------------------------------

    @classmethod
    def project_estimate(
        cls,
        gross_floor_area: float,
        country: str
    ) -> Dict:

        items = cls.generate_cost_plan(
            gross_floor_area
        )

        total_usd = cls.total_cost_usd(
            items
        )

        adjusted = cls.adjusted_project_cost(
            total_usd,
            country
        )

        return {
            "gross_floor_area": gross_floor_area,
            "boq_items": [
                {
                    "section": item.section,
                    "description": item.description,
                    "quantity": item.quantity,
                    "unit": item.unit,
                    "rate_usd": item.rate_usd,
                    "amount_usd": item.amount_usd
                }
                for item in items
            ],
            "summary": adjusted
        }

    # ----------------------------------------
    # Procurement Package Builder
    # ----------------------------------------

    @staticmethod
    def procurement_packages():

        return [

            {
                "package": "PKG-001",
                "name": "Substructure Works"
            },

            {
                "package": "PKG-002",
                "name": "Structural Frame"
            },

            {
                "package": "PKG-003",
                "name": "MEP Installations"
            },

            {
                "package": "PKG-004",
                "name": "Architectural Finishes"
            }

        ]
