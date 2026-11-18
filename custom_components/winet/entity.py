"""Entita' base WINET."""

from __future__ import annotations

from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import WinetConfigEntry
from .const import DOMAIN, MODE_CLOUD, CONF_MODE
from .coordinator import WinetCoordinator


class WinetEntity(CoordinatorEntity[WinetCoordinator]):
    """Base per tutte le entita' della stufa."""

    _attr_has_entity_name = True

    def __init__(self, entry: WinetConfigEntry, key: str) -> None:
        super().__init__(entry.runtime_data.coordinator)
        self._api = entry.runtime_data.api
        self._attr_unique_id = f"{entry.unique_id}_{key}"

        info = entry.runtime_data.info
        cloud = entry.data[CONF_MODE] == MODE_CLOUD
        device = DeviceInfo(
            identifiers={(DOMAIN, entry.unique_id)},
            name=entry.title,
            manufacturer="Stufasmart / WINET",
            model="WINET (cloud)" if cloud else "WINET (locale)",
        )
        if info.get("mac"):
            device["connections"] = {(CONNECTION_NETWORK_MAC, str(info["mac"]).lower())}
        if info.get("id"):
            device["serial_number"] = str(info["id"])
        self._attr_device_info = device
