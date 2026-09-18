"""Entity helpers."""

from __future__ import annotations

from homeassistant.helpers.entity import Entity

from .const import DOMAIN


class HomeBatteryEntity(Entity):
    _attr_has_entity_name = True

    def __init__(self, entry, coordinator, key: str, name: str) -> None:
        self.entry = entry
        self.coordinator = coordinator
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{key}"

    @property
    def available(self) -> bool:
        return True

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.entry.entry_id)},
            "name": self.entry.title,
            "manufacturer": "Home Battery Control",
        }
