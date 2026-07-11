"""DataUpdateCoordinator for the Haven Lighting integration."""
from __future__ import annotations

from datetime import timedelta
import logging

from havenlighting import HavenClient
from havenlighting.devices.light import Light
from havenlighting.devices.location import Location
from havenlighting.exceptions import ApiError, AuthenticationError

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

# Conservative on purpose: other users of Haven's community integrations have
# had their accounts rate-limited/flagged for polling too aggressively (see
# haven-python's project history). Poll gently rather than aggressively.
UPDATE_INTERVAL = timedelta(seconds=60)

type HavenConfigEntry = ConfigEntry["HavenCoordinator"]


class HavenCoordinator(DataUpdateCoordinator[dict[int, Light]]):
    """Fetch all lights for one Haven location on a shared schedule."""

    config_entry: HavenConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: HavenConfigEntry,
        client: HavenClient,
        location: Location,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name="Haven Lighting",
            update_interval=UPDATE_INTERVAL,
        )
        self.client = client
        self.location = location

    async def _async_update_data(self) -> dict[int, Light]:
        """Fetch the latest light states for this location."""
        try:
            return await self.hass.async_add_executor_job(self.location.get_lights)
        except AuthenticationError as err:
            raise ConfigEntryAuthFailed(
                "Haven Lighting authentication expired"
            ) from err
        except ApiError as err:
            raise UpdateFailed(f"Error communicating with Haven Lighting: {err}") from err
