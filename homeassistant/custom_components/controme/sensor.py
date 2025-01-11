"""Platform for Controme sensors."""

from __future__ import annotations

from datetime import timedelta
from logging import getLogger

import voluptuous as vol

from homeassistant.components.sensor import (
    PLATFORM_SCHEMA as SENSOR_PLATFORM_SCHEMA,
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
    UnitOfTemperature,
)
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import CONF_HOME_ID, DOMAIN
from .controme_client import ContromeClient, ContromeSensor, ContromeThermostat

_LOGGER = getLogger(__name__)
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=1)

PLATFORM_SCHEMA = SENSOR_PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=80): int,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_HOME_ID): str,
    }
)


# async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
#    """Set up homeassistant-controme from a config entry."""
#
#    _LOGGER.info("Setting up controme integration")
#    # client = await hass.async_add_executor_job(create_and_update_instance, entry)
#
#    # entry.async_on_unload(entry.add_update_listener(update_listener))
#
#    hass.data.setdefault(DOMAIN, {})
#
#    _LOGGER.info(entry.data)
#    # hass.data[DOMAIN][entry.entry_id] = client
#
#    # await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
#
#    return True


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""
    _LOGGER.info("Setting up Controme sensor platform")
    hass.data.setdefault(DOMAIN, {})
    host = config[CONF_HOST]
    port = config[CONF_PORT]
    username = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]
    home_id = config[CONF_HOME_ID]
    client = ContromeClient(host, port, username, password, home_id)
    entities = client.get_entities()
    _LOGGER.info("Loaded entities")
    _LOGGER.info(len(entities))
    controme_sensors = [
        ReturnFlowSensor(entity, client)
        for entity in entities
        if isinstance(entity, ContromeSensor)
        and not isinstance(entity, ContromeThermostat)
    ]
    add_entities(controme_sensors)


class ReturnFlowSensor(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "Return Flow Temperature"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, sensor: ContromeSensor, client: ContromeClient) -> None:
        """Initialize the sensor entity.

        Args:
            sensor (ContromeSensor): The sensor object containing sensor details.
            client (ContromeClient): The client object for interacting with the Controme API.

        Attributes:
            _sensor (ContromeSensor): Stores the sensor object.
            _client (ContromeClient): Stores the client object.
            _attr_name (str): The name attribute for the sensor entity.
            _attr_unique_id (str): The unique ID attribute for the sensor entity.
            _attr_extra_state_attributes (dict): Additional state attributes for the sensor entity, including floor, room, and last updated information.

        """
        super().__init__()
        self._sensor = sensor
        self._client = client
        self._attr_name = f"Return Flow: {sensor.name}"
        self._attr_unique_id = f"{sensor.id}-return-flow"
        self._attr_extra_state_attributes = {
            "floor": sensor.floor,
            "room": sensor.room,
            "last_updated": sensor.last_updated,
        }
        self._attr_native_value = sensor.state

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        room_entities = self._client.get_entities(room_id=self._sensor.room)
        state = next(
            (entity.state for entity in room_entities if entity.id == self._sensor.id),
            None,
        )
        last_updated = next(
            (
                entity.last_updated
                for entity in room_entities
                if entity.id == self._sensor.id
            ),
            None,
        )
        self._attr_native_value = 0.0 if state is None else state
        self._attr_extra_state_attributes["last_updated"] = (
            "n/a" if last_updated is None else last_updated
        )


# class ExampleSensor(SensorEntity):
#    """Representation of a Sensor."""
#
#    _attr_name = "Example Temperature"
#    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
#    _attr_device_class = SensorDeviceClass.TEMPERATURE
#    _attr_state_class = SensorStateClass.MEASUREMENT
#
#    def update(self) -> None:
#        """Fetch new state data for the sensor.
#
#        This is the only method that should fetch new data for Home Assistant.
#        """
#        self._attr_native_value = 23


# """The homeassistant-controme integration."""
#
# from __future__ import annotations
#
# from datetime import timedelta
# import logging
#
# from common.controme_client import ContromeClient
#
# from homeassistant.config_entries import ConfigEntry
# from homeassistant.const import Platform
# from homeassistant.core import HomeAssistant
# from homeassistant.helpers import device_registry as dr, entity_registry as er
# from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceRegistry
#
# from .const import (
#    CONST_HOME_ID,
#    CONST_HOST,
#    CONST_PASSWORD,
#    CONST_PORT,
#    CONST_USERNAME,
#    DOMAIN,
#    PLATFORMS,
# )
#
# _LOGGER = logging.getLogger(__name__)
# MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=1)
#
## TO-DO Create ConfigEntry type alias with API object
## TO-DO Rename type alias and update all entry annotations
## type New_NameConfigEntry = ConfigEntry[MyApi]  # noqa: F821
#
#
## TO-DO Update entry annotation
# async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
#    """Set up homeassistant-controme from a config entry."""
#
#    _LOGGER.info("Setting up controme integration")
#    client = await hass.async_add_executor_job(create_and_update_instance, entry)
#
#    entry.async_on_unload(entry.add_update_listener(update_listener))
#
#    hass.data.setdefault(DOMAIN, {})
#
#    hass.data[DOMAIN][entry.entry_id] = client
#
#    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
#
#    return True
#
#
# def create_and_update_instance(entry: ConfigEntry) -> ContromeClient:
#    _LOGGER.info(f"Creating Controme Client for '{host}' and home '{home_id}'")
#    client = ContromeClient(
#        entry.data[CONST_HOST],
#        entry.data[CONST_PORT],
#        entry.data[CONST_USERNAME],
#        entry.data[CONST_PASSWORD],
#        entry.data[CONST_HOME_ID],
#    )
#    client.load_entities()
#    return client
#
#
# async def update_listener(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
#    """Handle options update."""
#
#    await hass.config_entries.async_reload(config_entry.entry_id)
#
#    registry = er.async_get(hass)
#    entities = er.async_entries_for_config_entry(registry, config_entry.entry_id)
#
#    # Remove orphaned entities
#    # for entity in entities:
#    #    currency = entity.unique_id.split("-")[-1]
#    #    if (
#    #        "xe" in entity.unique_id
#    #        and currency not in config_entry.options.get(CONF_EXCHANGE_RATES, [])
#    #        or "wallet" in entity.unique_id
#    #        and currency not in config_entry.options.get(CONF_CURRENCIES, [])
#    #    ):
#    #        registry.async_remove(entity.entity_id)
#
#
# async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
#    """Unload a config entry."""
#    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
#    if unload_ok:
#        hass.data[DOMAIN].pop(entry.entry_id)
#    return unload_ok
#
