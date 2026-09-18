"""Dashboard panel registration."""

from __future__ import annotations

from homeassistant.components import frontend

from .const import DOMAIN


async def async_register_dashboard(hass, entry) -> None:
    panel_path = f"/{DOMAIN}/panel.js"
    frontend.async_register_built_in_panel(
        hass,
        component_name="custom",
        sidebar_title="Battery Control",
        sidebar_icon="mdi:battery-heart-variant",
        frontend_url_path=f"{DOMAIN}-{entry.entry_id}",
        config={"module_url": panel_path},
        require_admin=False,
    )
