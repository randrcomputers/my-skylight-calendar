"""Visibility filter switches (on = show calendar, off = hide)."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import CONF_BIRTHDAYS_CALENDAR, CONF_FAMILY_CALENDAR, CONF_HOLIDAYS_CALENDAR, CONF_MEMBERS, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = {**entry.data, **entry.options}
    entities: list[SkylightFilterSwitch] = []

    for member in data.get(CONF_MEMBERS) or []:
        slot = member.get("slot")
        if not slot:
            continue
        entities.append(
            SkylightFilterSwitch(
                entry.entry_id,
                slot=slot,
                name=f"{member.get('name') or slot} calendar",
                icon="mdi:calendar-account",
            )
        )

    for key, slot, label, icon in (
        (CONF_FAMILY_CALENDAR, "family", "Family calendar", "mdi:calendar-multiple"),
        (CONF_BIRTHDAYS_CALENDAR, "birthdays", "Birthdays calendar", "mdi:cake-variant"),
        (CONF_HOLIDAYS_CALENDAR, "holidays", "Holidays calendar", "mdi:beach"),
    ):
        if data.get(key):
            entities.append(
                SkylightFilterSwitch(
                    entry.entry_id,
                    slot=slot,
                    name=label,
                    icon=icon,
                )
            )

    async_add_entities(entities)


class SkylightFilterSwitch(SwitchEntity, RestoreEntity):
    """Show/hide a calendar in the planner (maps to regex .* / ^$)."""

    _attr_has_entity_name = False
    _attr_should_poll = False

    def __init__(self, entry_id: str, *, slot: str, name: str, icon: str) -> None:
        self._entry_id = entry_id
        self._slot = slot
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}_filter_{slot}"
        self._attr_icon = icon
        self._attr_is_on = True
        self.entity_id = f"switch.skylight_filter_{slot}"

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last = await self.async_get_last_state()
        if last is not None:
            self._attr_is_on = last.state == "on"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": "Skylight Family Calendar",
            "manufacturer": "R&R / community fork",
            "model": "Wizard",
        }

    async def async_turn_on(self, **kwargs) -> None:
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        self._attr_is_on = False
        self.async_write_ha_state()
