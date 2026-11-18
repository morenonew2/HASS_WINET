"""Termostato WINET (sostituisce il generic_thermostat del vecchio package)."""

from __future__ import annotations

from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import WinetConfigEntry
from .const import (
    ACTIVE_STATUSES,
    MAX_AIR_TEMP,
    MIN_AIR_TEMP,
    STATUS_ON,
)
from .entity import WinetEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WinetConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([WinetClimate(entry)])


class WinetClimate(WinetEntity, ClimateEntity):
    """Controllo della temperatura aria."""

    _attr_translation_key = "stove"
    _attr_name = None  # usa il nome del dispositivo
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT]
    _attr_min_temp = MIN_AIR_TEMP
    _attr_max_temp = MAX_AIR_TEMP
    _attr_target_temperature_step = 1
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )

    def __init__(self, entry: WinetConfigEntry) -> None:
        super().__init__(entry, "climate")

    @property
    def current_temperature(self) -> float | None:
        return self.coordinator.data.air_temp

    @property
    def target_temperature(self) -> float | None:
        return self.coordinator.data.air_setpoint

    @property
    def hvac_mode(self) -> HVACMode:
        if self.coordinator.data.status in ACTIVE_STATUSES:
            return HVACMode.HEAT
        return HVACMode.OFF

    @property
    def hvac_action(self) -> HVACAction:
        status = self.coordinator.data.status
        if status == STATUS_ON:
            return HVACAction.HEATING
        if status in ACTIVE_STATUSES:
            return HVACAction.IDLE
        return HVACAction.OFF

    async def async_set_temperature(self, **kwargs: Any) -> None:
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return
        await self._api.async_set_air_temp(temperature)
        await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode == HVACMode.HEAT:
            await self._api.async_turn_on()
        else:
            await self._api.async_turn_off()
        await self.coordinator.async_request_refresh()
