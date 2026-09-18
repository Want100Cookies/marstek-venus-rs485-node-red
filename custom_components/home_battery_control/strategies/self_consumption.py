"""Self-consumption strategy with PID and distribution."""

from __future__ import annotations

from ..models import BatteryCommand, BatteryTelemetry, PIDStateSnapshot, StrategyContext, StrategyResult
from ..pid import PIDController
from ..priority import ordered_batteries


class SelfConsumptionStrategy:
    def __init__(self, pid: PIDController) -> None:
        self._pid = pid

    def run(self, context: StrategyContext, batteries: list[BatteryTelemetry]) -> StrategyResult:
        error = context.target_grid_power_w - context.grid_power_w
        pid = self._pid.calculate(error, dt=1.0)
        command_total = pid["output"]

        if abs(error) < abs(context.hysteresis_w):
            command_total = 0.0

        if context.master_mode in {"manual_control", "marstek_control"}:
            command_total = 0.0

        ordered = ordered_batteries(
            batteries,
            mode=context.settings.get("priority_mode", "never"),
            manual_priority_index=int(context.settings.get("priority_index", 0)),
            now=context.now,
            cycle_anchor=context.settings.get("priority_anchor"),
        )

        remaining = command_total
        commands: list[BatteryCommand] = []
        for battery in ordered:
            cmd = _compute_battery_command(battery, remaining, context)
            commands.append(cmd)
            remaining -= cmd.power_w

        return StrategyResult(
            selected_strategy="self_consumption",
            selected_sub_strategy="self_consumption",
            commands=commands,
            pid=PIDStateSnapshot(
                error=pid["error"],
                filtered_error=pid["filtered_error"],
                derivative=pid["derivative"],
                p_term=pid["p_term"],
                i_term=pid["i_term"],
                d_term=pid["d_term"],
                output=command_total,
            ),
            trace=[f"pid output={command_total:.2f}W", f"remaining={remaining:.2f}W"],
            write_enabled=context.master_mode == "full_control",
        )


def _compute_battery_command(battery: BatteryTelemetry, target_w: float, context: StrategyContext) -> BatteryCommand:
    if not battery.available:
        return BatteryCommand(battery.mapping.id, "stop", 0.0)

    charge_limit = max(0.0, battery.max_charge_w)
    discharge_limit = max(0.0, battery.max_discharge_w)

    if battery.soc >= max(95.0, battery.mapping.max_soc):
        charge_limit *= 0.2
    if battery.soc <= min(10.0, battery.mapping.min_soc):
        discharge_limit *= 0.2

    if context.disable_charge:
        charge_limit = 0.0
    if context.disable_discharge:
        discharge_limit = 0.0

    requested = target_w
    requested = min(requested, charge_limit)
    requested = max(requested, -discharge_limit)

    if requested > 0:
        mode = "charge"
    elif requested < 0:
        mode = "discharge"
    else:
        mode = "stop"

    return BatteryCommand(battery.mapping.id, mode, round(requested, 2))
