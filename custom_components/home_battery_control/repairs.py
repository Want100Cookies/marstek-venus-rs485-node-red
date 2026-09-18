"""Repairs placeholders for runtime issues."""

from __future__ import annotations

from homeassistant.helpers.issue_registry import IssueSeverity, async_create_issue, async_delete_issue

from .const import DOMAIN


def update_runtime_repairs(hass, entry, *, missing_grid=False, invalid_mapping=False, missing_provider=False, unsafe_state=False):
    _set_issue(hass, entry.entry_id, "missing_grid_sensor", missing_grid, "Grid power sensor is missing")
    _set_issue(hass, entry.entry_id, "invalid_battery_mapping", invalid_mapping, "Battery mapping is invalid")
    _set_issue(hass, entry.entry_id, "dynamic_provider_missing", missing_provider, "Dynamic provider has no data")
    _set_issue(hass, entry.entry_id, "unsafe_full_control", unsafe_state, "Full control enabled without checklist confirmation")


def _set_issue(hass, entry_id: str, issue_id: str, enabled: bool, translation_key: str) -> None:
    if enabled:
        async_create_issue(
            hass,
            DOMAIN,
            f"{entry_id}_{issue_id}",
            is_fixable=False,
            severity=IssueSeverity.WARNING,
            translation_key=translation_key,
        )
    else:
        async_delete_issue(hass, DOMAIN, f"{entry_id}_{issue_id}")
