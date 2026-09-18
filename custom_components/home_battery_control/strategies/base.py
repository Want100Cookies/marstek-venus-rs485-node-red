"""Strategy interfaces and registry."""

from __future__ import annotations

from typing import Protocol

from ..models import BatteryTelemetry, StrategyContext, StrategyResult


class Strategy(Protocol):
    def run(self, context: StrategyContext, batteries: list[BatteryTelemetry]) -> StrategyResult:
        ...


class StrategyRegistry:
    def __init__(self) -> None:
        self._strategies: dict[str, Strategy] = {}

    def register(self, name: str, strategy: Strategy) -> None:
        self._strategies[name] = strategy

    def get(self, name: str) -> Strategy:
        return self._strategies[name]

    def run(self, name: str, context: StrategyContext, batteries: list[BatteryTelemetry]) -> StrategyResult:
        return self.get(name).run(context, batteries)
