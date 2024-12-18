"""The Haven Lighting integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from havenlighting import HavenClient

PLATFORMS: list[Platform] = [Platform.LIGHT]
DOMAIN = "haven"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Haven Lighting from a config entry."""
    client = HavenClient()
    
    # Authenticate with Haven
    authenticated = await hass.async_add_executor_job(
        client.authenticate,
        entry.data["email"],
        entry.data["password"]
    )

    if not authenticated:
        return False

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = client

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok 