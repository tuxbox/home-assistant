"""the data update coordinator for the controme api."""

from datetime import timedelta
from logging import getLogger

from controme_client import ContromeClient, ContromeSensor

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = getLogger(__name__)


class ContromeCoordinator(DataUpdateCoordinator):
    """The data update coordinator for the controme api."""

    def __init__(self, hass: HomeAssistant, client: ContromeClient) -> None:
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
        self._client = client
        self._entities: list[ContromeSensor] = []

    async def _async_setup(self) -> None:
        """Set up the coordinator.

        This is the place to set up your coordinator,
        or to load data, that only needs to be loaded once.

        This method will be called automatically during
        coordinator.async_config_entry_first_refresh.
        """
        self._entities = self._client.get_entities()

    async def _async_update_data(self) -> dict[str, ContromeSensor]:
        """Fetch the latest data from the controme api."""
        self._entities = self._client.get_entities()
        result = {}
        result["controme"] = self._entities
        return result
