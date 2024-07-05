"""Constants for gRPC Bridge."""

from .version import __version__ as VERSION  # noqa: N812

ISSUE_URL = "https://github.com/moonen-home-automation/hass-bridge-companion/issues"

DOMAIN = "grpc_bridge"
DOMAIN_DATA = f"{DOMAIN}_data"

CONF_ID = "id"
CONF_TYPE = "type"
CONF_SERVICE_SLUG = "service_slug"
CONF_DEVICE_SLUG = "device_slug"
CONF_ENTITY_SLUG = "entity_slug"
CONF_STATE = "state"
CONF_ATTRIBUTES = "attributes"
CONF_CONFIG = "config"
CONF_EVENT_TYPE = "event_type"
CONF_EVENT_DATA = "event_data"
CONF_PLATFORM = "platform"
CONF_DEVICE_INFO = "device_info"
CONF_AVAILABLE = "available"
CONF_REMOVE = "remove"
CONF_VERSION = "version"
CONF_ICON = "icon"
CONF_NAME = "name"
CONF_DEVICE_CLASS = "device_class"
CONF_ENTITY_CATEGORY = "entity_category"
CONF_UNIT_OF_MEASUREMENT = "unit_of_measurement"
CONF_OPTIONS = "options"
CONF_LAST_RESET = "last_reset"
CONF_STATE_CLASS = "state_class"
CONF_EVENT_TYPES = "event_types"

# Platforms
PLATFORM_BINARY_SENSOR = "binary_sensor"
PLATFORM_SWITCH = "switch"
PLATFORM_SENSOR = "sensor"
PLATFORM_EVENT = "event"

SUPPORTED_PLATFORMS = [
    PLATFORM_SWITCH,
    PLATFORM_SENSOR,
    PLATFORM_EVENT,
    PLATFORM_BINARY_SENSOR,
]

BRIDGE_ENTITY_STATE = "bridge_entity_state_{}_{}_{}"
BRIDGE_ENTITY_CONFIG = "bridge_entity_config_{}_{}_{}"
BRIDGE_ENTITY_EVENT = "bridge_entity_event_{}_{}_{}"
BRIDGE_ENTITY_ADD = "bridge_entity_add"
BRIDGE_ENTITY_ADD_UPDATED = "bridge_entity_add_updated_{}"
BRIDGE_ENTITY_ADD_NEW = "bridge_entity_add_new_{}"
BRIDGE_ENTITY_AVAILABLE = "bridge_entity_available_{}_{}_{}"

# Defaults
NAME = "gRPC Bridge Companion"
NUMBER_ICON = "mdi:numeric"
SWITCH_ICON = "mdi:electric-switch-closed"
SELECT_ICON = "mdi:format-list-bulleted"
TEXT_ICON = "mdi:form-textbox"
TIME_ICON = "mdi:clock-time-three"

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
