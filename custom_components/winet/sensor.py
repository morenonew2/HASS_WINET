"""Sensori WINET."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import EntityCategory, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import WinetConfigEntry
from .api import WinetData
from .const import STATUS_OPTIONS
from .entity import WinetEntity


@dataclass(frozen=True, kw_only=True)
class WinetSensorDescription(SensorEntityDescription):
    """Descrizione sensore con funzione di lettura."""

    value_fn: Callable[[WinetData], str | int | float | None]
    local_only: bool = False


SENSORS: tuple[WinetSensorDescription, ...] = (
    WinetSensorDescription(
        key="status",
        translation_key="status",
        device_class=SensorDeviceClass.ENUM,
        options=STATUS_OPTIONS,
        value_fn=lambda d: d.status,
    ),
    WinetSensorDescription(
        key="status_description",
        translation_key="status_description",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.description,
        local_only=True,
    ),
    WinetSensorDescription(
        key="power",
        translation_key="power",
        icon="mdi:fire-circle",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.power,
    ),
    WinetSensorDescription(
        key="air_temp",
        translation_key="air_temp",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.air_temp,
    ),
    WinetSensorDescription(
        key="air_setpoint",
        translation_key="air_setpoint",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda d: d.air_setpoint,
    ),
    WinetSensorDescription(
        key="water_temp",
        translation_key="water_temp",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.water_temp,
        local_only=True,
    ),
    WinetSensorDescription(
        key="water_setpoint",
        translation_key="water_setpoint",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda d: d.water_setpoint,
        local_only=True,
    ),
    WinetSensorDescription(
        key="flue_temp",
        translation_key="flue_temp",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.flue_temp,
        local_only=True,
    ),
    WinetSensorDescription(
        key="extractor_rpm",
        translation_key="extractor_rpm",
        native_unit_of_measurement="rpm",
        icon="mdi:fan",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.extractor_rpm,
        local_only=True,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WinetConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Crea i sensori."""
    api = entry.runtime_data.api
    async_add_entities(
        WinetSensor(entry, desc)
        for desc in SENSORS
        if api.local_only_sensors or not desc.local_only
    )


class WinetSensor(WinetEntity, SensorEntity):
    """Sensore WINET."""

    entity_description: WinetSensorDescription

    def __init__(self, entry: WinetConfigEntry, description: WinetSensorDescription) -> None:
        super().__init__(entry, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> str | int | float | None:
        return self.entity_description.value_fn(self.coordinator.data)
