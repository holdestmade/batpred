"""Binary sensor platform for Batpred integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, DEVICE_INVERTER, DEVICE_GRID, DEVICE_RATES, DEVICE_CAR
from .coordinator import BatpredCoordinator
from .entity import BatpredEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class BatpredBinarySensorDescription(BinarySensorEntityDescription):
    """Description of a Batpred binary sensor."""

    device: str = ""
    source_suffix: str = ""  # suffix from entity_id = prefix + source_suffix


BINARY_SENSOR_DESCRIPTIONS: tuple[BatpredBinarySensorDescription, ...] = (
    # ── Inverter ──────────────────────────────────────────────────────────────
    BatpredBinarySensorDescription(
        key="charging",
        name="Charging",
        device=DEVICE_INVERTER,
        source_suffix="_charging",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
        icon="mdi:battery-arrow-up",
    ),
    BatpredBinarySensorDescription(
        key="demand",
        name="Demand Mode",
        device=DEVICE_INVERTER,
        source_suffix="_demand",
        icon="mdi:battery-arrow-down",
    ),
    # ── Grid ──────────────────────────────────────────────────────────────────
    BatpredBinarySensorDescription(
        key="grid_connected",
        name="Grid Connected",
        device=DEVICE_GRID,
        source_suffix="_grid_connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        icon="mdi:transmission-tower",
    ),
    # ── Rates ─────────────────────────────────────────────────────────────────
    BatpredBinarySensorDescription(
        key="low_rate_slot",
        name="Low Rate Slot",
        device=DEVICE_RATES,
        source_suffix="_low_rate_slot",
        icon="mdi:home-lightning-bolt-outline",
    ),
    BatpredBinarySensorDescription(
        key="octopus_saving_session",
        name="Octopus Saving Session",
        device=DEVICE_RATES,
        source_suffix="_octopus_saving_session",
        icon="mdi:leaf",
    ),
    BatpredBinarySensorDescription(
        key="high_rate_export_slot",
        name="High Rate Export Slot",
        device=DEVICE_RATES,
        source_suffix="_high_rate_export_slot",
        icon="mdi:transmission-tower-export",
    ),
    # ── Car ───────────────────────────────────────────────────────────────────
    BatpredBinarySensorDescription(
        key="car_charging_slot",
        name="Car Charging Slot",
        device=DEVICE_CAR,
        source_suffix="_car_charging_slot",
        device_class=BinarySensorDeviceClass.PLUG,
        icon="mdi:car-electric",
    ),
)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Batpred binary sensors from a config entry."""
    coordinator: BatpredCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [BatpredBinarySensor(coordinator, description) for description in BINARY_SENSOR_DESCRIPTIONS]
    _LOGGER.debug("Setting up %d Batpred binary sensor entities", len(entities))
    async_add_entities(entities)
    _LOGGER.debug("Batpred binary_sensor platform setup complete")


class BatpredBinarySensor(BatpredEntity, BinarySensorEntity):
    """Representation of a Batpred binary sensor."""

    entity_description: BatpredBinarySensorDescription

    def __init__(self, coordinator: BatpredCoordinator, description: BatpredBinarySensorDescription) -> None:
        """Initialize the binary sensor."""
        super().__init__(
            coordinator=coordinator,
            device_name=description.device,
            entity_key=description.key,
            name=description.name,
            icon=description.icon,
        )
        self.entity_description = description
        _LOGGER.debug("Initialized binary sensor '%s' (source: binary_sensor.%s%s)", description.name, coordinator.prefix, description.source_suffix)

    @property
    def _source_entity_id(self) -> str:
        """Derive source entity ID: binary_sensor.{prefix}{suffix}."""
        return f"binary_sensor.{self.coordinator.prefix}{self.entity_description.source_suffix}"

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        state = self._raw_state()
        if state is None or state in ("unknown", "unavailable"):
            return None
        return state.lower() == "on"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        return self._raw_attributes()
