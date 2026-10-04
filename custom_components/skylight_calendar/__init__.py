"""Skylight Family Calendar — visual setup wizard."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_BIRTHDAYS_CALENDAR,
    CONF_CREATE_LOCAL,
    CONF_DASHBOARD_PATH,
    CONF_FAMILY_CALENDAR,
    CONF_HOLIDAYS_CALENDAR,
    CONF_INSTALL_DASHBOARD,
    CONF_MEMBERS,
    DOMAIN,
    PLATFORMS,
)
from .dashboard_install import install_lovelace_dashboard, write_dashboard_files
from .local_calendars import ensure_local_calendar
from .preflight import ensure_week_planner_plus_resource, notify_setup_complete

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)
CONF_WELCOME_SENT = "welcome_sent"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    hass.data.setdefault(DOMAIN, {})
    from .services import async_setup_services

    await async_setup_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    from .services import async_setup_services

    await async_setup_services(hass)
    hass.data[DOMAIN][entry.entry_id] = {"data": {**entry.data, **entry.options}}

    await _async_provision(hass, entry, force_notify=False)

    await hass.config_entries.async_forward_entry_setups(
        entry, [Platform(p) for p in PLATFORMS]
    )

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, [Platform(p) for p in PLATFORMS]
    )
    if unload_ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return unload_ok


async def async_fix_setup(hass: HomeAssistant) -> dict:
    """Re-run Plus preflight + dashboard install + notification (one-click fix)."""
    entries = hass.config_entries.async_entries(DOMAIN)
    if not entries:
        return {"ok": False, "message": "Integration not configured"}
    entry = entries[0]
    await _async_provision(hass, entry, force_notify=True)
    data = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
    return {"ok": True, "message": "fix_setup complete", "data": data.get("last_plus")}


async def _async_provision(
    hass: HomeAssistant, entry: ConfigEntry, *, force_notify: bool
) -> None:
    """Create missing calendars + install/update dashboard."""
    data = {**entry.data, **entry.options}
    create_local = data.get(CONF_CREATE_LOCAL, True)
    install_dash = data.get(CONF_INSTALL_DASHBOARD, True)

    members = list(data.get(CONF_MEMBERS) or [])
    changed = False

    if create_local:
        for i, member in enumerate(members):
            cal = member.get("calendar")
            name = member.get("name") or member.get("slot") or f"Person {i+1}"
            if cal and hass.states.get(cal) is not None:
                continue
            if not member.get("create_local_if_missing", True):
                continue
            create_name = member.get("local_name") or name
            entity_id = await ensure_local_calendar(hass, create_name)
            if entity_id:
                members[i] = {**member, "calendar": entity_id}
                changed = True
                _LOGGER.info("Ensured local calendar %s (%s)", create_name, entity_id)

        for conf_key, default_name in (
            (CONF_FAMILY_CALENDAR, "Family"),
            (CONF_HOLIDAYS_CALENDAR, None),
            (CONF_BIRTHDAYS_CALENDAR, "Birthdays"),
        ):
            if conf_key == CONF_HOLIDAYS_CALENDAR:
                continue
            ent = data.get(conf_key)
            if ent and hass.states.get(ent) is not None:
                continue
            if ent is None and conf_key == CONF_FAMILY_CALENDAR:
                entity_id = await ensure_local_calendar(hass, default_name)
                if entity_id:
                    data[conf_key] = entity_id
                    changed = True

    data[CONF_MEMBERS] = members
    hass.data[DOMAIN][entry.entry_id]["data"] = data

    if changed:
        new_data = {**entry.data, CONF_MEMBERS: members}
        if data.get(CONF_FAMILY_CALENDAR) and not entry.data.get(CONF_FAMILY_CALENDAR):
            new_data[CONF_FAMILY_CALENDAR] = data[CONF_FAMILY_CALENDAR]
        hass.config_entries.async_update_entry(entry, data=new_data)

    try:
        path = await write_dashboard_files(hass, data)
        _LOGGER.info("Wrote Skylight dashboard file to %s", path)
    except Exception as err:  # noqa: BLE001
        _LOGGER.warning("Could not write dashboard file: %s", err)

    plus_info = await ensure_week_planner_plus_resource(hass)
    hass.data[DOMAIN][entry.entry_id]["last_plus"] = plus_info
    _LOGGER.info("Plus preflight: %s", plus_info.get("message"))

    url = None
    if install_dash:
        url = await install_lovelace_dashboard(hass, data)
        if url:
            _LOGGER.info("Skylight dashboard available at /%s", url)

    # One welcome notification (or when user calls fix_setup). Ongoing Plus
    # problems surface as Settings → System → Repairs + sensor.needs_attention.
    welcome_sent = bool(entry.data.get(CONF_WELCOME_SENT))
    should_notify = force_notify or not welcome_sent
    if should_notify:
        await notify_setup_complete(
            hass,
            dashboard_path=url or data.get(CONF_DASHBOARD_PATH),
            plus_info=plus_info,
        )
        if not welcome_sent:
            hass.config_entries.async_update_entry(
                entry, data={**entry.data, CONF_WELCOME_SENT: True}
            )
