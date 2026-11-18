"""Integrazione WINET (Stufasmart) per Home Assistant."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import WinetApi, WinetApiError, WinetCloudApi, WinetLocalApi
from .const import CONF_API_KEY, CONF_MODE, MODE_CLOUD
from .coordinator import WinetCoordinator

PLATFORMS = [Platform.SENSOR, Platform.SWITCH, Platform.CLIMATE, Platform.NUMBER]


@dataclass
class WinetRuntime:
    """Oggetti condivisi dalle piattaforme."""

    api: WinetApi
    coordinator: WinetCoordinator
    info: dict[str, Any] = field(default_factory=dict)


type WinetConfigEntry = ConfigEntry[WinetRuntime]


async def async_setup_entry(hass: HomeAssistant, entry: WinetConfigEntry) -> bool:
    """Configura una stufa WINET."""
    session = async_get_clientsession(hass)

    api: WinetApi
    info: dict[str, Any] = {}
    if entry.data[CONF_MODE] == MODE_CLOUD:
        api = WinetCloudApi(session, entry.data[CONF_API_KEY])
    else:
        local = WinetLocalApi(session, entry.data[CONF_HOST])
        try:
            info = await local.async_get_info()
        except WinetApiError:
            info = {}  # non bloccante: servono solo per il device
        api = local

    coordinator = WinetCoordinator(hass, entry, api)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = WinetRuntime(api=api, coordinator=coordinator, info=info)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_update_listener(hass: HomeAssistant, entry: WinetConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: WinetConfigEntry) -> bool:
    """Rimuove la stufa."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
