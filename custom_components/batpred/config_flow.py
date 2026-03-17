"""Config flow for Batpred integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_TIMEZONE,
    DEFAULT_THREADS,
    DEFAULT_CURRENCY_SYMBOLS,
    DEFAULT_SOLCAST_HOST,
    DEFAULT_SOLCAST_POLL_HOURS,
    DEFAULT_INVERTER_TYPE,
    DEFAULT_NUM_INVERTERS,
    DEFAULT_INVERTER_RESERVE_MAX,
    DEFAULT_BALANCE_INVERTERS_SECONDS,
    DEFAULT_LOAD_FILTER_THRESHOLD,
    DEFAULT_BATTERY_SCALING,
    DEFAULT_IMPORT_EXPORT_SCALING,
    DEFAULT_DAYS_PREVIOUS,
    DEFAULT_FORECAST_HOURS,
    DEFAULT_OCTOPUS_SAVING_SESSION_OCTOPOINTS_PER_PENNY,
    CONF_PREFIX,
    CONF_SCAN_INTERVAL,
    CONF_TIMEZONE,
    CONF_THREADS,
    CONF_CURRENCY_SYMBOLS,
    CONF_METRIC_OCTOPUS_IMPORT,
    CONF_METRIC_OCTOPUS_EXPORT,
    CONF_METRIC_STANDING_CHARGE,
    CONF_OCTOPUS_SAVING_SESSION,
    CONF_OCTOPUS_SAVING_SESSION_OCTOPOINTS_PER_PENNY,
    CONF_SOLCAST_API_KEY,
    CONF_SOLCAST_HOST,
    CONF_SOLCAST_POLL_HOURS,
    CONF_INVERTER_TYPE,
    CONF_NUM_INVERTERS,
    CONF_INVERTER_LIMIT,
    CONF_INVERTER_LIMIT_CHARGE,
    CONF_INVERTER_LIMIT_DISCHARGE,
    CONF_INVERTER_RESERVE_MAX,
    CONF_BALANCE_INVERTERS_SECONDS,
    CONF_GESERIAL,
    CONF_LOAD_TODAY,
    CONF_IMPORT_TODAY,
    CONF_EXPORT_TODAY,
    CONF_PV_TODAY,
    CONF_BATTERY_POWER,
    CONF_PV_POWER,
    CONF_LOAD_POWER,
    CONF_GRID_POWER,
    CONF_SOC_KW,
    CONF_SOC_MAX,
    CONF_INVERTER_MODE,
    CONF_CHARGE_RATE,
    CONF_DISCHARGE_RATE,
    CONF_RESERVE,
    CONF_CHARGE_START_TIME,
    CONF_CHARGE_END_TIME,
    CONF_DISCHARGE_START_TIME,
    CONF_DISCHARGE_END_TIME,
    CONF_LOAD_FILTER_THRESHOLD,
    CONF_BATTERY_SCALING,
    CONF_IMPORT_EXPORT_SCALING,
    CONF_DAYS_PREVIOUS,
    CONF_FORECAST_HOURS,
)

_LOGGER = logging.getLogger(__name__)


def _list_to_str(value: list | str | None) -> str:
    """Convert a list to a newline-separated string for display in text fields."""
    if value is None:
        return ""
    if isinstance(value, list):
        return "\n".join(str(v) for v in value)
    return str(value)


def _str_to_list(value: str) -> list[str]:
    """Convert a newline-separated string back to a list, stripping blank lines."""
    if not value:
        return []
    return [line.strip() for line in value.splitlines() if line.strip()]


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Batpred."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialise the config flow."""
        self._data: dict[str, Any] = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial (basic) step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(f"batpred_{user_input[CONF_PREFIX]}")
            self._abort_if_unique_id_configured()
            self._data.update(user_input)
            return await self.async_step_rates()

        schema = vol.Schema(
            {
                vol.Required(CONF_PREFIX, default="predbat"): str,
                vol.Optional(CONF_TIMEZONE, default=DEFAULT_TIMEZONE): str,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
                    int, vol.Range(min=60, max=3600)
                ),
                vol.Optional(CONF_THREADS, default=DEFAULT_THREADS): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_rates(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the currency & rates step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_solar()

        schema = vol.Schema(
            {
                vol.Optional(CONF_CURRENCY_SYMBOLS, default=DEFAULT_CURRENCY_SYMBOLS): str,
                vol.Optional(CONF_METRIC_OCTOPUS_IMPORT, default=""): str,
                vol.Optional(CONF_METRIC_OCTOPUS_EXPORT, default=""): str,
                vol.Optional(CONF_METRIC_STANDING_CHARGE, default=""): str,
                vol.Optional(CONF_OCTOPUS_SAVING_SESSION, default=""): str,
                vol.Optional(
                    CONF_OCTOPUS_SAVING_SESSION_OCTOPOINTS_PER_PENNY,
                    default=DEFAULT_OCTOPUS_SAVING_SESSION_OCTOPOINTS_PER_PENNY,
                ): vol.All(int, vol.Range(min=1)),
            }
        )
        return self.async_show_form(step_id="rates", data_schema=schema, errors=errors)

    async def async_step_solar(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the solar & forecast step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_inverter()

        schema = vol.Schema(
            {
                vol.Optional(CONF_SOLCAST_API_KEY, default=""): str,
                vol.Optional(CONF_SOLCAST_HOST, default=DEFAULT_SOLCAST_HOST): str,
                vol.Optional(CONF_SOLCAST_POLL_HOURS, default=DEFAULT_SOLCAST_POLL_HOURS): vol.All(
                    int, vol.Range(min=1, max=24)
                ),
            }
        )
        return self.async_show_form(step_id="solar", data_schema=schema, errors=errors)

    async def async_step_inverter(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the inverter configuration step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_sensors()

        schema = vol.Schema(
            {
                vol.Optional(CONF_INVERTER_TYPE, default=DEFAULT_INVERTER_TYPE): str,
                vol.Optional(CONF_NUM_INVERTERS, default=DEFAULT_NUM_INVERTERS): vol.All(
                    int, vol.Range(min=1, max=10)
                ),
                vol.Optional(CONF_INVERTER_LIMIT, default=""): str,
                vol.Optional(CONF_INVERTER_LIMIT_CHARGE, default=""): str,
                vol.Optional(CONF_INVERTER_LIMIT_DISCHARGE, default=""): str,
                vol.Optional(CONF_INVERTER_RESERVE_MAX, default=DEFAULT_INVERTER_RESERVE_MAX): vol.All(
                    int, vol.Range(min=0, max=100)
                ),
                vol.Optional(CONF_BALANCE_INVERTERS_SECONDS, default=DEFAULT_BALANCE_INVERTERS_SECONDS): vol.All(
                    int, vol.Range(min=0)
                ),
            }
        )
        return self.async_show_form(step_id="inverter", data_schema=schema, errors=errors)

    async def async_step_sensors(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the sensor entity mapping step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_controls()

        schema = vol.Schema(
            {
                vol.Optional(CONF_GESERIAL, default=""): str,
                vol.Optional(CONF_LOAD_TODAY, default=""): str,
                vol.Optional(CONF_IMPORT_TODAY, default=""): str,
                vol.Optional(CONF_EXPORT_TODAY, default=""): str,
                vol.Optional(CONF_PV_TODAY, default=""): str,
                vol.Optional(CONF_BATTERY_POWER, default=""): str,
                vol.Optional(CONF_PV_POWER, default=""): str,
                vol.Optional(CONF_LOAD_POWER, default=""): str,
                vol.Optional(CONF_GRID_POWER, default=""): str,
                vol.Optional(CONF_SOC_KW, default=""): str,
                vol.Optional(CONF_SOC_MAX, default=""): str,
                vol.Optional(CONF_INVERTER_MODE, default=""): str,
            }
        )
        return self.async_show_form(step_id="sensors", data_schema=schema, errors=errors)

    async def async_step_controls(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the control entity mapping step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_advanced()

        schema = vol.Schema(
            {
                vol.Optional(CONF_CHARGE_RATE, default=""): str,
                vol.Optional(CONF_DISCHARGE_RATE, default=""): str,
                vol.Optional(CONF_RESERVE, default=""): str,
                vol.Optional(CONF_CHARGE_START_TIME, default=""): str,
                vol.Optional(CONF_CHARGE_END_TIME, default=""): str,
                vol.Optional(CONF_DISCHARGE_START_TIME, default=""): str,
                vol.Optional(CONF_DISCHARGE_END_TIME, default=""): str,
            }
        )
        return self.async_show_form(step_id="controls", data_schema=schema, errors=errors)

    async def async_step_advanced(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the advanced settings step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)
            title = f"Batpred ({self._data[CONF_PREFIX]})"
            return self.async_create_entry(title=title, data=self._data)

        schema = vol.Schema(
            {
                vol.Optional(CONF_LOAD_FILTER_THRESHOLD, default=DEFAULT_LOAD_FILTER_THRESHOLD): vol.All(
                    int, vol.Range(min=1, max=1440)
                ),
                vol.Optional(CONF_BATTERY_SCALING, default=DEFAULT_BATTERY_SCALING): str,
                vol.Optional(CONF_IMPORT_EXPORT_SCALING, default=DEFAULT_IMPORT_EXPORT_SCALING): vol.Coerce(float),
                vol.Optional(CONF_DAYS_PREVIOUS, default=DEFAULT_DAYS_PREVIOUS): str,
                vol.Optional(CONF_FORECAST_HOURS, default=DEFAULT_FORECAST_HOURS): vol.All(
                    int, vol.Range(min=1, max=168)
                ),
            }
        )
        return self.async_show_form(step_id="advanced", data_schema=schema, errors=errors)

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> OptionsFlowHandler:
        """Return the options flow."""
        return OptionsFlowHandler()


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for Batpred."""

    def __init__(self) -> None:
        """Initialize options flow."""
        super().__init__()
        self._data: dict[str, Any] = {}

    def _get(self, key: str, default: Any) -> Any:
        """Return the current stored value for a key, preferring options over data."""
        return self.config_entry.options.get(key, self.config_entry.data.get(key, default))

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Show the basic options step (entry point for options flow)."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_rates()

        schema = vol.Schema(
            {
                vol.Optional(CONF_PREFIX, default=self._get(CONF_PREFIX, "predbat")): str,
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=self._get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                ): vol.All(int, vol.Range(min=60, max=3600)),
                vol.Optional(CONF_TIMEZONE, default=self._get(CONF_TIMEZONE, DEFAULT_TIMEZONE)): str,
                vol.Optional(CONF_THREADS, default=self._get(CONF_THREADS, DEFAULT_THREADS)): str,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)

    async def async_step_rates(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the currency & rates options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_solar()

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_CURRENCY_SYMBOLS,
                    default=self._get(CONF_CURRENCY_SYMBOLS, DEFAULT_CURRENCY_SYMBOLS),
                ): str,
                vol.Optional(
                    CONF_METRIC_OCTOPUS_IMPORT,
                    default=self._get(CONF_METRIC_OCTOPUS_IMPORT, ""),
                ): str,
                vol.Optional(
                    CONF_METRIC_OCTOPUS_EXPORT,
                    default=self._get(CONF_METRIC_OCTOPUS_EXPORT, ""),
                ): str,
                vol.Optional(
                    CONF_METRIC_STANDING_CHARGE,
                    default=self._get(CONF_METRIC_STANDING_CHARGE, ""),
                ): str,
                vol.Optional(
                    CONF_OCTOPUS_SAVING_SESSION,
                    default=self._get(CONF_OCTOPUS_SAVING_SESSION, ""),
                ): str,
                vol.Optional(
                    CONF_OCTOPUS_SAVING_SESSION_OCTOPOINTS_PER_PENNY,
                    default=self._get(
                        CONF_OCTOPUS_SAVING_SESSION_OCTOPOINTS_PER_PENNY,
                        DEFAULT_OCTOPUS_SAVING_SESSION_OCTOPOINTS_PER_PENNY,
                    ),
                ): vol.All(int, vol.Range(min=1)),
            }
        )
        return self.async_show_form(step_id="rates", data_schema=schema, errors=errors)

    async def async_step_solar(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the solar & forecast options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_inverter()

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_SOLCAST_API_KEY,
                    default=self._get(CONF_SOLCAST_API_KEY, ""),
                ): str,
                vol.Optional(
                    CONF_SOLCAST_HOST,
                    default=self._get(CONF_SOLCAST_HOST, DEFAULT_SOLCAST_HOST),
                ): str,
                vol.Optional(
                    CONF_SOLCAST_POLL_HOURS,
                    default=self._get(CONF_SOLCAST_POLL_HOURS, DEFAULT_SOLCAST_POLL_HOURS),
                ): vol.All(int, vol.Range(min=1, max=24)),
            }
        )
        return self.async_show_form(step_id="solar", data_schema=schema, errors=errors)

    async def async_step_inverter(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the inverter configuration options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_sensors()

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_INVERTER_TYPE,
                    default=self._get(CONF_INVERTER_TYPE, DEFAULT_INVERTER_TYPE),
                ): str,
                vol.Optional(
                    CONF_NUM_INVERTERS,
                    default=self._get(CONF_NUM_INVERTERS, DEFAULT_NUM_INVERTERS),
                ): vol.All(int, vol.Range(min=1, max=10)),
                vol.Optional(
                    CONF_INVERTER_LIMIT,
                    default=self._get(CONF_INVERTER_LIMIT, ""),
                ): str,
                vol.Optional(
                    CONF_INVERTER_LIMIT_CHARGE,
                    default=self._get(CONF_INVERTER_LIMIT_CHARGE, ""),
                ): str,
                vol.Optional(
                    CONF_INVERTER_LIMIT_DISCHARGE,
                    default=self._get(CONF_INVERTER_LIMIT_DISCHARGE, ""),
                ): str,
                vol.Optional(
                    CONF_INVERTER_RESERVE_MAX,
                    default=self._get(CONF_INVERTER_RESERVE_MAX, DEFAULT_INVERTER_RESERVE_MAX),
                ): vol.All(int, vol.Range(min=0, max=100)),
                vol.Optional(
                    CONF_BALANCE_INVERTERS_SECONDS,
                    default=self._get(CONF_BALANCE_INVERTERS_SECONDS, DEFAULT_BALANCE_INVERTERS_SECONDS),
                ): vol.All(int, vol.Range(min=0)),
            }
        )
        return self.async_show_form(step_id="inverter", data_schema=schema, errors=errors)

    async def async_step_sensors(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the sensor entity mapping options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_controls()

        schema = vol.Schema(
            {
                vol.Optional(CONF_GESERIAL, default=self._get(CONF_GESERIAL, "")): str,
                vol.Optional(CONF_LOAD_TODAY, default=self._get(CONF_LOAD_TODAY, "")): str,
                vol.Optional(CONF_IMPORT_TODAY, default=self._get(CONF_IMPORT_TODAY, "")): str,
                vol.Optional(CONF_EXPORT_TODAY, default=self._get(CONF_EXPORT_TODAY, "")): str,
                vol.Optional(CONF_PV_TODAY, default=self._get(CONF_PV_TODAY, "")): str,
                vol.Optional(CONF_BATTERY_POWER, default=self._get(CONF_BATTERY_POWER, "")): str,
                vol.Optional(CONF_PV_POWER, default=self._get(CONF_PV_POWER, "")): str,
                vol.Optional(CONF_LOAD_POWER, default=self._get(CONF_LOAD_POWER, "")): str,
                vol.Optional(CONF_GRID_POWER, default=self._get(CONF_GRID_POWER, "")): str,
                vol.Optional(CONF_SOC_KW, default=self._get(CONF_SOC_KW, "")): str,
                vol.Optional(CONF_SOC_MAX, default=self._get(CONF_SOC_MAX, "")): str,
                vol.Optional(CONF_INVERTER_MODE, default=self._get(CONF_INVERTER_MODE, "")): str,
            }
        )
        return self.async_show_form(step_id="sensors", data_schema=schema, errors=errors)

    async def async_step_controls(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the control entity mapping options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_advanced()

        schema = vol.Schema(
            {
                vol.Optional(CONF_CHARGE_RATE, default=self._get(CONF_CHARGE_RATE, "")): str,
                vol.Optional(CONF_DISCHARGE_RATE, default=self._get(CONF_DISCHARGE_RATE, "")): str,
                vol.Optional(CONF_RESERVE, default=self._get(CONF_RESERVE, "")): str,
                vol.Optional(CONF_CHARGE_START_TIME, default=self._get(CONF_CHARGE_START_TIME, "")): str,
                vol.Optional(CONF_CHARGE_END_TIME, default=self._get(CONF_CHARGE_END_TIME, "")): str,
                vol.Optional(CONF_DISCHARGE_START_TIME, default=self._get(CONF_DISCHARGE_START_TIME, "")): str,
                vol.Optional(CONF_DISCHARGE_END_TIME, default=self._get(CONF_DISCHARGE_END_TIME, "")): str,
            }
        )
        return self.async_show_form(step_id="controls", data_schema=schema, errors=errors)

    async def async_step_advanced(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the advanced settings options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(title="", data=self._data)

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_LOAD_FILTER_THRESHOLD,
                    default=self._get(CONF_LOAD_FILTER_THRESHOLD, DEFAULT_LOAD_FILTER_THRESHOLD),
                ): vol.All(int, vol.Range(min=1, max=1440)),
                vol.Optional(
                    CONF_BATTERY_SCALING,
                    default=self._get(CONF_BATTERY_SCALING, DEFAULT_BATTERY_SCALING),
                ): str,
                vol.Optional(
                    CONF_IMPORT_EXPORT_SCALING,
                    default=self._get(CONF_IMPORT_EXPORT_SCALING, DEFAULT_IMPORT_EXPORT_SCALING),
                ): vol.Coerce(float),
                vol.Optional(
                    CONF_DAYS_PREVIOUS,
                    default=self._get(CONF_DAYS_PREVIOUS, DEFAULT_DAYS_PREVIOUS),
                ): str,
                vol.Optional(
                    CONF_FORECAST_HOURS,
                    default=self._get(CONF_FORECAST_HOURS, DEFAULT_FORECAST_HOURS),
                ): vol.All(int, vol.Range(min=1, max=168)),
            }
        )
        return self.async_show_form(step_id="advanced", data_schema=schema, errors=errors)
