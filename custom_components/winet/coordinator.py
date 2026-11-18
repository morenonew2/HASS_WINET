"""Coordinator per WINET."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import WinetApi, WinetApiError, WinetData
from .const import DOMAIN, SCAN_INTERVAL

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class WinetCoordinator(DataUpdateCoordinator[WinetData]):
    """Legge periodicamente lo stato della stufa."""

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, api: WinetApi
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.api = api

    async def _async_update_data(self) -> WinetData:
        try:
            return await self.api.async_get_data()
        except WinetApiError as err:
            raise UpdateFailed(f"Errore di comunicazione con la stufa: {err}") from err
