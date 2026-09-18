"""Dynamic strategy based on tariff marks."""

from __future__ import annotations

from ..models import BatteryTelemetry, StrategyContext, StrategyResult
from ..tariffs import EmptyProvider, TariffProvider, mark_extreme_pairs
from .base import StrategyRegistry


class DynamicStrategy:
    def __init__(self, registry: StrategyRegistry, provider: TariffProvider | None = None) -> None:
        self._registry = registry
        self._provider = provider or EmptyProvider()

    def run(self, context: StrategyContext, batteries: list[BatteryTelemetry]) -> StrategyResult:
        intervals = self._provider.get_intervals(context.now)
        if not intervals:
            fallback = context.settings.get("dynamic_fallback_strategy", "charge_pv")
            result = self._registry.run(fallback, context, batteries)
            result.selected_strategy = "dynamic"
            result.selected_sub_strategy = fallback
            result.trace.append("dynamic fallback because provider returned no data")
            return result

        marks = mark_extreme_pairs(
            intervals,
            min_delta=float(context.settings.get("dynamic_min_delta", 0.05)),
            max_cheap_hours=int(context.settings.get("dynamic_max_cheap_hours", 0)),
            max_expensive_hours=int(context.settings.get("dynamic_max_expensive_hours", 0)),
            datapoints_per_hour=int(context.settings.get("dynamic_datapoints_per_hour", 1)),
            now=context.now,
        )

        if marks.mark_now == "low":
            selected = context.settings.get("dynamic_low_strategy", "charge")
        elif marks.mark_now == "high":
            selected = context.settings.get("dynamic_high_strategy", "sell")
        else:
            selected = context.settings.get("dynamic_neutral_strategy", "charge_pv")

        result = self._registry.run(selected, context, batteries)
        result.selected_strategy = "dynamic"
        result.selected_sub_strategy = selected
        result.trace.extend(marks.trace)
        result.trace.append(f"mark_now={marks.mark_now}")
        return result
