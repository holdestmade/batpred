"""Base entity classes for Batpred integration."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import BatpredCoordinator


def _device_info(coordinator: BatpredCoordinator, device_name: str) -> DeviceInfo:
    """Build DeviceInfo for a given logical device."""
    identifier = f"{coordinator.prefix}_{device_name.lower().replace(' ', '_')}"
    return DeviceInfo(
        identifiers={(DOMAIN, identifier)},
        name=f"Batpred {device_name}",
        manufacturer=MANUFACTURER,
        model=MODEL,
        suggested_area=device_name,
    )


class BatpredEntity(CoordinatorEntity[BatpredCoordinator]):
    """Base class for all Batpred entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: BatpredCoordinator,
        device_name: str,
        entity_key: str,
        name: str,
        icon: str | None = None,
    ) -> None:
        """Initialize the base entity."""
        super().__init__(coordinator)
        self._device_name = device_name
        self._entity_key = entity_key
        self._attr_name = name
        self._attr_icon = icon
        # Unique ID is based on prefix + device + key
        self._attr_unique_id = f"{coordinator.prefix}_{device_name.lower().replace(' ', '_')}_{entity_key}"
        self._attr_device_info = _device_info(coordinator, device_name)

    @property
    def _source_entity_id(self) -> str:
        """Return the source entity_id to read state from."""
        raise NotImplementedError

    def _raw_state(self) -> Any:
        """Return raw state value from coordinator data."""
        return self.coordinator.get_entity_state(self._source_entity_id)

    def _raw_attributes(self) -> dict[str, Any]:
        """Return raw attributes from coordinator data."""
        return self.coordinator.get_entity_attributes(self._source_entity_id)
