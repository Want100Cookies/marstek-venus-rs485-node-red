"""Select entities."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity

from .const import MASTER_MODES
from .entity_base import HomeBatteryEntity


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data["home_battery_control"][entry.entry_id]["coordinator"]
    async_add_entities(
        [
            StrategySelect(entry, coordinator),
            MasterModeSelect(entry, coordinator),
            PIDPresetSelect(entry, coordinator),
        ]
    )


class StrategySelect(HomeBatteryEntity, SelectEntity):
    _attr_options = [
        "full_stop",
        "self_consumption",
        "timed",
        "dynamic",
        "charge",
        "charge_pv",
        "sell",
        "zero_import",
        "standby_peak_shave",
    ]

    def __init__(self, entry, coordinator) -> None:
        super().__init__(entry, coordinator, "strategy", "Strategy")

    @property
    def current_option(self):
        return self.entry.options.get("strategy", self.entry.data.get("strategy", "full_stop"))

    async def async_select_option(self, option: str) -> None:
        options = dict(self.entry.options)
        options["strategy"] = option
        self.hass.config_entries.async_update_entry(self.entry, options=options)
        self.async_write_ha_state()


class MasterModeSelect(HomeBatteryEntity, SelectEntity):
    _attr_options = MASTER_MODES

    def __init__(self, entry, coordinator) -> None:
        super().__init__(entry, coordinator, "master_mode", "Master mode")

    @property
    def current_option(self):
        return self.entry.options.get("master_mode", self.entry.data.get("master_mode", "manual_control"))

    async def async_select_option(self, option: str) -> None:
        options = dict(self.entry.options)
        options["master_mode"] = option
        self.hass.config_entries.async_update_entry(self.entry, options=options)
        self.async_write_ha_state()


class PIDPresetSelect(HomeBatteryEntity, SelectEntity):
    _attr_options = ["custom", "very_safe", "safe", "regular"]

    def __init__(self, entry, coordinator) -> None:
        super().__init__(entry, coordinator, "pid_preset", "PID preset")

    @property
    def current_option(self):
        return self.entry.options.get("pid_preset", "custom")

    async def async_select_option(self, option: str) -> None:
        options = dict(self.entry.options)
        options["pid_preset"] = option
        self.hass.config_entries.async_update_entry(self.entry, options=options)
        self.async_write_ha_state()
