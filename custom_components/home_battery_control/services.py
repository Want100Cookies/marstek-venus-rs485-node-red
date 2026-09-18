"""Service registration."""

from __future__ import annotations

from homeassistant.core import HomeAssistant, ServiceCall

from .const import (
    DOMAIN,
    PID_PRESETS,
    SERVICE_APPLY_PID_PRESET,
    SERVICE_EMERGENCY_STOP,
    SERVICE_PAUSE_CONTROL,
    SERVICE_RELOAD_MAPPINGS,
    SERVICE_RESET_PID_INTEGRAL,
    SERVICE_RESUME_CONTROL,
    SERVICE_SET_STRATEGY,
)


async def async_register_services(hass: HomeAssistant) -> None:
    async def set_strategy(call: ServiceCall) -> None:
        strategy = call.data.get("strategy", "full_stop")
        for entry_id, data in hass.data.get(DOMAIN, {}).items():
            entry = data["entry"]
            options = dict(entry.options)
            options["strategy"] = strategy
            hass.config_entries.async_update_entry(entry, options=options)

    async def pause_control(call: ServiceCall) -> None:
        await _set_control_enabled(hass, False)

    async def resume_control(call: ServiceCall) -> None:
        await _set_control_enabled(hass, True)

    async def emergency_stop(call: ServiceCall) -> None:
        await _set_control_enabled(hass, False)
        await set_strategy(ServiceCall(DOMAIN, SERVICE_SET_STRATEGY, {"strategy": "full_stop"}))

    async def reset_pid_integral(call: ServiceCall) -> None:
        for data in hass.data.get(DOMAIN, {}).values():
            data["coordinator"].pid.runtime.integral_ws = 0.0

    async def apply_pid_preset(call: ServiceCall) -> None:
        preset = call.data.get("preset", "regular")
        values = PID_PRESETS.get(preset, {})
        for data in hass.data.get(DOMAIN, {}).values():
            controller = data["coordinator"].pid
            if "kp" in values:
                controller.config.kp = float(values["kp"])
            if "ki" in values:
                controller.apply_ki_change(float(values["ki"]))
            if "kd" in values:
                controller.config.kd = float(values["kd"])
            if "input_dampening" in values:
                controller.config.input_dampening = float(values["input_dampening"])
            if "output_dampening" in values:
                controller.config.output_dampening = float(values["output_dampening"])

    async def reload_mappings(call: ServiceCall) -> None:
        for data in hass.data.get(DOMAIN, {}).values():
            await data["coordinator"].run_cycle()

    hass.services.async_register(DOMAIN, SERVICE_SET_STRATEGY, set_strategy)
    hass.services.async_register(DOMAIN, SERVICE_PAUSE_CONTROL, pause_control)
    hass.services.async_register(DOMAIN, SERVICE_RESUME_CONTROL, resume_control)
    hass.services.async_register(DOMAIN, SERVICE_EMERGENCY_STOP, emergency_stop)
    hass.services.async_register(DOMAIN, SERVICE_RESET_PID_INTEGRAL, reset_pid_integral)
    hass.services.async_register(DOMAIN, SERVICE_APPLY_PID_PRESET, apply_pid_preset)
    hass.services.async_register(DOMAIN, SERVICE_RELOAD_MAPPINGS, reload_mappings)


async def _set_control_enabled(hass: HomeAssistant, enabled: bool) -> None:
    for data in hass.data.get(DOMAIN, {}).values():
        entry = data["entry"]
        options = dict(entry.options)
        options["control_enabled"] = enabled
        hass.config_entries.async_update_entry(entry, options=options)
