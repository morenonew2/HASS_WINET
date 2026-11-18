"""Controlli numerici WINET: potenza e temperatura acqua."""

from __future__ import annotations

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import WinetConfigEntry
from .const import (
    CONF_MAX_POWER,
    DEFAULT_MAX_POWER,
    MAX_WATER_TEMP,
    MIN_WATER_TEMP,
)
from .entity import WinetEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WinetConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    entities: list[NumberEntity] = [WinetPower(entry)]
    if entry.runtime_data.api.supports_water:
        entities.append(WinetWaterSetpoint(entry))
    async_add_entities(entities)


class WinetPower(WinetEntity, NumberEntity):
    """Livello di potenza (1..N, N configurabile nelle opzioni)."""

    _attr_translation_key = "power_level"
    _attr_icon = "mdi:fire-circle"
    _attr_native_min_value = 1
    _attr_native_step = 1
    _attr_mode = NumberMode.BOX

    def __init__(self, entry: WinetConfigEntry) -> None:
        super().__init__(entry, "power_level")
        self._attr_native_max_value = entry.options.get(CONF_MAX_POWER, DEFAULT_MAX_POWER)

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data.power

    async def async_set_native_value(self, value: float) -> None:
        await self._api.async_set_power(int(value))
        await self.coordinator.async_request_refresh()


class WinetWaterSetpoint(WinetEntity, NumberEntity):
    """Temperatura acqua impostata (solo API locale)."""

    _attr_translation_key = "water_target"
    _attr_device_class = NumberDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_native_min_value = MIN_WATER_TEMP
    _attr_native_max_value = MAX_WATER_TEMP
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    def __init__(self, entry: WinetConfigEntry) -> None:
        super().__init__(entry, "water_target")

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data.water_setpoint

    async def async_set_native_value(self, value: float) -> None:
        await self._api.async_set_water_temp(value)
        await self.coordinator.async_request_refresh()
