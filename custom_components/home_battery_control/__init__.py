"""Home Battery Control integration."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval
from .const import DOMAIN
from .coordinator import HomeBatteryCoordinator
from .dashboard import async_register_dashboard
from .services import async_register_services

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SWITCH,
    Platform.TIME,
]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    hass.data.setdefault(DOMAIN, {})
    await async_register_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = HomeBatteryCoordinator(hass, entry)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {"coordinator": coordinator, "entry": entry}
    hass.http.register_static_path(f"/{DOMAIN}", hass.config.path(f"custom_components/{DOMAIN}/frontend"), cache_headers=False)
    if entry.options.get("dashboard_enabled", True):
        await async_register_dashboard(hass, entry)

    async def _tick(_now):
        await coordinator.run_cycle()

    unsub = async_track_time_interval(hass, _tick, timedelta(seconds=1))
    hass.data[DOMAIN][entry.entry_id]["unsub"] = unsub

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if data := hass.data.get(DOMAIN, {}).get(entry.entry_id):
        if "unsub" in data:
            data["unsub"]()
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
