"""Binary sensor entities."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity

from .entity_base import HomeBatteryEntity


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data["home_battery_control"][entry.entry_id]["coordinator"]
    async_add_entities(
        [
            RuntimeBinary(entry, coordinator, "write_enabled", "Writes enabled"),
            RuntimeBinary(entry, coordinator, "dynamic_data_available", "Dynamic provider data available"),
        ]
    )


class RuntimeBinary(HomeBatteryEntity, BinarySensorEntity):
    def __init__(self, entry, coordinator, key, name):
        super().__init__(entry, coordinator, key, name)

    @property
    def is_on(self):
        result = self.coordinator.state.last_result
        if self._key == "write_enabled":
            return bool(result and result.write_enabled)
        if self._key == "dynamic_data_available":
            return self.entry.options.get("dynamic_provider", "none") != "none"
        return False
