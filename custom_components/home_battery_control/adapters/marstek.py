"""Marstek preset and sign translation helpers."""

from __future__ import annotations

from ..models import BatteryCommand


def marstek_preset_from_index(index: int) -> dict[str, str]:
    prefix = f"marstek_m{index}_"
    return {
        "soc_entity": f"sensor.{prefix}soc",
        "power_entity": f"sensor.{prefix}battery_power",
        "max_charge_entity": f"number.{prefix}max_charge_power",
        "max_discharge_entity": f"number.{prefix}max_discharge_power",
        "command_power_entity": f"number.{prefix}power_control_value",
        "command_mode_entity": f"select.{prefix}forcible_charge_discharge",
        "rs485_mode_entity": f"switch.{prefix}rs485_enable",
    }


def translate_internal_command(command: BatteryCommand) -> tuple[str, float]:
    if command.mode == "charge":
        return "charge", abs(command.power_w)
    if command.mode == "discharge":
        return "discharge", abs(command.power_w)
    return "stop", 0.0
