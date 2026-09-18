"""Timed strategy routing."""

from __future__ import annotations

from datetime import time

from ..models import BatteryTelemetry, StrategyContext, StrategyResult
from .base import StrategyRegistry


class TimedStrategy:
    def __init__(self, registry: StrategyRegistry) -> None:
        self._registry = registry

    def run(self, context: StrategyContext, batteries: list[BatteryTelemetry]) -> StrategyResult:
        periods = context.settings.get("timed_periods", [])
        now_t = context.now.timetz().replace(tzinfo=None)
        selected = context.settings.get("timed_default_strategy", "charge_pv")
        selected_period = "default"

        for period in periods:
            if not period.get("enabled", True):
                continue
            start = _parse_time(period["start"])
            end = _parse_time(period["end"])
            if _in_window(now_t, start, end):
                selected = period["strategy"]
                selected_period = period["name"]
                break

        result = self._registry.run(selected, context, batteries)
        result.selected_strategy = "timed"
        result.selected_sub_strategy = selected
        result.trace.append(f"active_period={selected_period}")
        return result


def _parse_time(value: str) -> time:
    hh, mm = value.split(":")
    return time(int(hh), int(mm))


def _in_window(now: time, start: time, end: time) -> bool:
    if start <= end:
        return start <= now < end
    return now >= start or now < end
