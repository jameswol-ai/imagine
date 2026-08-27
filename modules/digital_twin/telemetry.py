"""
Telemetry Engine
"""

from datetime import datetime


class TelemetryService:

    @staticmethod
    def record(
        sensor_id,
        value,
        unit
    ):

        return {
            "sensor_id": sensor_id,
            "value": value,
            "unit": unit,
            "timestamp":
                datetime.utcnow().isoformat()
        }
