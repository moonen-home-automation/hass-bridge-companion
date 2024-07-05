"""Switch platform for grpc bridge."""

import logging
from collections.abc import Callable
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.components.websocket_api.connection import ActiveConnection
from homeassistant.components.websocket_api.messages import event_message
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_ICON,
    CONF_ID,
    CONF_STATE,
    CONF_TYPE,
    EVENT_STATE_CHANGED,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from . import BridgeStateEntity
from .const import BRIDGE_ENTITY_ADD_NEW, CONF_CONFIG, PLATFORM_SWITCH, SWITCH_ICON

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,  # noqa: ARG001
    async_add_devices: Callable[[list[BridgeStateEntity]], None],
) -> None:
    """Set up binary sensor platform."""

    async def async_discovery(
        config: dict[str, Any],
        connection: ActiveConnection,
    ) -> None:
        await _async_setup_entity(hass, config, async_add_devices, connection)

    async_dispatcher_connect(
        hass, BRIDGE_ENTITY_ADD_NEW.format(PLATFORM_SWITCH), async_discovery
    )


async def _async_setup_entity(
    hass: HomeAssistant,
    config: dict[str, Any],
    async_add_devices: Callable[[list[BridgeStateEntity]], None],
    connection: ActiveConnection,
) -> None:
    """Set up bridge binary sensor."""
    async_add_devices([BridgeSwitch(hass, config, connection)])


class BridgeSwitch(BridgeStateEntity, SwitchEntity):
    """gRPC Bridge Switch class."""

    _platform = PLATFORM_SWITCH
    _bidirectional = True

    def __init__(
        self, hass: HomeAssistant, config: dict[str, Any], connection: ActiveConnection
    ) -> None:
        """Initialize the switch platform."""
        super().__init__(hass, config)
        self._message_id = config[CONF_ID]
        self._connection = connection

        self._attr_state = config.get(CONF_STATE, True)
        self._attr_icon = self._config.get(CONF_ICON)

    @property
    def is_on(self) -> bool | None:
        """Return the state of the switch."""
        return self._attr_state

    async def async_turn_off(self, **kwargs: dict[str, Any]) -> None:  # noqa: ARG002
        """Turn off the switch."""
        self._update_bridge(state=False)

    async def async_turn_on(self, **kwargs: dict[str, Any]) -> None:  # noqa: ARG002
        """Turn on the switch."""
        self._update_bridge(state=True)

    def _update_bridge(self, state: bool) -> None:  # noqa: FBT001
        """Update the bridge through websocket."""
        self._connection.send_message(
            event_message(
                self._message_id, {CONF_TYPE: EVENT_STATE_CHANGED, CONF_STATE: state}
            )
        )

    def update_entity_state_attributes(self, msg: dict[str, Any]) -> None:
        """Update entity state atrributes."""
        self._attr_state = msg.get(CONF_STATE)
        super().update_entity_state_attributes(msg)

    def update_discovery_config(self, msg: dict[str, Any]) -> None:
        """Update the entity config."""
        super().update_discovery_config(msg)
        self._attr_icon = msg[CONF_CONFIG].get(CONF_ICON, SWITCH_ICON)
