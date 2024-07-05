"""Sensor platform for gRPC Bridge."""

import logging
from collections.abc import Callable
from datetime import datetime
from typing import Any

from dateutil import parser
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor.const import SensorDeviceClass
from homeassistant.components.websocket_api.connection import ActiveConnection
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_STATE, CONF_UNIT_OF_MEASUREMENT, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from . import BridgeStateEntity
from .const import (
    BRIDGE_ENTITY_ADD_NEW,
    CONF_CONFIG,
    CONF_LAST_RESET,
    CONF_STATE_CLASS,
    PLATFORM_SENSOR,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,  # noqa: ARG001
    async_add_entities: Callable[[list[BridgeStateEntity]], None],
) -> None:
    """Set up sensor platform."""

    async def async_discover(
        config: dict[str, Any],
        connection: ActiveConnection,  # noqa: ARG001
    ) -> None:
        await _async_setup_entity(hass, config, async_add_entities)

    async_dispatcher_connect(
        hass,
        BRIDGE_ENTITY_ADD_NEW.format(PLATFORM_SENSOR),
        async_discover,
    )


async def _async_setup_entity(
    hass: HomeAssistant,
    config: dict[str, Any],
    async_add_entities: Callable[[list[BridgeStateEntity]], None],
) -> None:
    """Set up the gRPC bridge sensor."""
    async_add_entities([BridgeSensor(hass, config)])


class BridgeSensor(BridgeStateEntity, SensorEntity):
    """gRPC Bridge sensor class."""

    _platform = PLATFORM_SENSOR

    def __init__(self, hass: HomeAssistant, config: dict[str, Any]) -> None:
        """Initialize the sensor."""
        super().__init__(hass, config)
        self._attr_unit_of_measurement = None
        self._attr_native_value = self.convert_state(config.get(CONF_STATE))
        self._attr_native_unit_of_measurement = self._config.get(
            CONF_UNIT_OF_MEASUREMENT
        )
        self._attr_state_class = self._config.get(CONF_STATE_CLASS)

    @property
    def last_reset(self) -> datetime | None:
        """Return the last reset."""
        reset = self._config.get(CONF_LAST_RESET)
        if reset is not None:
            try:
                return parser.parse(reset)
            except (ValueError, TypeError):
                _LOGGER.error(  # noqa: TRY400
                    "Invalid ISO date string (%s): %s requires last_reset to be an iso date formatted string",  # noqa: E501
                    reset,
                    self.entity_id,
                )
        return None

    def convert_state(
        self, state: Any | None
    ) -> datetime | float | int | str | bool | None:
        """Convert state if needed."""
        if state is not None and self.device_class in [
            SensorDeviceClass.TIMESTAMP,
            SensorDeviceClass.DATE,
        ]:
            try:
                return parser.parse(state)
            except (ValueError, TypeError):
                _LOGGER.error(  # noqa: TRY400
                    "Invalid ISO date string (%s): %s has a timestamp device class",
                    state,
                    self.entity_id,
                )
                return None

        return state

    def update_entity_state_attributes(self, msg: dict[str, Any]) -> None:
        """Update entity state attributes."""
        super().update_entity_state_attributes(msg)
        self._attr_native_value = self.convert_state(msg.get(CONF_STATE))

    def update_discovery_config(self, msg: dict[str, Any]) -> None:
        """Update entity config."""
        super().update_discovery_config(msg)
        self._attr_native_unit_of_measurement = msg[CONF_CONFIG].get(
            CONF_UNIT_OF_MEASUREMENT
        )
        self._attr_unit_of_measurement = None
        self._attr_state_class = msg[CONF_CONFIG].get(CONF_STATE_CLASS)

    def entity_category_mapper(self, category: str) -> EntityCategory | None:
        """Map bridge category to Home Assistant entity category."""
        if category == "config":
            _LOGGER.warning(
                "Sensor %s has category 'config' which is not supported", self.name
            )
        if category == "diagnostic":
            return EntityCategory.DIAGNOSTIC
        return None
