"""Config flow for Haven Lighting integration."""
from __future__ import annotations

from collections.abc import Mapping
import logging
from typing import Any

import voluptuous as vol

from havenlighting import HavenClient

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class HavenConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Haven Lighting."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            client = HavenClient()
            try:
                authenticated = await self.hass.async_add_executor_job(
                    client.authenticate,
                    user_input[CONF_EMAIL],
                    user_input[CONF_PASSWORD],
                )
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                if authenticated:
                    await self.async_set_unique_id(user_input[CONF_EMAIL])
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=user_input[CONF_EMAIL], data=user_input
                    )
                errors["base"] = "invalid_auth"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Handle reauthentication upon a Haven Lighting authentication error."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm reauthentication dialog."""
        errors: dict[str, str] = {}
        reauth_entry = self._get_reauth_entry()

        if user_input is not None:
            client = HavenClient()
            try:
                authenticated = await self.hass.async_add_executor_job(
                    client.authenticate,
                    user_input[CONF_EMAIL],
                    user_input[CONF_PASSWORD],
                )
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                if authenticated:
                    return self.async_update_reload_and_abort(
                        reauth_entry, data_updates=user_input
                    )
                errors["base"] = "invalid_auth"

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_EMAIL, default=reauth_entry.data[CONF_EMAIL]
                    ): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )
