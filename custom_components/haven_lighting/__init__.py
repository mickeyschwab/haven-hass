"""The Haven Lighting integration."""
from __future__ import annotations

from havenlighting import HavenClient
from havenlighting.exceptions import ApiError, AuthenticationError

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady

from .coordinator import HavenConfigEntry, HavenCoordinator

PLATFORMS: list[Platform] = [Platform.LIGHT]

async def async_setup_entry(hass: HomeAssistant, entry: HavenConfigEntry) -> bool:
    """Set up Haven Lighting from a config entry."""
    client = HavenClient()

    authenticated = await hass.async_add_executor_job(
        client.authenticate,
        entry.data["email"],
        entry.data["password"],
    )
    if not authenticated:
        raise ConfigEntryAuthFailed("Invalid Haven Lighting credentials")

    try:
        locations = await hass.async_add_executor_job(client.discover_locations)
    except (ApiError, AuthenticationError) as err:
        raise ConfigEntryNotReady(f"Error connecting to Haven Lighting: {err}") from err

    if not locations:
        raise ConfigEntryNotReady("No Haven Lighting location found for this account")

    location = next(iter(locations.values()))

    coordinator = HavenCoordinator(hass, entry, client, location)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: HavenConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
