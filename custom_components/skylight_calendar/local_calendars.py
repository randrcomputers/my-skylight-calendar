"""Create missing Local Calendar config entries when requested."""

from __future__ import annotations

import logging
import re

from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

_LOGGER = logging.getLogger(__name__)


def _slug_calendar_entity(name: str) -> str:
    slug = re.sub(r"[^a-z0-9_]+", "_", name.lower().strip()).strip("_")
    return f"calendar.{slug}"


async def ensure_local_calendar(hass: HomeAssistant, name: str) -> str | None:
    """Create a Local Calendar named ``name`` if needed; return entity_id or None."""
    entity_id = _slug_calendar_entity(name)
    if hass.states.get(entity_id) is not None:
        return entity_id

    # Already configured under a different entity_id?
    for state in hass.states.async_all("calendar"):
        if (state.attributes.get("friendly_name") or "").lower() == name.lower():
            return state.entity_id

    try:
        result = await hass.config_entries.flow.async_init(
            "local_calendar",
            context={"source": "user"},
        )
    except Exception as err:  # noqa: BLE001
        _LOGGER.warning("Could not start local_calendar flow for %s: %s", name, err)
        return None

    flow_id = result.get("flow_id")
    if not flow_id:
        return None

    # Walk forms until create/abort (schema differs slightly by HA version).
    for _ in range(5):
        if result.get("type") == FlowResultType.CREATE_ENTRY:
            # Prefer predictable entity from name
            if hass.states.get(entity_id) is not None:
                return entity_id
            # Fall back: newest calendar matching name
            for state in hass.states.async_all("calendar"):
                if (state.attributes.get("friendly_name") or "").lower() == name.lower():
                    return state.entity_id
            return entity_id

        if result.get("type") == FlowResultType.ABORT:
            _LOGGER.info("local_calendar flow aborted for %s: %s", name, result.get("reason"))
            return entity_id if hass.states.get(entity_id) else None

        if result.get("type") != FlowResultType.FORM:
            break

        schema = result.get("data_schema")
        data: dict = {}
        # Try common field names
        for key, value in (
            ("calendar_name", name),
            ("name", name),
        ):
            try:
                if schema is not None and key in schema.schema:
                    data[key] = value
            except Exception:  # noqa: BLE001
                data[key] = value
        if not data:
            data = {"calendar_name": name}

        try:
            result = await hass.config_entries.flow.async_configure(flow_id, data)
        except Exception as err:  # noqa: BLE001
            _LOGGER.warning("local_calendar configure failed for %s: %s", name, err)
            return None

    return entity_id if hass.states.get(entity_id) else None
