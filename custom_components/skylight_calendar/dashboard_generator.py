"""Build the original Skylight-look Lovelace dashboard from wizard answers."""

from __future__ import annotations

from typing import Any

PLANNER_CARD_MOD = """
:host { overflow: hidden; }
ha-card {
  background: rgba(255, 255, 255, 0.6) !important;
  border-radius: 24px !important;
  box-shadow: none !important;
  height: clamp(480px, 70vh, 900px) !important;
  max-height: clamp(480px, 70vh, 900px) !important;
}
.container {
  display: grid !important;
  grid-template-columns: repeat(7, minmax(0, 1fr)) !important;
  grid-auto-flow: row dense !important;
  gap: 0 !important;
}
.container .navigation,
.container .header { grid-column: 1 / -1 !important; }
.day.header {
  display: block !important;
  grid-column: auto !important;
  margin: 0 !important;
  padding: 0.2em !important;
  text-align: center !important;
  box-sizing: border-box !important;
}
.day {
  border: solid 1px whitesmoke !important;
  padding: 0.2% !important;
  width: auto !important;
  min-width: 0 !important;
  margin: 0 !important;
  box-sizing: border-box !important;
  align-self: stretch !important;
  justify-self: stretch !important;
}
.event.past { opacity: .2 !important; background-color: gray !important; }
.time { color: #333333 !important; font-size: 0.8em !important; }
.event {
  color: #333333 !important;
  line-height: 16px !important;
  background-color: var(--border-color) !important;
  border-radius: 10px !important;
  max-height: 80px !important;
  overflow: hidden !important;
  font-size: 1.1em !important;
}
.today .number {
  border-radius: 5px !important;
  background-color: orange !important;
  padding-left: 4px !important;
  padding-right: 4px !important;
}
.day .date .text { font-size: 1em !important; font-weight: bold !important; }
.day .date .number { font-weight: bold !important; font-size: 3em !important; }
"""

TRANSPARENT_CARD_MOD = """
ha-card {
  background: transparent !important;
  box-shadow: none !important;
  border: none !important;
}
"""


def _filter_js(switch_id: str) -> str:
    return "${ " + f"is_state('{switch_id}', 'on') ? '.*' : '^$'" + " }"


def _bubble_person(
    *,
    name: str,
    color: str,
    switch_id: str,
    person: str | None,
    icon: str | None = None,
) -> dict[str, Any]:
    """Colored pill that toggles the person's calendar on/off."""
    styles = (
        ".bubble-button-background {\n"
        "  opacity: 1 !important;\n"
        f"  background-color: ${{hass.states['{switch_id}']?.state === 'on'"
        f" ? '{color}' : 'lightgrey'}} !important;\n"
        "}\n"
    )
    card: dict[str, Any] = {
        "type": "custom:bubble-card",
        "card_type": "button",
        "show_icon": True,
        "show_name": True,
        "name": name,
        "tap_action": {
            "action": "perform-action",
            "perform_action": "switch.toggle",
            "target": {"entity_id": switch_id},
        },
        "styles": styles,
        "entity": person or switch_id,
    }
    if person:
        card["button_type"] = "state"
    else:
        card["button_type"] = "name"
        card["icon"] = icon or "mdi:account"
    return card


def build_dashboard_config(data: dict[str, Any]) -> dict[str, Any]:
    """Return a storage-mode Lovelace config matching the original Skylight look.

    Needs HACS frontend: Week Planner Card Plus, Bubble Card, Config Template
    Card, card-mod, Better Moment Card. Weather Card is used when a weather
    entity is set. Browser Mod is not required (tap a day to add/edit).
    """
    members: list[dict[str, Any]] = data.get("members") or []
    family = data.get("family_calendar")
    holidays = data.get("holidays_calendar")
    birthdays = data.get("birthdays_calendar")
    weather = data.get("weather")
    add_target = family or next(
        (m.get("calendar") for m in members if m.get("calendar")), None
    )

    watch: list[str] = ["select.skylight_view"]
    calendars: list[dict[str, Any]] = []
    pills: list[dict[str, Any]] = []

    for member in members:
        entity = member.get("calendar")
        slot = member.get("slot")
        name = member.get("name") or slot or "Person"
        color = member.get("color") or "#6D9DC5"
        if not entity or not slot:
            continue
        switch_id = f"switch.skylight_filter_{slot}"
        watch.append(switch_id)
        calendars.append(
            {
                "entity": entity,
                "name": name,
                "color": color,
                "filter": _filter_js(switch_id),
            }
        )
        pills.append(
            _bubble_person(
                name=name,
                color=color,
                switch_id=switch_id,
                person=member.get("person"),
            )
        )

    for entity, slot, name, color, icon in (
        (family, "family", "Family", "#4A90E2", "mdi:human-male-female-child"),
        (birthdays, "birthdays", "Birthdays", "#33a02c", "mdi:cake-variant"),
        (holidays, "holidays", "Holidays", "#ff7f00", "mdi:bag-personal"),
    ):
        if not entity:
            continue
        switch_id = f"switch.skylight_filter_{slot}"
        watch.append(switch_id)
        calendars.append(
            {
                "entity": entity,
                "name": name,
                "color": color,
                "filter": _filter_js(switch_id),
            }
        )
        pills.append(
            _bubble_person(
                name=name,
                color=color,
                switch_id=switch_id,
                person=None,
                icon=icon,
            )
        )

    planner: dict[str, Any] = {
        "type": "custom:week-planner-card-plus",
        "calendars": calendars,
        "days": "${ DAYS }",
        "startingDay": "${ STARTDAY }",
        "showNavigation": True,
        "showWeekDayText": False,
        "startingDayOffset": 0,
        "hideWeekend": False,
        "noCardBackground": False,
        "compact": False,
        "showLocation": True,
        "hidePastEvents": False,
        "combineSimilarEvents": True,
        "showLegend": False,
        "legendToggle": False,
        "clickEmptyDayToAdd": True,
        "card_mod": {"style": PLANNER_CARD_MOD},
    }
    if weather:
        planner["weather"] = {
            "showCondition": True,
            "showTemperature": True,
            "showLowTemperature": True,
            "useTwiceDaily": False,
            "entity": weather,
        }

    wrapped_planner = {
        "type": "custom:config-template-card",
        "entities": watch,
        "variables": {
            "VIEW": "states['select.skylight_view']?.state",
            "STARTDAY": (
                "(() => {\n"
                "  const calendarView = states['select.skylight_view']?.state;\n"
                "  if (calendarView === 'Today') return 'today';\n"
                "  if (calendarView === 'Tomorrow') return 'tomorrow';\n"
                "  return 'monday';\n"
                "})()"
            ),
            "DAYS": (
                "(() => {\n"
                "  const calendarView = states['select.skylight_view']?.state;\n"
                "  if (calendarView === 'Today') return 1;\n"
                "  if (calendarView === 'Tomorrow') return 2;\n"
                "  if (calendarView === 'Week') return 7;\n"
                "  if (calendarView === 'Biweek') return 14;\n"
                "  return 'month';\n"
                "})()"
            ),
        },
        "card": planner,
    }

    header_cards: list[dict[str, Any]] = [
        {
            "type": "custom:better-moment-card",
            "parentStyle": "line-height:normal;",
            "moment": [
                {
                    "parentStyle": "font-size:1em; text-align:center; margin-top:5px;",
                    "templateRaw": "{{moment format=cccc}}",
                },
                {
                    "parentStyle": "font-size:1.5em; text-align:center; margin-top:5px;",
                    "templateRaw": "{{moment format=LLLL dd, yyyy}}",
                },
                {
                    "parentStyle": "font-size:4em; text-align:center; font-weight:400;",
                    "templateRaw": "{{moment format=HH:mm}}",
                },
            ],
            "grid_options": {"columns": 20},
            "card_mod": {"style": TRANSPARENT_CARD_MOD},
        }
    ]
    if weather:
        header_cards.append(
            {
                "type": "custom:weather-card",
                "entity": weather,
                "current": True,
                "details": True,
                "forecast": False,
                "grid_options": {"columns": 20, "rows": 3},
            }
        )
        header_cards.append(
            {
                "type": "weather-forecast",
                "show_current": False,
                "show_forecast": True,
                "entity": weather,
                "forecast_type": "daily",
                "name": "Weather Forecast",
                "grid_options": {"columns": 20, "rows": 3},
                "card_mod": {"style": TRANSPARENT_CARD_MOD},
            }
        )

    add_event: dict[str, Any] = {
        "type": "custom:bubble-card",
        "card_type": "button",
        "button_type": "name",
        "card_layout": "large",
        "name": "Add Event",
        "icon": "mdi:calendar-plus",
        "styles": (
            "* { font-size: 1.05em !important; }\n"
            "ha-card { --bubble-main-background-color: #393745 !important; width: 300px; }\n"
            ".bubble-icon { --mdc-icon-size: 30px !important; color: snow !important; opacity: 1; }\n"
            ".bubble-icon-container { background: #393745 !important; display: flex; }\n"
            ".bubble-name { color: snow !important; opacity: 1; }\n"
        ),
        "grid_options": {"columns": 10, "rows": 1},
    }
    if add_target:
        add_event["tap_action"] = {"action": "more-info", "entity": add_target}
    else:
        add_event["tap_action"] = {"action": "none"}

    controls: list[dict[str, Any]] = [
        {
            "type": "markdown",
            "content": '<font color="Black" size="6">Family Calendar</font>',
            "grid_options": {"columns": 18, "rows": "auto"},
            "card_mod": {"style": TRANSPARENT_CARD_MOD},
        },
        {
            "type": "horizontal-stack",
            "cards": pills,
            "grid_options": {"columns": 45, "rows": "auto"},
        },
        add_event,
        {
            "type": "custom:bubble-card",
            "card_type": "select",
            "entity": "select.skylight_view",
            "show_name": True,
            "show_state": True,
            "name": "Select View",
            "show_last_changed": False,
            "show_attribute": False,
        },
    ]

    view = {
        "title": "Family Calendar",
        "path": "family-calendar",
        "type": "sections",
        "max_columns": 10,
        "theme": "Skylight",
        "sections": [
            {"type": "grid", "cards": header_cards, "column_span": 10},
            {"type": "grid", "cards": controls, "column_span": 10},
            {"type": "grid", "cards": [wrapped_planner], "column_span": 10},
        ],
    }
    return {"views": [view]}
