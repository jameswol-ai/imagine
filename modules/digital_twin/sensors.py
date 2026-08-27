"""
Sensor Registry
"""

import uuid


class SensorService:

    @staticmethod
    def create_sensor(
        sensor_type,
        location
    ):

        return {
            "id": str(uuid.uuid4()),
            "sensor_type": sensor_type,
            "location": location,
            "active": True
        }
