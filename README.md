# Home Battery Control (HACS Integration)

Home Battery Control is now shipped as a Home Assistant custom integration that can be installed with HACS and includes a bundled dashboard panel.

> Legacy Node-RED flows remain in this repository as behavior reference and rollback path.

## What ships in this release

- HACS metadata and installable integration: `custom_components/home_battery_control`
- Native strategy/runtime engine (no Node-RED runtime dependency)
- Generic battery mapping + Marstek preset helper
- Config flow + options flow + services + diagnostics/repairs
- Bundled frontend panel assets served by the integration
- Optional fallback YAML dashboard for migration users
- Parity fixtures and unit tests for strategy/PID/dynamic primitives

## Quick start (HACS)

1. Add this repository as a custom repository in HACS (Integration type).
2. Install **Home Battery Control**.
3. Restart Home Assistant.
4. Add integration from **Settings → Devices & Services**.
5. Select your grid/P1 power sensor (W, positive = import).
6. Map batteries (or choose Marstek preset).
7. Keep control disabled, validate limits, then enable Full control only after safety checks.

## Safety

- First functional test: **800 W max charge/discharge**.
- Confirm Full stop works before enabling dynamic/timed automation.
- Ensure command mode and command power entities are mapped correctly.

## Migration from legacy helpers

During config flow, the integration can seed options from old helpers where available:

- `input_select.house_battery_strategy`
- `input_number.house_target_grid_consumption_in_w`

Legacy helper IDs are not required for ongoing operation.

## Dashboard

- Preferred UX: bundled integration panel.
- Optional fallback: `home assistant/dashboard.yaml` (manual import/update only).
- Integration will not overwrite an existing Lovelace storage dashboard.

## Documentation

- [Getting started](docs/01-getting-started.md)
- [Battery mapping / Modbus](docs/02-modbus-setup.md)
- [Strategies](docs/03-strategies.md)
- [Self-consumption & PID](docs/04-setup-self-consumption.md)
- [Dynamic strategy](docs/05-setup-dynamic.md)
- [Advanced features](docs/06-advanced-features.md)
- [Troubleshooting](docs/07-troubleshooting.md)
- [How to update](docs/08-how-to-update.md)

## Legacy reference

- Node-RED behavior reference: `node-red/`
- Legacy helper/templates: `home assistant/packages/`

