"""Core domain models for Home Battery Control."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class BatteryMapping:
    """Mapping from integration model to Home Assistant entities."""

    id: str
    name: str
    soc_entity: str
    power_entity: str
    max_charge_entity: str
    max_discharge_entity: str
    command_power_entity: str
    command_mode_entity: str | None = None
    remaining_capacity_entity: str | None = None
    total_energy_entity: str | None = None
    rs485_mode_entity: str | None = None
    user_work_mode_entity: str | None = None
    inverter_state_entity: str | None = None
    min_soc: float = 10.0
    max_soc: float = 95.0


@dataclass(slots=True)
class BatteryTelemetry:
    """Normalized battery telemetry."""

    mapping: BatteryMapping
    soc: float
    power_w: float
    max_charge_w: float
    max_discharge_w: float
    remaining_capacity_kwh: float | None = None
    total_energy_kwh: float | None = None
    inverter_state: str | None = None
    available: bool = True


@dataclass(slots=True)
class BatteryCommand:
    """Battery command in internal sign convention."""

    battery_id: str
    mode: str
    power_w: float


@dataclass(slots=True)
class PIDStateSnapshot:
    error: float = 0.0
    filtered_error: float = 0.0
    derivative: float = 0.0
    p_term: float = 0.0
    i_term: float = 0.0
    d_term: float = 0.0
    output: float = 0.0


@dataclass(slots=True)
class StrategyContext:
    now: datetime
    grid_power_w: float
    selected_strategy: str
    target_grid_power_w: float = 0.0
    master_mode: str = "manual_control"
    ev_is_charging: bool = False
    ev_override_strategy: str = "full_stop"
    disable_charge: bool = False
    disable_discharge: bool = False
    import_limit_w: float = 0.0
    export_limit_w: float = 0.0
    hysteresis_w: float = 20.0
    settings: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class StrategyResult:
    selected_strategy: str
    selected_sub_strategy: str
    commands: list[BatteryCommand] = field(default_factory=list)
    pid: PIDStateSnapshot = field(default_factory=PIDStateSnapshot)
    trace: list[str] = field(default_factory=list)
    write_enabled: bool = False


@dataclass(slots=True)
class DynamicInterval:
    start: datetime
    end: datetime
    price: float
    mark: str = "neutral"


@dataclass(slots=True)
class DynamicMarkResult:
    intervals: list[DynamicInterval]
    mark_now: str
    gross_spread: float
    datapoints_per_hour: int
    trace: list[str] = field(default_factory=list)
