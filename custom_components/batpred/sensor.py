"""Sensor platform for Batpred integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfEnergy,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, DEVICE_INVERTER, DEVICE_BATTERY, DEVICE_GRID, DEVICE_SOLAR, DEVICE_PREDICTION, DEVICE_RATES, DEVICE_CAR
from .coordinator import BatpredCoordinator
from .entity import BatpredEntity

_LOGGER = logging.getLogger(__name__)

# Currency unit (pence)
CURRENCY_PENCE = "p"
CURRENCY_POUNDS = "£"


@dataclass(frozen=True)
class BatpredSensorDescription(SensorEntityDescription):
    """Description of a Batpred sensor."""

    device: str = ""
    source_suffix: str = ""  # suffix appended to prefix to form entity_id


# ──────────────────────────────────────────────────────────────────────────────
# Sensor definitions grouped by device
# ──────────────────────────────────────────────────────────────────────────────

SENSOR_DESCRIPTIONS: tuple[BatpredSensorDescription, ...] = (
    # ── Inverter ──────────────────────────────────────────────────────────────
    BatpredSensorDescription(
        key="soc",
        name="State of Charge",
        device=DEVICE_INVERTER,
        source_suffix=".soc",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery",
    ),
    BatpredSensorDescription(
        key="soc_kw",
        name="State of Charge (kWh)",
        device=DEVICE_INVERTER,
        source_suffix=".soc_kw",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY_STORAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery",
    ),
    BatpredSensorDescription(
        key="battery_power",
        name="Battery Power",
        device=DEVICE_INVERTER,
        source_suffix=".battery_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:lightning-bolt",
    ),
    BatpredSensorDescription(
        key="pv_power",
        name="PV Power",
        device=DEVICE_INVERTER,
        source_suffix=".pv_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-power",
    ),
    BatpredSensorDescription(
        key="load_power",
        name="Load Power",
        device=DEVICE_INVERTER,
        source_suffix=".load_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:home-lightning-bolt",
    ),
    BatpredSensorDescription(
        key="charge_rate",
        name="Charge Rate",
        device=DEVICE_INVERTER,
        source_suffix=".charge_rate",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-arrow-up",
    ),
    BatpredSensorDescription(
        key="discharge_rate",
        name="Discharge Rate",
        device=DEVICE_INVERTER,
        source_suffix=".discharge_rate",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-arrow-down",
    ),
    BatpredSensorDescription(
        key="inverter_time",
        name="Inverter Time",
        device=DEVICE_INVERTER,
        source_suffix=".inverter_time",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock",
    ),
    # ── Battery ───────────────────────────────────────────────────────────────
    BatpredSensorDescription(
        key="battery_size_kwh",
        name="Battery Capacity",
        device=DEVICE_BATTERY,
        source_suffix=".battery_size_kwh",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY_STORAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-high",
    ),
    BatpredSensorDescription(
        key="reserve",
        name="Reserve",
        device=DEVICE_BATTERY,
        source_suffix=".reserve",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-low",
    ),
    BatpredSensorDescription(
        key="charge_limit",
        name="Charge Limit",
        device=DEVICE_BATTERY,
        source_suffix=".charge_limit",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-charging-100",
    ),
    BatpredSensorDescription(
        key="charge_limit_kw",
        name="Charge Limit (kWh)",
        device=DEVICE_BATTERY,
        source_suffix=".charge_limit_kw",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY_STORAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-charging-high",
    ),
    # ── Grid ──────────────────────────────────────────────────────────────────
    BatpredSensorDescription(
        key="grid_import_power",
        name="Grid Import Power",
        device=DEVICE_GRID,
        source_suffix=".grid_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower-import",
    ),
    BatpredSensorDescription(
        key="grid_import_kwh",
        name="Grid Import (kWh)",
        device=DEVICE_GRID,
        source_suffix=".import_kwh",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:transmission-tower-import",
    ),
    BatpredSensorDescription(
        key="grid_export_kwh",
        name="Grid Export (kWh)",
        device=DEVICE_GRID,
        source_suffix=".export_kwh",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:transmission-tower-export",
    ),
    # ── Solar ─────────────────────────────────────────────────────────────────
    BatpredSensorDescription(
        key="pv_today",
        name="PV Today",
        device=DEVICE_SOLAR,
        source_suffix=".pv_today",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:solar-power",
    ),
    BatpredSensorDescription(
        key="pv_forecast_today",
        name="PV Forecast Today",
        device=DEVICE_SOLAR,
        source_suffix=".pv_forecast_today",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:weather-sunny",
    ),
    BatpredSensorDescription(
        key="pv_forecast_tomorrow",
        name="PV Forecast Tomorrow",
        device=DEVICE_SOLAR,
        source_suffix=".pv_forecast_tomorrow",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:weather-sunny",
    ),
    BatpredSensorDescription(
        key="pv_forecast_h0",
        name="PV Forecast D+2",
        device=DEVICE_SOLAR,
        source_suffix=".pv_forecast_h0",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:weather-partly-cloudy",
    ),
    # ── Prediction ────────────────────────────────────────────────────────────
    BatpredSensorDescription(
        key="best_soc_min",
        name="Best SOC Min",
        device=DEVICE_PREDICTION,
        source_suffix=".best_soc_min",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-low",
    ),
    BatpredSensorDescription(
        key="best_soc_max",
        name="Best SOC Max",
        device=DEVICE_PREDICTION,
        source_suffix=".best_soc_max",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-high",
    ),
    BatpredSensorDescription(
        key="best_soc_keep",
        name="Best SOC Keep",
        device=DEVICE_PREDICTION,
        source_suffix=".best_soc_keep",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-medium",
    ),
    BatpredSensorDescription(
        key="metric",
        name="Metric",
        device=DEVICE_PREDICTION,
        source_suffix=".metric",
        native_unit_of_measurement=CURRENCY_PENCE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:currency-gbp",
    ),
    BatpredSensorDescription(
        key="cost_today",
        name="Cost Today",
        device=DEVICE_PREDICTION,
        source_suffix=".cost_today",
        native_unit_of_measurement=CURRENCY_PENCE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:cash",
    ),
    BatpredSensorDescription(
        key="cost_today_import",
        name="Cost Today (Import)",
        device=DEVICE_PREDICTION,
        source_suffix=".cost_today_import",
        native_unit_of_measurement=CURRENCY_PENCE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:cash",
    ),
    BatpredSensorDescription(
        key="cost_today_export",
        name="Cost Today (Export)",
        device=DEVICE_PREDICTION,
        source_suffix=".cost_today_export",
        native_unit_of_measurement=CURRENCY_PENCE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:cash",
    ),
    BatpredSensorDescription(
        key="ppkwh_today",
        name="Price Today (p/kWh)",
        device=DEVICE_PREDICTION,
        source_suffix=".ppkwh_today",
        native_unit_of_measurement=CURRENCY_PENCE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:currency-gbp",
    ),
    BatpredSensorDescription(
        key="best_charge_start",
        name="Best Charge Start",
        device=DEVICE_PREDICTION,
        source_suffix=".best_charge_start",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:table-clock",
    ),
    BatpredSensorDescription(
        key="best_charge_end",
        name="Best Charge End",
        device=DEVICE_PREDICTION,
        source_suffix=".best_charge_end",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:table-clock",
    ),
    BatpredSensorDescription(
        key="best_export_start",
        name="Best Export Start",
        device=DEVICE_PREDICTION,
        source_suffix=".best_export_start",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:table-clock",
    ),
    BatpredSensorDescription(
        key="best_export_end",
        name="Best Export End",
        device=DEVICE_PREDICTION,
        source_suffix=".best_export_end",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:table-clock",
    ),
    BatpredSensorDescription(
        key="status",
        name="Status",
        device=DEVICE_PREDICTION,
        source_suffix=".status",
        icon="mdi:information-outline",
    ),
    BatpredSensorDescription(
        key="predbat_version",
        name="Version",
        device=DEVICE_PREDICTION,
        source_suffix=".predbat_version",
        icon="mdi:tag",
    ),
    # ── Rates ─────────────────────────────────────────────────────────────────
    BatpredSensorDescription(
        key="low_rate_cost",
        name="Low Rate Cost",
        device=DEVICE_RATES,
        source_suffix=".low_rate_cost",
        native_unit_of_measurement=CURRENCY_PENCE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:currency-gbp",
    ),
    BatpredSensorDescription(
        key="low_rate_start",
        name="Low Rate Start",
        device=DEVICE_RATES,
        source_suffix=".low_rate_start",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock-start",
    ),
    BatpredSensorDescription(
        key="low_rate_end",
        name="Low Rate End",
        device=DEVICE_RATES,
        source_suffix=".low_rate_end",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock-end",
    ),
    BatpredSensorDescription(
        key="low_rate_duration",
        name="Low Rate Duration",
        device=DEVICE_RATES,
        source_suffix=".low_rate_duration",
        native_unit_of_measurement="min",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:timer",
    ),
    BatpredSensorDescription(
        key="high_rate_export_cost",
        name="High Export Rate Cost",
        device=DEVICE_RATES,
        source_suffix=".high_rate_export_cost",
        native_unit_of_measurement=CURRENCY_PENCE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:currency-gbp",
    ),
    BatpredSensorDescription(
        key="high_rate_export_start",
        name="High Export Rate Start",
        device=DEVICE_RATES,
        source_suffix=".high_rate_export_start",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock-start",
    ),
    BatpredSensorDescription(
        key="high_rate_export_end",
        name="High Export Rate End",
        device=DEVICE_RATES,
        source_suffix=".high_rate_export_end",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock-end",
    ),
    BatpredSensorDescription(
        key="high_rate_export_duration",
        name="High Export Rate Duration",
        device=DEVICE_RATES,
        source_suffix=".high_rate_export_duration",
        native_unit_of_measurement="min",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:timer",
    ),
    # ── Car Charging ──────────────────────────────────────────────────────────
    BatpredSensorDescription(
        key="car_charging_start",
        name="Car Charging Start",
        device=DEVICE_CAR,
        source_suffix=".car_charging_start",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:car-electric",
    ),
    BatpredSensorDescription(
        key="car_soc",
        name="Car State of Charge",
        device=DEVICE_CAR,
        source_suffix=".car_soc",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:car-electric",
    ),
    BatpredSensorDescription(
        key="car_battery_size_kwh",
        name="Car Battery Size",
        device=DEVICE_CAR,
        source_suffix=".car_battery_size_kwh",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY_STORAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-electric-vehicle",
    ),
)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Batpred sensors from a config entry."""
    coordinator: BatpredCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [BatpredSensor(coordinator, description) for description in SENSOR_DESCRIPTIONS]
    async_add_entities(entities)


class BatpredSensor(BatpredEntity, SensorEntity):
    """Representation of a Batpred sensor."""

    entity_description: BatpredSensorDescription

    def __init__(self, coordinator: BatpredCoordinator, description: BatpredSensorDescription) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator=coordinator,
            device_name=description.device,
            entity_key=description.key,
            name=description.name,
            icon=description.icon,
        )
        self.entity_description = description

    @property
    def _source_entity_id(self) -> str:
        """Derive source entity ID from prefix + suffix."""
        return f"{self.coordinator.prefix}{self.entity_description.source_suffix}"

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        state = self._raw_state()
        if state is None or state in ("unknown", "unavailable"):
            return None
        # Try numeric conversion for numeric sensors
        if self.entity_description.native_unit_of_measurement and self.entity_description.device_class not in (SensorDeviceClass.TIMESTAMP,):
            try:
                return float(state)
            except (ValueError, TypeError):
                pass
        return state

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        return self._raw_attributes()
