# Description: Diagnostics export for Spectra LS read-only shadow parity, Phase 2 scaffold snapshots, and Phase 6 control-center settings/readiness visibility.
# Version: 2026.04.22.4
# Last updated: 2026-04-22

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, LEGACY_SURFACES


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    source_states: dict[str, str] = {}
    for key, entity_id in LEGACY_SURFACES.items():
        state = hass.states.get(entity_id)
        source_states[key] = state.state if state is not None else "missing"

    return {
        "entry_id": entry.entry_id,
        "control_center_settings": coordinator.data.get("write_controls", {}).get("control_center_settings", {}),
        "control_center_validation": coordinator.data.get("control_center_validation", {}),
        "control_center_last_attempt": coordinator.data.get("write_controls", {}).get("control_center_last_attempt", {}),
        "source_states": source_states,
        "shadow_snapshot": coordinator.data,
    }
