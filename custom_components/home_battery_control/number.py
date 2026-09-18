"""Number entities."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity

from .entity_base import HomeBatteryEntity


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data["home_battery_control"][entry.entry_id]["coordinator"]
    async_add_entities(
        [
            ConfigNumber(entry, coordinator, "target_grid_power_w", "Target grid power", -15000, 15000, 1, "W"),
            ConfigNumber(entry, coordinator, "hysteresis_w", "PID hysteresis", 0, 500, 1, "W"),
            ConfigNumber(entry, coordinator, "import_limit_w", "Import limit", 0, 20000, 1, "W"),
            ConfigNumber(entry, coordinator, "export_limit_w", "Export limit", 0, 20000, 1, "W"),
        ]
    )


class ConfigNumber(HomeBatteryEntity, NumberEntity):
    def __init__(self, entry, coordinator, key, name, min_v, max_v, step, unit):
        super().__init__(entry, coordinator, key, name)
        self._attr_native_min_value = min_v
        self._attr_native_max_value = max_v
        self._attr_native_step = step
        self._attr_native_unit_of_measurement = unit

    @property
    def native_value(self):
        return float(self.entry.options.get(self._key, self.entry.data.get(self._key, 0.0)))

    async def async_set_native_value(self, value: float) -> None:
        options = dict(self.entry.options)
        options[self._key] = value
        self.hass.config_entries.async_update_entry(self.entry, options=options)
        self.async_write_ha_state()
