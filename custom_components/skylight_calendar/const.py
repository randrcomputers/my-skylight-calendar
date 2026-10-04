"""Constants for Skylight Family Calendar wizard."""

from __future__ import annotations

DOMAIN = "skylight_calendar"
PLATFORMS = ["switch", "select", "sensor"]

CONF_MEMBERS = "members"
CONF_FAMILY_CALENDAR = "family_calendar"
CONF_HOLIDAYS_CALENDAR = "holidays_calendar"
CONF_BIRTHDAYS_CALENDAR = "birthdays_calendar"
CONF_WEATHER = "weather"
CONF_CREATE_LOCAL = "create_local_calendars"
CONF_INSTALL_DASHBOARD = "install_dashboard"
CONF_DASHBOARD_PATH = "dashboard_path"
CONF_SHOW_LEGACY_POPUP = "show_legacy_add_popup"

DEFAULT_DASHBOARD_PATH = "skylight-calendar"
DEFAULT_COLORS = [
    "#E07A5F",
    "#3D405B",
    "#81B29A",
    "#F2CC8F",
    "#6D9DC5",
    "#C77DFF",
]

# View select options (entity: select.skylight_calendar_view)
VIEW_OPTIONS = ["Today", "Tomorrow", "Week", "Biweek", "Month"]

STORAGE_DIRNAME = "skylight_calendar"
