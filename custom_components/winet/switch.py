"""Interruttore accensione/spegnimento WINET."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import WinetConfigEntry
from .const import ACTIVE_STATUSES
from .entity import WinetEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WinetConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([WinetSwitch(entry)])


class WinetSwitch(WinetEntity, SwitchEntity):
    """Accende e spegne la stufa."""

    _attr_translation_key = "power_switch"
    _attr_assumed_state = False

    def __init__(self, entry: WinetConfigEntry) -> None:
        super().__init__(entry, "power_switch")

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.status in ACTIVE_STATUSES

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._api.async_turn_on()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._api.async_turn_off()
        await self.coordinator.async_request_refresh()
