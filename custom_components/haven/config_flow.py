"""Config flow for Haven Lighting integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.data_entry_flow import FlowResult

from havenlighting import HavenClient
from havenlighting.exceptions import AuthenticationError

_LOGGER = logging.getLogger(__name__)

DOMAIN = "haven"

class HavenConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Haven Lighting."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                client = HavenClient()
                authenticated = await self.hass.async_add_executor_job(
                    client.authenticate,
                    user_input[CONF_EMAIL],
                    user_input[CONF_PASSWORD],
                )

                if authenticated:
                    return self.async_create_entry(
                        title=user_input[CONF_EMAIL],
                        data=user_input,
                    )
                else:
                    errors["base"] = "invalid_auth"

            except AuthenticationError:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_EMAIL): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        ) 