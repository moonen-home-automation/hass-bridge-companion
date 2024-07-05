"""Binary sensor platform for gRPC Bridge."""

from collections.abc import Callable
from numbers import Number
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.websocket_api.connection import ActiveConnection
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_HOME, STATE_ON, STATE_OPEN, STATE_UNLOCKED
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from . import BridgeStateEntity
from .const import CONF_STATE, PLATFORM_BINARY_SENSOR
from .discovery import BRIDGE_ENTITY_ADD_NEW


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,  # noqa: ARG001
    async_add_devices: Callable[[list[BridgeStateEntity]], None],
) -> None:
    """Set up binary sensor platform."""

    async def async_discovery(
        config: dict[str, Any],
        connection: ActiveConnection,  # noqa: ARG001
    ) -> None:
        await _async_setup_entity(hass, config, async_add_devices)

    async_dispatcher_connect(
        hass, BRIDGE_ENTITY_ADD_NEW.format(PLATFORM_BINARY_SENSOR), async_discovery
    )


async def _async_setup_entity(
    hass: HomeAssistant,
    config: dict[str, Any],
    async_add_devices: Callable[[list[BridgeStateEntity]], None],
) -> None:
    """Set up bridge binary sensor."""
    async_add_devices([BridgeBinarySensor(hass, config)])


class BridgeBinarySensor(BridgeStateEntity, BinarySensorEntity):
    """Bridge binary sensor class."""

    on_states = (
        "1",
        "true",
        "yes",
        "enable",
        STATE_ON,
        STATE_OPEN,
        STATE_HOME,
        STATE_UNLOCKED,
    )
    _platform = PLATFORM_BINARY_SENSOR

    def __init__(self, hass: HomeAssistant, config: dict[str, Any]) -> None:
        """Initialize the binary sensor."""
        self._attr_state = config.get(CONF_STATE)
        super().__init__(hass, config)

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        value = self._attr_state

        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            value = value.lower().strip()
            if value in BridgeBinarySensor.on_states:
                return True
        elif isinstance(value, Number):
            return value != 0

        return False

    def update_entity_state_attributes(self, msg: dict[str, Any]) -> None:
        """Update entity state atrributes."""
        self._attr_state = msg.get(CONF_STATE)
        super().update_entity_state_attributes(msg)
