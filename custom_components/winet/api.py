"""Client API per le schede WINET (locale e cloud)."""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import aiohttp

from .const import (
    CLOUD_BASE_URL,
    REQUEST_TIMEOUT,
    STATUS_ALARM,
    STATUS_BRAZIER_CLEANING,
    STATUS_FINAL_CLEANING,
    STATUS_FLAME_WAIT,
    STATUS_OFF,
    STATUS_ON,
    STATUS_STANDBY,
    STATUS_UNKNOWN,
    STATUS_UNMANAGED,
)

LOCAL_STATUS = {
    0: STATUS_OFF,
    1: STATUS_ON,
    2: STATUS_FINAL_CLEANING,
    3: STATUS_ALARM,
    4: STATUS_UNMANAGED,
}

CLOUD_STATUS = {
    0: STATUS_OFF,
    1: STATUS_FLAME_WAIT,
    2: STATUS_FLAME_WAIT,
    3: STATUS_ON,
    4: STATUS_ON,
    5: STATUS_STANDBY,
    6: STATUS_FINAL_CLEANING,
    7: STATUS_BRAZIER_CLEANING,
    8: STATUS_ALARM,
    9: STATUS_ALARM,
}


class WinetApiError(Exception):
    """Errore di comunicazione con la stufa."""


class WinetInvalidAuth(WinetApiError):
    """Chiave API cloud non valida."""


@dataclass
class WinetData:
    """Dati letti dalla stufa."""

    status: str = STATUS_UNKNOWN
    description: str | None = None
    power: int | None = None
    air_temp: float | None = None
    air_setpoint: float | None = None
    water_temp: float | None = None
    water_setpoint: float | None = None
    flue_temp: float | None = None
    extractor_rpm: float | None = None


def _to_float(value: Any, divisor: float = 1) -> float | None:
    """Converte in float, None se non possibile."""
    if value is None:
        return None
    try:
        return float(value) / divisor
    except (TypeError, ValueError):
        return None


def _to_int(value: Any) -> int | None:
    number = _to_float(value)
    return None if number is None else int(number)


class WinetApi(ABC):
    """Interfaccia comune alle due modalita'."""

    supports_water = False
    local_only_sensors = False

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session

    async def _request(self, url: str, parse: bool = True) -> Any:
        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                async with self._session.get(url) as resp:
                    resp.raise_for_status()
                    if not parse:
                        return None
                    return await resp.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            raise WinetApiError(str(err)) from err

    @abstractmethod
    async def async_get_data(self) -> WinetData:
        """Legge lo stato completo."""

    @abstractmethod
    async def async_turn_on(self) -> None:
        """Accende la stufa."""

    @abstractmethod
    async def async_turn_off(self) -> None:
        """Spegne la stufa."""

    @abstractmethod
    async def async_set_power(self, power: int) -> None:
        """Imposta la potenza."""

    @abstractmethod
    async def async_set_air_temp(self, temperature: float) -> None:
        """Imposta la temperatura aria."""

    async def async_set_water_temp(self, temperature: float) -> None:
        """Imposta la temperatura acqua (solo API locale)."""
        raise NotImplementedError


class WinetLocalApi(WinetApi):
    """API HTTP locale della scheda WINET (http://<ip>/api/...)."""

    supports_water = True
    local_only_sensors = True

    def __init__(self, session: aiohttp.ClientSession, host: str) -> None:
        super().__init__(session)
        self._base = f"http://{host}/api"

    async def async_get_info(self) -> dict[str, Any]:
        """Legge id, mac e SSID della scheda."""
        data = await self._request(f"{self._base}/id")
        if not isinstance(data, dict):
            raise WinetApiError("Risposta /api/id non valida")
        return data

    async def async_get_data(self) -> WinetData:
        raw = await self._request(f"{self._base}/global")
        if not isinstance(raw, dict) or "status" not in raw:
            raise WinetApiError("Risposta /api/global non valida")

        flue = _to_float(raw.get("gasflue"))
        if flue is not None and flue <= 30:
            flue = None  # come nel package originale: <= 30 = non disponibile

        return WinetData(
            status=LOCAL_STATUS.get(_to_int(raw.get("status")), STATUS_UNKNOWN),
            description=raw.get("description"),
            power=_to_int(raw.get("power")),
            air_temp=_to_float(raw.get("air"), 2),
            air_setpoint=_to_float(raw.get("setAir"), 2),
            water_temp=_to_float(raw.get("water")),
            water_setpoint=_to_float(raw.get("setWater")),
            flue_temp=flue,
            extractor_rpm=_to_float(raw.get("rpmExtractor")) or 0,
        )

    async def async_turn_on(self) -> None:
        await self._request(f"{self._base}/status/1", parse=False)

    async def async_turn_off(self) -> None:
        await self._request(f"{self._base}/status/0", parse=False)

    async def async_set_power(self, power: int) -> None:
        await self._request(f"{self._base}/power/{int(power)}", parse=False)

    async def async_set_air_temp(self, temperature: float) -> None:
        # la scheda lavora in mezzi gradi
        await self._request(
            f"{self._base}/temperature/air/{int(round(temperature * 2))}", parse=False
        )

    async def async_set_water_temp(self, temperature: float) -> None:
        await self._request(
            f"{self._base}/temperature/water/{int(round(temperature))}", parse=False
        )


class WinetCloudApi(WinetApi):
    """API cloud (ws.cloudwinet.it) identificata dalla chiave API."""

    def __init__(self, session: aiohttp.ClientSession, api_key: str) -> None:
        super().__init__(session)
        self._key = api_key

    def _url(self, method: str, *params: Any) -> str:
        if params:
            return f"{CLOUD_BASE_URL}/{method}/{self._key};{';'.join(map(str, params))}"
        return f"{CLOUD_BASE_URL}/{method}/{self._key}"

    async def async_get_data(self) -> WinetData:
        status_raw, power_raw, air_raw, set_raw = await asyncio.gather(
            self._request(self._url("GetStatus")),
            self._request(self._url("GetPower")),
            self._request(self._url("GetActualTemperature")),
            self._request(self._url("GetTemperature")),
        )
        if not isinstance(status_raw, dict) or "Status" not in status_raw:
            raise WinetInvalidAuth("Risposta GetStatus non valida")

        def result(raw: Any) -> Any:
            return raw.get("Result") if isinstance(raw, dict) else None

        return WinetData(
            status=CLOUD_STATUS.get(_to_int(status_raw.get("Status")), STATUS_UNKNOWN),
            power=_to_int(result(power_raw)),
            air_temp=_to_float(result(air_raw)),
            air_setpoint=_to_float(result(set_raw)),
        )

    async def async_turn_on(self) -> None:
        await self._request(self._url("Ignit"), parse=False)

    async def async_turn_off(self) -> None:
        await self._request(self._url("Shutdown"), parse=False)

    async def async_set_power(self, power: int) -> None:
        await self._request(self._url("SetPower", int(power)), parse=False)

    async def async_set_air_temp(self, temperature: float) -> None:
        await self._request(
            self._url("SetTemperature", int(round(temperature))), parse=False
        )
