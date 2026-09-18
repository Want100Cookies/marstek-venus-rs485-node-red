"""Adapter interface for battery command IO."""

from __future__ import annotations

from typing import Protocol

from ..models import BatteryCommand, BatteryMapping, BatteryTelemetry


class BatteryAdapter(Protocol):
    async def read_battery(self, mapping: BatteryMapping) -> BatteryTelemetry:
        ...

    async def apply_command(self, mapping: BatteryMapping, command: BatteryCommand) -> dict:
        ...
