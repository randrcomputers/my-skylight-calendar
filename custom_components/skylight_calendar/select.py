"""View mode select for the Family Calendar dashboard."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN, VIEW_OPTIONS


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([SkylightViewSelect(entry.entry_id)])


class SkylightViewSelect(SelectEntity, RestoreEntity):
    _attr_has_entity_name = False
    _attr_should_poll = False
    _attr_icon = "mdi:calendar-range"
    _attr_options = VIEW_OPTIONS

    def __init__(self, entry_id: str) -> None:
        self._entry_id = entry_id
        self._attr_name = "Skylight view"
        self._attr_unique_id = f"{entry_id}_view"
        self._attr_current_option = "Week"
        self.entity_id = "select.skylight_view"

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last = await self.async_get_last_state()
        if last and last.state in VIEW_OPTIONS:
            self._attr_current_option = last.state

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": "Skylight Family Calendar",
            "manufacturer": "R&R / community fork",
            "model": "Wizard",
        }

    async def async_select_option(self, option: str) -> None:
        if option not in VIEW_OPTIONS:
            return
        self._attr_current_option = option
        self.async_write_ha_state()
