"""The Batpred integration."""

from __future__ import annotations

import logging

import homeassistant.helpers.config_validation as cv

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall

from .const import (
    DOMAIN,
    PLATFORMS,
    SERVICE_FORCE_CHARGE,
    SERVICE_FORCE_DISCHARGE,
    SERVICE_RESET_PLAN,
    SERVICE_REFRESH_RATES,
)
from .coordinator import BatpredCoordinator

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Batpred component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Batpred from a config entry."""
    _LOGGER.debug("Setting up Batpred config entry: %s", config_entry.entry_id)
    coordinator = BatpredCoordinator(hass, config_entry)

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = coordinator

    # Set up all platforms
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    _LOGGER.debug("Batpred platform setup complete for entry: %s", config_entry.entry_id)

    # Register services
    _register_services(hass, coordinator)

    # Listen for option updates
    config_entry.async_on_unload(config_entry.add_update_listener(_async_update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id, None)

    return unload_ok


async def _async_update_listener(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)


def _register_services(hass: HomeAssistant, coordinator: BatpredCoordinator) -> None:
    """Register Batpred HA services."""
    prefix = coordinator.prefix

    async def handle_force_charge(call: ServiceCall) -> None:
        """Handle the force_charge service call."""
        target_soc = call.data.get("target_soc")
        charge_rate = call.data.get("charge_rate")
        # Set manual_charge override - predbat reads this as a direct SOC target
        # The option format matches what predbat's manual_charge select accepts
        option = str(int(target_soc)) if target_soc is not None else "100"
        await coordinator.async_call_service(
            "input_select",
            "select_option",
            {"entity_id": f"{prefix}.manual_charge", "option": option},
        )
        if charge_rate is not None:
            await coordinator.async_set_state(f"{prefix}.charge_rate", str(charge_rate))
        await coordinator.async_request_refresh()

    async def handle_force_discharge(call: ServiceCall) -> None:
        """Handle the force_discharge service call."""
        discharge_rate = call.data.get("discharge_rate")
        await coordinator.async_call_service(
            "input_select",
            "select_option",
            {"entity_id": f"{prefix}.manual_discharge", "option": "on"},
        )
        if discharge_rate is not None:
            await coordinator.async_set_state(f"{prefix}.discharge_rate", str(discharge_rate))
        await coordinator.async_request_refresh()

    async def handle_reset_plan(call: ServiceCall) -> None:
        """Handle the reset_plan service call."""
        # Fire a HA event that Predbat listens to for plan reset
        await coordinator.async_call_service(
            "homeassistant",
            "update_entity",
            {"entity_id": f"{prefix}.status"},
        )
        await coordinator.async_request_refresh()

    async def handle_refresh_rates(call: ServiceCall) -> None:
        """Handle the refresh_rates service call."""
        await coordinator.async_call_service(
            "homeassistant",
            "update_entity",
            {"entity_id": f"{prefix}.rates"},
        )
        await coordinator.async_request_refresh()

    # Only register once (in case multiple entries)
    if not hass.services.has_service(DOMAIN, SERVICE_FORCE_CHARGE):
        hass.services.async_register(DOMAIN, SERVICE_FORCE_CHARGE, handle_force_charge)
    if not hass.services.has_service(DOMAIN, SERVICE_FORCE_DISCHARGE):
        hass.services.async_register(DOMAIN, SERVICE_FORCE_DISCHARGE, handle_force_discharge)
    if not hass.services.has_service(DOMAIN, SERVICE_RESET_PLAN):
        hass.services.async_register(DOMAIN, SERVICE_RESET_PLAN, handle_reset_plan)
    if not hass.services.has_service(DOMAIN, SERVICE_REFRESH_RATES):
        hass.services.async_register(DOMAIN, SERVICE_REFRESH_RATES, handle_refresh_rates)
