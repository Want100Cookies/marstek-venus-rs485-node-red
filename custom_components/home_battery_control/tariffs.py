"""Tariff providers and dynamic interval marking."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from .models import DynamicInterval, DynamicMarkResult


class TariffProvider(Protocol):
    def get_intervals(self, now: datetime) -> list[DynamicInterval]:
        """Return intervals for local-calendar day."""


@dataclass(slots=True)
class EmptyProvider:
    def get_intervals(self, now: datetime) -> list[DynamicInterval]:
        return []


def mark_extreme_pairs(
    intervals: list[DynamicInterval],
    min_delta: float,
    max_cheap_hours: int = 0,
    max_expensive_hours: int = 0,
    datapoints_per_hour: int = 1,
    now: datetime | None = None,
) -> DynamicMarkResult:
    """Mark cheapest and most expensive intervals in pairs until spread fails."""

    if not intervals:
        return DynamicMarkResult([], "neutral", 0.0, datapoints_per_hour, ["dynamic provider returned no intervals"])

    sorted_by_price = sorted(intervals, key=lambda i: i.price)
    cheap_cap = max_cheap_hours * datapoints_per_hour if max_cheap_hours > 0 else len(intervals)
    expensive_cap = max_expensive_hours * datapoints_per_hour if max_expensive_hours > 0 else len(intervals)

    cheap_used = 0
    expensive_used = 0
    for cheap, expensive in zip(sorted_by_price, reversed(sorted_by_price)):
        spread = expensive.price - cheap.price
        if spread < min_delta:
            break
        if cheap_used < cheap_cap:
            cheap.mark = "low"
            cheap_used += 1
        if expensive_used < expensive_cap:
            expensive.mark = "high"
            expensive_used += 1
        if cheap_used >= cheap_cap and expensive_used >= expensive_cap:
            break

    gross_spread = max(i.price for i in intervals) - min(i.price for i in intervals)
    now = now or datetime.now()
    current = next((i for i in intervals if i.start <= now < i.end), None)
    mark_now = current.mark if current else "neutral"
    return DynamicMarkResult(
        intervals=intervals,
        mark_now=mark_now,
        gross_spread=gross_spread,
        datapoints_per_hour=datapoints_per_hour,
        trace=[f"marked {cheap_used} low and {expensive_used} high intervals"],
    )
