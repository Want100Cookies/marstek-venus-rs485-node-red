"""Diagnostics support."""

from __future__ import annotations

from homeassistant.components.diagnostics import async_redact_data

TO_REDACT = {"token", "api_key", "password"}


async def async_get_config_entry_diagnostics(hass, entry):
    coordinator = hass.data["home_battery_control"][entry.entry_id]["coordinator"]
    return async_redact_data(
        {
            "entry": {"data": dict(entry.data), "options": dict(entry.options)},
            "last_result": coordinator.state.last_result,
            "runtime": {
                "last_cycle_at": coordinator.state.last_cycle_at,
                "last_grid_power_w": coordinator.state.last_grid_power_w,
                "write_lock_until": coordinator.state.write_lock_until,
            },
        },
        TO_REDACT,
    )
