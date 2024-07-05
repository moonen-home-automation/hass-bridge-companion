"""Support the adding of new entities."""

import asyncio
import logging
from typing import Any

from homeassistant.components.websocket_api.connection import ActiveConnection
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import (
    async_dispatcher_connect,
    async_dispatcher_send,
)

from .const import (
    BRIDGE_ENTITY_ADD,
    BRIDGE_ENTITY_ADD_NEW,
    BRIDGE_ENTITY_ADD_UPDATED,
    CONF_DEVICE_SLUG,
    CONF_ENTITY_SLUG,
    CONF_PLATFORM,
    CONF_REMOVE,
    CONF_SERVICE_SLUG,
    DOMAIN,
    DOMAIN_DATA,
    SUPPORTED_PLATFORMS,
)

_LOGGER = logging.getLogger(__name__)

ALREADY_DISCOVERED = "discovered_components"
CHANGE_ENTITY_TYPE = "change_entity_type"
CONFIG_ENTRY_LOCK = "config_entry_lock"
CONFIG_ENTRY_IS_SETUP = "config_entry_is_setup"
DISCOVERY_DISPATCHER = "discovery_dispatcher"


async def start_discovery(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Initiate discovery."""

    async def async_device_message_received(
        msg: dict[str, Any], connection: ActiveConnection
    ) -> None:
        """Process the received message."""
        platform: str = msg[CONF_PLATFORM]
        service_slug: str = msg[CONF_SERVICE_SLUG]
        device_slug: str = msg[CONF_DEVICE_SLUG]
        entity_slug: str = msg[CONF_ENTITY_SLUG]

        if platform not in SUPPORTED_PLATFORMS:
            _LOGGER.warning("Integration %s not supported", platform)
            return

        discover_hash = f"{DOMAIN}-{msg[CONF_SERVICE_SLUG]}-{msg[CONF_DEVICE_SLUG]}-{msg[CONF_ENTITY_SLUG]}"  # noqa: E501
        data = hass.data[DOMAIN_DATA]

        _LOGGER.debug("Discovery message: %s", msg)

        if ALREADY_DISCOVERED not in data:
            data[ALREADY_DISCOVERED] = {}
        if discover_hash in data[ALREADY_DISCOVERED]:
            if data[ALREADY_DISCOVERED][discover_hash] != platform:
                # Remove old
                log_text = f"Changing {data[ALREADY_DISCOVERED][discover_hash]} to"
                msg[CONF_REMOVE] = CHANGE_ENTITY_TYPE
            elif CONF_REMOVE in msg:
                log_text = "Removing"
            else:
                # Dispatch update
                log_text = "Updating"

            _LOGGER.info(
                "%s %s %s %s %s",
                log_text,
                platform,
                service_slug,
                device_slug,
                entity_slug,
            )

            data[ALREADY_DISCOVERED][discover_hash] = platform
            async_dispatcher_send(
                hass, BRIDGE_ENTITY_ADD_UPDATED.format(discover_hash), msg, connection
            )
        else:
            # Add component
            _LOGGER.info(
                "Creating %s %s %s %s", platform, service_slug, device_slug, entity_slug
            )
            data[ALREADY_DISCOVERED][discover_hash] = platform

            async with data[CONFIG_ENTRY_LOCK]:
                if platform not in data[CONFIG_ENTRY_IS_SETUP]:
                    await hass.config_entries.async_forward_entry_setup(
                        config_entry, platform
                    )
                    data[CONFIG_ENTRY_IS_SETUP].add(platform)

            async_dispatcher_send(
                hass, BRIDGE_ENTITY_ADD_NEW.format(platform), msg, connection
            )

    hass.data[DOMAIN_DATA][CONFIG_ENTRY_LOCK] = asyncio.Lock()
    hass.data[DOMAIN_DATA][CONFIG_ENTRY_IS_SETUP] = set()

    hass.data[DOMAIN_DATA][DISCOVERY_DISPATCHER] = async_dispatcher_connect(
        hass, BRIDGE_ENTITY_ADD, async_device_message_received
    )


def stop_discovery(hass: HomeAssistant) -> None:
    """Remove discovery dispatcher."""
    hass.data[DOMAIN_DATA][DISCOVERY_DISPATCHER]()
