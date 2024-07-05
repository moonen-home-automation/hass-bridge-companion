"""Event platform for gRPC Bridge."""

from collections.abc import Callable
from typing import Any

from homeassistant.components.event import EventEntity
from homeassistant.components.websocket_api.connection import ActiveConnection
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from . import BridgeEntity
from .const import (
    BRIDGE_ENTITY_EVENT,
    CONF_CONFIG,
    CONF_DEVICE_CLASS,
    CONF_EVENT_DATA,
    CONF_EVENT_TYPE,
    CONF_EVENT_TYPES,
    PLATFORM_EVENT,
)
from .discovery import BRIDGE_ENTITY_ADD_NEW


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,  # noqa: ARG001
    async_add_devices: Callable[[list[BridgeEntity]], None],
) -> None:
    """Set up binary sensor platform."""

    async def async_discovery(
        config: dict[str, Any],
        connection: ActiveConnection,  # noqa: ARG001
    ) -> None:
        await _async_setup_entity(hass, config, async_add_devices)

    async_dispatcher_connect(
        hass, BRIDGE_ENTITY_ADD_NEW.format(PLATFORM_EVENT), async_discovery
    )


async def _async_setup_entity(
    hass: HomeAssistant,
    config: dict[str, Any],
    async_add_devices: Callable[[list[BridgeEntity]], None],
) -> None:
    """Set up bridge binary sensor."""
    async_add_devices([BridgeEvent(hass, config)])


class BridgeEvent(BridgeEntity, EventEntity):
    """Event class."""

    def __init__(self, hass: HomeAssistant, config: dict[str, Any]) -> None:
        """Initialize the binary sensor."""
        self._attr_device_class = config.get(CONF_DEVICE_CLASS)
        types = config[CONF_CONFIG].get(CONF_EVENT_TYPES)
        assert types is not None  # noqa: S101
        self._attr_event_types = types
        super().__init__(hass, config)

    def update_discovery_config(self, msg: dict[str, Any]) -> None:
        """Update entity config."""
        super().update_discovery_config(msg)
        self._attr_device_class = msg[CONF_CONFIG].get(CONF_DEVICE_CLASS)
        types = msg[CONF_CONFIG].get(CONF_EVENT_TYPES)
        assert types is not None  # noqa: S101
        self._attr_event_types = types

    @callback
    def _async_handle_event(self, msg: dict[str, Any]) -> None:
        """Handle event firing."""
        self._trigger_event(msg[CONF_EVENT_TYPE], msg[CONF_EVENT_DATA])
        self.hass.bus.async_fire(msg[CONF_EVENT_TYPE], msg[CONF_EVENT_DATA])
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()

        self._remove_signal_entity_event = async_dispatcher_connect(
            self.hass,
            BRIDGE_ENTITY_EVENT.format(
                self._service_slug, self._device_slug, self._entity_slug
            ),
            self._async_handle_event,
        )
