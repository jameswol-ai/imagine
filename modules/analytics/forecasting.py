"""
Forecasting Engine
"""

class ForecastingService:

    @staticmethod
    def linear_forecast(
        current_value,
        growth_rate,
        periods
    ):

        results = []

        value = current_value

        for p in range(periods):

            value *= (1 + growth_rate)

            results.append(
                round(value, 2)
            )

        return results
