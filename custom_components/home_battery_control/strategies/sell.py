"""Sell strategy."""

from __future__ import annotations

from ..models import BatteryCommand, BatteryTelemetry, StrategyContext, StrategyResult
from .partials import ChargePVStrategy
from .self_consumption import SelfConsumptionStrategy


class SellStrategy:
    def __init__(self, self_consumption: SelfConsumptionStrategy, fallback: ChargePVStrategy) -> None:
        self._self = self_consumption
        self._fallback = fallback

    def run(self, context: StrategyContext, batteries: list[BatteryTelemetry]) -> StrategyResult:
        goal = context.settings.get("sell_goal", "min_soc")
        reached = _is_goal_reached(goal, batteries, context)
        if reached:
            result = self._fallback.run(context, batteries)
            result.selected_sub_strategy = "sell_goal_reached_follow_up"
            return result

        if context.settings.get("sell_export_limit_mode", False):
            ctx = StrategyContext(**{**context.__dict__, "target_grid_power_w": -abs(context.settings.get("sell_export_limit_w", 0)), "disable_charge": True})
            result = self._self.run(ctx, batteries)
            result.selected_sub_strategy = "sell_limited"
            return result

        commands = [BatteryCommand(b.mapping.id, "discharge", -b.max_discharge_w) for b in batteries if b.available]
        return StrategyResult("sell", "sell_max", commands, trace=["discharging at max power"], write_enabled=context.master_mode == "full_control")


def _is_goal_reached(goal: str, batteries: list[BatteryTelemetry], context: StrategyContext) -> bool:
    socs = [b.soc for b in batteries if b.available]
    if not socs:
        return True
    avg_soc = sum(socs) / len(socs)
    if goal == "min_soc":
        return all(soc <= float(context.settings.get("sell_min_soc", 10)) for soc in socs)
    if goal == "target_soc":
        return avg_soc <= float(context.settings.get("sell_target_soc", 20))
    if goal == "energy_floor_kwh":
        floor = float(context.settings.get("sell_floor_kwh", 0.0))
        total = sum((b.remaining_capacity_kwh or 0.0) for b in batteries if b.available)
        return total <= floor
    return True
