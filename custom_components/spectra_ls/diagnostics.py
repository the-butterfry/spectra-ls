# Description: Diagnostics export for Spectra LS read-only shadow parity and Phase 2 scaffold snapshots.
# Version: 2026.04.19.2
# Last updated: 2026-04-19

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
        "source_states": source_states,
        "shadow_snapshot": coordinator.data,
    }
