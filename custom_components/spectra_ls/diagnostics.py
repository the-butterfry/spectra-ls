# Description: Diagnostics export for Spectra LS read-only shadow parity integration.
# Version: 2026.04.19.1
# Last updated: 2026-04-19

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, LEGACY_SURFACES


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    source_states = {
        key: hass.states.get(entity_id).state if hass.states.get(entity_id) is not None else "missing"
        for key, entity_id in LEGACY_SURFACES.items()
    }

    return {
        "entry_id": entry.entry_id,
        "source_states": source_states,
        "shadow_snapshot": coordinator.data,
    }
