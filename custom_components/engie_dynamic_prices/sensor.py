"""Sensor entities for Engie Dynamic Prices."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import EngieCoordinator, EngieData

PRICE_UNIT = "EUR/kWh"


@dataclass(frozen=True, kw_only=True)
class EngieSensorEntityDescription(SensorEntityDescription):
    """Describes an Engie sensor."""

    value_fn: Callable[[EngieData], float | None]
    extra_attrs_fn: Callable[[EngieData], dict[str, Any]] | None = None


SENSOR_DESCRIPTIONS: tuple[EngieSensorEntityDescription, ...] = (
    EngieSensorEntityDescription(
        key="current_price",
        translation_key="current_price",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda data: data.current_price,
    ),
    EngieSensorEntityDescription(
        key="next_price",
        translation_key="next_price",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda data: data.next_price,
    ),
    EngieSensorEntityDescription(
        key="average_price",
        translation_key="average_price",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda data: data.average_price,
        extra_attrs_fn=lambda data: {"cheapest_hours": data.cheapest_hours},
    ),
    EngieSensorEntityDescription(
        key="min_price",
        translation_key="min_price",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda data: data.min_price,
    ),
    EngieSensorEntityDescription(
        key="max_price",
        translation_key="max_price",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda data: data.max_price,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Engie sensors from a config entry."""
    coordinator: EngieCoordinator = entry.runtime_data
    async_add_entities(
        EngieSensor(coordinator, description) for description in SENSOR_DESCRIPTIONS
    )


class EngieSensor(CoordinatorEntity[EngieCoordinator], SensorEntity):
    """A sensor that reports an Engie dynamic electricity price."""

    entity_description: EngieSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EngieCoordinator,
        description: EngieSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{description.key}"
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, DOMAIN)},
            name="Engie Dynamic Prices",
            manufacturer="Engie",
        )

    @property
    def native_value(self) -> float | None:
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if self.entity_description.extra_attrs_fn is None:
            return None
        return self.entity_description.extra_attrs_fn(self.coordinator.data)
