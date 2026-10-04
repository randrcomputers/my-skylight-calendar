"""Foolproof install helpers: probe Plus, register resource, repair, notify."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.components.persistent_notification import (
    async_create as async_create_notification,
)
from homeassistant.helpers import issue_registry as ir

from .const import DOMAIN, STORAGE_DIRNAME

_LOGGER = logging.getLogger(__name__)

ISSUE_MISSING_PLUS = "missing_week_planner_plus"
ISSUE_PLUS_RESOURCE = "plus_resource_not_registered"
ISSUE_MISSING_LOOK_CARDS = "missing_skylight_look_cards"

PLUS_REPO = "https://github.com/randrcomputers/week-planner-card-plus"
PLUS_MY_HACS = (
    "https://my.home-assistant.io/redirect/hacs_repository/"
    "?owner=randrcomputers&repository=week-planner-card-plus&category=plugin"
)

# Extra HACS frontend cards for the original Skylight chrome (pills, clock, filters).
LOOK_CARDS: tuple[dict[str, Any], ...] = (
    {
        "id": "bubble-card",
        "name": "Bubble Card",
        "paths": (
            "www/community/bubble-card/bubble-card.js",
            "www/community/Bubble-Card/bubble-card.js",
        ),
        "url_hint": "bubble-card",
    },
    {
        "id": "config-template-card",
        "name": "Config Template Card",
        "paths": (
            "www/community/config-template-card/config-template-card.js",
        ),
        "url_hint": "config-template-card",
    },
    {
        "id": "card-mod",
        "name": "card-mod",
        "paths": (
            "www/community/lovelace-card-mod/card-mod.js",
            "www/community/card-mod/card-mod.js",
        ),
        "url_hint": "card-mod",
    },
    {
        "id": "better-moment-card",
        "name": "Better Moment Card",
        "paths": (
            "www/community/better-moment-card/better-moment-card.js",
        ),
        "url_hint": "better-moment-card",
    },
    {
        "id": "weather-card",
        "name": "Weather Card",
        "paths": (
            "www/community/weather-card/weather-card.js",
            "www/community/lovelace-weather-card/weather-card.js",
        ),
        "url_hint": "weather-card",
    },
)

# Common HACS / manual paths for the Plus card module
_PLUS_CANDIDATES = (
    "www/community/week-planner-card-plus/week-planner-card-plus.js",
    "www/week-planner-card-plus/week-planner-card-plus.js",
)


def _plus_url_for_path(rel: str) -> str:
    # HA serves /config/www as /local/
    if rel.startswith("www/"):
        return "/local/" + rel[len("www/") :]
    return "/local/" + rel


async def probe_week_planner_plus(hass: HomeAssistant) -> dict[str, Any]:
    """Read-only check: JS on disk + Lovelace resource registration."""
    result: dict[str, Any] = {
        "file_found": False,
        "url": None,
        "resource_ok": False,
        "resource_url": None,
        "message": "",
        "my_hacs": PLUS_MY_HACS,
        "repo": PLUS_REPO,
    }

    found_rel: str | None = None
    for rel in _PLUS_CANDIDATES:
        path = Path(hass.config.path(rel))
        if await hass.async_add_executor_job(path.is_file):
            found_rel = rel
            break

    hacs_url = "/hacsfiles/week-planner-card-plus/week-planner-card-plus.js"
    if found_rel:
        result["file_found"] = True
        url = _plus_url_for_path(found_rel)
        if found_rel.startswith("www/community/"):
            url = hacs_url
        result["url"] = url

    # Scan Lovelace resources even if file missing (HACS URL-only installs)
    try:
        lovelace = hass.data.get("lovelace")
        resources = getattr(lovelace, "resources", None) if lovelace else None
        items: list[Any] = []
        if resources is not None:
            if hasattr(resources, "async_items"):
                items = list(resources.async_items())
            elif hasattr(resources, "data"):
                items = list(getattr(resources, "data", {}).values())

        for item in items:
            if isinstance(item, dict):
                item_url = str(item.get("url") or "")
            else:
                item_url = str(getattr(item, "url", "") or "")
            if "week-planner-card-plus" in item_url:
                result["resource_ok"] = True
                result["resource_url"] = item_url
                break
    except Exception as err:  # noqa: BLE001
        _LOGGER.debug("Could not scan Lovelace resources: %s", err)

    if result["resource_ok"] and result["file_found"]:
        result["message"] = f"Week Planner Card Plus ready ({result['resource_url']})."
    elif result["resource_ok"]:
        result["message"] = (
            f"Plus is in Lovelace resources ({result['resource_url']}). Hard-refresh (Ctrl+F5)."
        )
    elif result["file_found"]:
        result["message"] = (
            f"Plus JS found at {result['url']} but not in Lovelace resources yet."
        )
    else:
        result["message"] = (
            "Week Planner Card Plus is not installed. "
            "HACS → Frontend → Week Planner Card Plus, then restart HA."
        )

    return result


async def _lovelace_resource_urls(hass: HomeAssistant) -> list[str]:
    urls: list[str] = []
    try:
        lovelace = hass.data.get("lovelace")
        resources = getattr(lovelace, "resources", None) if lovelace else None
        items: list[Any] = []
        if resources is not None:
            if hasattr(resources, "async_items"):
                items = list(resources.async_items())
            elif hasattr(resources, "data"):
                items = list(getattr(resources, "data", {}).values())
        for item in items:
            if isinstance(item, dict):
                urls.append(str(item.get("url") or ""))
            else:
                urls.append(str(getattr(item, "url", "") or ""))
    except Exception as err:  # noqa: BLE001
        _LOGGER.debug("Could not scan Lovelace resources: %s", err)
    return urls


async def probe_look_cards(hass: HomeAssistant) -> dict[str, Any]:
    """Which original-look frontend cards are present on disk or in resources."""
    urls = await _lovelace_resource_urls(hass)
    joined = " ".join(urls).lower()
    missing: list[str] = []
    found: list[str] = []
    for card in LOOK_CARDS:
        on_disk = False
        for rel in card["paths"]:
            path = Path(hass.config.path(rel))
            if await hass.async_add_executor_job(path.is_file):
                on_disk = True
                break
        in_res = card["url_hint"] in joined
        if on_disk or in_res:
            found.append(card["name"])
        else:
            missing.append(card["name"])
    return {"found": found, "missing": missing}


async def ensure_week_planner_plus_resource(hass: HomeAssistant) -> dict[str, Any]:
    """Probe Plus and register the Lovelace module resource when possible."""
    result = await probe_week_planner_plus(hass)

    async def _finish() -> dict[str, Any]:
        await sync_plus_issues(hass, result)
        look = await probe_look_cards(hass)
        result["look_found"] = look["found"]
        result["look_missing"] = look["missing"]
        await sync_look_issues(hass, look)
        return result

    if result["resource_ok"] or not result["file_found"]:
        return await _finish()

    url = result["url"]
    try:
        lovelace = hass.data.get("lovelace")
        resources = getattr(lovelace, "resources", None) if lovelace else None
        if resources is None:
            result["message"] = (
                f"Plus file found ({url}) but Lovelace resources API unavailable. "
                "Add it manually: Settings → Dashboards → ⋮ → Resources → Add Resource "
                f"→ URL `{url}` → type JavaScript Module."
            )
            return await _finish()

        if hasattr(resources, "async_create_item"):
            await resources.async_create_item({"res_type": "module", "url": url})
            result["resource_ok"] = True
            result["resource_url"] = url
            result["message"] = f"Registered Lovelace resource: {url}"
            _LOGGER.info("Registered week-planner-card-plus resource %s", url)
        else:
            result["message"] = (
                f"Plus file found at {url}. Add manually as a module resource "
                "if the card is missing on the dashboard."
            )
    except Exception as err:  # noqa: BLE001
        _LOGGER.warning("Could not register Plus resource: %s", err)
        result["message"] = f"Could not auto-register resource: {err}"

    return await _finish()


async def sync_plus_issues(hass: HomeAssistant, plus_info: dict[str, Any]) -> None:
    """Create/clear Settings → System → Repairs entries for Plus problems."""
    # Clear both, then create the matching one
    ir.async_delete_issue(hass, DOMAIN, ISSUE_MISSING_PLUS)
    ir.async_delete_issue(hass, DOMAIN, ISSUE_PLUS_RESOURCE)

    if plus_info.get("resource_ok"):
        return

    if not plus_info.get("file_found"):
        ir.async_create_issue(
            hass,
            DOMAIN,
            ISSUE_MISSING_PLUS,
            is_fixable=False,
            severity=ir.IssueSeverity.ERROR,
            translation_key="missing_week_planner_plus",
            learn_more_url=PLUS_REPO,
        )
        return

    ir.async_create_issue(
        hass,
        DOMAIN,
        ISSUE_PLUS_RESOURCE,
        is_fixable=True,
        severity=ir.IssueSeverity.WARNING,
        translation_key="plus_resource_not_registered",
        learn_more_url=PLUS_REPO,
    )


async def sync_look_issues(hass: HomeAssistant, look: dict[str, Any]) -> None:
    """Repair if original Skylight chrome cards are missing."""
    ir.async_delete_issue(hass, DOMAIN, ISSUE_MISSING_LOOK_CARDS)
    missing = look.get("missing") or []
    if not missing:
        return
    ir.async_create_issue(
        hass,
        DOMAIN,
        ISSUE_MISSING_LOOK_CARDS,
        is_fixable=False,
        severity=ir.IssueSeverity.WARNING,
        translation_key="missing_skylight_look_cards",
        translation_placeholders={"cards": ", ".join(missing)},
        learn_more_url="https://github.com/randrcomputers/my-skylight-calendar",
    )


async def notify_setup_complete(
    hass: HomeAssistant,
    *,
    dashboard_path: str | None,
    plus_info: dict[str, Any],
) -> None:
    """Persistent notification with a short foolproof checklist."""
    dash_line = (
        f"Open sidebar **Family Calendar** (`/{dashboard_path}`)"
        if dashboard_path
        else (
            f"Paste `/config/{STORAGE_DIRNAME}/dashboard_generated.yaml` "
            "into a new dashboard (Raw editor)"
        )
    )
    plus_ok = bool(plus_info.get("resource_ok"))
    plus_line = (
        f"✅ {plus_info.get('message')}"
        if plus_ok
        else f"⚠️ {plus_info.get('message')}\n  One-click HACS: {PLUS_MY_HACS}"
    )
    look_missing = plus_info.get("look_missing") or []
    look_line = (
        "✅ Original-look cards found (Bubble, Config Template, card-mod, Better Moment, Weather)"
        if not look_missing
        else "⚠️ Install via HACS → Frontend: " + ", ".join(look_missing)
    )

    message = (
        "Skylight Family Calendar setup finished.\n\n"
        "**Do these 3 things:**\n"
        "1. Hard-refresh the browser (**Ctrl+F5**)\n"
        f"2. {dash_line}\n"
        "3. Check `sensor.skylight_setup_status` — should be **ready**\n\n"
        f"**Week Planner Card Plus:**\n{plus_line}\n\n"
        f"**Original Skylight look:**\n{look_line}\n\n"
        "Tap a person pill to show/hide. Tap an empty day or event to Add/Edit.\n\n"
        f"One-click fix: Developer Tools → Services → `{DOMAIN}.fix_setup`"
    )
    async_create_notification(
        hass,
        message,
        title="Skylight calendar — next steps",
        notification_id=f"{DOMAIN}_setup_complete",
    )
