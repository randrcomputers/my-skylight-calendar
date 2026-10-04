"""Visual setup wizard for Skylight Family Calendar."""

from __future__ import annotations

import re
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    CONF_BIRTHDAYS_CALENDAR,
    CONF_CREATE_LOCAL,
    CONF_DASHBOARD_PATH,
    CONF_FAMILY_CALENDAR,
    CONF_HOLIDAYS_CALENDAR,
    CONF_INSTALL_DASHBOARD,
    CONF_MEMBERS,
    CONF_WEATHER,
    DEFAULT_COLORS,
    DEFAULT_DASHBOARD_PATH,
    DOMAIN,
)
from .preflight import PLUS_MY_HACS, probe_week_planner_plus


def _slot(name: str, index: int) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", (name or f"m{index}").lower()).strip("_")
    return slug or f"m{index}"


class SkylightCalendarConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Multi-step wizard: size → members → shared → options."""

    VERSION = 1

    def __init__(self) -> None:
        self._member_count = 2
        self._members: list[dict[str, Any]] = []
        self._shared: dict[str, Any] = {}
        self._index = 0

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        plus = await probe_week_planner_plus(self.hass)
        if plus.get("resource_ok"):
            plus_status = f"✅ {plus.get('message')}"
        elif plus.get("file_found"):
            plus_status = (
                f"⚠️ Plus JS is on disk but not registered yet — "
                f"the wizard will try to fix that.\n{plus.get('message')}"
            )
        else:
            plus_status = (
                "⚠️ Week Planner Card Plus is **not** installed yet.\n"
                "Install it first (HACS → Frontend), or continue and fix later "
                "with `skylight_calendar.fix_setup`.\n"
                f"[Open in HACS]({PLUS_MY_HACS})"
            )

        if user_input is not None:
            self._member_count = int(user_input["member_count"])
            self._index = 0
            self._members = []
            return await self.async_step_member()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("member_count", default=2): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=6,
                            mode=selector.NumberSelectorMode.BOX,
                            step=1,
                        )
                    ),
                }
            ),
            description_placeholders={
                "plus": "Week Planner Card Plus",
                "plus_status": plus_status,
            },
        )

    async def async_step_member(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        n = self._index + 1
        if user_input is not None:
            name = (user_input.get("name") or f"Person {n}").strip()
            slot = _slot(name, n)
            # Avoid duplicate slots
            existing = {m["slot"] for m in self._members}
            base = slot
            i = 2
            while slot in existing:
                slot = f"{base}_{i}"
                i += 1

            color = str(
                user_input.get("color")
                or DEFAULT_COLORS[(n - 1) % len(DEFAULT_COLORS)]
            ).strip()
            if not color.startswith("#"):
                color = DEFAULT_COLORS[(n - 1) % len(DEFAULT_COLORS)]

            cal = user_input.get("calendar")
            create_new = bool(user_input.get("create_local_if_missing", True))
            self._members.append(
                {
                    "slot": slot,
                    "name": name,
                    "calendar": cal,
                    "person": user_input.get("person"),
                    "color": color,
                    "local_name": name,
                    "create_local_if_missing": create_new,
                }
            )
            self._index += 1
            if self._index < self._member_count:
                return await self.async_step_member()
            return await self.async_step_shared()

        default_color = DEFAULT_COLORS[self._index % len(DEFAULT_COLORS)]
        return self.async_show_form(
            step_id="member",
            data_schema=vol.Schema(
                {
                    vol.Required("name", default=f"Person {n}"): selector.TextSelector(),
                    vol.Optional("calendar"): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="calendar", multiple=False)
                    ),
                    vol.Optional("person"): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="person", multiple=False)
                    ),
                    vol.Optional("color", default=default_color): selector.TextSelector(),
                    vol.Required("create_local_if_missing", default=True): selector.BooleanSelector(),
                }
            ),
            description_placeholders={
                "n": str(n),
                "total": str(self._member_count),
            },
        )

    async def async_step_shared(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            self._shared = user_input
            return await self.async_step_options()

        return self.async_show_form(
            step_id="shared",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_FAMILY_CALENDAR): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="calendar")
                    ),
                    vol.Optional(CONF_HOLIDAYS_CALENDAR): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="calendar")
                    ),
                    vol.Optional(CONF_BIRTHDAYS_CALENDAR): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="calendar")
                    ),
                    vol.Optional(CONF_WEATHER): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="weather")
                    ),
                }
            ),
        )

    async def async_step_options(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            data = {
                CONF_MEMBERS: self._members,
                CONF_FAMILY_CALENDAR: self._shared.get(CONF_FAMILY_CALENDAR),
                CONF_HOLIDAYS_CALENDAR: self._shared.get(CONF_HOLIDAYS_CALENDAR),
                CONF_BIRTHDAYS_CALENDAR: self._shared.get(CONF_BIRTHDAYS_CALENDAR),
                CONF_WEATHER: self._shared.get(CONF_WEATHER),
                CONF_CREATE_LOCAL: bool(user_input.get(CONF_CREATE_LOCAL, True)),
                CONF_INSTALL_DASHBOARD: bool(
                    user_input.get(CONF_INSTALL_DASHBOARD, True)
                ),
                CONF_DASHBOARD_PATH: (
                    user_input.get(CONF_DASHBOARD_PATH) or DEFAULT_DASHBOARD_PATH
                ).strip()
                or DEFAULT_DASHBOARD_PATH,
            }
            return self.async_create_entry(title="Skylight Family Calendar", data=data)

        return self.async_show_form(
            step_id="options",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_CREATE_LOCAL, default=True): selector.BooleanSelector(),
                    vol.Required(
                        CONF_INSTALL_DASHBOARD, default=True
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_DASHBOARD_PATH, default=DEFAULT_DASHBOARD_PATH
                    ): selector.TextSelector(),
                }
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        return SkylightOptionsFlow(config_entry)


class SkylightOptionsFlow(config_entries.OptionsFlow):
    """Re-run dashboard install / tweak shared entities."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        cur = {**self._entry.data, **self._entry.options}
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_FAMILY_CALENDAR,
                        default=cur.get(CONF_FAMILY_CALENDAR),
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="calendar")
                    ),
                    vol.Optional(
                        CONF_HOLIDAYS_CALENDAR,
                        default=cur.get(CONF_HOLIDAYS_CALENDAR),
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="calendar")
                    ),
                    vol.Optional(
                        CONF_BIRTHDAYS_CALENDAR,
                        default=cur.get(CONF_BIRTHDAYS_CALENDAR),
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="calendar")
                    ),
                    vol.Optional(
                        CONF_WEATHER, default=cur.get(CONF_WEATHER)
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="weather")
                    ),
                    vol.Required(
                        CONF_CREATE_LOCAL,
                        default=cur.get(CONF_CREATE_LOCAL, True),
                    ): selector.BooleanSelector(),
                    vol.Required(
                        CONF_INSTALL_DASHBOARD,
                        default=cur.get(CONF_INSTALL_DASHBOARD, True),
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_DASHBOARD_PATH,
                        default=cur.get(CONF_DASHBOARD_PATH, DEFAULT_DASHBOARD_PATH),
                    ): selector.TextSelector(),
                }
            ),
        )
