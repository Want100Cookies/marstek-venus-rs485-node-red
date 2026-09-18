"""Full stop strategy."""

from __future__ import annotations

from ..models import BatteryCommand, BatteryTelemetry, StrategyContext, StrategyResult


class FullStopStrategy:
    def run(self, context: StrategyContext, batteries: list[BatteryTelemetry]) -> StrategyResult:
        return StrategyResult(
            selected_strategy="full_stop",
            selected_sub_strategy="full_stop",
            commands=[BatteryCommand(b.mapping.id, "stop", 0.0) for b in batteries],
            trace=["full stop enforced"],
            write_enabled=False,
        )
