"""DataUpdateCoordinator for Batpred."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_HA_TOKEN, CONF_HA_URL, CONF_PREFIX, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class BatpredCoordinator(DataUpdateCoordinator):
    """Coordinator that fetches all Batpred entity states from Home Assistant."""

    def __init__(self, hass: HomeAssistant, config_entry) -> None:
        """Initialize the coordinator."""
        self.config_entry = config_entry
        self.ha_url = config_entry.data[CONF_HA_URL].rstrip("/")
        self.ha_token = config_entry.data[CONF_HA_TOKEN]
        self.prefix = config_entry.data.get(CONF_PREFIX, "predbat")
        scan_interval = config_entry.options.get(CONF_SCAN_INTERVAL, config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
        self._session: aiohttp.ClientSession | None = None

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    @property
    def _headers(self) -> dict[str, str]:
        """Return common HTTP headers."""
        return {
            "Authorization": f"Bearer {self.ha_token}",
            "Content-Type": "application/json",
        }

    async def _get_session(self) -> aiohttp.ClientSession:
        """Return a reusable aiohttp session, creating one if needed."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def async_shutdown(self) -> None:
        """Close the aiohttp session on shutdown."""
        if self._session and not self._session.closed:
            await self._session.close()
        await super().async_shutdown()

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch all batpred entity states from HA REST API."""
        data: dict[str, Any] = {}
        try:
            session = await self._get_session()
            async with session.get(
                f"{self.ha_url}/api/states",
                headers=self._headers,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status != 200:
                    raise UpdateFailed(f"Error communicating with HA API: {resp.status}")
                states = await resp.json()

            # Filter states belonging to batpred prefix
            prefix = self.prefix
            for state_obj in states:
                entity_id: str = state_obj.get("entity_id", "")
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
                    data[entity_id] = {
                        "state": state_obj.get("state"),
                        "attributes": state_obj.get("attributes", {}),
                    }

        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with Batpred: {err}") from err

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
        """Call a HA service via REST API."""
        url = f"{self.ha_url}/api/services/{domain}/{service}"
        payload = service_data or {}

        session = await self._get_session()
        async with session.post(url, json=payload, headers=self._headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status not in (200, 201):
                raise UpdateFailed(f"Failed to call service {domain}.{service}: {resp.status}")

    async def async_set_state(self, entity_id: str, state: str, attributes: dict[str, Any] | None = None) -> None:
        """Set the state of a HA entity via REST API."""
        url = f"{self.ha_url}/api/states/{entity_id}"
        payload: dict[str, Any] = {"state": state}
        if attributes:
            payload["attributes"] = attributes

        session = await self._get_session()
        async with session.post(url, json=payload, headers=self._headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status not in (200, 201):
                raise UpdateFailed(f"Failed to set state {entity_id}: {resp.status}")
