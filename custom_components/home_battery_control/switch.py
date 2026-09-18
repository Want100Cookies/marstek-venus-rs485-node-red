"""Switch entities."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity

from .entity_base import HomeBatteryEntity


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data["home_battery_control"][entry.entry_id]["coordinator"]
    async_add_entities(
        [
            ConfigSwitch(entry, coordinator, "control_enabled", "Control enabled", False),
            ConfigSwitch(entry, coordinator, "dashboard_enabled", "Dashboard panel enabled", True),
            ConfigSwitch(entry, coordinator, "debug_enabled", "Debug mode", False),
        ]
    )


class ConfigSwitch(HomeBatteryEntity, SwitchEntity):
    def __init__(self, entry, coordinator, key, name, default):
        super().__init__(entry, coordinator, key, name)
        self._default = default

    @property
    def is_on(self):
        return bool(self.entry.options.get(self._key, self.entry.data.get(self._key, self._default)))

    async def async_turn_on(self, **kwargs):
        await self._set(True)

    async def async_turn_off(self, **kwargs):
        await self._set(False)

    async def _set(self, value: bool) -> None:
        options = dict(self.entry.options)
        options[self._key] = value
        self.hass.config_entries.async_update_entry(self.entry, options=options)
        self.async_write_ha_state()
