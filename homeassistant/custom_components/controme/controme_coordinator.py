"""the data update coordinator for the controme api."""

from datetime import timedelta
from enum import Enum
from logging import getLogger

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .controme_client import (
    ContromeClient,
    ContromeEntity,
    ContromeSensor,
    ContromeThermostat,
)

_LOGGER = getLogger(__name__)


class ContromeEntityType(Enum):
    """The type of entity to fetch from the controme api."""

    SENSOR = "sensor"
    THERMOSTAT = "thermostat"


class ContromeCoordinator(DataUpdateCoordinator):
    """The data update coordinator for the controme api."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: ContromeClient,
        type: ContromeEntityType = ContromeEntityType.SENSOR,
    ) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="Controme Sensors",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(minutes=15),
            # Set always_update to `False` if the data returned from the
            # api can be compared via `__eq__` to avoid duplicate updates
            # being dispatched to listeners
            always_update=True,
        )
        _LOGGER.info("Setting up controme coordinator")
        self._client = client
        self._entities: list[ContromeEntity] = []
        self._entity_type = type

    async def _async_setup(self) -> None:
        """Set up the coordinator.

        This is the place to set up your coordinator,
        or to load data, that only needs to be loaded once.

        This method will be called automatically during
        coordinator.async_config_entry_first_refresh.
        """
        _LOGGER.info("Async initial setup of the coordinator")
        self._entities = [
            entity
            for entity in await self._client.get_entities()
            if (
                isinstance(entity, ContromeThermostat)
                and self._entity_type == ContromeEntityType.THERMOSTAT
            )
            or (
                isinstance(entity, ContromeSensor)
                and self._entity_type == ContromeEntityType.SENSOR
            )
        ]

    async def _async_update_data(self) -> dict[str, ContromeSensor]:
        """Fetch the latest data from the controme api."""
        _LOGGER.info("Call to update data")
        self._entities = await self._client.get_entities()
        result = {}
        for entity in self._entities:
            if (
                isinstance(entity, ContromeThermostat)
                and self._entity_type == ContromeEntityType.THERMOSTAT
                or isinstance(entity, ContromeSensor)
                and self._entity_type == ContromeEntityType.SENSOR
            ):
                result[entity.id] = entity
            elif (
                isinstance(entity, ContromeThermostat)
                and self._entity_type == ContromeEntityType.SENSOR
            ):
                _LOGGER.error(
                    "Coordinator is set up for sensors, but got a thermostat entity"
                )
            elif (
                isinstance(entity, ContromeSensor)
                and self._entity_type == ContromeEntityType.THERMOSTAT
            ):
                _LOGGER.error(
                    "Coordinator is set up for thermostats, but got a sensor entity"
                )
            else:
                _LOGGER.error("Unknown entity type: %s", self._entity_type)
        return result
