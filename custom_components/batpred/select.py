"""Select platform for Batpred integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, DEVICE_INVERTER, DEVICE_PREDICTION, DEVICE_CAR
from .coordinator import BatpredCoordinator
from .entity import BatpredEntity

_LOGGER = logging.getLogger(__name__)

# Mode options matching predbat's PREDBAT_MODE_OPTIONS
PREDBAT_MODE_OPTIONS = ["Monitor", "Control SOC only", "Control charge", "Control charge & discharge"]


@dataclass(frozen=True)
class BatpredSelectDescription(SelectEntityDescription):
    """Description of a Batpred select entity."""

    device: str = ""
    source_suffix: str = ""
    service_entity_prefix: str = "input_select"
    options: list[str] = field(default_factory=list)


SELECT_DESCRIPTIONS: tuple[BatpredSelectDescription, ...] = (
    # ── Inverter / Prediction ─────────────────────────────────────────────────
    BatpredSelectDescription(
        key="mode",
        name="Operating Mode",
        device=DEVICE_PREDICTION,
        source_suffix=".mode",
        options=PREDBAT_MODE_OPTIONS,
        icon="mdi:state-machine",
    ),
    BatpredSelectDescription(
        key="manual_charge",
        name="Manual Charge Override",
        device=DEVICE_INVERTER,
        source_suffix=".manual_charge",
        options=["off"],
        icon="mdi:battery-charging",
    ),
    BatpredSelectDescription(
        key="manual_discharge",
        name="Manual Discharge Override",
        device=DEVICE_INVERTER,
        source_suffix=".manual_discharge",
        options=["off"],
        icon="mdi:battery-arrow-down",
    ),
    BatpredSelectDescription(
        key="manual_export",
        name="Manual Export Override",
        device=DEVICE_INVERTER,
        source_suffix=".manual_export",
        options=["off"],
        icon="mdi:transmission-tower-export",
    ),
    BatpredSelectDescription(
        key="manual_demand",
        name="Manual Demand Override",
        device=DEVICE_INVERTER,
        source_suffix=".manual_demand",
        options=["off"],
        icon="mdi:home-lightning-bolt",
    ),
    # ── Car Charging ──────────────────────────────────────────────────────────
    BatpredSelectDescription(
        key="car_charging_limit",
        name="Car Charging Limit",
        device=DEVICE_CAR,
        source_suffix=".car_charging_limit",
        options=[f"{v}%" for v in range(10, 110, 10)],
        icon="mdi:ev-station",
    ),
)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Batpred select entities from a config entry."""
    coordinator: BatpredCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [BatpredSelect(coordinator, description) for description in SELECT_DESCRIPTIONS]
    async_add_entities(entities)


class BatpredSelect(BatpredEntity, SelectEntity):
    """Representation of a Batpred select entity."""

    entity_description: BatpredSelectDescription

    def __init__(self, coordinator: BatpredCoordinator, description: BatpredSelectDescription) -> None:
        """Initialize the select entity."""
        super().__init__(
            coordinator=coordinator,
            device_name=description.device,
            entity_key=description.key,
            name=description.name,
            icon=description.icon,
        )
        self.entity_description = description
        self._attr_options = description.options

    @property
    def _source_entity_id(self) -> str:
        """Derive source entity ID."""
        return f"{self.coordinator.prefix}{self.entity_description.source_suffix}"

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        state = self._raw_state()
        if state in (None, "unknown", "unavailable"):
            return None
        return state

    async def async_select_option(self, option: str) -> None:
        """Change the selected option by calling HA service."""
        entity_id = self._source_entity_id
        await self.coordinator.async_call_service(
            "input_select",
            "select_option",
            {"entity_id": entity_id, "option": option},
        )
        await self.coordinator.async_request_refresh()
