"""
IMAGINE Costing Module

Foreign Exchange Engine

Version 24.1
"""


class ForexService:

    RATES = {

        "UGX": 3700.00,
        "KES": 129.49,
        "TZS": 2625.00,
        "RWF": 1350.00,
        "SSP": 4626.40,
        "USD": 1.0
    }

    @classmethod
    def convert_usd(
        cls,
        amount_usd,
        currency
    ):

        rate = cls.RATES.get(
            currency,
            1.0
        )

        return {

            "currency": currency,

            "exchange_rate": rate,

            "amount_local":
                round(
                    amount_usd * rate,
                    2
                )
        }

    @classmethod
    def supported_currencies(
        cls
    ):

        return list(
            cls.RATES.keys()
        )
