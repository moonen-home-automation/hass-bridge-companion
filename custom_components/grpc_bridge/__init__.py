"""
Component to intergrate with gRPC Bridge.

For more details please refer to
https://github.com/moonen-home-automation/hass-bridge-companion
"""

import asyncio
import logging
from typing import Any

from homeassistant.components.websocket_api.connection import ActiveConnection
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.dispatcher import (
    async_dispatcher_connect,
    async_dispatcher_send,
)
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_registry import async_get

from .const import (
    BRIDGE_ENTITY_ADD,
    BRIDGE_ENTITY_ADD_UPDATED,
    BRIDGE_ENTITY_AVAILABLE,
    BRIDGE_ENTITY_CONFIG,
    BRIDGE_ENTITY_STATE,
    CONF_ATTRIBUTES,
    CONF_AVAILABLE,
    CONF_CONFIG,
    CONF_DEVICE_CLASS,
    CONF_DEVICE_INFO,
    CONF_DEVICE_SLUG,
    CONF_ENTITY_CATEGORY,
    CONF_ENTITY_SLUG,
    CONF_ICON,
    CONF_ID,
    CONF_NAME,
    CONF_OPTIONS,
    CONF_REMOVE,
    CONF_SERVICE_SLUG,
    CONF_TYPE,
    CONF_UNIT_OF_MEASUREMENT,
    CONF_VERSION,
    DOMAIN,
    DOMAIN_DATA,
    STARTUP_MESSAGE,
)
from .discovery import (
    ALREADY_DISCOVERED,
    CHANGE_ENTITY_TYPE,
    CONFIG_ENTRY_IS_SETUP,
    start_discovery,
    stop_discovery,
)
from .version import __version__ as VERSION  # noqa: N812
from .websocket import register_websocket_handlers

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN_DATA) is None:
        hass.data.setdefault(DOMAIN_DATA, {})
        _LOGGER.info(STARTUP_MESSAGE)

    register_websocket_handlers(hass)
    await start_discovery(hass, entry)
    hass.bus.async_fire(DOMAIN, {CONF_TYPE: "loaded", CONF_VERSION: VERSION})

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in hass.data[DOMAIN_DATA][CONFIG_ENTRY_IS_SETUP]
            ]
        )
    )

    if unloaded:
        stop_discovery(hass)
        hass.data.pop(DOMAIN_DATA)
        hass.bus.async_fire(DOMAIN, {CONF_TYPE: "unloaded"})

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Realod config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


class BridgeEntity(Entity):
    """Bridge entity class."""

    _platform: str | None = None
    remove_signal_discovery_update = None
    remove_signal_entity_update = None
    _bidirectional = False

    def __init__(self, hass: HomeAssistant, config: Any) -> None:
        """Initialize the entity."""
        self.hass = hass
        self._device_info = config.get(CONF_DEVICE_INFO)
        self._service_slug = config[CONF_SERVICE_SLUG]
        self._device_slug = config[CONF_DEVICE_SLUG]
        self._entity_slug = config[CONF_ENTITY_SLUG]
        self._attr_unique_id = (
            f"{DOMAIN}-{self._service_slug}-{self._device_slug}-{self._entity_slug}"
        )
        self._attr_should_poll = False

        self.update_discovery_config(config)

    @property
    def device_info(self) -> dict[str, Any] | None:
        """Return device specific attributes."""
        info = None
        if self._device_info is not None:
            info = {"identifiers": {(DOMAIN, self._service_slug, self._device_slug)}}
            info.update(self._device_info)
        return info

    @callback
    def handle_config_update(self, msg: dict[str, Any]) -> None:
        """Handle config update."""
        self.update_config(msg)
        self.async_write_ha_state()

    @callback
    def handle_availability_update(self, msg: dict[str, Any]) -> None:
        """Handle availbility updates."""
        self._attr_available = msg.get(CONF_AVAILABLE, True)
        self.async_write_ha_state()

    @callback
    def handle_lost_connection(self) -> None:
        """Set availability to False when disconnected."""
        self._attr_available = False
        self.async_write_ha_state()

    @callback
    def handle_discovery_update(
        self, msg: dict[str, Any], connection: ActiveConnection
    ) -> None:
        """Update entity config."""
        if CONF_REMOVE in msg:
            if msg[CONF_REMOVE] == CHANGE_ENTITY_TYPE:
                # Recreate entity if platform type changed
                @callback
                def recreate_entity() -> None:
                    """Create entity with new type."""
                    del msg[CONF_REMOVE]
                    async_dispatcher_send(self.hass, BRIDGE_ENTITY_ADD, msg, connection)

                self.async_on_remove(recreate_entity)

            # Remove entity
            self.hass.async_create_task(self.async_remove(force_remove=True))
        else:
            self.update_discovery_config(msg)
            self.update_discovery_device_info(msg)

            if self._bidirectional:
                self._attr_available = True
                self._message_id = msg[CONF_ID]
                self._connection = connection
                self._connection.subscriptions[msg[CONF_ID]] = (
                    self.handle_lost_connection
                )
            self._async_write_ha_state()

    def entity_category_mapper(self, category: str) -> EntityCategory | None:
        """Map bridge category to hass category."""
        if category == "config":
            return EntityCategory.CONFIG
        if category == "diagnostic":
            return EntityCategory.DIAGNOSTIC
        return None

    def update_discovery_config(self, msg: dict[str, Any]) -> None:
        """Update entity config."""
        self._config = msg[CONF_CONFIG]
        self._attr_icon = self._config.get(CONF_ICON)
        self._attr_name = self._config.get(CONF_NAME)
        self._attr_device_class = self._config.get(CONF_DEVICE_CLASS)
        self._attr_entity_category = self.entity_category_mapper(
            self._config.get(CONF_ENTITY_CATEGORY)
        )
        self._attr_unit_of_measurement = self._config.get(CONF_UNIT_OF_MEASUREMENT)

    def update_config(self, msg: dict[str, Any]) -> None:
        """Update entity config."""
        config = msg.get(CONF_CONFIG, {})

        if config.get(CONF_NAME):
            self._attr_name = config.get(CONF_NAME)
        if config.get(CONF_ICON):
            self._attr_icon = config.get(CONF_ICON)
        if config.get(CONF_OPTIONS):
            self._attr_options = config.get(CONF_OPTIONS)

    def update_discovery_device_info(self, msg: dict[str, Any]) -> None:
        """Update entity device info."""
        if self.unique_id is None:
            return
        entity_registry = async_get(self.hass)
        assert self._platform is not None  # noqa: S101
        entity_id = entity_registry.async_get_entity_id(
            self._platform, DOMAIN, self.unique_id
        )
        self._device_info = msg.get(CONF_DEVICE_INFO)

        # Remove entity from device registry if device info is removed
        if self._device_info is None and entity_id is not None:
            entity_registry.async_update_entity(entity_id, device_id=None)

        # Update device info
        if self._device_info is not None:
            device_registry = dr.async_get(self.hass)
            device_info = self.device_info
            assert device_info is not None  # noqa: S101
            identifiers = device_info.pop("identifiers")
            device = device_registry.async_get_device(identifiers)
            if device is not None:
                device_registry.async_update_device(device.id, **device_info)
                # Add entity to device
                if entity_id is not None:
                    entity_registry.async_update_entity(entity_id, device_id=device.id)

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        self._remove_signal_discovery_update = async_dispatcher_connect(
            self.hass,
            BRIDGE_ENTITY_ADD_UPDATED.format(self.unique_id),
            self.handle_discovery_update,
        )
        self._remove_signal_config_update = async_dispatcher_connect(
            self.hass,
            BRIDGE_ENTITY_CONFIG.format(
                self._service_slug, self._device_slug, self._entity_slug
            ),
            self.handle_config_update,
        )
        self._remove_signal_availability_update = async_dispatcher_connect(
            self.hass,
            BRIDGE_ENTITY_AVAILABLE.format(
                self._service_slug, self._device_slug, self._entity_slug
            ),
            self.handle_availability_update,
        )

        if self._bidirectional:
            self._connection.subscriptions[self._message_id] = (
                self.handle_lost_connection
            )

    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed from hass."""
        if self.unique_id is None:
            return
        if self._remove_signal_discovery_update is not None:
            self._remove_signal_discovery_update()
        if self._remove_signal_availability_update is not None:
            self._remove_signal_availability_update()

        del self.hass.data[DOMAIN_DATA][ALREADY_DISCOVERED][self.unique_id]

        # Remove the entity_id from the entity registry
        entity_registry = async_get(self.hass)
        assert self._platform is not None  # noqa: S101
        entity_id = entity_registry.async_get_entity_id(
            self._platform, DOMAIN, self.unique_id
        )
        if entity_id:
            entity_registry.async_remove(entity_id)


class BridgeStateEntity(BridgeEntity):
    """BridgeStateEntity class."""

    def __init__(self, hass: HomeAssistant, config: Any) -> None:
        """Initialize BridgeStateEntity."""
        super().__init__(hass, config)

        self.update_entity_state_attributes(config)

    @callback
    def handle_entity_update(self, msg: dict[str, Any]) -> None:
        """Update entity state."""
        self.update_entity_state_attributes(msg)
        self.async_write_ha_state()

    def update_config(self, msg: dict[str, Any]) -> None:
        """Update entity config."""
        super().update_config(msg)
        config = msg.get(CONF_CONFIG, {})
        if config.get(CONF_DEVICE_CLASS):
            self._attr_device_class = config.get(CONF_DEVICE_CLASS)

    def update_entity_state_attributes(self, msg: dict[str, Any]) -> None:
        """Update entity state attributes."""
        self._attr_extra_state_attributes = msg.get(CONF_ATTRIBUTES, {})

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()

        self._remove_signal_entity_update = async_dispatcher_connect(
            self.hass,
            BRIDGE_ENTITY_STATE.format(
                self._service_slug, self._device_slug, self._entity_slug
            ),
            self.handle_entity_update,
        )

    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed from hass."""
        if self._remove_signal_entity_update is not None:
            self._remove_signal_entity_update()
        await super().async_will_remove_from_hass()
