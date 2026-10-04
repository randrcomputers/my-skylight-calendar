"""Services for Skylight Family Calendar."""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant, ServiceCall

from .const import DOMAIN
from .dashboard_install import install_lovelace_dashboard, write_dashboard_files
from .local_calendars import ensure_local_calendar
from .preflight import ensure_week_planner_plus_resource, notify_setup_complete

_LOGGER = logging.getLogger(__name__)


async def async_setup_services(hass: HomeAssistant) -> None:
    if hass.data.get(f"{DOMAIN}_services"):
        return
    hass.data[f"{DOMAIN}_services"] = True

    async def _entry_data():
        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            return None, None
        entry = entries[0]
        data = {**entry.data, **entry.options}
        return entry, data

    async def install_dashboard(_call: ServiceCall) -> None:
        entry, data = await _entry_data()
        if not data:
            _LOGGER.error("No skylight_calendar config entry")
            return
        await ensure_week_planner_plus_resource(hass)
        await write_dashboard_files(hass, data)
        url = await install_lovelace_dashboard(hass, data)
        _LOGGER.info("Dashboard install finished path=%s", url)

    async def create_missing(_call: ServiceCall) -> None:
        entry, data = await _entry_data()
        if not entry or not data:
            return
        members = list(data.get("members") or [])
        changed = False
        for i, m in enumerate(members):
            cal = m.get("calendar")
            if cal and hass.states.get(cal):
                continue
            name = m.get("local_name") or m.get("name") or m.get("slot")
            entity_id = await ensure_local_calendar(hass, name)
            if entity_id:
                members[i] = {**m, "calendar": entity_id}
                changed = True
        if changed:
            hass.config_entries.async_update_entry(
                entry, data={**entry.data, "members": members}
            )
            await hass.config_entries.async_reload(entry.entry_id)

    async def fix_setup(_call: ServiceCall) -> None:
        """One-click: register Plus, reinstall dashboard, show checklist."""
        from . import async_fix_setup

        result = await async_fix_setup(hass)
        _LOGGER.info("fix_setup: %s", result)

    hass.services.async_register(DOMAIN, "install_dashboard", install_dashboard)
    hass.services.async_register(
        DOMAIN, "create_missing_calendars", create_missing
    )
    hass.services.async_register(DOMAIN, "fix_setup", fix_setup)
