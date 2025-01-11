"""Support for Controme sensors."""

from typing import Any

from controme_client import ContromeClient

from homeassistant.helpers.entity import Entity


class ContromeSensor(Entity):
    """Representation of a Controme sensor."""

    def __init__(self, controme: ContromeClient, sensor_id: str, name: str) -> None:
        """Initialize the sensor."""
        self._controme = controme
        self._sensor_id = sensor_id
        self._name = name
        self._attrs: dict[str, Any] = {}
        self._state = None

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self._sensor_id

    @property
    def state(self) -> None:
        """Return the state of the sensor."""
        return self._state

    @property
    def device_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return self._attrs

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        await self._controme.async_update()
        self._state = self._controme.get_sensor_state(self._sensor_id)
