# Description: Constants for Spectra LS custom integration shadow parity, Phase 3 guarded routing write-path controls, Phase 4 diagnostics scaffolding (F4-S01/F4-S03), Phase 5 metadata trial contract service, and Phase 6/8 control-center settings and fast-remap preset contracts including startup MA-readiness gating constants and selection-ownership migration services.
# Version: 2026.05.04.3
# Last updated: 2026-05-04
# PARITY DIRECTIVE (until full cutover): behavior/contract edits here require same-slice two-track parity review
# and version-metadata review in runtime (`packages/` + `esphome/`) and component (`custom_components/spectra_ls/`) tracks.

from __future__ import annotations

from typing import Any, Mapping

from homeassistant.const import Platform

DOMAIN = "spectra_ls"

SERVICE_REBUILD_REGISTRY = "rebuild_registry"
SERVICE_VALIDATE_CONTRACTS = "validate_contracts"
SERVICE_DUMP_ROUTE_TRACE = "dump_route_trace"
SERVICE_SET_WRITE_AUTHORITY = "set_write_authority"
SERVICE_ROUTE_WRITE_TRIAL = "route_write_trial"
SERVICE_METADATA_WRITE_TRIAL = "metadata_write_trial"
SERVICE_RUN_P3_S01_SEQUENCE = "run_p3_s01_sequence"
SERVICE_RUN_P3_S02_SEQUENCE = "run_p3_s02_sequence"
SERVICE_VALIDATE_METADATA_PREP = "validate_metadata_prep"
SERVICE_VALIDATE_METADATA_POLICY = "validate_metadata_policy"
SERVICE_GET_AUTHORITY_CONTRACT = "get_authority_contract"
SERVICE_GET_HOST_CUTOVER_GATE = "get_host_cutover_gate"
SERVICE_RUN_P5_S02_SEQUENCE = "run_p5_s02_sequence"
SERVICE_RUN_P3_S03_SEQUENCE = "run_p3_s03_sequence"
SERVICE_VALIDATE_CAPABILITY_PROFILE = "validate_capability_profile"
SERVICE_RUN_F4_S01_SEQUENCE = "run_f4_s01_sequence"
SERVICE_VALIDATE_ACTION_CATALOG = "validate_action_catalog"
SERVICE_RUN_F4_S02_SEQUENCE = "run_f4_s02_sequence"
SERVICE_VALIDATE_CROSSFADE_BALANCE = "validate_crossfade_balance"
SERVICE_RUN_F4_S03_SEQUENCE = "run_f4_s03_sequence"
SERVICE_SET_CONTROL_CENTER_SETTINGS = "set_control_center_settings"
SERVICE_EXECUTE_CONTROL_CENTER_INPUT = "execute_control_center_input"
SERVICE_VALIDATE_SCHEDULER = "validate_scheduler"
SERVICE_RUN_SCHEDULER_CHOICE = "run_scheduler_choice"
SERVICE_APPLY_SCHEDULER_CHOICE = "apply_scheduler_choice"
SERVICE_BUILD_TARGET_OPTIONS_SCAFFOLD = "build_target_options_scaffold"
SERVICE_RUN_AUTO_SELECT_SCAFFOLD = "run_auto_select_scaffold"
SERVICE_RUN_METADATA_RESOLVER_SCAFFOLD = "run_metadata_resolver_scaffold"
SERVICE_RUN_METADATA_TRIAL_BRIDGE_SCAFFOLD = "run_metadata_trial_bridge_scaffold"
SERVICE_CYCLE_ACTIVE_TARGET = "cycle_active_target"
SERVICE_RESTORE_LAST_VALID_TARGET = "restore_last_valid_target"
SERVICE_TRACK_LAST_VALID_TARGET = "track_last_valid_target"
SERVICE_SET_ACTIVE_TARGET = "set_active_target"
SERVICE_SET_METADATA_OVERRIDE = "set_metadata_override"

PLATFORMS: tuple[Platform, ...] = (
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
)

ENTRY_TITLE = "Spectra LS"
SINGLETON_UNIQUE_ID = "spectra_ls_shadow"

WRITE_AUTH_LEGACY = "legacy"
WRITE_AUTH_COMPONENT = "component"
WRITE_AUTH_ALLOWED: tuple[str, ...] = (
    WRITE_AUTH_LEGACY,
    WRITE_AUTH_COMPONENT,
)
WRITE_DEBOUNCE_SECONDS = 2.0

METADATA_AUTH_OWNER_LEGACY = "legacy_contract_surfaces"
METADATA_AUTH_OWNER_COMPONENT = "component_contract_surfaces"
METADATA_CUTOVER_BLOCK_NOT_CUT_OVER = "metadata_authority_not_cut_over"
METADATA_CUTOVER_BLOCK_LEGACY_MODE = "metadata_authority_legacy_mode"
METADATA_CUTOVER_BLOCK_PREP_NOT_READY = "metadata_prep_not_ready"
METADATA_CUTOVER_BLOCK_RESOLVER_CANDIDATE_MISSING = "resolver_candidate_missing"

# Fabric/MA authority contract tokens (must stay 1:1 with architecture docs).
FABRIC_AUTH_MODE_PRIMARY = "ma_primary"
FABRIC_AUTH_MODE_DEGRADED_FALLBACK = "ma_degraded_fallback"
FABRIC_AUTH_REASON_DEGRADED_ACTIVE = "ma_degraded_fallback_active"
FABRIC_AUTH_REASON_PAYLOAD_STALE = "ma_payload_stale"
FABRIC_AUTH_REASON_PAYLOAD_SHAPE_INVALID = "ma_payload_shape_invalid"
FABRIC_AUTH_REASON_API_UNREACHABLE = "ma_api_unreachable"

LEGACY_ACTIVE_TARGET = "sensor.ma_active_target"
LEGACY_ACTIVE_CONTROL_PATH = "sensor.ma_active_control_path"
LEGACY_ACTIVE_CONTROL_CAPABLE = "binary_sensor.ma_active_control_capable"
LEGACY_CONTROL_AMBIGUOUS = "binary_sensor.ma_control_ambiguous"
LEGACY_NO_CONTROL_CAPABLE_HOSTS = "binary_sensor.ma_no_control_capable_hosts"
LEGACY_ACTIVE_TARGET_HELPER = "input_select.ma_active_target"
LEGACY_ACTIVE_META_ENTITY = "sensor.ma_active_meta_entity"
LEGACY_META_RESOLVER = "sensor.ma_meta_resolver"
LEGACY_META_DETECTED_ENTITY = "sensor.ma_meta_detected_entity"
LEGACY_META_OVERRIDE_ACTIVE = "input_boolean.ma_meta_override_active"
LEGACY_META_OVERRIDE_ENTITY = "input_text.ma_meta_override_entity"
LEGACY_META_STALE = "binary_sensor.ma_meta_stale"
LEGACY_META_PAUSED_HIDE_S = "input_number.ma_meta_paused_hide_s"
LEGACY_META_STALE_S = "input_number.ma_meta_stale_s"
LEGACY_META_CONFIDENCE_MIN = "input_number.ma_meta_confidence_min"

# --- Auto-metadata policy defaults ---
# These are the canonical fallback values used when the HA helper is unavailable.
# All tuneable thresholds should read from their HA helper first and fall back to these.
META_POLICY_DEFAULTS: dict[str, Any] = {
    "mode": "auto",              # Auto-only metadata UX posture
    "meta_stale_s": 45.0,        # Short freshness window for play/pause signal freshness
    "paused_hide_s": 600.0,      # Extended idle clear: hide metadata after paused this long
    "confidence_min": 4.0,       # Minimum confidence score for meta candidate acceptance
    "clear_when_no_active_playback": True,  # Fail-closed: clear display when no fresh signal
    "control_host_coupling": True,          # Metadata confidence remains coupled to host/route readiness
}

# Suppression reason tokens — used in both runtime (jinja comment context) and component diagnostics.
# Keep these in sync with the reason strings emitted by _build_now_playing_signal.
META_SUPPRESSION_PLAYING = "playing"                      # Entity is actively playing — no suppression
META_SUPPRESSION_PLAYING_STALE = "playing_stale_hidden"   # Entity reports playing but progress clock is stale
META_SUPPRESSION_PAUSED_FRESH = "paused_fresh"            # Paused but within paused_hide_s — still shown
META_SUPPRESSION_PAUSED_STALE = "paused_stale_hidden"     # Paused beyond paused_hide_s — hidden
META_SUPPRESSION_LONG_IDLE = "long_idle_stale_hidden"     # Entity is idle/off/stopped — hidden
META_SUPPRESSION_NO_FRESH_SIGNAL = "no_fresh_play_signal" # No usable play/pause signal at all — hidden
META_SUPPRESSION_ENTITY_MISSING = "entity_missing"        # Entity not in HA state machine — hidden
LEGACY_OVERRIDE_ACTIVE = "input_boolean.ma_override_active"
LEGACY_LAST_VALID_TARGET = "input_text.ma_last_valid_target"
LEGACY_NOW_PLAYING_ENTITY = "sensor.now_playing_entity"
LEGACY_NOW_PLAYING_STATE = "sensor.now_playing_state"
LEGACY_NOW_PLAYING_TITLE = "sensor.now_playing_title"
LEGACY_NOW_PLAYING_POSITION = "sensor.now_playing_position"
LEGACY_NOW_PLAYING_DURATION = "sensor.now_playing_duration"
LEGACY_NOW_PLAYING_MEDIA_CLASS = "sensor.now_playing_media_class"
LEGACY_NOW_PLAYING_PREVIEW_KEY = "sensor.now_playing_preview_key"
LEGACY_NOW_PLAYING_DISPLAY_ALLOWED = "binary_sensor.now_playing_display_allowed"
LEGACY_ACTIVE_DURATION = "sensor.ma_active_duration"
LEGACY_META_CANDIDATES = "sensor.ma_meta_candidates"
LEGACY_MA_PLAYERS = "sensor.ma_players"
LEGACY_CONTROL_HOSTS = "sensor.ma_control_hosts"
LEGACY_CONTROL_HOST = "sensor.ma_control_host"
LEGACY_CONTROL_TARGETS = "sensor.ma_control_targets"
LEGACY_SERVER_PROFILE = "input_select.ma_server_profile"
LEGACY_SERVER_PROFILE_EFFECTIVE = "sensor.ma_server_profile_effective"
LEGACY_ROOMS_JSON = "sensor.spectra_ls_rooms_json"
LEGACY_ROOMS_RAW = "sensor.spectra_ls_rooms_raw"

# Legacy scaffold governance split (LC-05):
# - compat_required: still consumed by active component/runtime compatibility paths
# - retire_candidate: intentionally retained legacy scaffolds with explicit retirement gates
LEGACY_RETIRE_GATE_LC_05 = "LC-05"
LEGACY_RETIRE_GATE_LC_06 = "LC-06"

LEGACY_COMPAT_REQUIRED_CONSTANTS: dict[str, str] = {
    "LEGACY_ACTIVE_TARGET": LEGACY_ACTIVE_TARGET,
    "LEGACY_ACTIVE_CONTROL_PATH": LEGACY_ACTIVE_CONTROL_PATH,
    "LEGACY_ACTIVE_CONTROL_CAPABLE": LEGACY_ACTIVE_CONTROL_CAPABLE,
    "LEGACY_ACTIVE_TARGET_HELPER": LEGACY_ACTIVE_TARGET_HELPER,
    "LEGACY_ACTIVE_META_ENTITY": LEGACY_ACTIVE_META_ENTITY,
    "LEGACY_META_RESOLVER": LEGACY_META_RESOLVER,
    "LEGACY_META_DETECTED_ENTITY": LEGACY_META_DETECTED_ENTITY,
    "LEGACY_META_OVERRIDE_ACTIVE": LEGACY_META_OVERRIDE_ACTIVE,
    "LEGACY_META_OVERRIDE_ENTITY": LEGACY_META_OVERRIDE_ENTITY,
    "LEGACY_META_STALE": LEGACY_META_STALE,
    "LEGACY_META_PAUSED_HIDE_S": LEGACY_META_PAUSED_HIDE_S,
    "LEGACY_META_STALE_S": LEGACY_META_STALE_S,
    "LEGACY_META_CONFIDENCE_MIN": LEGACY_META_CONFIDENCE_MIN,
    "LEGACY_META_CANDIDATES": LEGACY_META_CANDIDATES,
    "LEGACY_MA_PLAYERS": LEGACY_MA_PLAYERS,
    "LEGACY_CONTROL_HOST": LEGACY_CONTROL_HOST,
    "LEGACY_CONTROL_HOSTS": LEGACY_CONTROL_HOSTS,
    "LEGACY_CONTROL_TARGETS": LEGACY_CONTROL_TARGETS,
    "LEGACY_ROOMS_JSON": LEGACY_ROOMS_JSON,
    "LEGACY_ROOMS_RAW": LEGACY_ROOMS_RAW,
}

LEGACY_RETIRE_CANDIDATE_CONSTANTS: dict[str, str] = {
    "LEGACY_CONTROL_AMBIGUOUS": LEGACY_CONTROL_AMBIGUOUS,
    "LEGACY_NO_CONTROL_CAPABLE_HOSTS": LEGACY_NO_CONTROL_CAPABLE_HOSTS,
    "LEGACY_OVERRIDE_ACTIVE": LEGACY_OVERRIDE_ACTIVE,
    "LEGACY_LAST_VALID_TARGET": LEGACY_LAST_VALID_TARGET,
    "LEGACY_NOW_PLAYING_ENTITY": LEGACY_NOW_PLAYING_ENTITY,
    "LEGACY_NOW_PLAYING_STATE": LEGACY_NOW_PLAYING_STATE,
    "LEGACY_NOW_PLAYING_TITLE": LEGACY_NOW_PLAYING_TITLE,
    "LEGACY_NOW_PLAYING_POSITION": LEGACY_NOW_PLAYING_POSITION,
    "LEGACY_NOW_PLAYING_DURATION": LEGACY_NOW_PLAYING_DURATION,
    "LEGACY_NOW_PLAYING_MEDIA_CLASS": LEGACY_NOW_PLAYING_MEDIA_CLASS,
    "LEGACY_NOW_PLAYING_PREVIEW_KEY": LEGACY_NOW_PLAYING_PREVIEW_KEY,
    "LEGACY_NOW_PLAYING_DISPLAY_ALLOWED": LEGACY_NOW_PLAYING_DISPLAY_ALLOWED,
    "LEGACY_ACTIVE_DURATION": LEGACY_ACTIVE_DURATION,
    "LEGACY_SERVER_PROFILE": LEGACY_SERVER_PROFILE,
    "LEGACY_SERVER_PROFILE_EFFECTIVE": LEGACY_SERVER_PROFILE_EFFECTIVE,
}

LEGACY_RETIREMENT_GATES: dict[str, str] = {
    **{key: LEGACY_RETIRE_GATE_LC_06 for key in LEGACY_RETIRE_CANDIDATE_CONSTANTS},
    **{key: LEGACY_RETIRE_GATE_LC_05 for key in LEGACY_COMPAT_REQUIRED_CONSTANTS},
}

LEGACY_SURFACES: dict[str, str] = {
    "active_target": LEGACY_ACTIVE_TARGET,
    "active_control_path": LEGACY_ACTIVE_CONTROL_PATH,
    "active_control_capable": LEGACY_ACTIVE_CONTROL_CAPABLE,
    "control_hosts": LEGACY_CONTROL_HOSTS,
}

OPT_READ_ONLY_MODE = "read_only_mode"
OPT_ENCODER_TURN_ACTION = "encoder_turn_action"
OPT_ENCODER_PRESS_ACTION = "encoder_press_action"
OPT_ENCODER_LONG_PRESS_ACTION = "encoder_long_press_action"
OPT_BUTTON_1_SCENE = "button_1_scene"
OPT_BUTTON_2_SCENE = "button_2_scene"
OPT_BUTTON_3_SCENE = "button_3_scene"
OPT_BUTTON_4_SCENE = "button_4_scene"
OPT_MAPPING_PRESET = "mapping_preset"
OPT_DEFAULT_WRITE_AUTHORITY_MODE = "default_write_authority_mode"

CONTROL_CENTER_ACTIONS: tuple[str, ...] = (
    "volume",
    "brightness",
    "target_cycle",
    "source_cycle",
)

CONTROL_CENTER_PRESS_ACTIONS: tuple[str, ...] = (
    "play_pause",
    "mute_toggle",
    "scene_quick_trigger",
    "no_op",
)

CONTROL_CENTER_MAPPING_PRESETS: tuple[str, ...] = (
    "media_default",
    "scene_focus",
    "target_navigation",
    "custom",
)

CONTROL_CENTER_PRESET_VALUES: dict[str, dict[str, Any]] = {
    "media_default": {
        OPT_ENCODER_TURN_ACTION: "volume",
        OPT_ENCODER_PRESS_ACTION: "play_pause",
        OPT_ENCODER_LONG_PRESS_ACTION: "mute_toggle",
        OPT_BUTTON_1_SCENE: "scene.none",
        OPT_BUTTON_2_SCENE: "scene.none",
        OPT_BUTTON_3_SCENE: "scene.none",
        OPT_BUTTON_4_SCENE: "scene.none",
    },
    "scene_focus": {
        OPT_ENCODER_TURN_ACTION: "volume",
        OPT_ENCODER_PRESS_ACTION: "scene_quick_trigger",
        OPT_ENCODER_LONG_PRESS_ACTION: "no_op",
        OPT_BUTTON_1_SCENE: "scene.none",
        OPT_BUTTON_2_SCENE: "scene.none",
        OPT_BUTTON_3_SCENE: "scene.none",
        OPT_BUTTON_4_SCENE: "scene.none",
    },
    "target_navigation": {
        OPT_ENCODER_TURN_ACTION: "target_cycle",
        OPT_ENCODER_PRESS_ACTION: "no_op",
        OPT_ENCODER_LONG_PRESS_ACTION: "no_op",
        OPT_BUTTON_1_SCENE: "scene.none",
        OPT_BUTTON_2_SCENE: "scene.none",
        OPT_BUTTON_3_SCENE: "scene.none",
        OPT_BUTTON_4_SCENE: "scene.none",
    },
}

CONTROL_CENTER_DEFAULTS: dict[str, Any] = {
    OPT_READ_ONLY_MODE: True,
    OPT_MAPPING_PRESET: "custom",
    OPT_ENCODER_TURN_ACTION: "volume",
    OPT_ENCODER_PRESS_ACTION: "scene_quick_trigger",
    OPT_ENCODER_LONG_PRESS_ACTION: "no_op",
    OPT_BUTTON_1_SCENE: "scene.none",
    OPT_BUTTON_2_SCENE: "scene.none",
    OPT_BUTTON_3_SCENE: "scene.none",
    OPT_BUTTON_4_SCENE: "scene.none",
}

CONTROL_CENTER_INPUT_EVENTS: tuple[str, ...] = (
    "encoder_turn",
    "encoder_press",
    "encoder_long_press",
    "button_1",
    "button_2",
    "button_3",
    "button_4",
)


def normalize_control_center_settings(raw_options: Mapping[str, Any] | None) -> dict[str, Any]:
    """Return normalized P6 control-center settings with safe defaults."""
    options = dict(CONTROL_CENTER_DEFAULTS)
    if raw_options is None:
        return options

    mapping_preset = str(raw_options.get(OPT_MAPPING_PRESET, options[OPT_MAPPING_PRESET]) or "").strip().lower()
    if mapping_preset not in CONTROL_CENTER_MAPPING_PRESETS:
        mapping_preset = str(options[OPT_MAPPING_PRESET])
    options[OPT_MAPPING_PRESET] = mapping_preset

    preset_values = CONTROL_CENTER_PRESET_VALUES.get(mapping_preset)
    if isinstance(preset_values, dict):
        options.update(preset_values)

    raw_read_only = raw_options.get(OPT_READ_ONLY_MODE)
    if isinstance(raw_read_only, bool):
        options[OPT_READ_ONLY_MODE] = raw_read_only

    turn_action = str(raw_options.get(OPT_ENCODER_TURN_ACTION, options[OPT_ENCODER_TURN_ACTION]) or "").strip()
    if turn_action in CONTROL_CENTER_ACTIONS:
        options[OPT_ENCODER_TURN_ACTION] = turn_action

    press_action = str(raw_options.get(OPT_ENCODER_PRESS_ACTION, options[OPT_ENCODER_PRESS_ACTION]) or "").strip()
    if press_action in CONTROL_CENTER_PRESS_ACTIONS:
        options[OPT_ENCODER_PRESS_ACTION] = press_action

    long_press_action = str(
        raw_options.get(OPT_ENCODER_LONG_PRESS_ACTION, options[OPT_ENCODER_LONG_PRESS_ACTION]) or ""
    ).strip()
    if long_press_action in CONTROL_CENTER_PRESS_ACTIONS:
        options[OPT_ENCODER_LONG_PRESS_ACTION] = long_press_action

    for key in (OPT_BUTTON_1_SCENE, OPT_BUTTON_2_SCENE, OPT_BUTTON_3_SCENE, OPT_BUTTON_4_SCENE):
        scene_value = str(raw_options.get(key, options[key]) or "").strip()
        normalized_scene = scene_value.lower()
        if normalized_scene in {"", "none", "scene.none"}:
            options[key] = "scene.none"
            continue

        options[key] = scene_value if scene_value.startswith("scene.") else "scene.none"

    return options
