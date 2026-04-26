# Description: Config and options flow for Spectra LS shadow parity integration with simplified single-step remap settings UX.
# Version: 2026.04.22.8
# Last updated: 2026-04-22

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import (
    CONTROL_CENTER_ACTIONS,
    CONTROL_CENTER_DEFAULTS,
    CONTROL_CENTER_MAPPING_PRESETS,
    CONTROL_CENTER_PRESET_VALUES,
    CONTROL_CENTER_PRESS_ACTIONS,
    DOMAIN,
    ENTRY_TITLE,
    OPT_BUTTON_1_SCENE,
    OPT_BUTTON_2_SCENE,
    OPT_BUTTON_3_SCENE,
    OPT_BUTTON_4_SCENE,
    OPT_ENCODER_LONG_PRESS_ACTION,
    OPT_ENCODER_PRESS_ACTION,
    OPT_ENCODER_TURN_ACTION,
    OPT_MAPPING_PRESET,
    OPT_READ_ONLY_MODE,
    SINGLETON_UNIQUE_ID,
    normalize_control_center_settings,
)


class SpectraLsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle config flow for Spectra LS."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Return options flow for control-center settings."""
        return SpectraLsOptionsFlow(config_entry)

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


class SpectraLsOptionsFlow(config_entries.OptionsFlow):
    """Handle Spectra LS control-center options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    @staticmethod
    def _preset_selector_options() -> list[selector.SelectOptionDict]:
        """Return labeled preset options for guided quick-remap UX."""
        return [
            selector.SelectOptionDict(value="media_default", label="Media default (volume / play / mute)"),
            selector.SelectOptionDict(value="scene_focus", label="Scene focus (quick scene trigger)"),
            selector.SelectOptionDict(value="target_navigation", label="Target navigation (cycle targets)"),
            selector.SelectOptionDict(value="custom", label="Custom mapping (manual controls)"),
        ]

    @staticmethod
    def _turn_action_selector_options() -> list[selector.SelectOptionDict]:
        """Return labeled encoder-turn action options."""
        labels = {
            "volume": "Volume",
            "brightness": "Brightness",
            "target_cycle": "Target cycle",
            "source_cycle": "Source cycle",
        }
        return [selector.SelectOptionDict(value=val, label=labels.get(val, val)) for val in CONTROL_CENTER_ACTIONS]

    @staticmethod
    def _press_action_selector_options() -> list[selector.SelectOptionDict]:
        """Return labeled encoder press/long-press action options."""
        labels = {
            "play_pause": "Play / pause",
            "mute_toggle": "Mute toggle",
            "scene_quick_trigger": "Scene quick trigger",
            "no_op": "Do nothing",
        }
        return [selector.SelectOptionDict(value=val, label=labels.get(val, val)) for val in CONTROL_CENTER_PRESS_ACTIONS]

    def _suggest_default_scene_for_quick_trigger(self, current_scene_value: str) -> str:
        """Suggest a first scene binding for button 1 when still unconfigured."""
        normalized = str(current_scene_value or "").strip().lower()
        if normalized not in {"", "none", "scene.none"}:
            return current_scene_value

        scene_entities = sorted(state.entity_id for state in self.hass.states.async_all("scene"))
        return scene_entities[0] if scene_entities else "scene.none"

    def _apply_selected_preset(self, user_input: dict[str, Any]) -> dict[str, Any]:
        """Apply selected mapping preset to the submitted input payload."""
        selected_preset = str(user_input.get(OPT_MAPPING_PRESET, "custom") or "custom").strip().lower()
        if selected_preset not in CONTROL_CENTER_MAPPING_PRESETS:
            selected_preset = "custom"

        if selected_preset == "custom":
            return dict(user_input)

        patched = dict(user_input)
        patched[OPT_MAPPING_PRESET] = selected_preset
        preset_values = CONTROL_CENTER_PRESET_VALUES.get(selected_preset, {})
        if isinstance(preset_values, dict):
            patched.update(preset_values)
        return patched

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Single-step settings form for remap and scene bindings."""
        if user_input is not None:
            merged = normalize_control_center_settings({**self._config_entry.options, **user_input})
            normalized = normalize_control_center_settings(self._apply_selected_preset(merged))
            return self.async_create_entry(title="", data=normalized)

        existing = normalize_control_center_settings(self._config_entry.options)
        defaults = dict(CONTROL_CENTER_DEFAULTS)
        defaults.update(existing)

        scene_selector = selector.EntitySelector(
            selector.EntitySelectorConfig(
                domain=["scene"],
                multiple=False,
            )
        )

        defaults[OPT_BUTTON_1_SCENE] = self._suggest_default_scene_for_quick_trigger(defaults[OPT_BUTTON_1_SCENE])

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(OPT_READ_ONLY_MODE, default=defaults[OPT_READ_ONLY_MODE]): selector.BooleanSelector(),
                    vol.Optional(
                        OPT_MAPPING_PRESET,
                        default=defaults[OPT_MAPPING_PRESET],
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=self._preset_selector_options(),
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Optional(
                        OPT_ENCODER_TURN_ACTION,
                        default=defaults[OPT_ENCODER_TURN_ACTION],
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=self._turn_action_selector_options(),
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Optional(
                        OPT_ENCODER_PRESS_ACTION,
                        default=defaults[OPT_ENCODER_PRESS_ACTION],
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=self._press_action_selector_options(),
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Optional(
                        OPT_ENCODER_LONG_PRESS_ACTION,
                        default=defaults[OPT_ENCODER_LONG_PRESS_ACTION],
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=self._press_action_selector_options(),
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Optional(OPT_BUTTON_1_SCENE, default=defaults[OPT_BUTTON_1_SCENE]): scene_selector,
                    vol.Optional(OPT_BUTTON_2_SCENE, default=defaults[OPT_BUTTON_2_SCENE]): scene_selector,
                    vol.Optional(OPT_BUTTON_3_SCENE, default=defaults[OPT_BUTTON_3_SCENE]): scene_selector,
                    vol.Optional(OPT_BUTTON_4_SCENE, default=defaults[OPT_BUTTON_4_SCENE]): scene_selector,
                }
            ),
        )
