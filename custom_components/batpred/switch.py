"""Switch platform for Batpred integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, DEVICE_INVERTER, DEVICE_BATTERY, DEVICE_PREDICTION, DEVICE_CAR
from .coordinator import BatpredCoordinator
from .entity import BatpredEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class BatpredSwitchDescription(SwitchEntityDescription):
    """Description of a Batpred switch entity."""

    device: str = ""
    source_suffix: str = ""


SWITCH_DESCRIPTIONS: tuple[BatpredSwitchDescription, ...] = (
    # ── Prediction / System ───────────────────────────────────────────────────
    BatpredSwitchDescription(
        key="active",
        name="Predbat Active",
        device=DEVICE_PREDICTION,
        source_suffix=".active",
        entity_category=EntityCategory.CONFIG,
        icon="mdi:play-circle",
    ),
    BatpredSwitchDescription(
        key="expert_mode",
        name="Expert Mode",
        device=DEVICE_PREDICTION,
        source_suffix=".expert_mode",
        entity_category=EntityCategory.CONFIG,
        icon="mdi:account-cog",
    ),
    BatpredSwitchDescription(
        key="compare_active",
        name="Compare Active",
        device=DEVICE_PREDICTION,
        source_suffix=".compare_active",
        entity_category=EntityCategory.CONFIG,
        icon="mdi:compare",
    ),
    # ── Inverter ──────────────────────────────────────────────────────────────
    BatpredSwitchDescription(
        key="inverter_hybrid",
        name="Inverter Hybrid",
        device=DEVICE_INVERTER,
        source_suffix=".inverter_hybrid",
        entity_category=EntityCategory.CONFIG,
        icon="mdi:solar-power-variant",
    ),
    BatpredSwitchDescription(
        key="inverter_soc_reset",
        name="Inverter SoC Reset",
        device=DEVICE_INVERTER,
        source_suffix=".inverter_soc_reset",
        entity_category=EntityCategory.CONFIG,
        icon="mdi:restore",
    ),
    BatpredSwitchDescription(
        key="inverter_set_charge_before",
        name="Set Charge Window Before Start",
        device=DEVICE_INVERTER,
        source_suffix=".inverter_set_charge_before",
        entity_category=EntityCategory.CONFIG,
        icon="mdi:battery-clock",
    ),
    # ── Battery ───────────────────────────────────────────────────────────────
    BatpredSwitchDescription(
        key="battery_capacity_nominal",
        name="Use Nominal Battery Capacity",
        device=DEVICE_BATTERY,
        source_suffix=".battery_capacity_nominal",
        entity_category=EntityCategory.CONFIG,
        icon="mdi:battery-check",
    ),
    # ── Car Charging ──────────────────────────────────────────────────────────
    BatpredSwitchDescription(
        key="car_charging_hold",
        name="Car Charging Hold",
        device=DEVICE_CAR,
        source_suffix=".car_charging_hold",
        entity_category=EntityCategory.CONFIG,
        icon="mdi:car-electric",
    ),
    BatpredSwitchDescription(
        key="car_charging_from_battery",
        name="Car Charging from Battery",
        device=DEVICE_CAR,
        source_suffix=".car_charging_from_battery",
        entity_category=EntityCategory.CONFIG,
        icon="mdi:battery-electric-vehicle",
    ),
)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Batpred switch entities from a config entry."""
    coordinator: BatpredCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [BatpredSwitch(coordinator, description) for description in SWITCH_DESCRIPTIONS]
    async_add_entities(entities)


class BatpredSwitch(BatpredEntity, SwitchEntity):
    """Representation of a Batpred switch."""

    entity_description: BatpredSwitchDescription

    def __init__(self, coordinator: BatpredCoordinator, description: BatpredSwitchDescription) -> None:
        """Initialize the switch."""
        super().__init__(
            coordinator=coordinator,
            device_name=description.device,
            entity_key=description.key,
            name=description.name,
            icon=description.icon,
        )
        self.entity_description = description
        if description.entity_category:
            self._attr_entity_category = description.entity_category

    @property
    def _source_entity_id(self) -> str:
        """Derive source entity ID."""
        return f"{self.coordinator.prefix}{self.entity_description.source_suffix}"

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        state = self._raw_state()
        if state in (None, "unknown", "unavailable"):
            return None
        return state.lower() in ("on", "true", "yes", "1")

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self._set_state("on")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self._set_state("off")

    async def _set_state(self, new_state: str) -> None:
        """Set state via input_boolean service or direct state call."""
        entity_id = self._source_entity_id
        service = "turn_on" if new_state == "on" else "turn_off"
        await self.coordinator.async_call_service(
            "input_boolean",
            service,
            {"entity_id": entity_id},
        )
        await self.coordinator.async_request_refresh()
