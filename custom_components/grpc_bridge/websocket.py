"""WebSocket API for gRPC Bridge."""

from typing import Any

import voluptuous as vol
from homeassistant.components.websocket_api import (
    async_register_command,
)
from homeassistant.components.websocket_api.connection import ActiveConnection
from homeassistant.components.websocket_api.decorators import (
    async_response,
    require_admin,
    websocket_command,
)
from homeassistant.components.websocket_api.messages import (
    result_message,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import (
    config_validation as cv,
)
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.entity_registry import async_get

from .const import (
    BRIDGE_ENTITY_ADD,
    BRIDGE_ENTITY_AVAILABLE,
    BRIDGE_ENTITY_CONFIG,
    BRIDGE_ENTITY_EVENT,
    BRIDGE_ENTITY_STATE,
    CONF_ATTRIBUTES,
    CONF_AVAILABLE,
    CONF_CONFIG,
    CONF_DEVICE_INFO,
    CONF_DEVICE_SLUG,
    CONF_ENTITY_SLUG,
    CONF_EVENT_DATA,
    CONF_EVENT_TYPE,
    CONF_ID,
    CONF_PLATFORM,
    CONF_REMOVE,
    CONF_SERVICE_SLUG,
    CONF_STATE,
    CONF_TYPE,
    DOMAIN,
)


def register_websocket_handlers(hass: HomeAssistant) -> None:
    """Register the websocket handlers."""
    async_register_command(hass, websocket_entity_remove)
    async_register_command(hass, websocket_entity_available)
    async_register_command(hass, websocket_entity_add)
    async_register_command(hass, websocket_entity_state)
    async_register_command(hass, websocket_entity_config)
    async_register_command(hass, websocket_entity_event)


@require_admin
@websocket_command(
    {
        vol.Required(CONF_TYPE): "bridge/entity/remove",
        vol.Required(CONF_SERVICE_SLUG): cv.string,
        vol.Required(CONF_DEVICE_SLUG): cv.string,
        vol.Required(CONF_ENTITY_SLUG): cv.string,
        vol.Required(CONF_PLATFORM): cv.string,
    }
)
@async_response
async def websocket_entity_remove(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle the removal of an entity."""
    entity_registry = async_get(hass)
    entity_id = entity_registry.async_get_entity_id(
        DOMAIN,
        msg[CONF_PLATFORM],
        f"{DOMAIN}-{msg[CONF_SERVICE_SLUG]}-{msg[CONF_DEVICE_SLUG]}-{msg[CONF_ENTITY_SLUG]}",
    )
    assert entity_id is not None  # noqa: S101
    entity_registry.async_remove(entity_id)

    connection.send_message(result_message(msg[CONF_ID]))


@require_admin
@websocket_command(
    {
        vol.Required(CONF_TYPE): "bridge/entity/available",
        vol.Required(CONF_SERVICE_SLUG): cv.string,
        vol.Required(CONF_DEVICE_SLUG): cv.string,
        vol.Required(CONF_ENTITY_SLUG): cv.string,
        vol.Required(CONF_AVAILABLE): cv.boolean,
    }
)
def websocket_entity_available(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle availability update of entity."""
    async_dispatcher_send(
        hass,
        BRIDGE_ENTITY_AVAILABLE.format(
            msg[CONF_SERVICE_SLUG], msg[CONF_DEVICE_SLUG], msg[CONF_ENTITY_SLUG]
        ),
        msg,
    )
    connection.send_message(result_message(msg[CONF_ID]))


@require_admin
@websocket_command(
    {
        vol.Required(CONF_TYPE): "bridge/entity/add",
        vol.Required(CONF_SERVICE_SLUG): cv.string,
        vol.Required(CONF_DEVICE_SLUG): cv.string,
        vol.Required(CONF_ENTITY_SLUG): cv.string,
        vol.Required(CONF_PLATFORM): cv.string,
        vol.Required(CONF_DEVICE_INFO): dict,
        vol.Required(CONF_CONFIG): dict,
        vol.Optional(CONF_REMOVE): bool,
        vol.Optional(CONF_STATE): vol.Any(bool, str, int, float, None),
        vol.Optional(CONF_ATTRIBUTES): dict,
    }
)
def websocket_entity_add(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """Handle the adding of a new entity."""
    async_dispatcher_send(
        hass, BRIDGE_ENTITY_ADD.format(msg[CONF_PLATFORM]), msg, connection
    )
    connection.send_message(result_message(msg[CONF_ID]))


@require_admin
@websocket_command(
    {
        vol.Required(CONF_TYPE): "bridge/entity/state",
        vol.Required(CONF_SERVICE_SLUG): cv.string,
        vol.Required(CONF_DEVICE_SLUG): cv.string,
        vol.Required(CONF_ENTITY_SLUG): cv.string,
        vol.Optional(CONF_STATE): vol.Any(bool, str, int, float, None),
        vol.Optional(CONF_ATTRIBUTES): dict,
    }
)
def websocket_entity_state(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """Handle an entity state update."""
    async_dispatcher_send(
        hass,
        BRIDGE_ENTITY_STATE.format(
            msg[CONF_SERVICE_SLUG], msg[CONF_DEVICE_SLUG], msg[CONF_ENTITY_SLUG]
        ),
        msg,
    )
    connection.send_message(result_message(msg[CONF_ID]))


@require_admin
@websocket_command(
    {
        vol.Required(CONF_TYPE): "bridge/entity/config",
        vol.Required(CONF_SERVICE_SLUG): cv.string,
        vol.Required(CONF_DEVICE_SLUG): cv.string,
        vol.Required(CONF_ENTITY_SLUG): cv.string,
        vol.Optional(CONF_CONFIG): dict,
    }
)
def websocket_entity_config(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """Handle an entity config update."""
    async_dispatcher_send(
        hass,
        BRIDGE_ENTITY_CONFIG.format(
            msg[CONF_SERVICE_SLUG], msg[CONF_DEVICE_SLUG], msg[CONF_ENTITY_SLUG]
        ),
        msg,
    )
    connection.send_message(result_message(msg[CONF_ID]))


@require_admin
@websocket_command(
    {
        vol.Required(CONF_TYPE): "bridge/entity/event",
        vol.Required(CONF_SERVICE_SLUG): cv.string,
        vol.Required(CONF_DEVICE_SLUG): cv.string,
        vol.Required(CONF_ENTITY_SLUG): cv.string,
        vol.Required(CONF_EVENT_TYPE): cv.string,
        vol.Optional(CONF_EVENT_DATA): dict,
    }
)
def websocket_entity_event(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle the triggering of an entity event."""
    async_dispatcher_send(
        hass,
        BRIDGE_ENTITY_EVENT.format(
            msg[CONF_SERVICE_SLUG], msg[CONF_DEVICE_SLUG], msg[CONF_ENTITY_SLUG]
        ),
        msg,
    )
    connection.send_message(result_message(msg[CONF_ID]))
