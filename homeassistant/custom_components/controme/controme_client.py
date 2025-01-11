"""Controme client."""


class ContromeClient:
    """Controme client."""

    def __init__(
        self, host: str, port: int, username: str, password: str, home_id: int
    ) -> None:
        """Initialize the client."""
        self._host = host
        self._port = port
        self._username = username
        self._password = password

    def get_sensors(self) -> list[str]:
        """Get all sensors."""
        return []

    def get_thermostats(self) -> list[str]:
        """Get all thermostats."""
        return []

    def get_sensor_value(self, sensor_id: str) -> float:
        """Get the value of the specified sensor_id."""
        return 0

    def set_target_value(self, sensor_id: str, value: float) -> None:
        """Set the target value of the specified sensor_id."""

    def set_current_value(self, sensor_id: str, value: float) -> None:
        """Set the current value of the specified sensor_id."""
