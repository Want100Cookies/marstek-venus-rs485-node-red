"""Sensor entities."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity

from .entity_base import HomeBatteryEntity


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data["home_battery_control"][entry.entry_id]["coordinator"]
    async_add_entities(
        [
            RuntimeSensor(entry, coordinator, "active_sub_strategy", "Active sub-strategy"),
            RuntimeSensor(entry, coordinator, "last_cycle_duration_ms", "Last cycle duration", unit="ms"),
            RuntimeSensor(entry, coordinator, "rate_limiter_mode", "Rate limiter mode"),
            RuntimeSensor(entry, coordinator, "last_write_status", "Last write status"),
            RuntimeSensor(entry, coordinator, "pid_output", "PID output", unit="W"),
            RuntimeSensor(entry, coordinator, "pid_error", "PID error", unit="W"),
        ]
    )


class RuntimeSensor(HomeBatteryEntity, SensorEntity):
    def __init__(self, entry, coordinator, key, name, unit=None):
        super().__init__(entry, coordinator, key, name)
        if unit:
            self._attr_native_unit_of_measurement = unit

    @property
    def native_value(self):
        result = self.coordinator.state.last_result
        if self._key == "active_sub_strategy":
            return result.selected_sub_strategy if result else "unknown"
        if self._key == "last_cycle_duration_ms":
            return self.entry.options.get("last_cycle_duration_ms", 0)
        if self._key == "rate_limiter_mode":
            return self.entry.options.get("rate_limiter_mode", "idle")
        if self._key == "last_write_status":
            return self.entry.options.get("last_write_status", "none")
        if self._key == "pid_output":
            return result.pid.output if result else 0
        if self._key == "pid_error":
            return result.pid.error if result else 0
        return None
