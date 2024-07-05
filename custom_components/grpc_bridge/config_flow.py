"""Adds config flow to integration."""

from typing import Any

from homeassistant import config_entries

from .const import CONF_NAME, DOMAIN


@config_entries.HANDLERS.register(DOMAIN)
class BridgeFlowHandler(config_entries.ConfigFlow):
    """Config flow for gRPC Bridge."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    def __init__(self) -> None:
        """Initialize."""
        self._errors = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle a user initiated set up flow to create a webhook."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        if self.hass.data.get(DOMAIN):
            return self.async_abort(reason="single_instance_allowed")
        if user_input is None:
            return self.async_show_form(step_id="user")
        return self.async_create_entry(title=CONF_NAME, data={})