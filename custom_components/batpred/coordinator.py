"""DataUpdateCoordinator for Batpred."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_PREFIX, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class BatpredCoordinator(DataUpdateCoordinator):
    """Coordinator that fetches all Batpred entity states from Home Assistant."""

    def __init__(self, hass: HomeAssistant, config_entry) -> None:
        """Initialize the coordinator."""
        self.config_entry = config_entry
        self.prefix = config_entry.data.get(CONF_PREFIX, "predbat")
        scan_interval = config_entry.options.get(CONF_SCAN_INTERVAL, config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))

        _LOGGER.debug("Initializing BatpredCoordinator with prefix='%s', scan_interval=%s seconds", self.prefix, scan_interval)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch all batpred entity states via the internal HA API."""
        data: dict[str, Any] = {}
        try:
            prefix = self.prefix
            for state_obj in self.hass.states.async_all():
                entity_id: str = state_obj.entity_id
                # Match predbat.xxx, binary_sensor.predbat_xxx, sensor.predbat_xxx, etc.
                if (
                    entity_id.startswith(f"{prefix}.")
                    or entity_id.startswith(f"sensor.{prefix}_")
                    or entity_id.startswith(f"binary_sensor.{prefix}_")
                    or entity_id.startswith(f"switch.{prefix}_")
                    or entity_id.startswith(f"select.{prefix}_")
                    or entity_id.startswith(f"number.{prefix}_")
                    or entity_id.startswith(f"input_number.{prefix}_")
                    or entity_id.startswith(f"input_boolean.{prefix}_")
                    or entity_id.startswith(f"input_select.{prefix}_")
                ):
                    _LOGGER.debug("Found matching entity: %s (state=%s)", entity_id, state_obj.state)
                    data[entity_id] = {
                        "state": state_obj.state,
                        "attributes": dict(state_obj.attributes),
                    }
        except Exception as err:
            raise UpdateFailed(f"Error fetching batpred entity states: {err}") from err

        if data:
            _LOGGER.debug("Coordinator update complete: found %d matching entities", len(data))
        else:
            _LOGGER.warning("Coordinator update: no entities found matching prefix '%s' — check that Predbat is running", prefix)

        return data

    def get_entity_state(self, entity_id: str) -> str | None:
        """Get the state of a specific entity."""
        if self.data and entity_id in self.data:
            return self.data[entity_id]["state"]
        return None

    def get_entity_attributes(self, entity_id: str) -> dict[str, Any]:
        """Get the attributes of a specific entity."""
        if self.data and entity_id in self.data:
            return self.data[entity_id].get("attributes", {})
        return {}

    async def async_call_service(self, domain: str, service: str, service_data: dict[str, Any] | None = None) -> None:
        """Call a HA service via the internal HA API."""
        await self.hass.services.async_call(
            domain,
            service,
            service_data or {},
            blocking=True,
        )

    async def async_set_state(self, entity_id: str, state: str, attributes: dict[str, Any] | None = None) -> None:
        """Set the state of a HA entity via the internal HA API."""
        self.hass.states.async_set(entity_id, state, attributes or {})
