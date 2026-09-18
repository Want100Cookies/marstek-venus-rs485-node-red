"""Constants for Home Battery Control."""

from __future__ import annotations

DOMAIN = "home_battery_control"
PLATFORMS = ["sensor", "binary_sensor", "number", "select", "switch", "time"]

CONF_GRID_SENSOR = "grid_sensor"
CONF_BATTERIES = "batteries"
CONF_CONTROL_ENABLED = "control_enabled"
CONF_MASTER_MODE = "master_mode"
CONF_STRATEGY = "strategy"
CONF_DASHBOARD_ENABLED = "dashboard_enabled"
CONF_MIGRATED = "migrated_from_legacy_helpers"
CONF_RATE_LIMIT_DELTA_W = "rate_limit_delta_w"
CONF_RATE_LIMIT_DELTA_PERCENT = "rate_limit_delta_percent"

MASTER_MODE_MANUAL = "manual_control"
MASTER_MODE_MARSTEK = "marstek_control"
MASTER_MODE_FULL = "full_control"
MASTER_MODES = [MASTER_MODE_MANUAL, MASTER_MODE_MARSTEK, MASTER_MODE_FULL]

STRATEGY_FULL_STOP = "full_stop"
STRATEGY_SELF_CONSUMPTION = "self_consumption"
STRATEGY_TIMED = "timed"
STRATEGY_DYNAMIC = "dynamic"
STRATEGY_CHARGE = "charge"
STRATEGY_CHARGE_PV = "charge_pv"
STRATEGY_SELL = "sell"
STRATEGY_ZERO_IMPORT = "zero_import"
STRATEGY_STANDBY_PEAK_SHAVE = "standby_peak_shave"

DEFAULT_OPTIONS = {
    CONF_CONTROL_ENABLED: False,
    CONF_MASTER_MODE: MASTER_MODE_MANUAL,
    CONF_STRATEGY: STRATEGY_FULL_STOP,
    CONF_DASHBOARD_ENABLED: True,
    CONF_RATE_LIMIT_DELTA_W: 20.0,
    CONF_RATE_LIMIT_DELTA_PERCENT: 2.0,
}

SIGN_CONVENTION = {
    "grid_power_positive": "import",
    "battery_command_positive": "charge",
    "battery_command_negative": "discharge",
}

SERVICE_SET_STRATEGY = "set_strategy"
SERVICE_PAUSE_CONTROL = "pause_control"
SERVICE_RESUME_CONTROL = "resume_control"
SERVICE_EMERGENCY_STOP = "emergency_stop"
SERVICE_RESET_PID_INTEGRAL = "reset_pid_integral"
SERVICE_APPLY_PID_PRESET = "apply_pid_preset"
SERVICE_RELOAD_MAPPINGS = "reload_mappings"

PID_PRESETS = {
    "very_safe": {"kp": 0.1, "ki": 0.1, "kd": 0.0, "input_dampening": 0.0, "output_dampening": 0.1},
    "safe": {"kp": 0.3, "ki": 0.3, "kd": 0.1, "input_dampening": 0.2, "output_dampening": 0.0},
    "regular": {"kp": 0.3, "ki": 0.4, "kd": 0.8, "input_dampening": 0.5, "output_dampening": 0.1},
}
