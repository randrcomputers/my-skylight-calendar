"""Repair flows for Skylight setup problems."""

from __future__ import annotations

from homeassistant import data_entry_flow
from homeassistant.components.repairs import ConfirmRepairFlow, RepairsFlow
from homeassistant.core import HomeAssistant

from .preflight import ISSUE_PLUS_RESOURCE, ensure_week_planner_plus_resource


async def async_create_fix_flow(
    hass: HomeAssistant,
    issue_id: str,
) -> RepairsFlow:
    if issue_id == ISSUE_PLUS_RESOURCE:
        return PlusResourceRepairFlow()
    return ConfirmRepairFlow()


class PlusResourceRepairFlow(RepairsFlow):
    """Register the Week Planner Card Plus Lovelace resource."""

    async def async_step_init(
        self, user_input: dict[str, str] | None = None
    ) -> data_entry_flow.FlowResult:
        return await self.async_step_confirm()

    async def async_step_confirm(
        self, user_input: dict[str, str] | None = None
    ) -> data_entry_flow.FlowResult:
        if user_input is not None:
            info = await ensure_week_planner_plus_resource(self.hass)
            if info.get("resource_ok"):
                return self.async_create_entry(title="", data={})
            return self.async_abort(reason="still_missing")

        return self.async_show_form(step_id="confirm")
