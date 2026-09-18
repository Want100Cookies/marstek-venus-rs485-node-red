"""Charge strategy."""

from __future__ import annotations

from ..models import BatteryCommand, BatteryTelemetry, StrategyContext, StrategyResult
from .partials import ChargePVStrategy
from .self_consumption import SelfConsumptionStrategy


class ChargeStrategy:
    def __init__(self, self_consumption: SelfConsumptionStrategy, fallback: ChargePVStrategy) -> None:
        self._self = self_consumption
        self._fallback = fallback

    def run(self, context: StrategyContext, batteries: list[BatteryTelemetry]) -> StrategyResult:
        goal = context.settings.get("charge_goal", "full")
        reached = _is_goal_reached(goal, batteries, context)
        if reached:
            result = self._fallback.run(context, batteries)
            result.selected_sub_strategy = "charge_goal_reached_follow_up"
            return result

        if context.settings.get("charge_import_limit_mode", False):
            ctx = StrategyContext(**{**context.__dict__, "target_grid_power_w": context.settings.get("charge_import_limit_w", 0), "disable_discharge": True})
            result = self._self.run(ctx, batteries)
            result.selected_sub_strategy = "charge_limited"
            return result

        commands = [BatteryCommand(b.mapping.id, "charge", b.max_charge_w) for b in batteries if b.available]
        return StrategyResult("charge", "charge_max", commands, trace=["charging at max power"], write_enabled=context.master_mode == "full_control")


def _is_goal_reached(goal: str, batteries: list[BatteryTelemetry], context: StrategyContext) -> bool:
    socs = [b.soc for b in batteries if b.available]
    if not socs:
        return True
    avg_soc = sum(socs) / len(socs)
    if goal == "full":
        return all(soc >= 99 for soc in socs)
    if goal == "target_soc":
        return avg_soc >= float(context.settings.get("charge_target_soc", 95))
    if goal == "energy_reserve_kwh":
        reserve = float(context.settings.get("charge_target_kwh", 0.0))
        total = sum((b.remaining_capacity_kwh or 0.0) for b in batteries if b.available)
        return total >= reserve
    return True
