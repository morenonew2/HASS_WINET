"""Config flow WINET."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_HOST
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import WinetApiError, WinetCloudApi, WinetInvalidAuth, WinetLocalApi
from .const import (
    CONF_API_KEY,
    CONF_MAX_POWER,
    CONF_MODE,
    DEFAULT_MAX_POWER,
    DOMAIN,
    MODE_CLOUD,
    MODE_LOCAL,
)


class WinetConfigFlow(ConfigFlow, domain=DOMAIN):
    """Configurazione guidata."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Sceglie tra collegamento locale e cloud."""
        return self.async_show_menu(step_id="user", menu_options=[MODE_LOCAL, MODE_CLOUD])

    async def async_step_local(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            api = WinetLocalApi(async_get_clientsession(self.hass), host)
            try:
                info = await api.async_get_info()
                await api.async_get_data()
            except WinetApiError:
                errors["base"] = "cannot_connect"
            else:
                unique_id = str(info.get("mac") or host).lower()
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured(updates={CONF_HOST: host})
                return self.async_create_entry(
                    title=f"WINET {host}",
                    data={CONF_MODE: MODE_LOCAL, CONF_HOST: host},
                )

        return self.async_show_form(
            step_id="local",
            data_schema=vol.Schema(
                {vol.Required(CONF_HOST, default=(user_input or {}).get(CONF_HOST, "")): str}
            ),
            errors=errors,
        )

    async def async_step_cloud(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            key = user_input[CONF_API_KEY].strip()
            api = WinetCloudApi(async_get_clientsession(self.hass), key)
            try:
                await api.async_get_data()
            except WinetInvalidAuth:
                errors["base"] = "invalid_auth"
            except WinetApiError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(f"cloud_{key}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="WINET cloud",
                    data={CONF_MODE: MODE_CLOUD, CONF_API_KEY: key},
                )

        return self.async_show_form(
            step_id="cloud",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> WinetOptionsFlow:
        return WinetOptionsFlow()


class WinetOptionsFlow(OptionsFlow):
    """Opzioni: potenza massima selezionabile."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_MAX_POWER,
                        default=self.config_entry.options.get(
                            CONF_MAX_POWER, DEFAULT_MAX_POWER
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=9))
                }
            ),
        )
