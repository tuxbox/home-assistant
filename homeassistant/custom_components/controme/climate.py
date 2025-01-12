"""Platform for Controme sensors."""

from __future__ import annotations

from datetime import timedelta
from logging import getLogger
from typing import Any

import voluptuous as vol

from homeassistant.components.climate import (
    PLATFORM_SCHEMA as CLIMATE_PLATFORM_SCHEMA,
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
    UnitOfTemperature,
)
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_HOME_ID, DOMAIN
from .controme_client import ContromeClient, ContromeThermostat
from .controme_coordinator import ContromeCoordinator, ContromeEntityType

_LOGGER = getLogger(__name__)
SCAN_INTERVAL = timedelta(minutes=15)

PLATFORM_SCHEMA = CLIMATE_PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=80): int,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_HOME_ID): str,
    }
)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""
    _LOGGER.debug("CONTROME---Setting up Controme climate platform (async)")
    _LOGGER.info("Setting up Controme climate platform (async)")
    hass.data.setdefault(DOMAIN, {})
    host = config[CONF_HOST]
    port = config[CONF_PORT]
    username = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]
    home_id = config[CONF_HOME_ID]

    session = async_create_clientsession(hass)
    client = ContromeClient(
        session=session,
        host=host,
        port=port,
        username=username,
        password=password,
        home_id=home_id,
    )
    coordinator = ContromeCoordinator(hass, client, type=ContromeEntityType.THERMOSTAT)
    await coordinator.async_config_entry_first_refresh()
    add_entities(
        [
            Thermostat(coordinator, client, thermostat)
            for thermostat in coordinator.data.values()
            if isinstance(thermostat, ContromeThermostat)
        ]
    )


class Thermostat(CoordinatorEntity, ClimateEntity):
    """Representation of a Sensor."""

    _attr_name = "Return Flow Temperature"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    # _attr_device_class = ClimateDeviceClass.THERMOSTAT
    # _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: ContromeCoordinator,
        client: ContromeClient,
        thermostat: ContromeThermostat,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, context=thermostat)
        _LOGGER.info(thermostat)
        self._thermostat = thermostat
        self._client = client
        self._attr_name = f"{thermostat.name}"
        self._attr_unique_id = f"{thermostat.id}-thermostat"
        self._attr_extra_state_attributes = {
            "floor": thermostat.floor,
            "room": thermostat.room,
            "last_updated": thermostat.last_updated,
        }
        self._attr_native_value = thermostat.state
        self._attr_target_temperature = thermostat.target_state
        self._attr_hvac_mode = HVACMode.HEAT
        self._attr_hvac_modes = [HVACMode.HEAT]
        self._attr_current_temperature = thermostat.state
        self._attr_max_temp = 30
        self._attr_min_temp = 10
        self._attr_target_temperature_high = 30
        self._attr_target_temperature_low = 10
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_target_temperature_step = 0.5
        self._attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs.get("temperature")
        if temperature is None:
            return
        await self._client.update_target_state(self._thermostat, float(temperature))
        await self.coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        entities: dict[str, Any] = self.coordinator.data
        data = entities.get(self._thermostat.id, None)
        if data is None:
            _LOGGER.error("No data found for thermostat %s", self._thermostat.id)
        else:
            self._attr_native_value = data.state
            self._attr_current_temperature = data.state
            self._attr_target_temperature = data.target_state
            self._attr_extra_state_attributes["last_updated"] = data.last_updated
        self.async_write_ha_state()
