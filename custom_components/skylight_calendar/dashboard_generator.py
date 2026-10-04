"""Build a foolproof Lovelace dashboard — only Week Planner Card Plus required."""

from __future__ import annotations

from typing import Any


def build_dashboard_config(data: dict[str, Any]) -> dict[str, Any]:
    """Return a storage-mode Lovelace config dict.

    Intentionally avoids Bubble Card, Config Template Card, Better Moment,
    and card-mod so a fresh install has fewer ways to break.
    """
    members: list[dict[str, Any]] = data.get("members") or []
    family = data.get("family_calendar")
    holidays = data.get("holidays_calendar")
    birthdays = data.get("birthdays_calendar")
    weather = data.get("weather")
    path = data.get("dashboard_path") or "skylight-calendar"

    calendars: list[dict[str, Any]] = []

    for idx, member in enumerate(members):
        entity = member.get("calendar")
        name = member.get("name") or member.get("slot") or f"m{idx + 1}"
        color = member.get("color") or "#6D9DC5"
        if entity:
            calendars.append({"entity": entity, "name": name, "color": color})

    for entity, name, color in (
        (family, "Family", "#E07A5F"),
        (birthdays, "Birthdays", "#81B29A"),
        (holidays, "Holidays", "#F2CC8F"),
    ):
        if not entity:
            continue
        calendars.append({"entity": entity, "name": name, "color": color})

    planner: dict[str, Any] = {
        "type": "custom:week-planner-card-plus",
        "calendars": calendars,
        # Fixed week grid — most people stuck on "vertical 7 days" need this.
        "days": 7,
        "startingDay": "monday",
        "showNavigation": True,
        "showWeekDayText": True,
        "startingDayOffset": 0,
        "hideWeekend": False,
        "noCardBackground": False,
        "compact": False,
        "showLocation": True,
        "hidePastEvents": False,
        "combineSimilarEvents": True,
        # Built-in show/hide — no config-template-card needed
        "showLegend": True,
        "legendToggle": True,
        "clickEmptyDayToAdd": True,
    }
    if weather:
        planner["weather"] = {
            "showCondition": True,
            "showTemperature": True,
            "showLowTemperature": True,
            "useTwiceDaily": False,
            "entity": weather,
        }

    header_cards: list[dict[str, Any]] = [
        {
            "type": "markdown",
            "content": (
                "## Family Calendar\n"
                "{{ now().strftime('%A, %B %d') }}\n\n"
                "# {{ now().strftime('%I:%M %p') }}\n\n"
                "Tap a **legend** name to show/hide that calendar. "
                "Tap an empty day or event to **Add / Edit**."
            ),
        }
    ]
    if weather:
        header_cards.append(
            {
                "type": "weather-forecast",
                "entity": weather,
                "show_current": True,
                "show_forecast": True,
                "forecast_type": "daily",
            }
        )

    view = {
        "title": "Family Calendar",
        "path": "family-calendar",
        "type": "sections",
        "max_columns": 3,
        "sections": [
            {"type": "grid", "cards": header_cards},
            {"type": "grid", "cards": [planner]},
            {
                "type": "markdown",
                "content": (
                    f"**Path:** `/{path}` · "
                    "Status: "
                    "{% if is_state('sensor.skylight_setup_status','ready') %}"
                    "✅ `sensor.skylight_setup_status` ready"
                    "{% else %}"
                    "⚠️ `sensor.skylight_setup_status` — open entity for `missing`"
                    "{% endif %}\n\n"
                    "Want Month view? Edit the planner card → set **days** to `month`."
                ),
            },
        ],
    }

    return {"views": [view]}
