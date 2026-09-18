"""Home Assistant entity adapter implementation."""

from __future__ import annotations

from homeassistant.core import HomeAssistant

from ..models import BatteryCommand, BatteryMapping, BatteryTelemetry
from .marstek import translate_internal_command


class HomeAssistantEntitiesAdapter:
    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass

    async def read_battery(self, mapping: BatteryMapping) -> BatteryTelemetry:
        return BatteryTelemetry(
            mapping=mapping,
            soc=_state_float(self.hass, mapping.soc_entity, 0.0),
            power_w=_state_float(self.hass, mapping.power_entity, 0.0),
            max_charge_w=_state_float(self.hass, mapping.max_charge_entity, 0.0),
            max_discharge_w=_state_float(self.hass, mapping.max_discharge_entity, 0.0),
            remaining_capacity_kwh=_state_float(self.hass, mapping.remaining_capacity_entity, 0.0)
            if mapping.remaining_capacity_entity
            else None,
            total_energy_kwh=_state_float(self.hass, mapping.total_energy_entity, 0.0)
            if mapping.total_energy_entity
            else None,
            inverter_state=_state_text(self.hass, mapping.inverter_state_entity)
            if mapping.inverter_state_entity
            else None,
            available=self.hass.states.get(mapping.soc_entity) is not None,
        )

    async def apply_command(self, mapping: BatteryMapping, command: BatteryCommand) -> dict:
        mode, power = translate_internal_command(command)
        if mapping.command_mode_entity:
            await self.hass.services.async_call(
                "select",
                "select_option",
                {"entity_id": mapping.command_mode_entity, "option": mode},
                blocking=True,
            )

        await self.hass.services.async_call(
            "number",
            "set_value",
            {"entity_id": mapping.command_power_entity, "value": abs(power)},
            blocking=True,
        )

        if mapping.rs485_mode_entity:
            await self.hass.services.async_call(
                "switch",
                "turn_on",
                {"entity_id": mapping.rs485_mode_entity},
                blocking=True,
            )

        return {"battery": mapping.id, "mode": mode, "power": power}


def _state_float(hass: HomeAssistant, entity_id: str | None, fallback: float) -> float:
    if not entity_id:
        return fallback
    state = hass.states.get(entity_id)
    if state is None:
        return fallback
    try:
        return float(state.state)
    except (TypeError, ValueError):
        return fallback


def _state_text(hass: HomeAssistant, entity_id: str | None) -> str | None:
    if not entity_id:
        return None
    state = hass.states.get(entity_id)
    return None if state is None else str(state.state)
