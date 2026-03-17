"""Number platform for Batpred integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, DEVICE_INVERTER, DEVICE_BATTERY, DEVICE_PREDICTION, DEVICE_CAR
from .coordinator import BatpredCoordinator
from .entity import BatpredEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class BatpredNumberDescription(NumberEntityDescription):
    """Description of a Batpred number entity."""

    device: str = ""
    source_suffix: str = ""
    input_domain: str = "input_number"


NUMBER_DESCRIPTIONS: tuple[BatpredNumberDescription, ...] = (
    # ── Inverter ──────────────────────────────────────────────────────────────
    BatpredNumberDescription(
        key="charge_rate",
        name="Charge Rate",
        device=DEVICE_INVERTER,
        source_suffix=".charge_rate",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=NumberDeviceClass.POWER,
        native_min_value=0,
        native_max_value=10000,
        native_step=100,
        mode=NumberMode.BOX,
        icon="mdi:battery-arrow-up",
    ),
    BatpredNumberDescription(
        key="discharge_rate",
        name="Discharge Rate",
        device=DEVICE_INVERTER,
        source_suffix=".discharge_rate",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=NumberDeviceClass.POWER,
        native_min_value=0,
        native_max_value=10000,
        native_step=100,
        mode=NumberMode.BOX,
        icon="mdi:battery-arrow-down",
    ),
    # ── Battery ───────────────────────────────────────────────────────────────
    BatpredNumberDescription(
        key="best_soc_keep",
        name="Best SOC Keep",
        device=DEVICE_BATTERY,
        source_suffix=".best_soc_keep",
        native_unit_of_measurement=PERCENTAGE,
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        mode=NumberMode.SLIDER,
        icon="mdi:battery-medium",
    ),
    BatpredNumberDescription(
        key="best_soc_min",
        name="Best SOC Min",
        device=DEVICE_BATTERY,
        source_suffix=".best_soc_min",
        native_unit_of_measurement=PERCENTAGE,
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        mode=NumberMode.SLIDER,
        icon="mdi:battery-low",
    ),
    BatpredNumberDescription(
        key="best_soc_max",
        name="Best SOC Max",
        device=DEVICE_BATTERY,
        source_suffix=".best_soc_max",
        native_unit_of_measurement=PERCENTAGE,
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        mode=NumberMode.SLIDER,
        icon="mdi:battery-high",
    ),
    BatpredNumberDescription(
        key="battery_loss",
        name="Battery Loss",
        device=DEVICE_BATTERY,
        source_suffix=".battery_loss",
        native_unit_of_measurement=PERCENTAGE,
        native_min_value=0,
        native_max_value=100,
        native_step=0.5,
        mode=NumberMode.BOX,
        icon="mdi:battery-minus",
    ),
    # ── Prediction ────────────────────────────────────────────────────────────
    BatpredNumberDescription(
        key="metric_min_improvement",
        name="Metric Min Improvement",
        device=DEVICE_PREDICTION,
        source_suffix=".metric_min_improvement",
        native_unit_of_measurement="p",
        native_min_value=0,
        native_max_value=100,
        native_step=0.5,
        mode=NumberMode.BOX,
        icon="mdi:currency-gbp",
    ),
    BatpredNumberDescription(
        key="pv_scaling",
        name="PV Scaling",
        device=DEVICE_PREDICTION,
        source_suffix=".pv_scaling",
        native_min_value=0,
        native_max_value=2,
        native_step=0.01,
        mode=NumberMode.BOX,
        icon="mdi:multiplication",
    ),
    BatpredNumberDescription(
        key="load_scaling",
        name="Load Scaling",
        device=DEVICE_PREDICTION,
        source_suffix=".load_scaling",
        native_min_value=0,
        native_max_value=2,
        native_step=0.01,
        mode=NumberMode.BOX,
        icon="mdi:multiplication",
    ),
    # ── Car Charging ──────────────────────────────────────────────────────────
    BatpredNumberDescription(
        key="car_charging_soc",
        name="Car Target SOC",
        device=DEVICE_CAR,
        source_suffix=".car_charging_soc",
        native_unit_of_measurement=PERCENTAGE,
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        mode=NumberMode.SLIDER,
        icon="mdi:ev-station",
    ),
    BatpredNumberDescription(
        key="car_charging_rate",
        name="Car Charging Rate",
        device=DEVICE_CAR,
        source_suffix=".car_charging_rate",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=NumberDeviceClass.POWER,
        native_min_value=0,
        native_max_value=22,
        native_step=0.5,
        mode=NumberMode.BOX,
        icon="mdi:ev-station",
    ),
)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Batpred number entities from a config entry."""
    coordinator: BatpredCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [BatpredNumber(coordinator, description) for description in NUMBER_DESCRIPTIONS]
    async_add_entities(entities)


class BatpredNumber(BatpredEntity, NumberEntity):
    """Representation of a Batpred number entity."""

    entity_description: BatpredNumberDescription

    def __init__(self, coordinator: BatpredCoordinator, description: BatpredNumberDescription) -> None:
        """Initialize the number entity."""
        super().__init__(
            coordinator=coordinator,
            device_name=description.device,
            entity_key=description.key,
            name=description.name,
            icon=description.icon,
        )
        self.entity_description = description
        self._attr_native_min_value = description.native_min_value
        self._attr_native_max_value = description.native_max_value
        self._attr_native_step = description.native_step
        self._attr_mode = description.mode

    @property
    def _source_entity_id(self) -> str:
        """Derive source entity ID."""
        return f"{self.coordinator.prefix}{self.entity_description.source_suffix}"

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        state = self._raw_state()
        if state in (None, "unknown", "unavailable"):
            return None
        try:
            return float(state)
        except (ValueError, TypeError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        """Update the value by calling HA input_number service."""
        entity_id = self._source_entity_id
        await self.coordinator.async_call_service(
            self.entity_description.input_domain,
            "set_value",
            {"entity_id": entity_id, "value": value},
        )
        await self.coordinator.async_request_refresh()
