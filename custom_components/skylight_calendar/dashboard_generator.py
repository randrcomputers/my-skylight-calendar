"""Build a Lovelace dashboard config from wizard selections."""

from __future__ import annotations

from typing import Any


def _filter_var(slot: str) -> str:
    return f"FILTER_{slot.upper()}"


def build_dashboard_config(data: dict[str, Any]) -> dict[str, Any]:
    """Return a storage-mode Lovelace config dict."""
    members: list[dict[str, Any]] = data.get("members") or []
    family = data.get("family_calendar")
    holidays = data.get("holidays_calendar")
    birthdays = data.get("birthdays_calendar")
    weather = data.get("weather") or "weather.home"
    path = data.get("dashboard_path") or "skylight-calendar"

    # config-template-card variables
    variables: dict[str, Any] = {
        "VIEW": "states['select.skylight_view']?.state",
        "STARTDAY": (
            "(() => {\n"
            "  const v = states['select.skylight_view']?.state;\n"
            "  if (v === 'Today') return 'today';\n"
            "  if (v === 'Tomorrow') return 'tomorrow';\n"
            "  return 'monday';\n"
            "})()"
        ),
        "DAYS": (
            "(() => {\n"
            "  const v = states['select.skylight_view']?.state;\n"
            "  if (v === 'Today') return 1;\n"
            "  if (v === 'Tomorrow') return 2;\n"
            "  if (v === 'Week') return 7;\n"
            "  if (v === 'Biweek') return 14;\n"
            "  return 'month';\n"
            "})()"
        ),
    }

    calendars_yaml: list[dict[str, Any]] = []
    person_buttons: list[dict[str, Any]] = []

    for idx, member in enumerate(members):
        slot = member.get("slot") or f"m{idx+1}"
        entity = member.get("calendar")
        name = member.get("name") or slot
        color = member.get("color") or "#6D9DC5"
        person = member.get("person")
        switch_id = f"switch.skylight_filter_{slot}"
        var = _filter_var(slot)
        variables[var] = (
            f"states['{switch_id}']?.state === 'on' ? '.*' : '^$'"
        )
        if entity:
            calendars_yaml.append(
                {
                    "entity": entity,
                    "name": name,
                    "color": color,
                    "filter": f"${{ {var} }}",
                }
            )
        btn: dict[str, Any] = {
            "type": "custom:bubble-card",
            "card_type": "button",
            "button_type": "switch",
            "entity": switch_id,
            "name": name,
            "show_state": False,
            "styles": (
                f".bubble-button-background {{ background: {color} !important; }}\n"
                f".bubble-icon {{ color: white !important; }}"
            ),
        }
        if person:
            btn["icon"] = "mdi:account"
            # Show person picture when available via card-mod / entity picture is limited;
            # keep icon and name for reliability.
        person_buttons.append(btn)

    for key, entity, name, color, slot in (
        ("family_calendar", family, "Family", "#E07A5F", "family"),
        ("birthdays_calendar", birthdays, "Birthdays", "#81B29A", "birthdays"),
        ("holidays_calendar", holidays, "Holidays", "#F2CC8F", "holidays"),
    ):
        if not entity:
            continue
        switch_id = f"switch.skylight_filter_{slot}"
        var = _filter_var(slot)
        variables[var] = f"states['{switch_id}']?.state === 'on' ? '.*' : '^$'"
        calendars_yaml.append(
            {
                "entity": entity,
                "name": name,
                "color": color,
                "filter": f"${{ {var} }}",
            }
        )
        person_buttons.append(
            {
                "type": "custom:bubble-card",
                "card_type": "button",
                "button_type": "switch",
                "entity": switch_id,
                "name": name,
                "show_state": False,
                "styles": (
                    f".bubble-button-background {{ background: {color} !important; }}\n"
                    f".bubble-icon {{ color: white !important; }}"
                ),
            }
        )

    watch_entities = ["select.skylight_view"]
    for i, m in enumerate(members):
        watch_entities.append(
            f"switch.skylight_filter_{m.get('slot') or f'm{i+1}'}"
        )
    if family:
        watch_entities.append("switch.skylight_filter_family")
    if birthdays:
        watch_entities.append("switch.skylight_filter_birthdays")
    if holidays:
        watch_entities.append("switch.skylight_filter_holidays")

    planner_card = {
        "type": "custom:config-template-card",
        "entities": watch_entities,
        "variables": variables,
        "card": {
            "type": "custom:week-planner-card-plus",
            "calendars": calendars_yaml,
            "days": "${ DAYS }",
            "startingDay": "${ STARTDAY }",
            "showNavigation": True,
            "showWeekDayText": False,
            "startingDayOffset": 0,
            "hideWeekend": False,
            "noCardBackground": False,
            "compact": False,
            "weather": {
                "showCondition": True,
                "showTemperature": True,
                "showLowTemperature": True,
                "useTwiceDaily": False,
                "entity": weather,
            },
            "showLocation": True,
            "hidePastEvents": False,
            "combineSimilarEvents": True,
            "showLegend": False,
            "legendToggle": False,
            "clickEmptyDayToAdd": True,
            "card_mod": {
                "style": (
                    "ha-card {\n"
                    "  background: rgba(255,255,255,0.65) !important;\n"
                    "  border-radius: 24px !important;\n"
                    "  box-shadow: none !important;\n"
                    "  min-height: 60vh;\n"
                    "}\n"
                    ".event { border-radius: 10px !important; }\n"
                    ".today .number {\n"
                    "  border-radius: 5px;\n"
                    "  background-color: orange !important;\n"
                    "  padding-left: 4px;\n"
                    "  padding-right: 4px;\n"
                    "}\n"
                )
            },
        },
    }

    view = {
        "type": "sections",
        "title": "Family Calendar",
        "path": "family-calendar",
        "max_columns": 4,
        "sections": [
            {
                "type": "grid",
                "cards": [
                    {
                        "type": "custom:better-moment-card",
                        "parentStyle": "line-height:normal;",
                        "moment": [
                            {
                                "parentStyle": "font-size:1.2em;text-align:center;",
                                "templateRaw": "{{moment format=cccc}}",
                            },
                            {
                                "parentStyle": "font-size:1.6em;text-align:center;",
                                "templateRaw": "{{moment format=LLLL dd, yyyy}}",
                            },
                            {
                                "parentStyle": "font-size:3.2em;text-align:center;font-weight:400;",
                                "templateRaw": "{{moment format=HH:mm}}",
                            },
                        ],
                        "card_mod": {
                            "style": (
                                "ha-card { background: transparent !important; "
                                "box-shadow: none !important; border: none !important; }"
                            )
                        },
                    },
                    {
                        "type": "weather-forecast",
                        "entity": weather,
                        "show_current": True,
                        "show_forecast": True,
                        "forecast_type": "daily",
                    },
                ],
            },
            {
                "type": "grid",
                "cards": [
                    {
                        "type": "entities",
                        "entities": [
                            {
                                "entity": "select.skylight_view",
                                "name": "View",
                            }
                        ],
                    },
                    *person_buttons,
                ],
            },
            {
                "type": "grid",
                "cards": [planner_card],
            },
            {
                "type": "markdown",
                "content": (
                    f"**Skylight Family Calendar** · dashboard `{path}`\n\n"
                    "Tap an empty day or an event to **Add / Edit** "
                    "(Week Planner Card Plus).\n"
                    "Use the person toggles to show/hide calendars."
                ),
            },
        ],
    }

    return {"views": [view]}
