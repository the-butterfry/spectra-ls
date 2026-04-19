# Description: Config flow for Spectra LS shadow parity integration.
# Version: 2026.04.19.1
# Last updated: 2026-04-19

from __future__ import annotations

from homeassistant import config_entries

from .const import DOMAIN, ENTRY_TITLE, SINGLETON_UNIQUE_ID


class SpectraLsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle config flow for Spectra LS."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Create a single config entry for shadow parity surfaces."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        await self.async_set_unique_id(SINGLETON_UNIQUE_ID)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=ENTRY_TITLE,
            data={},
        )
