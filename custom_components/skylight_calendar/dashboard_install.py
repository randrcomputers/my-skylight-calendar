"""Install or update the Family Calendar Lovelace dashboard."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.util.yaml import dump as yaml_dump

from .const import DEFAULT_DASHBOARD_PATH, STORAGE_DIRNAME
from .dashboard_generator import build_dashboard_config

_LOGGER = logging.getLogger(__name__)


async def write_dashboard_files(hass: HomeAssistant, data: dict[str, Any]) -> Path:
    """Always write generated YAML/JSON under config/skylight_calendar/."""
    config = build_dashboard_config(data)
    folder = Path(hass.config.path(STORAGE_DIRNAME))
    folder.mkdir(parents=True, exist_ok=True)
    yaml_path = folder / "dashboard_generated.yaml"
    json_path = folder / "dashboard_generated.json"

    def _write() -> None:
        yaml_path.write_text(yaml_dump(config), encoding="utf-8")
        json_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

    await hass.async_add_executor_job(_write)
    return yaml_path


async def install_lovelace_dashboard(hass: HomeAssistant, data: dict[str, Any]) -> str | None:
    """Create/update a storage Lovelace dashboard. Returns url_path or None."""
    url_path = data.get("dashboard_path") or DEFAULT_DASHBOARD_PATH
    title = "Family Calendar"
    config = build_dashboard_config(data)

    # Always persist files for manual paste / backup
    await write_dashboard_files(hass, data)

    try:
        lovelace = hass.data.get("lovelace")
        if lovelace is None:
            _LOGGER.warning("Lovelace not ready; wrote YAML only")
            return None

        dashboards = getattr(lovelace, "dashboards", None)
        if dashboards is None:
            _LOGGER.warning("Lovelace dashboards API unavailable; wrote YAML only")
            return None

        # Existing dashboard?
        dash = dashboards.get(url_path)
        if dash is None:
            # Try creating via config flow (HA 2024+)
            try:
                result = await hass.config_entries.flow.async_init(
                    "lovelace",
                    context={"source": "user"},
                    data={
                        "title": title,
                        "url_path": url_path,
                        "require_admin": False,
                        "show_in_sidebar": True,
                    },
                )
                # Some versions want configure step
                if result.get("type") == "form" and result.get("flow_id"):
                    result = await hass.config_entries.flow.async_configure(
                        result["flow_id"],
                        {
                            "title": title,
                            "icon": "mdi:calendar-month",
                            "url_path": url_path,
                            "require_admin": False,
                            "show_in_sidebar": True,
                        },
                    )
            except Exception as err:  # noqa: BLE001
                _LOGGER.info("lovelace dashboard flow: %s", err)

            dash = dashboards.get(url_path)

        if dash is not None and hasattr(dash, "async_save"):
            await dash.async_save(config)
            _LOGGER.info("Saved Skylight dashboard to lovelace path '%s'", url_path)
            return url_path

        _LOGGER.warning(
            "Could not auto-install Lovelace dashboard '%s'. "
            "Use /config/%s/dashboard_generated.yaml in Raw editor.",
            url_path,
            STORAGE_DIRNAME,
        )
        return None
    except Exception as err:  # noqa: BLE001
        _LOGGER.warning("Dashboard install failed: %s", err)
        return None
