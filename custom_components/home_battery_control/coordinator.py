"""Coordinator and runtime loop."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

from homeassistant.core import HomeAssistant

from .const import MASTER_MODE_FULL
from .models import BatteryCommand, BatteryMapping, BatteryTelemetry, StrategyContext, StrategyResult
from .pid import PIDConfig, PIDController
from .strategies.base import StrategyRegistry
from .strategies.charge import ChargeStrategy
from .strategies.dynamic import DynamicStrategy
from .strategies.full_stop import FullStopStrategy
from .strategies.partials import ChargePVStrategy, StandbyPeakShaveStrategy, ZeroImportStrategy
from .strategies.self_consumption import SelfConsumptionStrategy
from .strategies.sell import SellStrategy
from .strategies.timed import TimedStrategy
from .adapters.home_assistant_entities import HomeAssistantEntitiesAdapter

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class RuntimeState:
    last_cycle_at: datetime | None = None
    last_grid_power_w: float | None = None
    write_lock_until: datetime | None = None
    pending_commands: list[tuple[BatteryMapping, BatteryCommand]] | None = None
    last_result: StrategyResult | None = None


class HomeBatteryCoordinator:
    """Owns refresh and write cycle."""

    def __init__(self, hass: HomeAssistant, entry) -> None:
        self.hass = hass
        self.entry = entry
        self.state = RuntimeState()
        self.adapter = HomeAssistantEntitiesAdapter(hass)
        self.pid = PIDController(PIDConfig())
        self.registry = self._build_registry()

    def _build_registry(self) -> StrategyRegistry:
        reg = StrategyRegistry()
        self_consumption = SelfConsumptionStrategy(self.pid)
        charge_pv = ChargePVStrategy(self_consumption)
        reg.register("full_stop", FullStopStrategy())
        reg.register("self_consumption", self_consumption)
        reg.register("charge_pv", charge_pv)
        reg.register("zero_import", ZeroImportStrategy(self_consumption))
        reg.register("standby_peak_shave", StandbyPeakShaveStrategy(self_consumption))
        reg.register("charge", ChargeStrategy(self_consumption, charge_pv))
        reg.register("sell", SellStrategy(self_consumption, charge_pv))
        reg.register("timed", TimedStrategy(reg))
        reg.register("dynamic", DynamicStrategy(reg))
        return reg

    async def run_cycle(self) -> StrategyResult:
        now = datetime.now()
        grid_power_w = _state_float(self.hass, self.entry.data["grid_sensor"], 0.0)
        batteries = await self._read_batteries()
        selected_strategy = self.entry.options.get("strategy", self.entry.data.get("strategy", "full_stop"))

        if self.entry.options.get("ev_is_charging_entity"):
            ev_state = self.hass.states.get(self.entry.options["ev_is_charging_entity"])
            if ev_state and ev_state.state.lower() == "on":
                selected_strategy = self.entry.options.get("ev_override_strategy", "full_stop")

        context = StrategyContext(
            now=now,
            grid_power_w=grid_power_w,
            selected_strategy=selected_strategy,
            target_grid_power_w=float(self.entry.options.get("target_grid_power_w", 0.0)),
            master_mode=self.entry.options.get("master_mode", self.entry.data.get("master_mode", "manual_control")),
            import_limit_w=float(self.entry.options.get("import_limit_w", 0.0)),
            export_limit_w=float(self.entry.options.get("export_limit_w", 0.0)),
            hysteresis_w=float(self.entry.options.get("hysteresis_w", 20.0)),
            settings=dict(self.entry.options),
        )

        if selected_strategy == "full_stop":
            result = self.registry.run("full_stop", context, batteries)
        else:
            result = self.registry.run(selected_strategy, context, batteries)

        await self._maybe_apply_commands(now, batteries, result)
        self.state.last_result = result
        self.state.last_cycle_at = now
        self.state.last_grid_power_w = grid_power_w
        return result

    async def _read_batteries(self) -> list[BatteryTelemetry]:
        batteries: list[BatteryTelemetry] = []
        for cfg in self.entry.options.get("batteries", self.entry.data.get("batteries", [])):
            mapping = BatteryMapping(**cfg)
            telemetry = await self.adapter.read_battery(mapping)
            batteries.append(telemetry)
        return batteries

    async def _maybe_apply_commands(self, now: datetime, batteries: list[BatteryTelemetry], result: StrategyResult) -> None:
        if self.entry.options.get("control_enabled", False) is not True:
            result.trace.append("writes blocked: control disabled")
            return
        if self.entry.options.get("master_mode") != MASTER_MODE_FULL:
            result.trace.append("writes blocked: master mode not full_control")
            return

        if self.state.write_lock_until and now < self.state.write_lock_until:
            self.state.pending_commands = self._pair_commands(batteries, result.commands)
            result.trace.append("write lock active; coalesced pending commands")
            return

        self.state.write_lock_until = now + timedelta(seconds=30)
        try:
            await self._apply_now(batteries, result.commands)
            result.trace.append("write cycle applied")
        finally:
            self.state.write_lock_until = now + timedelta(seconds=1)

        if self.state.pending_commands:
            pending = self.state.pending_commands
            self.state.pending_commands = None
            for mapping, command in pending:
                await self.adapter.apply_command(mapping, command)
            result.trace.append("applied coalesced pending write")

    async def _apply_now(self, batteries: list[BatteryTelemetry], commands: list[BatteryCommand]) -> None:
        pairs = self._pair_commands(batteries, commands)
        for mapping, command in pairs:
            await self.adapter.apply_command(mapping, command)

    @staticmethod
    def _pair_commands(
        batteries: list[BatteryTelemetry],
        commands: list[BatteryCommand],
    ) -> list[tuple[BatteryMapping, BatteryCommand]]:
        by_id = {b.mapping.id: b.mapping for b in batteries}
        pairs: list[tuple[BatteryMapping, BatteryCommand]] = []
        for command in commands:
            mapping = by_id.get(command.battery_id)
            if mapping:
                pairs.append((mapping, command))
        return pairs


def _state_float(hass: HomeAssistant, entity_id: str, fallback: float) -> float:
    state = hass.states.get(entity_id)
    if state is None:
        return fallback
    try:
        return float(state.state)
    except (TypeError, ValueError):
        return fallback
