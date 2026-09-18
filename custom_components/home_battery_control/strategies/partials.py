"""Partial strategies built on self-consumption."""

from __future__ import annotations

from datetime import timedelta

from ..models import BatteryTelemetry, StrategyContext, StrategyResult
from .self_consumption import SelfConsumptionStrategy


class ChargePVStrategy:
    def __init__(self, self_consumption: SelfConsumptionStrategy) -> None:
        self._self = self_consumption

    def run(self, context: StrategyContext, batteries: list[BatteryTelemetry]) -> StrategyResult:
        ctx = _copy_context(context, disable_discharge=True)
        result = self._self.run(ctx, batteries)
        result.selected_sub_strategy = "charge_pv"
        return result


class ZeroImportStrategy:
    def __init__(self, self_consumption: SelfConsumptionStrategy) -> None:
        self._self = self_consumption

    def run(self, context: StrategyContext, batteries: list[BatteryTelemetry]) -> StrategyResult:
        ctx = _copy_context(context, disable_charge=True)
        result = self._self.run(ctx, batteries)
        result.selected_sub_strategy = "zero_import"
        return result


class StandbyPeakShaveStrategy:
    def __init__(self, self_consumption: SelfConsumptionStrategy) -> None:
        self._self = self_consumption
        self._latched_direction: str | None = None
        self._latched_until = None

    def run(self, context: StrategyContext, batteries: list[BatteryTelemetry]) -> StrategyResult:
        now = context.now
        import_limit = context.settings.get("peak_import_limit_w", context.import_limit_w)
        export_limit = context.settings.get("peak_export_limit_w", context.export_limit_w)

        if context.grid_power_w > import_limit > 0:
            self._latched_direction = "import"
            self._latched_until = now + timedelta(seconds=10)
        elif context.grid_power_w < -abs(export_limit) and export_limit > 0:
            self._latched_direction = "export"
            self._latched_until = now + timedelta(seconds=10)

        if self._latched_until and now <= self._latched_until and self._latched_direction:
            if self._latched_direction == "import":
                ctx = _copy_context(context, disable_charge=True)
            else:
                ctx = _copy_context(context, disable_discharge=True)
            result = self._self.run(ctx, batteries)
            result.selected_sub_strategy = f"standby_peak_shave_{self._latched_direction}"
            result.trace.append("peak shave direction latched")
            return result

        return StrategyResult(
            selected_strategy="standby_peak_shave",
            selected_sub_strategy="standby_peak_shave_idle",
            commands=[],
            trace=["standby idle"],
            write_enabled=False,
        )


def _copy_context(context: StrategyContext, **changes) -> StrategyContext:
    kwargs = context.__dict__.copy()
    kwargs.update(changes)
    return StrategyContext(**kwargs)
