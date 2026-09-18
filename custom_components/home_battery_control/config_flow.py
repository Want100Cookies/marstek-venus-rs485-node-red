"""Config flow for Home Battery Control."""

from __future__ import annotations

from collections.abc import Mapping

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import (
    CONF_BATTERIES,
    CONF_CONTROL_ENABLED,
    CONF_DASHBOARD_ENABLED,
    CONF_GRID_SENSOR,
    CONF_MASTER_MODE,
    CONF_MIGRATED,
    CONF_STRATEGY,
    DEFAULT_OPTIONS,
    DOMAIN,
)
from .adapters.marstek import marstek_preset_from_index


class HomeBatteryControlConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._data: dict = {}

    async def async_step_user(self, user_input: dict | None = None):
        if user_input is not None:
            self._data["name"] = user_input["name"]
            return await self.async_step_grid()

        schema = vol.Schema(
            {
                vol.Required("name", default="Home Battery Control"): str,
                vol.Required(CONF_CONTROL_ENABLED, default=False): bool,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_grid(self, user_input: dict | None = None):
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_batteries()

        schema = vol.Schema(
            {
                vol.Required(CONF_GRID_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor")
                ),
            }
        )
        return self.async_show_form(step_id="grid", data_schema=schema)

    async def async_step_batteries(self, user_input: dict | None = None):
        if user_input is not None:
            mappings = []
            count = int(user_input["count"])
            use_marstek = user_input.get("marstek_preset", True)
            for i in range(1, count + 1):
                if use_marstek:
                    mapping = {"id": f"battery_{i}", "name": f"Battery {i}"}
                    mapping.update(marstek_preset_from_index(i))
                    mappings.append(mapping)
            self._data[CONF_BATTERIES] = mappings
            return await self.async_step_finish()

        schema = vol.Schema(
            {
                vol.Required("count", default=1): vol.All(vol.Coerce(int), vol.Range(min=1, max=6)),
                vol.Required("marstek_preset", default=True): bool,
            }
        )
        return self.async_show_form(step_id="batteries", data_schema=schema)

    async def async_step_finish(self, user_input: dict | None = None):
        if user_input is not None:
            options = dict(DEFAULT_OPTIONS)
            options[CONF_STRATEGY] = user_input[CONF_STRATEGY]
            options[CONF_MASTER_MODE] = user_input[CONF_MASTER_MODE]
            options[CONF_DASHBOARD_ENABLED] = user_input[CONF_DASHBOARD_ENABLED]
            options[CONF_MIGRATED] = await _seed_from_legacy_helpers(self.hass, options)
            title = self._data.get("name", "Home Battery Control")
            data = {
                CONF_GRID_SENSOR: self._data[CONF_GRID_SENSOR],
                CONF_BATTERIES: self._data[CONF_BATTERIES],
                CONF_CONTROL_ENABLED: self._data.get(CONF_CONTROL_ENABLED, False),
                CONF_MASTER_MODE: options[CONF_MASTER_MODE],
                CONF_STRATEGY: options[CONF_STRATEGY],
            }
            return self.async_create_entry(title=title, data=data, options=options)

        schema = vol.Schema(
            {
                vol.Required(CONF_MASTER_MODE, default=DEFAULT_OPTIONS[CONF_MASTER_MODE]): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=["manual_control", "marstek_control", "full_control"])
                ),
                vol.Required(CONF_STRATEGY, default=DEFAULT_OPTIONS[CONF_STRATEGY]): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            "full_stop",
                            "self_consumption",
                            "timed",
                            "dynamic",
                            "charge",
                            "charge_pv",
                            "sell",
                            "zero_import",
                            "standby_peak_shave",
                        ]
                    )
                ),
                vol.Required(CONF_DASHBOARD_ENABLED, default=True): bool,
            }
        )
        return self.async_show_form(step_id="finish", data_schema=schema)

    @staticmethod
    def async_get_options_flow(config_entry):
        return HomeBatteryControlOptionsFlow(config_entry)


class HomeBatteryControlOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, entry) -> None:
        self.entry = entry

    async def async_step_init(self, user_input: dict | None = None):
        if user_input is not None:
            options = dict(self.entry.options)
            options.update(user_input)
            return self.async_create_entry(title="", data=options)

        schema = vol.Schema(
            {
                vol.Required(CONF_STRATEGY, default=self.entry.options.get(CONF_STRATEGY, "full_stop")): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            "full_stop",
                            "self_consumption",
                            "timed",
                            "dynamic",
                            "charge",
                            "charge_pv",
                            "sell",
                            "zero_import",
                            "standby_peak_shave",
                        ]
                    )
                ),
                vol.Required(CONF_MASTER_MODE, default=self.entry.options.get(CONF_MASTER_MODE, "manual_control")): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=["manual_control", "marstek_control", "full_control"])
                ),
                vol.Required("target_grid_power_w", default=self.entry.options.get("target_grid_power_w", 0.0)): vol.Coerce(float),
                vol.Required("hysteresis_w", default=self.entry.options.get("hysteresis_w", 20.0)): vol.Coerce(float),
                vol.Required(CONF_DASHBOARD_ENABLED, default=self.entry.options.get(CONF_DASHBOARD_ENABLED, True)): bool,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)


async def _seed_from_legacy_helpers(hass, options: dict) -> bool:
    strategy = hass.states.get("input_select.house_battery_strategy")
    if strategy and strategy.state:
        mapping = {
            "Full stop": "full_stop",
            "Self-consumption": "self_consumption",
            "Timed": "timed",
            "Dynamic": "dynamic",
            "Charge": "charge",
            "Charge PV": "charge_pv",
            "Sell": "sell",
            "Zero import": "zero_import",
            "Standby / peak shave": "standby_peak_shave",
        }
        options["strategy"] = mapping.get(strategy.state, options.get("strategy", "full_stop"))

    target = hass.states.get("input_number.house_target_grid_consumption_in_w")
    if target:
        try:
            options["target_grid_power_w"] = float(target.state)
        except ValueError:
            pass

    return bool(strategy or target)
