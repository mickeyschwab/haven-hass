"""Platform for Haven light integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo

from havenlighting import HavenClient
from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Haven Light from a config entry."""
    client: HavenClient = hass.data[DOMAIN][config_entry.entry_id]
    
    # Discover locations and lights
    locations = await hass.async_add_executor_job(client.discover_locations)
    
    entities = []
    for location in locations.values():
        lights = await hass.async_add_executor_job(location.get_lights)
        for light in lights.values():
            entities.append(HavenLight(light, location))
    
    async_add_entities(entities)

class HavenLight(LightEntity):
    """Representation of a Haven Light."""

    _attr_has_entity_name = True
    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}

    def __init__(self, light, location) -> None:
        """Initialize a Haven Light."""
        self._light = light
        self._location = location
        self._attr_unique_id = f"haven_light_{light.id}"
        self._attr_name = light.name
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, str(light.id))},
            name=light.name,
            manufacturer="Haven",
            model="Haven Light",
            via_device=(DOMAIN, str(location._location_id)),
        )

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._light.is_on

    @property
    def brightness(self) -> int:
        """Return the brightness of this light between 0..255."""
        return int(self._light._data.brightness * 4)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        await self.hass.async_add_executor_job(self._light.turn_on)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        await self.hass.async_add_executor_job(self._light.turn_off) 