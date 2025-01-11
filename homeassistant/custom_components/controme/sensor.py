"""Platform for Controme sensors."""

from __future__ import annotations

from logging import getLogger

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN

_LOGGER = getLogger(__name__)


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
    # add_entities([ExampleSensor()])


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
