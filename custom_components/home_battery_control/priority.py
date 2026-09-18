"""Battery ordering and cycling behavior."""

from __future__ import annotations

from datetime import datetime, timedelta

from .models import BatteryTelemetry


def ordered_batteries(
    batteries: list[BatteryTelemetry],
    mode: str,
    manual_priority_index: int = 0,
    now: datetime | None = None,
    cycle_anchor: datetime | None = None,
) -> list[BatteryTelemetry]:
    """Order batteries by selected priority mode."""

    if not batteries:
        return []

    if mode == "manual":
        idx = max(0, min(len(batteries) - 1, manual_priority_index))
        return batteries[idx:] + batteries[:idx]

    if mode == "never":
        return batteries

    if mode in {"auto_balance", "daily", "weekly"}:
        now = now or datetime.now()
        cycle_anchor = cycle_anchor or now
        if mode == "auto_balance":
            step = int((now - cycle_anchor) / timedelta(minutes=30))
        elif mode == "daily":
            step = (now.date() - cycle_anchor.date()).days
        else:
            step = int((now - cycle_anchor) / timedelta(days=7))
        shift = step % len(batteries)
        return batteries[shift:] + batteries[:shift]

    return batteries
