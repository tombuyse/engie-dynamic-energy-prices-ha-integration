"""Config flow for Engie Dynamic Prices."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import DOMAIN


class EngieConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the config flow for Engie Dynamic Prices."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial setup step."""
        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        if user_input is not None:
            return self.async_create_entry(title="Engie Dynamic Prices", data={})

        return self.async_show_form(step_id="user", data_schema=vol.Schema({}))
