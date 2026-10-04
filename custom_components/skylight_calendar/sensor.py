"""Setup status sensor — what’s missing for the Skylight dashboard."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import (
    CONF_BIRTHDAYS_CALENDAR,
    CONF_FAMILY_CALENDAR,
    CONF_HOLIDAYS_CALENDAR,
    CONF_MEMBERS,
    CONF_WEATHER,
    DOMAIN,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([SkylightSetupSensor(hass, entry)], True)


class SkylightSetupSensor(SensorEntity):
    _attr_has_entity_name = False
    _attr_icon = "mdi:clipboard-check"
    _attr_name = "Skylight setup status"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_setup_status"
        self.entity_id = "sensor.skylight_setup_status"
        self._attr_native_value = "unknown"
        self._attr_extra_state_attributes = {}

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "Skylight Family Calendar",
            "manufacturer": "R&R / community fork",
            "model": "Wizard",
        }

    async def async_added_to_hass(self) -> None:
        await self.async_update()

        @callback
        def _changed(_event) -> None:
            self.async_schedule_update_ha_state(True)

        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                self._watched_entities(),
                _changed,
            )
        )

    def _watched_entities(self) -> list[str]:
        data = {**self._entry.data, **self._entry.options}
        ents = ["select.skylight_view"]
        for m in data.get(CONF_MEMBERS) or []:
            if m.get("calendar"):
                ents.append(m["calendar"])
            slot = m.get("slot")
            if slot:
                ents.append(f"switch.skylight_filter_{slot}")
        for key in (CONF_FAMILY_CALENDAR, CONF_HOLIDAYS_CALENDAR, CONF_BIRTHDAYS_CALENDAR, CONF_WEATHER):
            if data.get(key):
                ents.append(data[key])
        return ents

    async def async_update(self) -> None:
        data = {**self._entry.data, **self._entry.options}
        missing: list[str] = []
        ok: list[str] = []

        for m in data.get(CONF_MEMBERS) or []:
            cal = m.get("calendar")
            label = m.get("name") or m.get("slot")
            if not cal:
                missing.append(f"member:{label}:no_calendar")
            elif self.hass.states.get(cal) is None:
                missing.append(cal)
            else:
                ok.append(cal)

        for key, label in (
            (CONF_FAMILY_CALENDAR, "family"),
            (CONF_HOLIDAYS_CALENDAR, "holidays"),
            (CONF_BIRTHDAYS_CALENDAR, "birthdays"),
            (CONF_WEATHER, "weather"),
        ):
            ent = data.get(key)
            if not ent:
                continue
            if self.hass.states.get(ent) is None:
                missing.append(ent)
            else:
                ok.append(ent)

        if self.hass.states.get("select.skylight_view") is None:
            missing.append("select.skylight_view")
        else:
            ok.append("select.skylight_view")

        # Frontend hint (cannot fully detect cards; expose as advice)
        advice = [
            "Install HACS frontend: week-planner-card-plus, bubble-card, config-template-card, card-mod, better-moment-card",
            "Hard-refresh browser after HACS installs (Ctrl+F5)",
        ]

        self._attr_native_value = "ready" if not missing else "needs_attention"
        self._attr_extra_state_attributes = {
            "ok": ok,
            "missing": missing,
            "advice": advice,
            "dashboard_file": f"/config/skylight_calendar/dashboard_generated.yaml",
        }
