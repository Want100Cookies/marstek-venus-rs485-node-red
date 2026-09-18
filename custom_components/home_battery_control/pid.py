"""Pure PID controller logic for self-consumption strategy."""

from __future__ import annotations

from dataclasses import dataclass

INTEGRAL_CLAMP_WS = 30_000.0


@dataclass(slots=True)
class PIDConfig:
    kp: float = 0.3
    ki: float = 0.4
    kd: float = 0.8
    input_dampening: float = 0.5
    output_dampening: float = 0.1


@dataclass(slots=True)
class PIDRuntime:
    filtered_error: float = 0.0
    prev_filtered_error: float = 0.0
    integral_ws: float = 0.0
    output: float = 0.0

    def reset(self) -> None:
        self.filtered_error = 0.0
        self.prev_filtered_error = 0.0
        self.integral_ws = 0.0
        self.output = 0.0


class PIDController:
    """PID with dampening and bumpless Ki changes."""

    def __init__(self, config: PIDConfig | None = None) -> None:
        self.config = config or PIDConfig()
        self.runtime = PIDRuntime()

    def apply_ki_change(self, new_ki: float) -> None:
        old_ki = self.config.ki
        self.config.ki = new_ki
        if old_ki == 0 and new_ki == 0:
            return
        if old_ki == 0:
            self.runtime.integral_ws = 0.0
            return
        i_output = old_ki * self.runtime.integral_ws
        self.runtime.integral_ws = 0.0 if new_ki == 0 else i_output / new_ki

    def calculate(self, error: float, dt: float) -> dict[str, float]:
        if dt <= 0:
            dt = 1.0

        alpha_in = _clamp01(1.0 - self.config.input_dampening)
        self.runtime.filtered_error = self.runtime.filtered_error + alpha_in * (error - self.runtime.filtered_error)

        p_term = self.config.kp * self.runtime.filtered_error
        self.runtime.integral_ws = _clamp(
            self.runtime.integral_ws + self.runtime.filtered_error * dt,
            -INTEGRAL_CLAMP_WS,
            INTEGRAL_CLAMP_WS,
        )
        i_term = self.config.ki * self.runtime.integral_ws

        derivative = (self.runtime.filtered_error - self.runtime.prev_filtered_error) / dt
        d_term = self.config.kd * derivative

        raw_output = p_term + i_term + d_term
        alpha_out = _clamp01(1.0 - self.config.output_dampening)
        self.runtime.output = self.runtime.output + alpha_out * (raw_output - self.runtime.output)
        self.runtime.prev_filtered_error = self.runtime.filtered_error

        return {
            "error": error,
            "filtered_error": self.runtime.filtered_error,
            "p_term": p_term,
            "i_term": i_term,
            "d_term": d_term,
            "derivative": derivative,
            "output": self.runtime.output,
        }


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _clamp01(value: float) -> float:
    return _clamp(value, 0.0, 1.0)
