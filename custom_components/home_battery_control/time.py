"""Time entities for timed strategy windows."""

from __future__ import annotations

from datetime import time as dt_time

from homeassistant.components.time import TimeEntity

from .entity_base import HomeBatteryEntity


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data["home_battery_control"][entry.entry_id]["coordinator"]
    async_add_entities(
        [
            TimedPeriodTime(entry, coordinator, "period_a_start", "Period A start", dt_time(0, 0)),
            TimedPeriodTime(entry, coordinator, "period_a_end", "Period A end", dt_time(23, 59)),
        ]
    )


class TimedPeriodTime(HomeBatteryEntity, TimeEntity):
    def __init__(self, entry, coordinator, key, name, default):
        super().__init__(entry, coordinator, key, name)
        self._default = default

    @property
    def native_value(self):
        raw = self.entry.options.get(self._key)
        if not raw:
            return self._default
        hh, mm = [int(x) for x in str(raw).split(":")]
        return dt_time(hh, mm)

    async def async_set_value(self, value: dt_time) -> None:
        options = dict(self.entry.options)
        options[self._key] = value.strftime("%H:%M")
        self.hass.config_entries.async_update_entry(self.entry, options=options)
        self.async_write_ha_state()
