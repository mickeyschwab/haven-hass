"""Platform for Haven light integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HavenConfigEntry, HavenCoordinator

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: HavenConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Haven Light from a config entry."""
    coordinator = config_entry.runtime_data
    location = coordinator.location

    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        identifiers={(DOMAIN, str(location.id))},
        manufacturer="Haven",
        name=location.name,
        model="Haven Location",
    )

    async_add_entities(
        HavenLight(coordinator, light_id) for light_id in coordinator.data
    )

class HavenLight(CoordinatorEntity[HavenCoordinator], LightEntity):
    """Representation of a Haven Light."""

    _attr_has_entity_name = True
    _attr_color_mode = ColorMode.ONOFF
    _attr_supported_color_modes = {ColorMode.ONOFF}

    def __init__(self, coordinator: HavenCoordinator, light_id: int) -> None:
        """Initialize a Haven Light."""
        super().__init__(coordinator, context=light_id)
        self._light_id = light_id
        light = coordinator.data[light_id]
        self._attr_unique_id = f"haven_light_{light_id}"
        # None, not light.name: this entity is the device's only feature, so
        # has_entity_name + a device name would otherwise show "Kitchen Kitchen".
        self._attr_name = None
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, str(light_id))},
            name=light.name,
            manufacturer="Haven",
            model="Haven Light",
            via_device=(DOMAIN, str(coordinator.location.id)),
        )

    @property
    def available(self) -> bool:
        """Return True if the light is still reported by the coordinator."""
        return super().available and self._light_id in self.coordinator.data

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self.coordinator.data[self._light_id].is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        light = self.coordinator.data[self._light_id]
        await self.hass.async_add_executor_job(light.turn_on)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        light = self.coordinator.data[self._light_id]
        await self.hass.async_add_executor_job(light.turn_off)
        await self.coordinator.async_request_refresh()
