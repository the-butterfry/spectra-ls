# Description: Extracted metadata stack workflows for Spectra LS (metadata prep/bridge/cutover validation and metadata trial services).
# Version: 2026.08.18.5
# Last updated: 2026-08-18
# PARITY DIRECTIVE (until full cutover): behavior/contract edits here require same-slice two-track parity review
# and version-metadata review in runtime (`packages/` + `esphome/`) and component (`custom_components/spectra_ls/`) tracks.

from __future__ import annotations

from datetime import UTC, datetime
import json
from typing import Any
from uuid import uuid4

from .const import (
	FABRIC_AUTH_MODE_DEGRADED_FALLBACK,
	FABRIC_AUTH_MODE_PRIMARY,
	FABRIC_AUTH_REASON_API_UNREACHABLE,
	FABRIC_AUTH_REASON_DEGRADED_ACTIVE,
	FABRIC_AUTH_REASON_PAYLOAD_SHAPE_INVALID,
	FABRIC_AUTH_REASON_PAYLOAD_STALE,
	LEGACY_ACTIVE_DURATION,
	LEGACY_ACTIVE_META_ENTITY,
	LEGACY_ACTIVE_TARGET_HELPER,
	LEGACY_META_CANDIDATES,
	LEGACY_META_CONFIDENCE_MIN,
	LEGACY_META_OVERRIDE_ACTIVE,
	LEGACY_META_OVERRIDE_ENTITY,
	LEGACY_META_PAUSED_HIDE_S,
	LEGACY_META_RESOLVER,
	LEGACY_NOW_PLAYING_DISPLAY_ALLOWED,
	LEGACY_NOW_PLAYING_DURATION,
	LEGACY_NOW_PLAYING_ENTITY,
	LEGACY_NOW_PLAYING_MEDIA_CLASS,
	LEGACY_NOW_PLAYING_POSITION,
	LEGACY_NOW_PLAYING_PREVIEW_KEY,
	LEGACY_NOW_PLAYING_STATE,
	LEGACY_NOW_PLAYING_TITLE,
	META_POLICY_DEFAULTS,
	META_SUPPRESSION_ENTITY_MISSING,
	META_SUPPRESSION_LONG_IDLE,
	META_SUPPRESSION_NO_FRESH_SIGNAL,
	META_SUPPRESSION_PAUSED_FRESH,
	META_SUPPRESSION_PAUSED_STALE,
	META_SUPPRESSION_PLAYING,
	META_SUPPRESSION_PLAYING_STALE,
	METADATA_AUTH_OWNER_COMPONENT,
	METADATA_AUTH_OWNER_LEGACY,
	METADATA_CUTOVER_BLOCK_LEGACY_MODE,
	METADATA_CUTOVER_BLOCK_NOT_CUT_OVER,
	METADATA_CUTOVER_BLOCK_PREP_NOT_READY,
	METADATA_CUTOVER_BLOCK_RESOLVER_CANDIDATE_MISSING,
	WRITE_AUTH_COMPONENT,
)
from .metadata_selection_policy import pick_now_playing_candidate
from .write_path_fabric import WritePathFabric


class MetadataStackWorkflow:
	"""Owns metadata-stack logic extracted from the coordinator."""

	NON_META_SOURCE_TOKENS: tuple[str, ...] = (
		"optical",
		"line in",
		"line-in",
		"aux",
		"coax",
		"hdmi",
		"arc",
	)
	PLAYING_STATIC_GRACE_MAX_S = 12.0

	def __init__(self, coordinator: Any) -> None:
		self._coordinator = coordinator
		self._metadata_trial_in_progress = False
		self._last_metadata_trial_attempt: dict[str, Any] = {
			"status": "never_attempted",
			"requested_at": None,
			"completed_at": None,
			"reason": "No metadata trial attempts yet",
			"audit_payload_complete": False,
			"audit_payload_state": "N/A",
			"missing_audit_fields": [],
			"blocking_reasons": [],
			"trial_gate_verdict": "N/A",
			"eligible_for_closeout": False,
		}
		self._last_metadata_resolver_attempt: dict[str, Any] = {
			"status": "never_attempted",
			"requested_at": None,
			"completed_at": None,
			"reason": "No metadata-resolver scaffold attempts requested yet",
			"dry_run": True,
			"force": False,
			"selected_meta_entity": "",
			"selection_reason": "",
		}
		self._last_metadata_bridge_attempt: dict[str, Any] = {
			"status": "never_attempted",
			"requested_at": None,
			"completed_at": None,
			"reason": "No metadata-trial bridge scaffold attempts requested yet",
			"resolver_status": "never_attempted",
			"trial_status": "never_attempted",
		}
		self._last_metadata_override_attempt: dict[str, Any] = {
			"status": "never_attempted",
			"requested_at": None,
			"completed_at": None,
			"reason": "No metadata override apply/clear attempts requested yet",
			"enable": False,
			"entity_id": "",
		}
		self._last_passthrough_metadata_cache: dict[str, Any] = {
			"title": "",
			"artist": "",
			"album": "",
			"app": "",
			"captured_at": 0.0,
		}
		self._last_progress_clock_cache: dict[str, Any] = {
			"entity": "",
			"title": "",
			"source": "",
			"position": None,
			"duration": None,
			"captured_at": 0.0,
		}
		self._progress_signal_cache: dict[str, dict[str, Any]] = {}
		self._selector_lock: dict[str, Any] = {
			"entity": "",
			"title": "",
			"duration": None,
			"locked_at": 0.0,
			"last_position": None,
		}

	@property
	def metadata_trial_in_progress(self) -> bool:
		return self._metadata_trial_in_progress

	@property
	def last_metadata_trial_attempt(self) -> dict[str, Any]:
		return self._last_metadata_trial_attempt

	@property
	def last_metadata_resolver_attempt(self) -> dict[str, Any]:
		return self._last_metadata_resolver_attempt

	@property
	def last_metadata_bridge_attempt(self) -> dict[str, Any]:
		return self._last_metadata_bridge_attempt

	@property
	def last_metadata_override_attempt(self) -> dict[str, Any]:
		return self._last_metadata_override_attempt

	def set_last_metadata_bridge_attempt(self, payload: dict[str, Any]) -> None:
		self._last_metadata_bridge_attempt = payload

	@staticmethod
	def _normalized_entity_id(value: str) -> str:
		entity = str(value or "").strip().lower()
		if entity in {"", "none", "unknown", "unavailable", "null"}:
			return ""
		return entity

	@classmethod
	def _entity_ids_match(cls, left: str, right: str) -> bool:
		left_norm = cls._normalized_entity_id(left)
		right_norm = cls._normalized_entity_id(right)
		return left_norm != "" and right_norm != "" and left_norm == right_norm

	def _entity_payload_meta(self, entity_id: str) -> tuple[str, str, str]:
		"""Return normalized title/artist/album tuple for an entity."""
		c = self._coordinator
		if not c._is_resolved_state(entity_id):
			return "", "", ""
		state_obj = c.hass.states.get(entity_id)
		if state_obj is None:
			return "", "", ""
		title = str(state_obj.attributes.get("media_title", "") or "").strip()
		artist = str(state_obj.attributes.get("media_artist", "") or "").strip()
		album = str(state_obj.attributes.get("media_album_name", "") or "").strip()
		return title, artist, album

	def _entity_has_payload_meta(self, entity_id: str) -> bool:
		title, artist, album = self._entity_payload_meta(entity_id)
		return bool(title or artist or album)

	def _entity_has_track_identity_meta(self, entity_id: str) -> bool:
		title, artist, _album = self._entity_payload_meta(entity_id)
		return bool(title or artist)

	def _entity_meta_richness(self, entity_id: str) -> int:
		c = self._coordinator
		if not c._is_resolved_state(entity_id):
			return 0
		state_obj = c.hass.states.get(entity_id)
		if state_obj is None:
			return 0

		title, artist, album = self._entity_payload_meta(entity_id)
		app_name = str(state_obj.attributes.get("app_name", "") or "").strip()
		source = str(state_obj.attributes.get("source", "") or "").strip()

		richness = 0
		if title:
			richness += 40
		if artist:
			richness += 30
		if album:
			richness += 25
		if app_name:
			richness += 8
		if source:
			richness += 5
		return richness

	def _component_override_state(self) -> dict[str, Any]:
		c = self._coordinator
		state = getattr(c, "_component_metadata_override_state", None)
		if not isinstance(state, dict):
			state = {
				"active": False,
				"entity": "",
				"updated_at": None,
				"source": "component_default_state",
			}

		active = bool(state.get("active", False))
		entity = str(state.get("entity", "") or "").strip()
		if not c._is_resolved_state(entity):
			entity = ""

		if not active and entity == "":
			helper_active_state = c.hass.states.get(LEGACY_META_OVERRIDE_ACTIVE)
			helper_entity_state = c.hass.states.get(LEGACY_META_OVERRIDE_ENTITY)
			helper_active = c._normalize_state(
				helper_active_state.state if helper_active_state is not None else ""
			) == "on"
			helper_entity = str(helper_entity_state.state if helper_entity_state is not None else "").strip()
			if not c._is_resolved_state(helper_entity):
				helper_entity = ""
			if helper_active or helper_entity:
				active = bool(helper_active)
				entity = helper_entity
				state["source"] = "legacy_helper_seed"

		state["active"] = active
		state["entity"] = entity
		c._component_metadata_override_state = state
		return state

	def _persist_component_override_state(self, *, active: bool, entity: str, source: str) -> dict[str, Any]:
		c = self._coordinator
		state = self._component_override_state()
		normalized_entity = str(entity or "").strip()
		if not c._is_resolved_state(normalized_entity):
			normalized_entity = ""
		state["active"] = bool(active)
		state["entity"] = normalized_entity
		state["updated_at"] = datetime.now(UTC).isoformat()
		state["source"] = str(source or "component_state_update")
		c._component_metadata_override_state = state
		return state

	async def async_set_metadata_override(
		self,
		*,
		enable: bool,
		entity_id: str | None,
		dry_run: bool,
		force: bool,
		reason: str,
		correlation_id: str | None,
	) -> dict[str, Any]:
		c = self._coordinator
		requested_at = datetime.now(UTC).isoformat()
		corr = (correlation_id or "").strip() or f"meta-override-{uuid4().hex[:12]}"
		requested_entity = (entity_id or "").strip()
		reason_norm = (reason or "").strip()

		override_state = self._component_override_state()
		override_active_state = c.hass.states.get(LEGACY_META_OVERRIDE_ACTIVE)
		override_entity_state = c.hass.states.get(LEGACY_META_OVERRIDE_ENTITY)
		override_active_exists = True
		override_entity_exists = True
		current_override_active = bool(override_state.get("active", False))
		current_override_entity = str(override_state.get("entity", "") or "").strip()

		result: dict[str, Any] = {
			"status": "pending",
			"reason": "",
			"requested_at": requested_at,
			"completed_at": requested_at,
			"correlation_id": corr,
			"authority_mode": c._write_authority_mode,
			"dry_run": bool(dry_run),
			"force": bool(force),
			"enable": bool(enable),
			"entity_id": requested_entity,
			"override_active_entity": LEGACY_META_OVERRIDE_ACTIVE,
			"override_entity_helper": LEGACY_META_OVERRIDE_ENTITY,
			"override_active_exists": override_active_exists,
			"override_entity_exists": override_entity_exists,
			"current_override_active": current_override_active,
			"current_override_entity": current_override_entity,
			"operator_reason": reason_norm,
		}

		if enable and not c._is_resolved_state(requested_entity):
			result["status"] = "blocked_missing_entity"
			result["reason"] = "entity_id is required when enable=true"
		elif enable and c.hass.states.get(requested_entity) is None:
			result["status"] = "blocked_entity_not_found"
			result["reason"] = "Requested metadata entity is not present in HA state registry"
		else:
			WritePathFabric.apply_standard_write_guards(
				c,
				result,
				force=force,
				dry_run=dry_run,
				authority_required=WRITE_AUTH_COMPONENT,
				authority_block_reason="Write authority is not component; metadata override apply/clear is blocked",
			)

		desired_entity = requested_entity if enable else ""
		if (
			result["status"] == "pending"
			and current_override_active == bool(enable)
			and current_override_entity == desired_entity
		):
			result["status"] = "noop_already_applied"
			result["reason"] = "Metadata override helper state already matches requested payload"

		if result["status"] == "pending" and dry_run:
			result["status"] = "dry_run_ok"
			result["reason"] = "Metadata override guards passed (dry run)"

		if result["status"] == "pending":
			c._write_in_progress = True
			try:
				self._persist_component_override_state(
					active=bool(enable),
					entity=desired_entity,
					source="set_metadata_override",
				)

				result["status"] = "write_applied"
				result["reason"] = "Metadata override state updated in component store"
			except Exception as err:  # pragma: no cover - defensive runtime guard
				result["status"] = "write_error"
				result["reason"] = "Component metadata override state update failed"
				result["error"] = str(err)
			finally:
				c._write_in_progress = False

		if result["status"] in {"dry_run_ok", "noop_already_applied", "write_applied", "write_error"}:
			WritePathFabric.mark_write_touch(c)

		result["completed_at"] = datetime.now(UTC).isoformat()
		self._last_metadata_override_attempt = result
		WritePathFabric.stamp_last_write_attempt(
			c,
			result=result,
			source="set_metadata_override",
			correlation_id=corr,
			active_target=desired_entity,
		)
		c.refresh_snapshot()
		return result

	@staticmethod
	def metadata_trial_audit_missing_fields(payload: dict[str, Any]) -> list[str]:
		required_fields = {
			"status": payload.get("status"),
			"window_id": payload.get("window_id"),
			"requested_mode": payload.get("requested_mode"),
			"effective_mode": payload.get("effective_mode"),
			"dry_run": payload.get("dry_run"),
			"reason": payload.get("reason"),
			"correlation_id": payload.get("correlation_id"),
			"requested_at": payload.get("requested_at"),
			"completed_at": payload.get("completed_at"),
		}

		missing: list[str] = []
		for field, value in required_fields.items():
			if field == "dry_run":
				if value is None:
					missing.append(field)
				continue
			if value is None:
				missing.append(field)
				continue
			if isinstance(value, str) and value.strip() == "":
				missing.append(field)

		return missing

	def _recover_bridge_wait_status(
		self,
		*,
		ma_boot_ready: bool,
		bridge_attempt: dict[str, Any],
	) -> tuple[str, dict[str, Any]]:
		"""Normalize stale startup-wait bridge statuses after boot readiness recovers."""
		bridge_status = str(bridge_attempt.get("status", "never_attempted") or "never_attempted")
		stale_wait_statuses = {"waiting_for_startup_readiness", "waiting_for_ma_boot"}
		if not ma_boot_ready or bridge_status not in stale_wait_statuses:
			return bridge_status, bridge_attempt

		recovered_now_iso = datetime.now(UTC).isoformat()
		updated_bridge_attempt = dict(bridge_attempt)
		updated_bridge_attempt["status"] = "startup_readiness_recovered_pending_bridge_attempt"
		updated_bridge_attempt["completed_at"] = recovered_now_iso
		updated_bridge_attempt["recovered_from_status"] = bridge_status
		updated_bridge_attempt["startup_readiness_recovered"] = True
		if not str(updated_bridge_attempt.get("reason", "") or "").strip():
			updated_bridge_attempt["reason"] = (
				"Startup readiness is now satisfied; bridge wait posture was recovered to pending bridge attempt"
			)

		self._last_metadata_bridge_attempt = updated_bridge_attempt
		return str(updated_bridge_attempt.get("status", "") or ""), updated_bridge_attempt

	@staticmethod
	def _collect_failed_check_reasons(
		*,
		checks: dict[str, bool],
		reason_map: dict[str, str],
	) -> list[str]:
		"""Collect deterministic blocker reasons for checks that evaluate false."""
		failed_reasons: list[str] = []
		for key, passed in checks.items():
			if not passed and key in reason_map:
				failed_reasons.append(reason_map[key])
		return failed_reasons

	@staticmethod
	def _cutover_proof_windows(bridge_attempt: dict[str, Any]) -> tuple[dict[str, Any] | None, dict[str, Any] | None, dict[str, Any] | None]:
		"""Extract normalized cutover proof windows from the bridge attempt payload."""
		cutover_proof = (
			bridge_attempt.get("cutover_proof", {})
			if isinstance(bridge_attempt.get("cutover_proof", {}), dict)
			else {}
		)
		pre_window = cutover_proof.get("pre_window") if isinstance(cutover_proof.get("pre_window"), dict) else None
		in_window = cutover_proof.get("in_window") if isinstance(cutover_proof.get("in_window"), dict) else None
		post_window = cutover_proof.get("post_window") if isinstance(cutover_proof.get("post_window"), dict) else None
		return pre_window, in_window, post_window

	@staticmethod
	def _metadata_bridge_verdict(checks: dict[str, bool]) -> str:
		"""Compute bridge validation verdict from normalized check set."""
		if not bool(checks.get("ma_boot_ready", False)):
			return "WARN"
		if not bool(checks.get("metadata_prep_ready", False)) or not bool(checks.get("resolver_candidate_present", False)):
			return "FAIL"
		if not bool(checks.get("trial_authority_satisfied", False)):
			return "WARN"
		if not bool(checks.get("resolver_stage_ok", False)) or not bool(checks.get("trial_stage_ok", False)):
			return "WARN"
		return "PASS"

	@staticmethod
	def _metadata_bridge_blocking_reasons(
		*,
		checks: dict[str, bool],
		resolver_stage_required: bool,
		trial_stage_required: bool,
		resolver_status: str,
		trial_status: str,
	) -> list[str]:
		"""Build deterministic bridge blocking reason list with stage-attempt guards."""
		blocking_reasons: list[str] = []
		if not bool(checks.get("ma_boot_ready", False)):
			blocking_reasons.append("waiting_for_startup_readiness")
		if not bool(checks.get("metadata_prep_ready", False)):
			blocking_reasons.append("metadata_prep_not_ready")
		if not bool(checks.get("resolver_candidate_present", False)):
			blocking_reasons.append("resolver_candidate_missing")
		if bool(checks.get("ma_boot_ready", False)) and not bool(checks.get("trial_authority_satisfied", False)):
			blocking_reasons.append("trial_authority_not_component")
		if resolver_stage_required and not bool(checks.get("resolver_stage_ok", False)) and resolver_status != "never_attempted":
			blocking_reasons.append("resolver_stage_not_ok")
		if trial_stage_required and not bool(checks.get("trial_stage_ok", False)) and trial_status != "never_attempted":
			blocking_reasons.append("trial_stage_not_ok")
		return blocking_reasons

	def build_metadata_bridge_validation(
		self,
		*,
		metadata_prep_validation: dict[str, Any],
	) -> dict[str, Any]:
		c = self._coordinator
		ma_boot_ready, ma_boot_reasons = c._is_startup_recovery_boot_ready()
		ma_boot_wait_reason = c._format_startup_boot_wait_reasons(ma_boot_reasons)

		scaffolds = c._build_component_scaffolds()
		resolver_plan = (
			scaffolds.get("metadata_resolver_plan", {})
			if isinstance(scaffolds.get("metadata_resolver_plan", {}), dict)
			else {}
		)
		prep_values = (
			metadata_prep_validation.get("values", {})
			if isinstance(metadata_prep_validation.get("values", {}), dict)
			else {}
		)
		component_now_playing_entity = str(
			prep_values.get("now_playing_entity", "")
			or c.hass.states.get("sensor.component_now_playing_entity").state
			if c.hass.states.get("sensor.component_now_playing_entity") is not None
			else ""
		).strip()
		resolver_selected = str(
			resolver_plan.get("selected_meta_entity", "") or component_now_playing_entity
		).strip()
		resolver_attempt = self._last_metadata_resolver_attempt if isinstance(self._last_metadata_resolver_attempt, dict) else {}
		bridge_attempt = self._last_metadata_bridge_attempt if isinstance(self._last_metadata_bridge_attempt, dict) else {}
		trial_attempt = self._last_metadata_trial_attempt if isinstance(self._last_metadata_trial_attempt, dict) else {}

		resolver_status = str(resolver_attempt.get("status", "never_attempted") or "never_attempted")
		trial_status = str(trial_attempt.get("status", "never_attempted") or "never_attempted")
		bridge_status, bridge_attempt = self._recover_bridge_wait_status(
			ma_boot_ready=ma_boot_ready,
			bridge_attempt=bridge_attempt,
		)
		bridge_stages = bridge_attempt.get("stages", {}) if isinstance(bridge_attempt.get("stages", {}), dict) else {}
		bridge_trial_stage = (
			bridge_stages.get("metadata_trial", {})
			if isinstance(bridge_stages.get("metadata_trial", {}), dict)
			else {}
		)
		bridge_trial_stage_status = str(bridge_trial_stage.get("status", "") or "").strip()
		if trial_status == "never_attempted" and bridge_trial_stage_status:
			trial_status = bridge_trial_stage_status

		trial_status_unresolved = trial_status in {"", "unknown", "never_attempted"}
		if bridge_status == "bridge_completed" and trial_status_unresolved:
			trial_dry_run = bool(bridge_attempt.get("trial_dry_run", True))
			trial_status = "dry_run_ok" if trial_dry_run else "noop_applied"

		metadata_prep_ready = bool(metadata_prep_validation.get("ready_for_metadata_handoff", False))
		metadata_cutover_active = bool(metadata_prep_validation.get("metadata_cutover_active", False))
		component_mode_active = c._write_authority_mode == WRITE_AUTH_COMPONENT
		bridge_skip_component_no_mix = (
			component_mode_active and bridge_status == "skipped_component_startup_no_mix"
		)
		component_resolver_authority_ready = (
			metadata_prep_ready
			and metadata_cutover_active
			and c._is_resolved_state(component_now_playing_entity)
		)
		trial_authority_component = c._write_authority_mode == WRITE_AUTH_COMPONENT
		trial_authority_satisfied = (
			trial_authority_component
			or metadata_cutover_active
			or (bridge_skip_component_no_mix and component_resolver_authority_ready)
		)
		resolver_candidate_present = c._is_resolved_state(resolver_selected)
		resolver_stage_required = not (bridge_skip_component_no_mix and component_resolver_authority_ready)
		resolver_stage_ok = (
			resolver_status in {"dry_run_ok", "noop_already_selected", "write_applied"}
			or not resolver_stage_required
		)
		if not resolver_stage_required and resolver_status == "never_attempted":
			resolver_status = "skipped_component_authority_active"
		trial_stage_required = not metadata_cutover_active and not bridge_skip_component_no_mix
		trial_stage_ok = trial_status in {"dry_run_ok", "noop_applied"} or not trial_stage_required

		checks = {
			"metadata_prep_ready": metadata_prep_ready,
			"resolver_candidate_present": resolver_candidate_present,
			"component_resolver_authority_ready": component_resolver_authority_ready,
			"bridge_skip_component_no_mix": bridge_skip_component_no_mix,
			"trial_authority_component": trial_authority_component,
			"trial_authority_satisfied": trial_authority_satisfied,
			"resolver_stage_ok": resolver_stage_ok,
			"resolver_stage_required": resolver_stage_required,
			"trial_stage_ok": trial_stage_ok,
			"trial_stage_required": trial_stage_required,
			"metadata_cutover_active": metadata_cutover_active,
			"ma_boot_ready": ma_boot_ready,
		}

		verdict = self._metadata_bridge_verdict(checks)
		blocking_reasons = self._metadata_bridge_blocking_reasons(
			checks=checks,
			resolver_stage_required=resolver_stage_required,
			trial_stage_required=trial_stage_required,
			resolver_status=resolver_status,
			trial_status=trial_status,
		)

		return {
			"verdict": verdict,
			"ready_for_bridge": verdict == "PASS",
			"checks": checks,
			"blocking_reasons": blocking_reasons,
			"resolver_selected_meta_entity": resolver_selected,
			"resolver_status": resolver_status,
			"trial_status": trial_status,
			"bridge_status": bridge_status,
			"last_bridge_attempt": bridge_attempt,
			"waiting_for_startup_readiness": not ma_boot_ready,
			"waiting_for_ma_boot": not ma_boot_ready,
			"ma_boot_wait_reasons": ma_boot_reasons,
			"ma_boot_wait_reason": ma_boot_wait_reason,
		}

	def build_cutover_prep_validation(
		self,
		*,
		metadata_prep_validation: dict[str, Any],
		metadata_bridge_validation: dict[str, Any],
	) -> dict[str, Any]:
		c = self._coordinator
		owner = str(metadata_prep_validation.get("metadata_authority_owner", "") or "")
		cutover_active = bool(metadata_prep_validation.get("metadata_cutover_active", False))
		cutover_block_reason = str(metadata_prep_validation.get("cutover_block_reason", "") or "")
		metadata_ready = bool(metadata_prep_validation.get("ready_for_metadata_handoff", False))
		bridge_ready = bool(metadata_bridge_validation.get("ready_for_bridge", False))

		trial_attempt = self._last_metadata_trial_attempt if isinstance(self._last_metadata_trial_attempt, dict) else {}
		bridge_attempt = self._last_metadata_bridge_attempt if isinstance(self._last_metadata_bridge_attempt, dict) else {}
		trial_eligible_for_closeout = bool(trial_attempt.get("eligible_for_closeout", False))

		pre_window, in_window, post_window = self._cutover_proof_windows(bridge_attempt)

		checks = {
			"metadata_handoff_ready": metadata_ready,
			"metadata_owner_component": owner == METADATA_AUTH_OWNER_COMPONENT,
			"metadata_cutover_active": cutover_active,
			"cutover_unblocked": cutover_block_reason == "",
			"bridge_ready": bridge_ready,
			"trial_eligible_for_closeout": trial_eligible_for_closeout,
			"proof_pre_window_present": isinstance(pre_window, dict),
			"proof_in_window_present": isinstance(in_window, dict),
			"proof_post_window_present": isinstance(post_window, dict),
			"proof_in_window_cutover_active": bool(in_window.get("metadata_cutover_active", False))
			if isinstance(in_window, dict)
			else False,
			"proof_in_window_owner_component": str(in_window.get("metadata_authority_owner", "") or "")
			== METADATA_AUTH_OWNER_COMPONENT
			if isinstance(in_window, dict)
			else False,
		}

		reason_map = {
			"metadata_handoff_ready": "metadata_handoff_not_ready",
			"metadata_owner_component": "metadata_owner_not_component",
			"metadata_cutover_active": "metadata_cutover_not_active",
			"cutover_unblocked": "metadata_cutover_blocked",
			"bridge_ready": "metadata_bridge_not_ready",
			"trial_eligible_for_closeout": "metadata_trial_not_closeout_eligible",
			"proof_pre_window_present": "cutover_proof_pre_window_missing",
			"proof_in_window_present": "cutover_proof_in_window_missing",
			"proof_post_window_present": "cutover_proof_post_window_missing",
			"proof_in_window_cutover_active": "cutover_proof_in_window_not_cutover_active",
			"proof_in_window_owner_component": "cutover_proof_in_window_owner_not_component",
		}
		blocking_reasons = self._collect_failed_check_reasons(checks=checks, reason_map=reason_map)

		cutover_prep_complete = all(bool(value) for value in checks.values())
		verdict = "PASS" if cutover_prep_complete else "WARN"

		return {
			"verdict": verdict,
			"cutover_prep_complete": cutover_prep_complete,
			"checks": checks,
			"blocking_reasons": blocking_reasons,
			"expected_owner": METADATA_AUTH_OWNER_COMPONENT,
			"observed_owner": owner,
			"observed_cutover_active": cutover_active,
			"observed_cutover_block_reason": cutover_block_reason,
			"bridge_status": str(metadata_bridge_validation.get("bridge_status", "") or ""),
			"trial_status": str(metadata_bridge_validation.get("trial_status", "") or ""),
			"trial_closeout_eligible": trial_eligible_for_closeout,
		}

	def _resolve_metadata_authority_state(
		self,
		*,
		metadata_prep_ready: bool,
		resolver_selected: str,
	) -> dict[str, Any]:
		c = self._coordinator
		resolver_candidate_ready = c._is_resolved_state(resolver_selected)
		component_mode_active = c._write_authority_mode == WRITE_AUTH_COMPONENT
		component_cutover_ready = bool(metadata_prep_ready and resolver_candidate_ready)
		metadata_cutover_active = bool(component_mode_active and component_cutover_ready)

		# Ownership policy (no legacy fallback in component mode):
		# - component mode always reports component ownership, even if cutover is not yet active.
		# - legacy ownership is only reported when component mode itself is not active.
		metadata_authority_owner = (
			METADATA_AUTH_OWNER_COMPONENT if component_mode_active else METADATA_AUTH_OWNER_LEGACY
		)

		cutover_block_reason = ""
		if not metadata_cutover_active:
			if not component_mode_active:
				cutover_block_reason = METADATA_CUTOVER_BLOCK_LEGACY_MODE
			elif not metadata_prep_ready:
				cutover_block_reason = METADATA_CUTOVER_BLOCK_PREP_NOT_READY
			elif not resolver_candidate_ready:
				cutover_block_reason = METADATA_CUTOVER_BLOCK_RESOLVER_CANDIDATE_MISSING
			else:
				cutover_block_reason = METADATA_CUTOVER_BLOCK_NOT_CUT_OVER

		return {
			"metadata_authority_owner": metadata_authority_owner,
			"metadata_cutover_active": metadata_cutover_active,
			"cutover_block_reason": cutover_block_reason,
			"component_mode_active": component_mode_active,
			"resolver_candidate_ready": resolver_candidate_ready,
			"component_cutover_ready": component_cutover_ready,
		}

	def _missing_now_playing_signal(self, *, suppression_reason: str = META_SUPPRESSION_ENTITY_MISSING) -> dict[str, Any]:
		"""Return canonical missing-signal payload for unresolved/missing now-playing entities."""
		return {
			"resolved": False,
			"state": "missing",
			"play_state_attr": "",
			"is_playing_attr": None,
			"is_paused_attr": None,
			"position_age_s": None,
			"recent_progress": False,
			"recent_play_progress": False,
			"recent_paused_progress": False,
			"fresh_play_signal": False,
			"playing_without_fresh_signal": False,
			"paused_without_fresh_signal": False,
			"long_idle_stale_hidden": False,
			"suppression_reason": suppression_reason,
			"meta_stale_s": float(META_POLICY_DEFAULTS["meta_stale_s"]),
			"paused_hide_s": float(META_POLICY_DEFAULTS["paused_hide_s"]),
		}

	def _build_now_playing_signal(self, entity_id: str) -> dict[str, Any]:
		c = self._coordinator

		def _safe_float(raw_value: Any, default: float) -> float:
			try:
				return float(raw_value)
			except (TypeError, ValueError):
				return default

		def _coerce_number(raw_value: Any) -> float | None:
			try:
				return float(raw_value)
			except (TypeError, ValueError):
				return None

		if not c._is_resolved_state(entity_id):
			return self._missing_now_playing_signal()

		state = c.hass.states.get(entity_id)
		if state is None:
			return self._missing_now_playing_signal()

		state_norm = c._normalize_state(state.state)
		play_state_attr = c._normalize_state(str(state.attributes.get("play_state", "") or ""))
		is_playing_attr = state.attributes.get("is_playing")
		is_paused_attr = state.attributes.get("is_paused")
		pos_age_from_position = c._timestamp_age_seconds(state.attributes.get("media_position_updated_at"))
		pos_age_source = "media_position_updated_at"
		pos_age_s = pos_age_from_position
		if pos_age_s is None:
			pos_age_s = c._timestamp_age_seconds(state.last_updated)
			pos_age_source = "last_updated" if pos_age_s is not None else "missing"
		if pos_age_s is None:
			pos_age_s = c._timestamp_age_seconds(state.last_changed)
			pos_age_source = "last_changed" if pos_age_s is not None else "missing"

		meta_stale_s = float(META_POLICY_DEFAULTS["meta_stale_s"])
		paused_hide_s_state = c.hass.states.get(LEGACY_META_PAUSED_HIDE_S)
		paused_hide_s = _safe_float(paused_hide_s_state.state, float(META_POLICY_DEFAULTS["paused_hide_s"])) if (
			paused_hide_s_state is not None
			and paused_hide_s_state.state not in ("", "unknown", "unavailable")
		) else float(META_POLICY_DEFAULTS["paused_hide_s"])

		recent_play_progress = pos_age_s is not None and pos_age_s <= meta_stale_s
		recent_paused_progress = pos_age_s is not None and pos_age_s <= paused_hide_s
		has_progress_clock = pos_age_s is not None

		media_position = state.attributes.get("media_position")
		media_duration = state.attributes.get("media_duration")
		media_title = str(state.attributes.get("media_title", "") or "").strip()
		media_artist = str(state.attributes.get("media_artist", "") or "").strip()
		app_name = str(state.attributes.get("app_name", "") or "").strip()
		source_text = str(state.attributes.get("source", "") or "").strip()
		position_s = _coerce_number(media_position)
		duration_s = _coerce_number(media_duration)
		now_ts = datetime.now(UTC).timestamp()
		position_change_recent = False
		if isinstance(position_s, float):
			cache = self._progress_signal_cache.get(entity_id, {})
			last_pos = cache.get("position")
			last_change_at = float(cache.get("last_change_at", 0.0) or 0.0)
			if isinstance(last_pos, (int, float)):
				if abs(position_s - float(last_pos)) >= 0.05:
					last_change_at = now_ts
			elif last_change_at <= 0.0:
				last_change_at = now_ts
			self._progress_signal_cache[entity_id] = {
				"position": position_s,
				"sampled_at": now_ts,
				"last_change_at": last_change_at,
			}
			if last_change_at > 0.0:
				position_change_recent = (now_ts - last_change_at) <= meta_stale_s

		playing_signal = (
			state_norm == "playing"
			or play_state_attr in {"play", "playing"}
			or is_playing_attr is True
		)
		paused_signal = (
			state_norm == "paused"
			or play_state_attr in {"pause", "paused"}
			or is_paused_attr is True
		)

		playing_at_track_end_stuck = (
			playing_signal
			and isinstance(position_s, float)
			and isinstance(duration_s, float)
			and duration_s > 0
			and position_s >= max(duration_s - 1.5, duration_s * 0.995)
			and (pos_age_s is None or pos_age_s > 5.0)
		)

		playing_static_grace_s = max(3.0, min(self.PLAYING_STATIC_GRACE_MAX_S, meta_stale_s))
		has_track_or_progress_identity = bool(
			media_title
			or media_artist
			or (isinstance(position_s, float) and position_s > 0.0)
			or (isinstance(duration_s, float) and duration_s > 0.0)
		)
		playing_static_grace_active = (
			playing_signal
			and not playing_at_track_end_stuck
			and recent_play_progress
			and not position_change_recent
			and has_track_or_progress_identity
			and isinstance(pos_age_s, float)
			and pos_age_s <= playing_static_grace_s
		)

		playing_with_fresh_signal = (
			playing_signal
			and not playing_at_track_end_stuck
			and recent_play_progress
			and (position_change_recent or playing_static_grace_active)
		)
		playing_without_fresh_signal = (
			playing_signal
			and (
				playing_at_track_end_stuck
				or (not has_progress_clock)
				or (has_progress_clock and not recent_play_progress)
				or (
					has_progress_clock
					and recent_play_progress
					and not position_change_recent
					and not playing_static_grace_active
				)
			)
		)
		fresh_play_signal = playing_with_fresh_signal or (paused_signal and recent_paused_progress)
		paused_without_fresh_signal = paused_signal and not recent_paused_progress
		long_idle_stale_hidden = not playing_signal and not paused_signal

		if playing_with_fresh_signal:
			suppression_reason = META_SUPPRESSION_PLAYING
		elif paused_signal and recent_paused_progress:
			suppression_reason = META_SUPPRESSION_PAUSED_FRESH
		elif playing_without_fresh_signal:
			suppression_reason = META_SUPPRESSION_PLAYING_STALE
		elif paused_without_fresh_signal:
			suppression_reason = META_SUPPRESSION_PAUSED_STALE
		elif long_idle_stale_hidden:
			suppression_reason = META_SUPPRESSION_LONG_IDLE
		else:
			suppression_reason = META_SUPPRESSION_NO_FRESH_SIGNAL

		return {
			"resolved": True,
			"state": state_norm,
			"play_state_attr": play_state_attr,
			"is_playing_attr": is_playing_attr,
			"is_paused_attr": is_paused_attr,
			"position_age_s": round(pos_age_s, 1) if isinstance(pos_age_s, float) else None,
			"position_age_source": pos_age_source,
			"recent_progress": recent_paused_progress,
			"recent_play_progress": recent_play_progress,
			"recent_paused_progress": recent_paused_progress,
			"position_change_recent": position_change_recent,
			"playing_static_grace_active": playing_static_grace_active,
			"playing_static_grace_s": playing_static_grace_s,
			"playing_at_track_end_stuck": playing_at_track_end_stuck,
			"fresh_play_signal": fresh_play_signal,
			"playing_without_fresh_signal": playing_without_fresh_signal,
			"paused_without_fresh_signal": paused_without_fresh_signal,
			"long_idle_stale_hidden": long_idle_stale_hidden,
			"suppression_reason": suppression_reason,
			"meta_stale_s": meta_stale_s,
			"paused_hide_s": paused_hide_s,
		}

	def _metadata_candidate_payload_ready(self) -> bool:
		c = self._coordinator
		candidates_state = c.hass.states.get(LEGACY_META_CANDIDATES)
		if candidates_state is None:
			resolver_state = c.hass.states.get(LEGACY_META_RESOLVER)
			if resolver_state is None:
				return False
			resolver_best_entity = str(resolver_state.attributes.get("best_entity", "") or "").strip()
			resolver_best_score = resolver_state.attributes.get("best_score", 0)
			resolver_score_positive = isinstance(resolver_best_score, (int, float)) and float(resolver_best_score) > 0
			return c._is_resolved_state(resolver_best_entity) and resolver_score_positive

		def _parse_jsonish(value: Any) -> Any:
			if isinstance(value, (dict, list)):
				return value
			if isinstance(value, str):
				raw = value.strip()
				if not raw or raw in {"{}", "[]"}:
					return None
				try:
					return json.loads(raw)
				except json.JSONDecodeError:
					return None
			return None

		best_candidate_raw = candidates_state.attributes.get("best_candidate_json")
		best_candidate = _parse_jsonish(best_candidate_raw)
		if isinstance(best_candidate, dict):
			best_entity = str(best_candidate.get("entity", "") or "").strip()
			if best_entity:
				return True

		summary_raw = candidates_state.attributes.get("candidate_summary_json")
		summary = _parse_jsonish(summary_raw)
		if isinstance(summary, dict):
			entities = summary.get("entities", [])
			if isinstance(entities, list):
				if any(isinstance(entity, str) and entity.strip() for entity in entities):
					return True
			candidate_count = summary.get("candidate_count", 0)
			if isinstance(candidate_count, (int, float)) and candidate_count > 0:
				return True

		rows_raw = candidates_state.attributes.get("candidate_rows_json")
		rows = _parse_jsonish(rows_raw)
		if isinstance(rows, list):
			for row in rows:
				if isinstance(row, dict):
					entity = str(row.get("entity", "") or "").strip()
					if entity:
						return True

		resolver_state = c.hass.states.get(LEGACY_META_RESOLVER)
		if resolver_state is not None:
			resolver_best_entity = str(resolver_state.attributes.get("best_entity", "") or "").strip()
			resolver_best_score = resolver_state.attributes.get("best_score", 0)
			resolver_score_positive = isinstance(resolver_best_score, (int, float)) and float(resolver_best_score) > 0
			if c._is_resolved_state(resolver_best_entity) and resolver_score_positive:
				return True

		return False

	def _select_component_now_playing_entity(
		self,
		*,
		route_trace: dict[str, Any],
		active_meta_entity: str,
		legacy_now_playing_entity: str,
		resolver_selected_meta_entity: str = "",
		resolver_best_candidate: str = "",
		resolver_detected_candidate: str = "",
		passthrough_source_detected: bool = False,
	) -> tuple[str, str, dict[str, Any]]:
		"""Select component-preferred now-playing entity using deterministic policy pools."""
		c = self._coordinator
		active_target = str(route_trace.get("active_target", "") or "").strip()
		resolver_selected = str(resolver_selected_meta_entity or "").strip()

		candidates: list[tuple[str, str]] = []
		if c._is_resolved_state(resolver_selected):
			resolver_source = "resolver_selected_passthrough" if passthrough_source_detected else "resolver_selected_candidate"
			candidates.append((resolver_selected, resolver_source))
		if c._is_resolved_state(resolver_best_candidate):
			resolver_source = "resolver_best_candidate_passthrough" if passthrough_source_detected else "resolver_best_candidate"
			candidates.append((str(resolver_best_candidate).strip(), resolver_source))
		if c._is_resolved_state(resolver_detected_candidate):
			resolver_source = "resolver_detected_candidate_passthrough" if passthrough_source_detected else "resolver_detected_candidate"
			candidates.append((str(resolver_detected_candidate).strip(), resolver_source))

		candidates.extend(
			[
				(active_target, "route_active_target"),
				(active_meta_entity, "active_meta_entity"),
				(legacy_now_playing_entity, "legacy_now_playing_entity"),
			]
		)

		seen: set[str] = set()
		normalized_candidates: list[tuple[str, str]] = []
		for entity_id, source in candidates:
			entity_norm = str(entity_id or "").strip()
			if not c._is_resolved_state(entity_norm):
				continue
			if entity_norm in seen:
				continue
			seen.add(entity_norm)
			normalized_candidates.append((entity_norm, source))

		def _anchor_tokens(*entity_ids: str) -> list[str]:
			tokens: set[str] = set()
			for entity_id in entity_ids:
				entity_norm = str(entity_id or "").strip().lower()
				if not c._is_resolved_state(entity_norm):
					continue
				parts = entity_norm.replace(".", "_").split("_")
				for part in parts:
					part_norm = part.strip()
					if len(part_norm) >= 3 and part_norm not in {"media", "player", "component", "shadow"}:
						tokens.add(part_norm)

				state_obj = c.hass.states.get(entity_norm)
				if state_obj is not None:
					friendly = str(state_obj.attributes.get("friendly_name", "") or "").strip().lower()
					for part in friendly.replace("-", " ").replace("_", " ").split():
						part_norm = part.strip()
						if len(part_norm) >= 3:
							tokens.add(part_norm)
			return sorted(tokens)

		def _has_music_assistant_hint(entity_id: str) -> bool:
			state_obj = c.hass.states.get(entity_id)
			if state_obj is None:
				return False
			attrs = state_obj.attributes if isinstance(state_obj.attributes, dict) else {}
			entity_norm = str(entity_id or "").strip().lower()
			app_id = str(attrs.get("app_id", "") or "").strip().lower()
			app_name = str(attrs.get("app_name", "") or "").strip().lower()
			source = str(attrs.get("source", "") or "").strip().lower()
			has_explicit_ma_queue_marker = (
				"music assistant queue" in source
				or "ma queue" in source
				or "music_assistant_queue" in source
			)
			return (
				entity_norm.endswith("_ma")
				or "_ma_" in entity_norm
				or "_ma." in entity_norm
				or "music_assistant" in entity_norm
				or "music_assistant" in app_id
				or "music assistant" in app_name
				or "music assistant" in source
				or has_explicit_ma_queue_marker
			)

		def _is_sparse_transport_meta(entity_id: str) -> bool:
			state_obj = c.hass.states.get(entity_id)
			if state_obj is None:
				return False
			attrs = state_obj.attributes if isinstance(state_obj.attributes, dict) else {}
			source = str(attrs.get("source", "") or "").strip().lower()
			app_name = str(attrs.get("app_name", "") or "").strip().lower()
			title = str(attrs.get("media_title", "") or "").strip()
			artist = str(attrs.get("media_artist", "") or "").strip()
			album = str(attrs.get("media_album_name", "") or "").strip()
			transport_tokens = ("dlna", "upnp", "airplay", "spotify connect", "chromecast")
			has_transport_token = any(token in source or token in app_name for token in transport_tokens)
			has_sparse_payload = bool(title) and not bool(artist) and not bool(album)
			return has_transport_token and has_sparse_payload and not _has_music_assistant_hint(entity_id)

		def _looks_transport_mirror(entity_id: str) -> bool:
			state_obj = c.hass.states.get(entity_id)
			if state_obj is None:
				return False
			attrs = state_obj.attributes if isinstance(state_obj.attributes, dict) else {}
			source = str(attrs.get("source", "") or "").strip().lower()
			app_name = str(attrs.get("app_name", "") or "").strip().lower()
			meta_richness = self._entity_meta_richness(entity_id)
			transport_tokens = ("dlna", "upnp", "airplay", "spotify connect", "chromecast")
			has_transport_token = any(token in source or token in app_name for token in transport_tokens)
			return has_transport_token and not _has_music_assistant_hint(entity_id) and meta_richness <= 60

		def _discover_ma_rich_candidates() -> list[tuple[str, str]]:
			anchors = _anchor_tokens(active_target, active_meta_entity, legacy_now_playing_entity)
			matches: list[tuple[str, str]] = []
			fallback_matches: list[tuple[str, str]] = []
			for state_obj in c.hass.states.async_all("media_player"):
				entity_id = str(getattr(state_obj, "entity_id", "") or "").strip()
				if not c._is_resolved_state(entity_id):
					continue
				if not _has_music_assistant_hint(entity_id):
					continue
				if self._entity_meta_richness(entity_id) < 70:
					continue
				state_norm = c._normalize_state(str(getattr(state_obj, "state", "") or ""))
				if state_norm not in {"playing", "paused"}:
					continue

				friendly = str(state_obj.attributes.get("friendly_name", "") or "").strip().lower()
				entity_norm = entity_id.lower()
				if any(token in entity_norm or token in friendly for token in anchors):
					matches.append((entity_id, "discovered_ma_rich_candidate"))
				else:
					fallback_matches.append((entity_id, "discovered_ma_rich_global_fallback"))

			if len(matches) > 0:
				return matches
			return fallback_matches

		def _discover_passthrough_origin_candidates() -> list[tuple[str, str]]:
			if not passthrough_source_detected:
				return []

			route_state = c.hass.states.get(active_target) if c._is_resolved_state(active_target) else None
			route_attrs = route_state.attributes if route_state is not None and isinstance(route_state.attributes, dict) else {}
			route_title_hint = str(route_attrs.get("media_title", "") or "").strip().lower()
			route_artist_hint = str(route_attrs.get("media_artist", "") or "").strip().lower()
			route_has_meta = bool(route_title_hint or route_artist_hint)
			route_app_hints = {
				str(route_attrs.get("app_id", "") or "").strip().lower(),
				str(route_attrs.get("app_name", "") or "").strip().lower(),
			}
			route_app_hints = {hint for hint in route_app_hints if hint}

			matches: list[tuple[str, str, int]] = []
			fallback_matches: list[tuple[str, str, int]] = []
			for state_obj in c.hass.states.async_all("media_player"):
				entity_id = str(getattr(state_obj, "entity_id", "") or "").strip()
				if not c._is_resolved_state(entity_id):
					continue
				if entity_id == active_target:
					continue

				state_norm = c._normalize_state(str(getattr(state_obj, "state", "") or ""))
				if state_norm not in {"playing", "paused"}:
					continue

				title = str(state_obj.attributes.get("media_title", "") or "").strip()
				artist = str(state_obj.attributes.get("media_artist", "") or "").strip()
				if not (title or artist):
					continue

				signal = self._build_now_playing_signal(entity_id)
				fresh_signal = bool(signal.get("fresh_play_signal", False))
				recent_signal = bool(signal.get("recent_play_progress", False)) or bool(
					signal.get("recent_paused_progress", False)
				)

				source_text = str(state_obj.attributes.get("source", "") or "").strip()
				app_id = str(state_obj.attributes.get("app_id", "") or "").strip().lower()
				app_name = str(state_obj.attributes.get("app_name", "") or "").strip().lower()
				has_app_hint = bool(app_id or app_name)
				paused_origin_passthrough_ok = (
					state_norm == "paused"
					and bool(title)
					and has_app_hint
					and recent_signal
				)
				stale_origin_passthrough_ok = (
					state_norm == "playing"
					and bool(title or artist)
					and self._entity_meta_richness(entity_id) >= 70
					and not route_has_meta
				)
				if not (
					fresh_signal
					or recent_signal
					or paused_origin_passthrough_ok
					or stale_origin_passthrough_ok
				):
					continue
				if self._is_non_meta_source(source_text) and not has_app_hint:
					continue

				richness = self._entity_meta_richness(entity_id)
				score = richness
				if route_title_hint and title.lower() == route_title_hint:
					score += 60
				if route_artist_hint and artist.lower() == route_artist_hint:
					score += 35
				if route_app_hints and ((app_id in route_app_hints) or (app_name in route_app_hints)):
					score += 25
				if title and artist:
					score += 10

				if (route_title_hint or route_artist_hint or len(route_app_hints) > 0) and score >= 80:
					matches.append((entity_id, "discovered_passthrough_origin_candidate", score))
				elif score >= 70:
					fallback_matches.append((entity_id, "discovered_passthrough_origin_global_fallback", score))

			ordered_matches = sorted(matches, key=lambda item: (-item[2], item[0]))
			if len(ordered_matches) > 0:
				return [(entity_id, source) for entity_id, source, _score in ordered_matches[:3]]
			ordered_fallbacks = sorted(fallback_matches, key=lambda item: (-item[2], item[0]))
			return [(entity_id, source) for entity_id, source, _score in ordered_fallbacks[:3]]

		for entity_id, source in _discover_passthrough_origin_candidates():
			candidates.append((entity_id, source))

		for entity_id, source in _discover_ma_rich_candidates():
			candidates.append((entity_id, source))

		# Re-normalize after discovery append to preserve deterministic de-dup ordering.
		seen = set()
		normalized_candidates = []
		for entity_id, source in candidates:
			entity_norm = str(entity_id or "").strip()
			if not c._is_resolved_state(entity_norm):
				continue
			if entity_norm in seen:
				continue
			seen.add(entity_norm)
			normalized_candidates.append((entity_norm, source))

		source_rank = {
			"resolver_selected_passthrough": 0,
			"resolver_selected_candidate": 0,
			"resolver_best_candidate_passthrough": 1,
			"resolver_best_candidate": 1,
			"resolver_detected_candidate_passthrough": 2,
			"resolver_detected_candidate": 2,
			"discovered_passthrough_origin_candidate": 3,
			"discovered_passthrough_origin_global_fallback": 4,
			"active_meta_entity": 5,
			"route_active_target": 6,
			"legacy_now_playing_entity": 7,
			"discovered_ma_rich_candidate": 8,
			"discovered_ma_rich_global_fallback": 9,
		}

		candidate_rows: list[dict[str, Any]] = []
		eligible_rows: list[dict[str, Any]] = []
		ma_rich_active_exists = False

		for entity_id, source in normalized_candidates:
			state_obj = c.hass.states.get(entity_id)
			if state_obj is None:
				candidate_rows.append(
					{
						"entity": entity_id,
						"source": source,
						"eligible": False,
						"pool": "discarded",
						"reasons": ["state_missing"],
					}
				)
				continue

			signal = self._build_now_playing_signal(entity_id)
			state_norm = c._normalize_state(str(getattr(state_obj, "state", "") or ""))
			has_meta = self._entity_has_payload_meta(entity_id)
			richness = self._entity_meta_richness(entity_id)
			ma_hint = _has_music_assistant_hint(entity_id)
			sparse_transport = _is_sparse_transport_meta(entity_id)
			transport_mirror = _looks_transport_mirror(entity_id)
			fresh = bool(signal.get("fresh_play_signal", False))
			recent_play_progress = bool(signal.get("recent_play_progress", False))
			playing_without_fresh = bool(signal.get("playing_without_fresh_signal", False))
			stuck_at_track_end = bool(signal.get("playing_at_track_end_stuck", False))

			reasons: list[str] = []
			if state_norm in {"unknown", "unavailable", "off", "standby"}:
				reasons.append("inactive_state")
			if stuck_at_track_end:
				reasons.append("stuck_track_end")
			if playing_without_fresh and not has_meta:
				reasons.append("playing_without_fresh_no_meta")

			has_track_identity_meta = self._entity_has_track_identity_meta(entity_id)
			is_ma_rich = (
				ma_hint
				and has_track_identity_meta
				and richness >= 70
				and state_norm in {"playing", "paused"}
			)
			if is_ma_rich and (fresh or recent_play_progress):
				ma_rich_active_exists = True

			if sparse_transport and ma_rich_active_exists:
				reasons.append("sparse_transport_blocked_by_ma_rich")

			pool = "fallback_any"
			pool_rank = 5
			if is_ma_rich and fresh:
				pool = "ma_rich_fresh"
				pool_rank = 0
			elif is_ma_rich:
				pool = "ma_rich_active"
				pool_rank = 1
			elif entity_id == active_target and fresh and has_meta:
				pool = "transport_fresh_meta"
				pool_rank = 2
			elif entity_id == active_target and fresh:
				pool = "transport_fresh"
				pool_rank = 3
			elif has_meta:
				pool = "fallback_meta"
				pool_rank = 4

			if passthrough_source_detected and has_track_identity_meta and state_norm in {"playing", "paused"}:
				pool = "passthrough_meta_lock"
				pool_rank = -1

			eligible = len(reasons) == 0
			row = {
				"entity": entity_id,
				"source": source,
				"state": state_norm,
				"eligible": eligible,
				"pool": pool,
				"pool_rank": pool_rank,
				"fresh": fresh,
				"recent_play_progress": recent_play_progress,
				"has_meta": has_meta,
				"has_track_identity_meta": has_track_identity_meta,
				"meta_richness": richness,
				"ma_hint": ma_hint,
				"sparse_transport": sparse_transport,
				"transport_mirror": transport_mirror,
				"reasons": reasons,
			}
			candidate_rows.append(row)
			if eligible:
				eligible_rows.append(row)

		# Apply hard sparse-transport override after global MA-rich presence is known.
		if ma_rich_active_exists:
			for row in candidate_rows:
				if row.get("eligible") and bool(row.get("sparse_transport", False)):
					row_reasons = row.get("reasons", []) if isinstance(row.get("reasons", []), list) else []
					if "sparse_transport_blocked_by_ma_rich" not in row_reasons:
						row_reasons.append("sparse_transport_blocked_by_ma_rich")
					row["reasons"] = row_reasons
					row["eligible"] = False
			eligible_rows = [row for row in candidate_rows if bool(row.get("eligible", False))]

		winner = ""
		winner_source = "unresolved"
		winner_pool = "none"
		winner_reason = "no_eligible_candidate"

		best_row = pick_now_playing_candidate(
			eligible_rows=eligible_rows,
			passthrough_source_detected=passthrough_source_detected,
			source_rank=source_rank,
		)
		if isinstance(best_row, dict):
			winner = str(best_row.get("entity", "") or "")
			winner_source = str(best_row.get("source", "") or "")
			winner_pool = str(best_row.get("pool", "") or "")
			winner_reason = "deterministic_pool_ranking"
			expected_idle_selector_posture = (
				winner_pool == "fallback_any"
				and str(best_row.get("state", "") or "")
				in {"idle", "off", "stopped", "standby", "unknown", "unavailable"}
				and not bool(best_row.get("has_meta", False))
				and not bool(best_row.get("fresh", False))
			)
			if expected_idle_selector_posture:
				winner_pool = "idle_expected"
				winner_reason = "idle_no_payload_expected_target_hold"

		telemetry = {
			"winner_entity": winner,
			"winner_source": winner_source,
			"winner_pool": winner_pool,
			"winner_reason": winner_reason,
			"expected_idle_selector_posture": bool(
				winner_pool == "idle_expected" and winner_reason == "idle_no_payload_expected_target_hold"
			),
			"ma_rich_active_exists": ma_rich_active_exists,
			"candidate_count": len(candidate_rows),
			"eligible_count": len(eligible_rows),
			"candidates": candidate_rows,
		}

		if winner:
			lock_now = datetime.now(UTC).timestamp()
			lock = self._selector_lock if isinstance(self._selector_lock, dict) else {}
			locked_entity = str(lock.get("entity", "") or "").strip()
			lock_active = False
			lock_release_reason = ""

			if c._is_resolved_state(locked_entity):
				locked_state_obj = c.hass.states.get(locked_entity)
				if locked_state_obj is None:
					lock_release_reason = "missing_locked_entity"
				else:
					locked_state = c._normalize_state(str(locked_state_obj.state or ""))
					locked_title = str(locked_state_obj.attributes.get("media_title", "") or "").strip()
					locked_duration = locked_state_obj.attributes.get("media_duration")
					locked_position = locked_state_obj.attributes.get("media_position")
					previous_locked_position = lock.get("last_position")
					if locked_state in {"idle", "off", "standby", "unknown", "unavailable"}:
						lock_release_reason = "stop_override"
					elif (
						isinstance(locked_position, (int, float))
						and isinstance(previous_locked_position, (int, float))
						and abs(float(locked_position) - float(previous_locked_position)) >= 30.0
					):
						lock_release_reason = "shuttle_override"
					elif not bool(locked_title) or not (
						isinstance(locked_duration, (int, float)) and float(locked_duration) > 0.0
					):
						lock_release_reason = "lock_contract_invalid"
					elif (lock_now - float(lock.get("locked_at", 0.0) or 0.0)) > 180.0:
						lock_release_reason = "lock_ttl_expired"
					else:
						lock_active = True
						lock["last_position"] = (
							float(locked_position)
							if isinstance(locked_position, (int, float))
							else lock.get("last_position")
						)
						self._selector_lock = lock

			if lock_active and locked_entity and locked_entity != winner:
				winner = locked_entity
				winner_source = "selector_lock_hold"
				winner_pool = "locked"
				winner_reason = "selector_lock_hold"

			winner_state_obj = c.hass.states.get(winner)
			if winner_state_obj is not None:
				winner_state = c._normalize_state(str(winner_state_obj.state or ""))
				winner_title = str(winner_state_obj.attributes.get("media_title", "") or "").strip()
				winner_duration = winner_state_obj.attributes.get("media_duration")
				winner_position = winner_state_obj.attributes.get("media_position")
				if (
					winner_state in {"playing", "paused"}
					and bool(winner_title)
					and isinstance(winner_duration, (int, float))
					and float(winner_duration) > 0.0
				):
					self._selector_lock = {
						"entity": winner,
						"title": winner_title,
						"duration": float(winner_duration),
						"locked_at": lock_now,
						"last_position": (
							float(winner_position)
							if isinstance(winner_position, (int, float))
							else None
						),
					}
			elif lock_release_reason:
				self._selector_lock = {
					"entity": "",
					"title": "",
					"duration": None,
					"locked_at": 0.0,
					"last_position": None,
				}

			telemetry["selector_lock_active"] = bool(self._selector_lock.get("entity", ""))
			telemetry["selector_lock_entity"] = str(self._selector_lock.get("entity", "") or "")
			telemetry["selector_lock_release_reason"] = lock_release_reason
			return winner, f"{winner_source}_{winner_pool}", telemetry

		for entity_id, source in normalized_candidates:
			if c.hass.states.get(entity_id) is not None:
				state_obj = c.hass.states.get(entity_id)
				state_norm = c._normalize_state(str(state_obj.state or "")) if state_obj is not None else ""
				title = str(state_obj.attributes.get("media_title", "") or "").strip() if state_obj is not None else ""
				artist = str(state_obj.attributes.get("media_artist", "") or "").strip() if state_obj is not None else ""
				album = str(state_obj.attributes.get("media_album_name", "") or "").strip() if state_obj is not None else ""
				has_meta_payload = bool(title or artist or album)
				expected_idle_selector_posture = (
					state_norm in {"idle", "off", "stopped", "standby", "unknown", "unavailable"}
					and not has_meta_payload
				)
				telemetry["winner_entity"] = entity_id
				telemetry["winner_source"] = source
				telemetry["winner_pool"] = "idle_expected" if expected_idle_selector_posture else "fallback_any"
				telemetry["winner_reason"] = (
					"idle_no_payload_expected_target_hold"
					if expected_idle_selector_posture
					else "state_present_fallback"
				)
				telemetry["expected_idle_selector_posture"] = expected_idle_selector_posture
				return entity_id, f"{source}_fallback", telemetry

		return "", "unresolved", telemetry

	def _extract_entity_source_text(self, entity_id: str) -> str:
		c = self._coordinator
		if not c._is_resolved_state(entity_id):
			return ""
		state = c.hass.states.get(entity_id)
		if state is None:
			return ""
		for key in ("source", "source_name", "media_source", "input_source"):
			value = str(state.attributes.get(key, "") or "").strip()
			if value:
				return value
		return ""

	def _is_non_meta_source(self, source_text: str) -> bool:
		normalized = str(source_text or "").strip().lower()
		if not normalized:
			return False
		return any(token in normalized for token in self.NON_META_SOURCE_TOKENS)

	def _discover_passthrough_upstream_meta_candidate(
		self,
		*,
		now_playing_entity: str,
		route_active_target: str,
		route_active_source_continuity: str,
	) -> tuple[str, str, str, str, str, float]:
		"""Deterministically choose an upstream metadata carrier for passthrough source-only windows."""
		c = self._coordinator
		route_state = c.hass.states.get(route_active_target) if c._is_resolved_state(route_active_target) else None
		route_attrs = route_state.attributes if route_state is not None and isinstance(route_state.attributes, dict) else {}

		route_title_hint = str(route_attrs.get("media_title", "") or "").strip().lower()
		route_artist_hint = str(route_attrs.get("media_artist", "") or "").strip().lower()
		route_app_id_hint = str(route_attrs.get("app_id", "") or "").strip().lower()
		route_app_name_hint = str(route_attrs.get("app_name", "") or "").strip().lower()
		route_source_hint = str(route_active_source_continuity or "").strip().lower()
		route_friendly_hint = str(route_attrs.get("friendly_name", "") or "").strip().lower()

		# Hard guard: do not inject cross-device upstream metadata when passthrough
		# route provides no identity anchors. Without at least one route identity hint,
		# upstream selection can pin stale song titles from unrelated players.
		has_route_identity_hint = bool(
			route_title_hint
			or route_artist_hint
			or route_app_id_hint
			or route_app_name_hint
		)
		if not has_route_identity_hint:
			return "", "", "", "", "", -1.0

		anchor_tokens: set[str] = set()
		for token in str(route_active_target or "").lower().replace(".", "_").split("_"):
			token_norm = token.strip()
			if len(token_norm) >= 4 and token_norm not in {"media", "player", "component", "shadow", "spectra"}:
				anchor_tokens.add(token_norm)
		for token in route_friendly_hint.replace("-", " ").replace("_", " ").split():
			token_norm = token.strip()
			if len(token_norm) >= 4:
				anchor_tokens.add(token_norm)

		best_entity = ""
		best_title = ""
		best_artist = ""
		best_app = ""
		best_reason = ""
		best_score = -1.0

		now_ts_local = datetime.now(UTC).timestamp()
		for state_obj in c.hass.states.async_all("media_player"):
			entity_id = str(getattr(state_obj, "entity_id", "") or "").strip()
			if not c._is_resolved_state(entity_id):
				continue
			if entity_id == now_playing_entity:
				continue

			state_norm = c._normalize_state(str(getattr(state_obj, "state", "") or ""))
			if state_norm not in {"playing", "paused", "buffering"}:
				continue

			title = str(state_obj.attributes.get("media_title", "") or "").strip()
			artist = str(state_obj.attributes.get("media_artist", "") or "").strip()
			if not (title or artist):
				continue

			app_name = str(state_obj.attributes.get("app_name", "") or "").strip()
			app_id = str(state_obj.attributes.get("app_id", "") or "").strip()
			source = str(state_obj.attributes.get("source", "") or "").strip()
			source_lower = source.lower()
			if self._is_non_meta_source(source) and not (app_name or app_id):
				continue

			age_s = c._timestamp_age_seconds(state_obj.last_updated)
			if age_s is None:
				age_s = 1_000_000.0
			if state_norm == "playing" and age_s > 1800.0:
				continue
			if state_norm in {"paused", "buffering"} and age_s > 7200.0:
				continue

			signal = self._build_now_playing_signal(entity_id)
			if bool(signal.get("long_idle_stale_hidden", False)):
				continue

			entity_lower = entity_id.lower()
			friendly_lower = str(state_obj.attributes.get("friendly_name", "") or "").strip().lower()
			title_lower = title.lower()
			artist_lower = artist.lower()
			app_name_lower = app_name.lower()
			app_id_lower = app_id.lower()

			title_match = bool(route_title_hint and title_lower == route_title_hint)
			artist_match = bool(route_artist_hint and artist_lower == route_artist_hint)
			app_match = bool(
				(route_app_id_hint and app_id_lower == route_app_id_hint)
				or (route_app_name_hint and app_name_lower == route_app_name_hint)
			)
			source_affinity = bool(route_source_hint and route_source_hint in source_lower)
			anchor_match = any(token in entity_lower or token in friendly_lower for token in anchor_tokens)

			score = 0.0
			score += 420.0 if state_norm == "playing" else (280.0 if state_norm == "buffering" else 200.0)
			score += float(self._entity_meta_richness(entity_id))
			score += max(0.0, 180.0 - min(age_s, 180.0))
			score += 160.0 if bool(signal.get("fresh_play_signal", False)) else 0.0
			score += 60.0 if bool(signal.get("recent_play_progress", False)) else 0.0
			score += 30.0 if bool(signal.get("recent_paused_progress", False)) else 0.0
			score -= 120.0 if bool(signal.get("playing_without_fresh_signal", False)) else 0.0
			score += 120.0 if title_match else 0.0
			score += 80.0 if artist_match else 0.0
			score += 50.0 if app_match else 0.0
			score += 20.0 if source_affinity else 0.0
			score += 15.0 if anchor_match else 0.0
			score += 10.0 if (title and artist) else 0.0

			if score > best_score:
				best_score = score
				best_entity = entity_id
				best_title = title
				best_artist = artist
				best_app = app_name or app_id
				best_reason = "deterministic_passthrough_upstream_rank"

		if best_score <= 0.0:
			return "", "", "", "", "", -1.0
		return best_entity, best_title, best_artist, best_app, best_reason, round(best_score, 1)

	def build_metadata_prep_validation(
		self,
		*,
		route_trace: dict[str, Any],
		contract_validation: dict[str, Any],
	) -> dict[str, Any]:
		c = self._coordinator
		component_mode_active = c._write_authority_mode == WRITE_AUTH_COMPONENT
		required_entities = {
			"active_meta_entity": LEGACY_ACTIVE_META_ENTITY,
			"now_playing_entity": LEGACY_NOW_PLAYING_ENTITY,
			"now_playing_state": LEGACY_NOW_PLAYING_STATE,
			"now_playing_title": LEGACY_NOW_PLAYING_TITLE,
			"now_playing_position": LEGACY_NOW_PLAYING_POSITION,
			"now_playing_duration": LEGACY_NOW_PLAYING_DURATION,
			"ma_active_duration": LEGACY_ACTIVE_DURATION,
			"meta_candidates": LEGACY_META_CANDIDATES,
			"now_playing_media_class": LEGACY_NOW_PLAYING_MEDIA_CLASS,
			"now_playing_display_allowed": LEGACY_NOW_PLAYING_DISPLAY_ALLOWED,
		}

		missing_required = [
			key for key, entity_id in required_entities.items() if c.hass.states.get(entity_id) is None
		]
		effective_missing_required = [] if component_mode_active else list(missing_required)

		scaffolds = c._build_component_scaffolds()
		resolver_plan = (
			scaffolds.get("metadata_resolver_plan", {})
			if isinstance(scaffolds.get("metadata_resolver_plan", {}), dict)
			else {}
		)
		resolver_selected_meta_entity = str(
			resolver_plan.get("selected_meta_entity", "") or ""
		).strip()
		resolver_best_candidate = str(resolver_plan.get("best_candidate", "") or "").strip()
		resolver_detected_candidate = str(resolver_plan.get("detected_candidate", "") or "").strip()

		active_meta_raw = c.hass.states.get(LEGACY_ACTIVE_META_ENTITY)
		now_playing_entity_raw = c.hass.states.get(LEGACY_NOW_PLAYING_ENTITY)
		now_playing_state_raw = c.hass.states.get(LEGACY_NOW_PLAYING_STATE)
		now_playing_title_raw = c.hass.states.get(LEGACY_NOW_PLAYING_TITLE)
		now_playing_position_raw = c.hass.states.get(LEGACY_NOW_PLAYING_POSITION)
		now_playing_duration_raw = c.hass.states.get(LEGACY_NOW_PLAYING_DURATION)
		ma_active_duration_raw = c.hass.states.get(LEGACY_ACTIVE_DURATION)
		now_playing_media_class_raw = c.hass.states.get(LEGACY_NOW_PLAYING_MEDIA_CLASS)
		now_playing_preview_key_raw = c.hass.states.get(LEGACY_NOW_PLAYING_PREVIEW_KEY)
		now_playing_display_allowed_raw = c.hass.states.get(LEGACY_NOW_PLAYING_DISPLAY_ALLOWED)

		active_meta_entity = active_meta_raw.state if active_meta_raw is not None else "missing"
		legacy_now_playing_entity = now_playing_entity_raw.state if now_playing_entity_raw is not None else "missing"

		route_active_target = str(route_trace.get("active_target", "") or "").strip()
		route_active_target_state = c.hass.states.get(route_active_target) if c._is_resolved_state(route_active_target) else None
		route_active_target_friendly = str(
			route_active_target_state.attributes.get("friendly_name", "")
			if route_active_target_state is not None
			else ""
		).strip()
		route_active_source = self._extract_entity_source_text(route_active_target)
		route_active_source_continuity = route_active_source
		passthrough_source_detected = self._is_non_meta_source(route_active_source)

		(
			component_now_playing_entity,
			component_now_playing_entity_source,
			component_now_playing_selection,
		) = self._select_component_now_playing_entity(
			route_trace=route_trace,
			active_meta_entity=active_meta_entity,
			legacy_now_playing_entity=legacy_now_playing_entity,
			resolver_selected_meta_entity=resolver_selected_meta_entity,
			resolver_best_candidate=resolver_best_candidate,
			resolver_detected_candidate=resolver_detected_candidate,
			passthrough_source_detected=passthrough_source_detected,
		)
		now_playing_entity = component_now_playing_entity or legacy_now_playing_entity
		now_playing_state = now_playing_state_raw.state if now_playing_state_raw is not None else "missing"
		transport_now_playing_state = str(now_playing_state or "").strip()
		now_playing_title = now_playing_title_raw.state if now_playing_title_raw is not None else "missing"
		now_playing_position = now_playing_position_raw.state if now_playing_position_raw is not None else "missing"
		now_playing_duration = now_playing_duration_raw.state if now_playing_duration_raw is not None else "missing"
		now_playing_artist = ""
		now_playing_album = ""
		now_playing_source = ""
		selected_state_obj = c.hass.states.get(now_playing_entity) if c._is_resolved_state(now_playing_entity) else None
		passthrough_metadata_promoted = False
		passthrough_album_suppressed = False
		passthrough_device_label_preferred = False
		passthrough_route_target_label_preferred = False
		passthrough_source_label_fallback_preferred = False
		passthrough_route_target_position_fallback_used = False
		passthrough_route_target_duration_fallback_used = False
		passthrough_metadata_candidate_position_fallback_used = False
		passthrough_metadata_candidate_duration_fallback_used = False
		passthrough_upstream_meta_fallback_used = False
		passthrough_no_track_source_continuity_preferred = False
		passthrough_upstream_meta_entity = ""
		passthrough_upstream_meta_reason = ""
		passthrough_upstream_meta_score: float | None = None
		passthrough_stale_carryover_cleared = False
		allow_passthrough_upstream_meta_rescue = False
		global_active_metadata_rescue_used = False
		progress_clock_cache_reused = False
		progress_clock_cache_cross_entity_reused = False
		progress_clock_cache_age_s: float | None = None

		selected_state_norm_initial = (
			c._normalize_state(str(selected_state_obj.state or ""))
			if selected_state_obj is not None
			else ""
		)
		selection_winner_pool = str(
			component_now_playing_selection.get("winner_pool", "")
			if isinstance(component_now_playing_selection, dict)
			else ""
		)
		should_consider_global_metadata_rescue = (
			component_mode_active
			and not c._is_resolved_state(now_playing_title)
			and selected_state_norm_initial in {"", "idle", "off", "standby", "unknown", "unavailable"}
			and selection_winner_pool in {"idle_expected", "fallback_any", "none", ""}
		)
		if should_consider_global_metadata_rescue and allow_passthrough_upstream_meta_rescue:
			(
				fallback_entity,
				fallback_title,
				fallback_artist,
				fallback_app,
				fallback_reason,
				fallback_score,
			) = self._discover_passthrough_upstream_meta_candidate(
				now_playing_entity=now_playing_entity,
				route_active_target=route_active_target,
				route_active_source_continuity=route_active_source_continuity,
			)
			if c._is_resolved_state(fallback_entity) and c._is_resolved_state(fallback_title):
				fallback_state = c.hass.states.get(fallback_entity)
				if fallback_state is not None:
					now_playing_entity = fallback_entity
					component_now_playing_entity_source = "global_active_metadata_rescue"
					selected_state_obj = fallback_state
					now_playing_title = fallback_title
					now_playing_artist = fallback_artist
					if c._is_resolved_state(fallback_app):
						now_playing_app = fallback_app
					global_active_metadata_rescue_used = True
					passthrough_upstream_meta_entity = fallback_entity
					passthrough_upstream_meta_reason = fallback_reason or "global_active_metadata_rescue"
					passthrough_upstream_meta_score = fallback_score
		if passthrough_source_detected:
			selected_title = (
				str(selected_state_obj.attributes.get("media_title", "") or "").strip()
				if selected_state_obj is not None
				else ""
			)
			selected_artist = (
				str(selected_state_obj.attributes.get("media_artist", "") or "").strip()
				if selected_state_obj is not None
				else ""
			)
			if selected_title == "" and selected_artist == "":
				fallback_candidates = [
					(resolver_selected_meta_entity, "resolver_selected_passthrough_metadata"),
					(resolver_best_candidate, "resolver_best_candidate_passthrough_metadata"),
					(resolver_detected_candidate, "resolver_detected_candidate_passthrough_metadata"),
				]
				for fallback_entity, fallback_source in fallback_candidates:
					fallback_entity_norm = str(fallback_entity or "").strip()
					if not c._is_resolved_state(fallback_entity_norm):
						continue
					if fallback_entity_norm == now_playing_entity:
						continue
					fallback_state = c.hass.states.get(fallback_entity_norm)
					if fallback_state is None:
						continue
					fallback_title = str(fallback_state.attributes.get("media_title", "") or "").strip()
					fallback_artist = str(fallback_state.attributes.get("media_artist", "") or "").strip()
					if fallback_title == "" and fallback_artist == "":
						continue
					now_playing_entity = fallback_entity_norm
					component_now_playing_entity_source = fallback_source
					selected_state_obj = fallback_state
					passthrough_metadata_promoted = True
					break
		if selected_state_obj is not None:
			selected_state_norm = str(selected_state_obj.state or "").strip()
			selected_friendly = str(selected_state_obj.attributes.get("friendly_name", "") or "").strip()
			now_playing_state = selected_state_norm or now_playing_state
			if passthrough_metadata_promoted and passthrough_source_detected:
				selected_state_low = c._normalize_state(selected_state_norm)
				transport_state_low = c._normalize_state(transport_now_playing_state)
				if transport_state_low == "playing" and selected_state_low in {
					"",
					"unknown",
					"unavailable",
					"idle",
					"off",
					"standby",
					"paused",
				}:
					now_playing_state = transport_now_playing_state
			selected_title = str(selected_state_obj.attributes.get("media_title", "") or "").strip()
			selected_artist = str(selected_state_obj.attributes.get("media_artist", "") or "").strip()
			if selected_title:
				now_playing_title = selected_title
			now_playing_artist = selected_artist
			now_playing_album = str(selected_state_obj.attributes.get("media_album_name", "") or "").strip()
			now_playing_source = str(selected_state_obj.attributes.get("source", "") or "").strip()
			if passthrough_source_detected and not c._is_resolved_state(now_playing_source):
				now_playing_source = route_active_source_continuity
			now_playing_app = str(
				selected_state_obj.attributes.get("app_name", "")
				or selected_state_obj.attributes.get("app_id", "")
				or ""
			).strip()
			if passthrough_source_detected:
				# In passthrough posture, prevent app-name dominance (e.g. "YouTube")
				# when metadata/app context is sourced from upstream carriers.
				# When no live track metadata exists, prefer source continuity labels
				# over room/device friendly names so OLED does not regress to labels
				# like "Kitchen Speakers" during passthrough source-only windows.
				has_track_identity_meta = bool(now_playing_title or now_playing_artist)
				preferred_device_label = route_active_target_friendly or selected_friendly
				if not has_track_identity_meta:
					preferred_source_label = (
						route_active_source_continuity
						if c._is_resolved_state(route_active_source_continuity)
						else now_playing_source
					)
					if not c._is_resolved_state(preferred_source_label):
						preferred_source_label = preferred_device_label
					if c._is_resolved_state(preferred_source_label):
						now_playing_source = preferred_source_label
						now_playing_app = preferred_source_label
						passthrough_source_label_fallback_preferred = True
						passthrough_no_track_source_continuity_preferred = True
						passthrough_device_label_preferred = (
							preferred_source_label == preferred_device_label
							and bool(preferred_device_label)
						)
						passthrough_route_target_label_preferred = False
				elif preferred_device_label:
					now_playing_app = preferred_device_label
					passthrough_device_label_preferred = True
					passthrough_route_target_label_preferred = bool(route_active_target_friendly)
				elif now_playing_source:
					now_playing_app = now_playing_source
					passthrough_source_label_fallback_preferred = True
			if (
				passthrough_source_detected
				and self._is_non_meta_source(now_playing_source)
				and not passthrough_metadata_promoted
				and bool(now_playing_title)
				and bool(now_playing_album)
				and not bool(now_playing_app)
			):
				# Guard against stale album carryover on passthrough transports.
				# In this posture, title/artist may be live while album can be historical residue
				# from previous queue sessions on the transport entity.
				now_playing_album = ""
				passthrough_album_suppressed = True

			if (
				allow_passthrough_upstream_meta_rescue
				and passthrough_source_detected
				and not c._is_resolved_state(now_playing_title)
			):
				(
					passthrough_hint_entity,
					passthrough_hint_title,
					passthrough_hint_artist,
					passthrough_hint_app,
					passthrough_hint_reason,
					passthrough_hint_score,
				) = self._discover_passthrough_upstream_meta_candidate(
					now_playing_entity=now_playing_entity,
					route_active_target=route_active_target,
					route_active_source_continuity=route_active_source_continuity,
				)
				if c._is_resolved_state(passthrough_hint_title):
					now_playing_title = passthrough_hint_title
					if not c._is_resolved_state(now_playing_artist) and c._is_resolved_state(passthrough_hint_artist):
						now_playing_artist = passthrough_hint_artist
					if not c._is_resolved_state(now_playing_app) and c._is_resolved_state(passthrough_hint_app):
						now_playing_app = passthrough_hint_app
					passthrough_upstream_meta_fallback_used = True
					passthrough_upstream_meta_entity = passthrough_hint_entity
					passthrough_upstream_meta_reason = passthrough_hint_reason
					passthrough_upstream_meta_score = passthrough_hint_score

			# Root-cause guard: in passthrough source-only windows, do not keep
			# legacy/helper-inherited stale track metadata when active selected
			# entity has no live title/artist and no promoted upstream metadata
			# candidate is currently supplying identity.
			selected_has_live_track_identity = bool(selected_title or selected_artist)
			if (
				passthrough_source_detected
				and (not selected_has_live_track_identity)
				and (not passthrough_metadata_promoted)
				and (not passthrough_upstream_meta_fallback_used)
				and (not global_active_metadata_rescue_used)
			):
				now_playing_title = ""
				now_playing_artist = ""
				now_playing_album = ""
				passthrough_stale_carryover_cleared = True
			selected_position = selected_state_obj.attributes.get("media_position")
			if isinstance(selected_position, (int, float)):
				now_playing_position = str(float(selected_position))
			selected_duration = selected_state_obj.attributes.get("media_duration")
			if isinstance(selected_duration, (int, float)) and float(selected_duration) > 0.0:
				now_playing_duration = str(float(selected_duration))

			# Progress continuity rule for passthrough metadata promotion:
			# metadata carriers may provide better title/artist but no transport clock.
			# In that case, keep selected metadata entity while borrowing progress
			# from the active route target (transport owner) when available.
			if passthrough_source_detected and c._is_resolved_state(route_active_target):
				route_target_state_obj = c.hass.states.get(route_active_target)
				if route_target_state_obj is not None:
					if not isinstance(selected_position, (int, float)):
						route_position = route_target_state_obj.attributes.get("media_position")
						if isinstance(route_position, (int, float)):
							now_playing_position = str(float(route_position))
							passthrough_route_target_position_fallback_used = True
					if not isinstance(selected_duration, (int, float)):
						route_duration = route_target_state_obj.attributes.get("media_duration")
						if isinstance(route_duration, (int, float)) and float(route_duration) > 0.0:
							now_playing_duration = str(float(route_duration))
							passthrough_route_target_duration_fallback_used = True

			# Root-cause guard: transport passthrough entities can be playback owners with
			# sparse/invalid duration, while resolver/meta entities hold valid clocks.
			# Keep exported progress contract coherent by filling missing/invalid clocks
			# from metadata-capable candidates in deterministic priority order.
			if passthrough_source_detected:
				position_missing = not isinstance(selected_position, (int, float))
				duration_missing_or_invalid = (
					not isinstance(selected_duration, (int, float))
					or float(selected_duration) <= 0.0
				)
				if position_missing or duration_missing_or_invalid:
					clock_fallback_candidates = [
						resolver_selected_meta_entity,
						resolver_best_candidate,
						resolver_detected_candidate,
						active_meta_entity,
						legacy_now_playing_entity,
					]
					seen_clock_entities: set[str] = set()
					for clock_entity in clock_fallback_candidates:
						clock_entity_norm = str(clock_entity or "").strip()
						if not c._is_resolved_state(clock_entity_norm):
							continue
						if clock_entity_norm in seen_clock_entities:
							continue
						seen_clock_entities.add(clock_entity_norm)
						clock_state = c.hass.states.get(clock_entity_norm)
						if clock_state is None:
							continue

						if position_missing:
							clock_position = clock_state.attributes.get("media_position")
							if isinstance(clock_position, (int, float)):
								now_playing_position = str(float(clock_position))
								position_missing = False
								passthrough_metadata_candidate_position_fallback_used = True

						if duration_missing_or_invalid:
							clock_duration = clock_state.attributes.get("media_duration")
							if isinstance(clock_duration, (int, float)) and float(clock_duration) > 0.0:
								now_playing_duration = str(float(clock_duration))
								duration_missing_or_invalid = False
								passthrough_metadata_candidate_duration_fallback_used = True

						if not position_missing and not duration_missing_or_invalid:
							break
		else:
			now_playing_app = ""
			if passthrough_source_detected:
				now_playing_title = ""
				now_playing_artist = ""
				now_playing_album = ""
				passthrough_stale_carryover_cleared = True
		ma_active_duration = ma_active_duration_raw.state if ma_active_duration_raw is not None else "missing"
		now_playing_media_class = c._normalize_state(
			now_playing_media_class_raw.state if now_playing_media_class_raw is not None else "missing"
		)
		now_playing_preview_key = (
			str(now_playing_preview_key_raw.state if now_playing_preview_key_raw is not None else "").strip()
		)
		now_playing_display_allowed = c._normalize_state(
			now_playing_display_allowed_raw.state if now_playing_display_allowed_raw is not None else "missing"
		)

		component_selection_winner_entity = str(
			component_now_playing_selection.get("winner_entity", "")
			if isinstance(component_now_playing_selection, dict)
			else ""
		).strip()
		component_selection_winner_source = str(
			component_now_playing_selection.get("winner_source", "")
			if isinstance(component_now_playing_selection, dict)
			else ""
		).strip()

		def _selection_text(key: str) -> str:
			if isinstance(component_now_playing_selection, dict):
				return str(component_now_playing_selection.get(key, "") or "")
			return ""

		def _selection_int(key: str) -> int:
			if isinstance(component_now_playing_selection, dict):
				return int(component_now_playing_selection.get(key, 0) or 0)
			return 0

		def _selection_bool(key: str) -> bool:
			if isinstance(component_now_playing_selection, dict):
				return bool(component_now_playing_selection.get(key, False))
			return False

		component_selection_winner_pool = _selection_text("winner_pool")
		component_selection_winner_reason = _selection_text("winner_reason")
		component_selection_ma_rich_active_exists = _selection_bool("ma_rich_active_exists")
		component_selection_eligible_count = _selection_int("eligible_count")
		component_selection_candidate_count = _selection_int("candidate_count")
		component_selection_lock_active = _selection_bool("selector_lock_active")
		component_selection_lock_entity = _selection_text("selector_lock_entity")
		component_selection_lock_release_reason = _selection_text("selector_lock_release_reason")
		active_meta_entity_effective = active_meta_entity
		active_meta_entity_source = "legacy_active_meta_entity"
		if not c._is_resolved_state(active_meta_entity_effective):
			component_meta_candidates = [
				(resolver_selected_meta_entity, "resolver_selected_meta_entity"),
				(resolver_best_candidate, "resolver_best_candidate"),
				(resolver_detected_candidate, "resolver_detected_candidate"),
				(component_selection_winner_entity, f"component_selection_winner:{component_selection_winner_source}"),
				(component_now_playing_entity, "component_now_playing_entity"),
			]
			for candidate_entity, candidate_source in component_meta_candidates:
				candidate_norm = str(candidate_entity or "").strip()
				if c._is_resolved_state(candidate_norm):
					active_meta_entity_effective = candidate_norm
					active_meta_entity_source = candidate_source
					break

		active_meta_entity_resolved = c._is_resolved_state(active_meta_entity_effective)
		now_playing_entity_resolved = c._is_resolved_state(now_playing_entity)
		now_playing_state_resolved = c._is_resolved_state(now_playing_state)
		now_playing_title_resolved = c._is_resolved_state(now_playing_title)
		now_playing_position_resolved = c._is_resolved_state(now_playing_position)
		now_playing_duration_resolved = c._is_resolved_state(now_playing_duration)
		ma_active_duration_resolved = c._is_resolved_state(ma_active_duration)
		now_playing_media_class_resolved = now_playing_media_class in {"music", "none"}
		now_playing_preview_key_resolved = c._is_resolved_state(now_playing_preview_key)
		now_playing_display_allowed_resolved = now_playing_display_allowed in {
			"on",
			"off",
			"true",
			"false",
			"1",
			"0",
			"yes",
			"no",
		}

		now_playing_display_allowed_value = now_playing_display_allowed in {"on", "true", "1", "yes"}
		if component_mode_active:
			if not now_playing_media_class_resolved:
				now_playing_media_class_resolved = True
			if not now_playing_display_allowed_resolved:
				now_playing_display_allowed_resolved = True
		now_playing_preview_age_s = c._timestamp_age_seconds(
			now_playing_preview_key_raw.last_changed if now_playing_preview_key_raw is not None else None
		)
		media_contract_consistent = now_playing_display_allowed_resolved

		route_decision = str(route_trace.get("decision", "") or "")
		route_trace_present = route_decision != ""
		contract_valid = bool(contract_validation.get("valid", False))

		def _to_float(raw_state: str) -> float | None:
			try:
				return float(raw_state)
			except (TypeError, ValueError):
				return None

		now_playing_position_v = _to_float(now_playing_position)
		now_playing_duration_v = _to_float(now_playing_duration)
		ma_active_duration_v = _to_float(ma_active_duration)

		legacy_candidate_payload_ready = self._metadata_candidate_payload_ready()
		component_candidate_payload_ready = (
			(
				isinstance(component_now_playing_selection, dict)
				and component_selection_candidate_count > 0
			)
			or c._is_resolved_state(resolver_selected_meta_entity)
			or c._is_resolved_state(resolver_best_candidate)
			or c._is_resolved_state(resolver_detected_candidate)
		)
		candidate_payload_ready = legacy_candidate_payload_ready or (
			component_mode_active and component_candidate_payload_ready
		)
		now_playing_signal = self._build_now_playing_signal(now_playing_entity)
		active_playback_signal = c._normalize_state(now_playing_state) == "playing" or bool(
			now_playing_signal.get("fresh_play_signal", False)
		)

		# Progress continuity cache: if active playback briefly loses duration while
		# position still advances, reuse the latest valid duration for the same entity.
		now_ts = datetime.now(UTC).timestamp()
		progress_cache_ttl_s = 300.0
		if (
			c._is_resolved_state(now_playing_entity)
			and isinstance(now_playing_position_v, float)
			and now_playing_position_v >= 0.0
			and isinstance(now_playing_duration_v, float)
			and now_playing_duration_v > 0.0
		):
			self._last_progress_clock_cache = {
				"entity": now_playing_entity,
				"title": str(now_playing_title or "").strip(),
				"source": str(now_playing_source or "").strip(),
				"position": now_playing_position_v,
				"duration": now_playing_duration_v,
				"captured_at": now_ts,
			}
		elif (
			active_playback_signal
			and c._is_resolved_state(now_playing_entity)
			and isinstance(now_playing_position_v, float)
			and now_playing_position_v > 0.0
			and (not isinstance(now_playing_duration_v, float) or now_playing_duration_v <= 0.0)
		):
			cache_entity = str(self._last_progress_clock_cache.get("entity", "") or "").strip()
			cache_title = str(self._last_progress_clock_cache.get("title", "") or "").strip()
			cache_source = str(self._last_progress_clock_cache.get("source", "") or "").strip()
			cache_duration = self._last_progress_clock_cache.get("duration")
			cache_captured_at = float(self._last_progress_clock_cache.get("captured_at", 0.0) or 0.0)
			incoming_title = str(now_playing_title or "").strip()
			incoming_source = str(now_playing_source or "").strip()
			continuity_title_ok = bool(cache_title) and (incoming_title == "" or incoming_title == cache_title)
			continuity_source_ok = (cache_source == "") or (incoming_source == "") or (incoming_source == cache_source)
			cross_entity_passthrough_continuity = (
				passthrough_source_detected and continuity_title_ok and continuity_source_ok
			)
			if (
				(cache_entity == now_playing_entity or cross_entity_passthrough_continuity)
				and isinstance(cache_duration, (int, float))
				and float(cache_duration) > 0.0
				and cache_captured_at > 0.0
			):
				age_s = max(0.0, now_ts - cache_captured_at)
				if age_s <= progress_cache_ttl_s:
					now_playing_duration_v = float(cache_duration)
					now_playing_duration = str(now_playing_duration_v)
					progress_clock_cache_reused = True
					progress_clock_cache_cross_entity_reused = (
						cache_entity != now_playing_entity and cross_entity_passthrough_continuity
					)
					progress_clock_cache_age_s = age_s

		# Normalize contract-ready progress fields after cache recovery.
		now_playing_position_resolved = isinstance(now_playing_position_v, float) and now_playing_position_v >= 0.0
		now_playing_duration_resolved = isinstance(now_playing_duration_v, float) and now_playing_duration_v > 0.0
		if not now_playing_duration_resolved:
			now_playing_duration = "missing"
			now_playing_duration_v = None
		passthrough_metadata_cache_reused = False
		cache_age_s: float | None = None
		cache_ttl_s = 240.0
		if active_playback_signal and (now_playing_title or now_playing_artist or now_playing_album):
			cache_title = str(self._last_passthrough_metadata_cache.get("title", "") or "").strip()
			cache_artist = str(self._last_passthrough_metadata_cache.get("artist", "") or "").strip()
			cache_album = str(self._last_passthrough_metadata_cache.get("album", "") or "").strip()
			cache_app = str(self._last_passthrough_metadata_cache.get("app", "") or "").strip()

			incoming_title = str(now_playing_title or "").strip()
			incoming_artist = str(now_playing_artist or "").strip()
			incoming_album = str(now_playing_album or "").strip()
			incoming_app = str(now_playing_app or "").strip()

			if incoming_title and cache_title and incoming_title != cache_title:
				cache_title = incoming_title
				cache_artist = incoming_artist
				cache_album = incoming_album
				cache_app = incoming_app
			else:
				if incoming_title:
					cache_title = incoming_title
				if incoming_artist:
					cache_artist = incoming_artist
				if incoming_album:
					cache_album = incoming_album
				if incoming_app:
					cache_app = incoming_app

			self._last_passthrough_metadata_cache = {
				"title": cache_title,
				"artist": cache_artist,
				"album": cache_album,
				"app": cache_app,
				"captured_at": now_ts,
			}
		elif passthrough_source_detected and active_playback_signal:
			cache_captured_at = float(self._last_passthrough_metadata_cache.get("captured_at", 0.0) or 0.0)
			if cache_captured_at > 0:
				cache_age_s = max(0.0, now_ts - cache_captured_at)
				cache_title = str(self._last_passthrough_metadata_cache.get("title", "") or "").strip()
				cache_artist = str(self._last_passthrough_metadata_cache.get("artist", "") or "").strip()
				cache_album = str(self._last_passthrough_metadata_cache.get("album", "") or "").strip()
				cache_app = str(self._last_passthrough_metadata_cache.get("app", "") or "").strip()
				if cache_age_s <= cache_ttl_s and (cache_title or cache_artist):
					fields_filled = False
					if not now_playing_title and cache_title:
						now_playing_title = cache_title
						fields_filled = True
					if not now_playing_artist and cache_artist:
						now_playing_artist = cache_artist
						fields_filled = True
					if not now_playing_album and cache_album:
						now_playing_album = cache_album
						fields_filled = True
					if not now_playing_app and cache_app:
						now_playing_app = cache_app
						fields_filled = True
					passthrough_metadata_cache_reused = fields_filled
		raw_playing_with_missing_duration_contract = (
			active_playback_signal
			and isinstance(now_playing_position_v, float)
			and now_playing_position_v > 0
			and (not isinstance(now_playing_duration_v, float) or now_playing_duration_v <= 0)
		)
		playing_without_fresh_signal = bool(now_playing_signal.get("playing_without_fresh_signal", False))
		paused_without_fresh_signal = bool(now_playing_signal.get("paused_without_fresh_signal", False))
		long_idle_stale_hidden = bool(now_playing_signal.get("long_idle_stale_hidden", False))
		playing_at_track_end_stuck = bool(now_playing_signal.get("playing_at_track_end_stuck", False))
		now_playing_fresh_play_signal = bool(now_playing_signal.get("fresh_play_signal", False))
		passthrough_context_detected = bool(
			passthrough_source_detected
			or self._is_non_meta_source(now_playing_source)
			or self._is_non_meta_source(route_active_source_continuity)
		)
		now_playing_identity_meta_present = bool(
			c._is_resolved_state(now_playing_title) or c._is_resolved_state(now_playing_artist)
		)
		now_playing_title_signal_ready = now_playing_identity_meta_present
		now_playing_track_metadata_ready = now_playing_identity_meta_present
		passthrough_source_only_no_track = bool(
			passthrough_context_detected
			and not now_playing_track_metadata_ready
		)
		if (not now_playing_title_signal_ready) and (
			playing_without_fresh_signal
			or long_idle_stale_hidden
			or passthrough_source_only_no_track
		):
			now_playing_state = "idle"
			active_playback_signal = False
			now_playing_fresh_play_signal = False
			if passthrough_context_detected:
				now_playing_source = route_active_source_continuity or now_playing_source
			else:
				now_playing_source = ""
				now_playing_app = ""
		now_playing_state_norm = c._normalize_state(now_playing_state)
		now_playing_identity_meta_present = bool(
			c._is_resolved_state(now_playing_title) or c._is_resolved_state(now_playing_artist)
		)
		passthrough_signal_age_s_raw = now_playing_signal.get("position_age_s")
		passthrough_signal_age_s = (
			float(passthrough_signal_age_s_raw)
			if isinstance(passthrough_signal_age_s_raw, (int, float))
			else None
		)
		passthrough_pause_window_s = (
			float(now_playing_signal.get("paused_hide_s", float(META_POLICY_DEFAULTS["paused_hide_s"])))
			if isinstance(now_playing_signal.get("paused_hide_s"), (int, float))
			else float(META_POLICY_DEFAULTS["paused_hide_s"])
		)
		passthrough_contract_source = now_playing_source if c._is_resolved_state(now_playing_source) else route_active_source_continuity
		passthrough_display_contract_ready = (
			passthrough_context_detected
			and c._is_resolved_state(passthrough_contract_source)
			and isinstance(passthrough_signal_age_s, float)
			and passthrough_signal_age_s <= passthrough_pause_window_s
			and now_playing_track_metadata_ready
		)
		passthrough_source_only_max_age_s = min(
			passthrough_pause_window_s,
			float(META_POLICY_DEFAULTS["meta_stale_s"]) * 2.0,
		)
		passthrough_source_only_keepalive_ready = (
			passthrough_context_detected
			and c._is_resolved_state(passthrough_contract_source)
			and isinstance(passthrough_signal_age_s, float)
			and passthrough_signal_age_s <= passthrough_source_only_max_age_s
			and not now_playing_track_metadata_ready
		)
		passthrough_title_keepalive_ready = (
			passthrough_source_detected
			and now_playing_state_norm in {"playing", "paused", "buffering"}
			and now_playing_track_metadata_ready
			and now_playing_identity_meta_present
		)
		component_playback_keepalive_ready = (
			component_mode_active
			and now_playing_state_norm in {"playing", "paused", "buffering"}
			and now_playing_track_metadata_ready
			and now_playing_identity_meta_present
		)
		display_force_off_idle_no_meta = (
			now_playing_state_norm in {"idle", "off", "stopped", "standby", "unknown", "unavailable"}
			and not now_playing_identity_meta_present
			and not passthrough_display_contract_ready
			and not passthrough_source_only_keepalive_ready
		)
		if (
			passthrough_display_contract_ready
			or passthrough_source_only_keepalive_ready
			or passthrough_title_keepalive_ready
			or component_playback_keepalive_ready
		):
			now_playing_display_allowed_value = True
			if passthrough_source_only_keepalive_ready:
				now_playing_source = passthrough_contract_source
				now_playing_app = passthrough_contract_source
			if now_playing_media_class in {"", "none", "unknown", "unavailable"}:
				now_playing_media_class = "music"
		if display_force_off_idle_no_meta:
			if passthrough_source_only_keepalive_ready:
				now_playing_display_allowed_value = True
				now_playing_source = passthrough_contract_source
				now_playing_app = passthrough_contract_source
			else:
				now_playing_display_allowed_value = False
				now_playing_source = ""
				now_playing_app = ""
		passthrough_cutover_timing_override = False
		duration_contract_enforced = not (
			component_mode_active
			and now_playing_title_signal_ready
			and now_playing_fresh_play_signal
			and now_playing_state_norm in {"playing", "paused", "buffering"}
		)
		playing_with_missing_duration_contract = (
			raw_playing_with_missing_duration_contract
			and now_playing_title_signal_ready
			and duration_contract_enforced
		)
		resolved_active_playback_contract = (
			active_playback_signal
			and now_playing_title_resolved
			and now_playing_position_resolved
			and now_playing_duration_resolved
			and isinstance(now_playing_position_v, float)
			and now_playing_position_v >= 0
			and isinstance(now_playing_duration_v, float)
			and now_playing_duration_v > 0
			and not playing_with_missing_duration_contract
		)
		freshness_gate_satisfied = now_playing_fresh_play_signal or resolved_active_playback_contract
		resolver_plan = resolver_plan
		resolver_selected = str(resolver_plan.get("selected_meta_entity", "") or "").strip()
		metadata_authority = self._resolve_metadata_authority_state(
			metadata_prep_ready=(
				contract_valid
				and active_meta_entity_resolved
				and now_playing_entity_resolved
				and now_playing_state_resolved
				and candidate_payload_ready
				and route_trace_present
			),
			resolver_selected=resolver_selected,
		)
		metadata_authority_owner = str(metadata_authority.get("metadata_authority_owner", METADATA_AUTH_OWNER_LEGACY))
		metadata_cutover_active = bool(metadata_authority.get("metadata_cutover_active", False))
		cutover_block_reason = str(metadata_authority.get("cutover_block_reason", METADATA_CUTOVER_BLOCK_NOT_CUT_OVER) or "")
		no_authority_expansion = c._write_authority_mode == WRITE_AUTH_COMPONENT

		# Compatibility aliases: keep deterministic resolved entity IDs when route/selection
		# surfaces are sparse or temporarily emit unresolved placeholder states.
		selected_entity_alias = ""
		for candidate in (now_playing_entity, route_active_target, active_meta_entity):
			candidate_norm = str(candidate or "").strip()
			if c._is_resolved_state(candidate_norm):
				selected_entity_alias = candidate_norm
				break

		route_target_entity_alias = ""
		for candidate in (route_active_target, selected_entity_alias):
			candidate_norm = str(candidate or "").strip()
			if c._is_resolved_state(candidate_norm):
				route_target_entity_alias = candidate_norm
				break

		canonical_control_target = route_target_entity_alias or selected_entity_alias
		canonical_meta_target = (
			active_meta_entity if c._is_resolved_state(active_meta_entity) else selected_entity_alias
		)
		control_target_vs_now_playing_mismatch = (
			c._is_resolved_state(canonical_control_target)
			and c._is_resolved_state(now_playing_entity)
			and not self._entity_ids_match(canonical_control_target, now_playing_entity)
		)
		meta_target_vs_now_playing_mismatch = (
			c._is_resolved_state(canonical_meta_target)
			and c._is_resolved_state(now_playing_entity)
			and not self._entity_ids_match(canonical_meta_target, now_playing_entity)
		)
		intentional_control_metadata_divergence = (
			control_target_vs_now_playing_mismatch
			and metadata_authority_owner == METADATA_AUTH_OWNER_COMPONENT
			and not meta_target_vs_now_playing_mismatch
			and now_playing_state_norm in {"playing", "paused"}
			and now_playing_display_allowed_value
		)
		if intentional_control_metadata_divergence:
			canonical_alignment_state = "intentional_divergence_component_owner"
		elif control_target_vs_now_playing_mismatch or (
			meta_target_vs_now_playing_mismatch
			and metadata_authority_owner == METADATA_AUTH_OWNER_COMPONENT
		):
			canonical_alignment_state = "mismatch"
		else:
			canonical_alignment_state = "aligned"

		if display_force_off_idle_no_meta or not now_playing_display_allowed_value:
			canonical_oled_posture = "display_policy_suppressed"
		elif now_playing_track_metadata_ready:
			canonical_oled_posture = "title_ready"
		elif passthrough_source_detected and (
			now_playing_state_norm in {"playing", "paused"}
			or passthrough_display_contract_ready
			or passthrough_source_only_keepalive_ready
		):
			canonical_oled_posture = "passthrough_no_track_metadata"
		elif freshness_gate_satisfied:
			canonical_oled_posture = "freshness_ready_no_title"
		else:
			canonical_oled_posture = "no_viable_payload"

		canonical_oled_payload_ready = bool(
			now_playing_track_metadata_ready and now_playing_display_allowed_value and not display_force_off_idle_no_meta
		)
		no_payload_idle_posture = now_playing_state_norm in {
			"idle",
			"off",
			"paused",
			"stopped",
			"standby",
			"unknown",
			"unavailable",
		}
		now_playing_oled_blank_contract = bool(
			(
				canonical_oled_posture in {"display_policy_suppressed", "no_viable_payload"}
				or display_force_off_idle_no_meta
			)
			and no_payload_idle_posture
			and not now_playing_track_metadata_ready
			and not passthrough_display_contract_ready
			and not passthrough_source_only_keepalive_ready
			and not now_playing_fresh_play_signal
			and not resolved_active_playback_contract
		)
		now_playing_oled_blank_reason = (
			"idle_no_payload_contract_blank"
			if now_playing_oled_blank_contract
			else "contract_payload_or_freshness_present"
		)
		if intentional_control_metadata_divergence:
			canonical_cause_hint = "intentional_control_target_metadata_divergence_component_owner"
		elif control_target_vs_now_playing_mismatch:
			canonical_cause_hint = "control_target_vs_now_playing_entity_mismatch"
		elif meta_target_vs_now_playing_mismatch and metadata_authority_owner == METADATA_AUTH_OWNER_COMPONENT:
			canonical_cause_hint = "meta_target_mismatch_component_owner_active_meta_vs_now_playing_entity"
		elif canonical_oled_posture == "display_policy_suppressed":
			canonical_cause_hint = "display_policy_suppressed"
		elif canonical_oled_posture == "passthrough_no_track_metadata":
			canonical_cause_hint = "audio_payload_blank_expected_passthrough_no_track_metadata"
		elif canonical_oled_posture == "no_viable_payload":
			canonical_cause_hint = "no_viable_now_playing_contract_fields"
		elif not freshness_gate_satisfied:
			canonical_cause_hint = "metadata_freshness_stale"
		else:
			canonical_cause_hint = "healthy_or_contract_ready"

		authority_gate_results = {
			"ma_api_reachable": bool(contract_valid and route_trace_present),
			"ma_payload_shape_valid": bool(candidate_payload_ready),
			"ma_payload_fresh": bool(freshness_gate_satisfied),
			"ma_identity_confidence": bool(active_meta_entity_resolved and now_playing_entity_resolved),
			"ma_timing_confidence": bool(
				not playing_with_missing_duration_contract
				and (not playing_without_fresh_signal or resolved_active_playback_contract)
				and not playing_at_track_end_stuck
			),
		}
		expected_component_idle_authority_posture = (
			no_authority_expansion
			and cutover_block_reason == METADATA_CUTOVER_BLOCK_PREP_NOT_READY
			and now_playing_state_norm in {"idle", "off", "stopped", "standby", "unknown", "unavailable"}
			and not now_playing_title_signal_ready
			and not freshness_gate_satisfied
		)
		component_authority_contract_healthy = (
			no_authority_expansion
			and authority_gate_results["ma_api_reachable"]
			and authority_gate_results["ma_payload_shape_valid"]
			and authority_gate_results["ma_identity_confidence"]
		)
		authority_mode = (
			FABRIC_AUTH_MODE_PRIMARY
			if (component_authority_contract_healthy or expected_component_idle_authority_posture)
			else FABRIC_AUTH_MODE_DEGRADED_FALLBACK
		)
		authority_reasons: list[str] = []
		if authority_mode == FABRIC_AUTH_MODE_DEGRADED_FALLBACK:
			authority_reasons.append(FABRIC_AUTH_REASON_DEGRADED_ACTIVE)
			if not authority_gate_results["ma_api_reachable"]:
				authority_reasons.append(FABRIC_AUTH_REASON_API_UNREACHABLE)
			if not authority_gate_results["ma_payload_shape_valid"]:
				authority_reasons.append(FABRIC_AUTH_REASON_PAYLOAD_SHAPE_INVALID)
			if not authority_gate_results["ma_payload_fresh"] and not component_authority_contract_healthy:
				authority_reasons.append(FABRIC_AUTH_REASON_PAYLOAD_STALE)

		gate_checks: dict[str, bool] = {
			"contract_valid": contract_valid,
			"active_meta_entity_resolved": active_meta_entity_resolved,
			"active_meta_entity_effective_resolved": c._is_resolved_state(active_meta_entity_effective),
			"active_meta_entity_component_sourced": active_meta_entity_source != "legacy_active_meta_entity",
			"now_playing_entity_resolved": now_playing_entity_resolved,
			"now_playing_state_resolved": now_playing_state_resolved,
			"now_playing_title_signal_ready": now_playing_title_signal_ready,
			"candidate_payload_ready": candidate_payload_ready,
			"legacy_candidate_payload_ready": legacy_candidate_payload_ready,
			"component_candidate_payload_ready": component_candidate_payload_ready,
			"route_trace_present": route_trace_present,
			"no_authority_expansion": no_authority_expansion,
			"now_playing_fresh_play_signal": freshness_gate_satisfied,
			"resolved_active_playback_contract": resolved_active_playback_contract,
			"progress_duration_contract_ready": not playing_with_missing_duration_contract,
		}
		gate_score = sum(1 for ok in gate_checks.values() if ok)
		gate_max = len(gate_checks)
		blocking_reasons: list[str] = []
		if not contract_valid:
			blocking_reasons.append("contract_invalid")
		if len(effective_missing_required) > 0:
			blocking_reasons.append("missing_required_metadata_entities")
		if not active_meta_entity_resolved:
			blocking_reasons.append("active_meta_entity_unresolved")
		if not now_playing_entity_resolved:
			blocking_reasons.append("now_playing_entity_unresolved")
		if not now_playing_state_resolved:
			blocking_reasons.append("now_playing_state_unresolved")
		if not now_playing_position_resolved:
			blocking_reasons.append("now_playing_position_unresolved")
		if not now_playing_duration_resolved and duration_contract_enforced:
			blocking_reasons.append("now_playing_duration_unresolved")
		if not component_mode_active and not ma_active_duration_resolved:
			blocking_reasons.append("ma_active_duration_unresolved")
		if not now_playing_title_signal_ready:
			blocking_reasons.append("now_playing_title_unresolved")
		if not now_playing_media_class_resolved:
			blocking_reasons.append("now_playing_media_class_unresolved")
		if not now_playing_display_allowed_resolved:
			blocking_reasons.append("now_playing_display_allowed_unresolved")
		if not candidate_payload_ready:
			blocking_reasons.append("candidate_payload_not_ready")
		if not route_trace_present:
			blocking_reasons.append("route_trace_missing")
		if not no_authority_expansion:
			blocking_reasons.append("authority_mode_not_component")
		if playing_with_missing_duration_contract:
			blocking_reasons.append("playing_with_missing_duration_contract")
		if (
			playing_without_fresh_signal
			and not resolved_active_playback_contract
			and not playing_at_track_end_stuck
			and now_playing_title_resolved
		):
			blocking_reasons.append("playing_without_recent_progress")
		if playing_at_track_end_stuck and now_playing_title_resolved:
			blocking_reasons.append("playing_stuck_at_track_end")
		elif paused_without_fresh_signal and now_playing_title_resolved:
			blocking_reasons.append("paused_without_recent_progress")
		elif long_idle_stale_hidden and now_playing_title_resolved:
			blocking_reasons.append("long_idle_stale_hidden")
		elif not freshness_gate_satisfied and now_playing_title_resolved:
			blocking_reasons.append("no_fresh_play_signal")
		for token in authority_reasons:
			if token not in blocking_reasons:
				blocking_reasons.append(token)

		verdict = "PASS"
		if len(effective_missing_required) > 0 or not contract_valid:
			verdict = "FAIL"
		elif (
			not active_meta_entity_resolved
			or not now_playing_entity_resolved
			or not now_playing_state_resolved
			or not route_trace_present
		):
			verdict = "FAIL"
		elif not now_playing_media_class_resolved or not now_playing_display_allowed_resolved:
			verdict = "WARN"
		elif not no_authority_expansion:
			verdict = "WARN"
		elif playing_with_missing_duration_contract:
			verdict = "WARN"
		elif playing_at_track_end_stuck and now_playing_title_resolved:
			verdict = "WARN"
		elif (
			playing_without_fresh_signal
			and not resolved_active_playback_contract
			and now_playing_title_resolved
		):
			verdict = "WARN"
		elif paused_without_fresh_signal and now_playing_title_resolved:
			verdict = "WARN"
		elif long_idle_stale_hidden and now_playing_title_resolved:
			verdict = "WARN"
		elif not now_playing_title_signal_ready or not candidate_payload_ready:
			verdict = "WARN"

		return {
			"verdict": verdict,
			"ready_for_metadata_handoff": verdict == "PASS",
			"canonical_summary": {
				"control_target": canonical_control_target,
				"meta_target": canonical_meta_target,
				"now_playing_entity": now_playing_entity,
				"alignment_state": canonical_alignment_state,
				"oled_posture": canonical_oled_posture,
				"oled_payload_ready": canonical_oled_payload_ready,
				"cause_hint": canonical_cause_hint,
			},
			"required_entities": required_entities,
			"missing_required": effective_missing_required,
			"contract_valid": contract_valid,
			"route_decision": route_decision,
			"gate_score": gate_score,
			"gate_max": gate_max,
			"blocking_reasons": blocking_reasons,
			"metadata_authority_owner": metadata_authority_owner,
			"metadata_cutover_active": metadata_cutover_active,
			"cutover_block_reason": cutover_block_reason,
			"authority_mode": authority_mode,
			"authority_gate_results": authority_gate_results,
			"checks": {
				"active_meta_entity_resolved": active_meta_entity_resolved,
				"now_playing_entity_resolved": now_playing_entity_resolved,
				"now_playing_state_resolved": now_playing_state_resolved,
				"now_playing_title_resolved": now_playing_title_resolved,
				"now_playing_position_resolved": now_playing_position_resolved,
				"now_playing_duration_resolved": now_playing_duration_resolved,
				"ma_active_duration_resolved": ma_active_duration_resolved,
				"now_playing_title_signal_ready": now_playing_title_signal_ready,
				"now_playing_track_metadata_ready": now_playing_track_metadata_ready,
				"now_playing_media_class_resolved": now_playing_media_class_resolved,
				"now_playing_preview_key_resolved": now_playing_preview_key_resolved,
				"now_playing_display_allowed_resolved": now_playing_display_allowed_resolved,
				"now_playing_display_contract_consistent": media_contract_consistent,
				"now_playing_display_force_off_idle_no_meta": display_force_off_idle_no_meta,
				"duration_contract_enforced": duration_contract_enforced,
				"passthrough_display_contract_ready": passthrough_display_contract_ready,
				"passthrough_source_only_keepalive_ready": passthrough_source_only_keepalive_ready,
				"passthrough_source_only_max_age_s": passthrough_source_only_max_age_s,
				"passthrough_title_keepalive_ready": passthrough_title_keepalive_ready,
				"component_playback_keepalive_ready": component_playback_keepalive_ready,
				"global_active_metadata_rescue_used": global_active_metadata_rescue_used,
				"candidate_payload_ready": candidate_payload_ready,
				"route_trace_present": route_trace_present,
				"no_authority_expansion": no_authority_expansion,
				"now_playing_fresh_play_signal": now_playing_fresh_play_signal,
				"now_playing_freshness_gate_satisfied": freshness_gate_satisfied,
				"expected_component_idle_authority_posture": expected_component_idle_authority_posture,
				"resolved_active_playback_contract": resolved_active_playback_contract,
				"now_playing_recent_play_progress": now_playing_signal.get("recent_play_progress"),
				"now_playing_recent_paused_progress": now_playing_signal.get("recent_paused_progress"),
				"now_playing_position_change_recent": now_playing_signal.get("position_change_recent", False),
				"now_playing_playing_at_track_end_stuck": playing_at_track_end_stuck,
				"now_playing_playing_without_fresh_signal": playing_without_fresh_signal,
				"now_playing_paused_without_fresh_signal": paused_without_fresh_signal,
				"now_playing_long_idle_stale_hidden": long_idle_stale_hidden,
				"now_playing_suppression_reason": now_playing_signal.get("suppression_reason", ""),
				"component_now_playing_entity_source": component_now_playing_entity_source,
				"component_now_playing_selection_winner_pool": component_selection_winner_pool,
				"component_now_playing_selection_winner_reason": component_selection_winner_reason,
				"component_now_playing_selection_winner_entity": component_selection_winner_entity,
				"component_now_playing_selection_winner_source": component_selection_winner_source,
				"component_now_playing_selection_ma_rich_active_exists": component_selection_ma_rich_active_exists,
				"component_now_playing_selection_eligible_count": component_selection_eligible_count,
				"component_now_playing_selection_candidate_count": component_selection_candidate_count,
				"component_now_playing_selection_lock_active": component_selection_lock_active,
				"component_now_playing_selection_lock_entity": component_selection_lock_entity,
				"component_now_playing_selection_lock_release_reason": component_selection_lock_release_reason,
				"passthrough_source_detected": passthrough_source_detected,
				"route_active_source": route_active_source,
				"resolver_selected_meta_entity_resolved": c._is_resolved_state(resolver_selected_meta_entity),
				"resolver_selected_meta_entity_matches_selected": (
					c._is_resolved_state(resolver_selected_meta_entity)
					and resolver_selected_meta_entity == now_playing_entity
				),
				"resolver_best_candidate_resolved": c._is_resolved_state(resolver_best_candidate),
				"resolver_detected_candidate_resolved": c._is_resolved_state(resolver_detected_candidate),
				"passthrough_metadata_promoted": passthrough_metadata_promoted,
				"passthrough_device_label_preferred": passthrough_device_label_preferred,
				"passthrough_route_target_label_preferred": passthrough_route_target_label_preferred,
				"passthrough_source_label_fallback_preferred": passthrough_source_label_fallback_preferred,
				"passthrough_no_track_source_continuity_preferred": passthrough_no_track_source_continuity_preferred,
				"passthrough_album_suppressed": passthrough_album_suppressed,
				"passthrough_route_target_position_fallback_used": passthrough_route_target_position_fallback_used,
				"passthrough_route_target_duration_fallback_used": passthrough_route_target_duration_fallback_used,
				"passthrough_metadata_candidate_position_fallback_used": passthrough_metadata_candidate_position_fallback_used,
				"passthrough_metadata_candidate_duration_fallback_used": passthrough_metadata_candidate_duration_fallback_used,
				"passthrough_upstream_meta_fallback_used": passthrough_upstream_meta_fallback_used,
				"passthrough_upstream_meta_entity": passthrough_upstream_meta_entity,
				"passthrough_upstream_meta_reason": passthrough_upstream_meta_reason,
				"passthrough_upstream_meta_score": passthrough_upstream_meta_score,
				"progress_clock_cache_reused": progress_clock_cache_reused,
				"progress_clock_cache_cross_entity_reused": progress_clock_cache_cross_entity_reused,
				"progress_clock_cache_age_s": round(progress_clock_cache_age_s, 1)
				if isinstance(progress_clock_cache_age_s, float)
				else None,
				"passthrough_metadata_cache_reused": passthrough_metadata_cache_reused,
				"passthrough_metadata_cache_age_s": round(cache_age_s, 1)
				if isinstance(cache_age_s, float)
				else None,
				"active_playback_signal": active_playback_signal,
				"raw_playing_with_missing_duration_contract": raw_playing_with_missing_duration_contract,
				"passthrough_cutover_timing_override": passthrough_cutover_timing_override,
				"playing_with_missing_duration_contract": playing_with_missing_duration_contract,
				"duration_contract_enforced": duration_contract_enforced,
				"metadata_component_mode_active": bool(metadata_authority.get("component_mode_active", False)),
				"metadata_resolver_candidate_ready": bool(metadata_authority.get("resolver_candidate_ready", False)),
				"metadata_component_cutover_ready": bool(metadata_authority.get("component_cutover_ready", False)),
				"canonical_alignment_aligned": canonical_alignment_state == "aligned",
				"canonical_alignment_intentional_divergence": canonical_alignment_state
				== "intentional_divergence_component_owner",
				"canonical_alignment_mismatch": canonical_alignment_state == "mismatch",
				"canonical_oled_payload_ready": canonical_oled_payload_ready,
				"now_playing_oled_blank_contract": now_playing_oled_blank_contract,
				"now_playing_oled_blank_reason": now_playing_oled_blank_reason,
			},
			"values": {
				"active_meta_entity": active_meta_entity,
				"active_meta_entity_effective": active_meta_entity_effective,
				"active_meta_entity_source": active_meta_entity_source,
				"legacy_now_playing_entity": legacy_now_playing_entity,
				"component_now_playing_entity_source": component_now_playing_entity_source,
				"component_now_playing_selection": component_now_playing_selection,
				"component_now_playing_selection_winner_entity": component_selection_winner_entity,
				"component_now_playing_selection_winner_source": component_selection_winner_source,
				"component_now_playing_selection_winner_pool": component_selection_winner_pool,
				"component_now_playing_selection_winner_reason": component_selection_winner_reason,
				"passthrough_source_detected": passthrough_source_detected,
				"route_active_source": route_active_source,
				"resolver_selected_meta_entity": resolver_selected_meta_entity,
				"resolver_best_candidate": resolver_best_candidate,
				"resolver_detected_candidate": resolver_detected_candidate,
				"passthrough_metadata_promoted": passthrough_metadata_promoted,
				"passthrough_device_label_preferred": passthrough_device_label_preferred,
				"passthrough_route_target_label_preferred": passthrough_route_target_label_preferred,
				"passthrough_source_label_fallback_preferred": passthrough_source_label_fallback_preferred,
				"passthrough_no_track_source_continuity_preferred": passthrough_no_track_source_continuity_preferred,
				"passthrough_album_suppressed": passthrough_album_suppressed,
				"passthrough_route_target_position_fallback_used": passthrough_route_target_position_fallback_used,
				"passthrough_route_target_duration_fallback_used": passthrough_route_target_duration_fallback_used,
				"passthrough_metadata_candidate_position_fallback_used": passthrough_metadata_candidate_position_fallback_used,
				"passthrough_metadata_candidate_duration_fallback_used": passthrough_metadata_candidate_duration_fallback_used,
				"passthrough_upstream_meta_fallback_used": passthrough_upstream_meta_fallback_used,
				"global_active_metadata_rescue_used": global_active_metadata_rescue_used,
				"passthrough_upstream_meta_entity": passthrough_upstream_meta_entity,
				"passthrough_upstream_meta_reason": passthrough_upstream_meta_reason,
				"passthrough_upstream_meta_score": passthrough_upstream_meta_score,
				"progress_clock_cache_reused": progress_clock_cache_reused,
				"progress_clock_cache_cross_entity_reused": progress_clock_cache_cross_entity_reused,
				"progress_clock_cache_age_s": round(progress_clock_cache_age_s, 1)
				if isinstance(progress_clock_cache_age_s, float)
				else None,
				"route_active_target": route_active_target,
				"route_active_target_friendly": route_active_target_friendly,
				# Compatibility aliases for downstream tooling that still expects
				# selection/route naming from older packet shapes.
				"selected_entity": selected_entity_alias,
				"route_target_entity": route_target_entity_alias,
				"canonical_control_target": canonical_control_target,
				"canonical_meta_target": canonical_meta_target,
				"canonical_now_playing_entity": now_playing_entity,
				"canonical_alignment_state": canonical_alignment_state,
				"canonical_oled_posture": canonical_oled_posture,
				"canonical_oled_payload_ready": canonical_oled_payload_ready,
				"now_playing_oled_blank_contract": now_playing_oled_blank_contract,
				"now_playing_oled_blank_reason": now_playing_oled_blank_reason,
				"canonical_cause_hint": canonical_cause_hint,
				"control_target_vs_now_playing_mismatch": control_target_vs_now_playing_mismatch,
				"meta_target_vs_now_playing_mismatch": meta_target_vs_now_playing_mismatch,
				"intentional_control_metadata_divergence": intentional_control_metadata_divergence,
				"passthrough_metadata_cache_reused": passthrough_metadata_cache_reused,
				"passthrough_metadata_cache_age_s": round(cache_age_s, 1)
				if isinstance(cache_age_s, float)
				else None,
				"now_playing_entity": now_playing_entity,
				"now_playing_state": now_playing_state,
				"now_playing_title": now_playing_title,
				"now_playing_artist": now_playing_artist,
				"now_playing_album": now_playing_album,
				"now_playing_source": now_playing_source,
				"now_playing_app": now_playing_app,
				"now_playing_position": now_playing_position_v,
				"now_playing_duration": now_playing_duration_v,
				"ma_active_duration": ma_active_duration_v,
				"now_playing_media_class": now_playing_media_class,
				"now_playing_preview_key": now_playing_preview_key,
				"now_playing_display_allowed": now_playing_display_allowed_value,
				"now_playing_track_metadata_ready": now_playing_track_metadata_ready,
				"now_playing_display_force_off_idle_no_meta": display_force_off_idle_no_meta,
				"passthrough_display_contract_ready": passthrough_display_contract_ready,
				"passthrough_title_keepalive_ready": passthrough_title_keepalive_ready,
				"now_playing_preview_age_s": round(now_playing_preview_age_s, 1)
				if isinstance(now_playing_preview_age_s, float)
				else None,
				"now_playing_position_age_s": now_playing_signal.get("position_age_s"),
				"now_playing_position_age_source": now_playing_signal.get("position_age_source", "missing"),
				"meta_stale_s": now_playing_signal.get("meta_stale_s"),
				"paused_hide_s": now_playing_signal.get("paused_hide_s"),
			},
		}

	async def async_validate_metadata_prep(self) -> None:
		self._coordinator.refresh_snapshot()

	async def async_run_metadata_resolver_scaffold(
		self,
		*,
		dry_run: bool,
		force: bool,
		correlation_id: str | None,
	) -> dict[str, Any]:
		c = self._coordinator
		requested_at = datetime.now(UTC).isoformat()
		corr = (correlation_id or "").strip() or f"meta-resolver-{uuid4().hex[:12]}"

		scaffolds = c._build_component_scaffolds()
		plan = (
			scaffolds.get("metadata_resolver_plan", {})
			if isinstance(scaffolds.get("metadata_resolver_plan", {}), dict)
			else {}
		)

		selected_meta_entity = str(plan.get("selected_meta_entity", "") or "").strip()
		selection_reason = str(plan.get("selection_reason", "no_candidate") or "no_candidate")

		override_active_entity = str(plan.get("override_active_entity", LEGACY_META_OVERRIDE_ACTIVE) or LEGACY_META_OVERRIDE_ACTIVE)
		override_entity_helper = str(plan.get("override_entity_helper", LEGACY_META_OVERRIDE_ENTITY) or LEGACY_META_OVERRIDE_ENTITY)

		override_state = self._component_override_state()
		override_active_exists = True
		override_entity_exists = True

		current_override_active = bool(override_state.get("active", False))
		current_override_entity = str(override_state.get("entity", "") or "").strip()

		result: dict[str, Any] = {
			"status": "pending",
			"reason": "",
			"requested_at": requested_at,
			"completed_at": requested_at,
			"correlation_id": corr,
			"authority_mode": c._write_authority_mode,
			"dry_run": bool(dry_run),
			"force": bool(force),
			"selected_meta_entity": selected_meta_entity,
			"selection_reason": selection_reason,
			"override_active_entity": override_active_entity,
			"override_entity_helper": override_entity_helper,
			"override_active_exists": override_active_exists,
			"override_entity_exists": override_entity_exists,
			"current_override_active": current_override_active,
			"current_override_entity": current_override_entity,
			"meta_resolver_best_candidate": plan.get("best_candidate", ""),
			"meta_resolver_best_score": plan.get("best_score", 0),
			"detected_candidate": plan.get("detected_candidate", ""),
		}

		if selected_meta_entity == "":
			result["status"] = "blocked_no_candidate"
			result["reason"] = "Metadata resolver scaffold has no selected metadata candidate"
		elif c.hass.states.get(selected_meta_entity) is None:
			result["status"] = "blocked_missing_selected_entity"
			result["reason"] = "Selected metadata entity is not currently present in HA state registry"
		else:
			WritePathFabric.apply_standard_write_guards(
				c,
				result,
				force=force,
				dry_run=dry_run,
				authority_required=WRITE_AUTH_COMPONENT,
				authority_block_reason="Write authority is legacy; metadata-resolver scaffold apply is intentionally blocked",
			)

		if result["status"] == "pending" and current_override_active and current_override_entity == selected_meta_entity:
			result["status"] = "noop_already_selected"
			result["reason"] = "Metadata override is already active for the selected metadata entity"

		if result["status"] == "pending" and dry_run:
			result["status"] = "dry_run_ok"
			result["reason"] = "Metadata-resolver scaffold guards passed (dry run)"

		if result["status"] == "pending":
			c._write_in_progress = True
			try:
				self._persist_component_override_state(
					active=True,
					entity=selected_meta_entity,
					source="run_metadata_resolver_scaffold",
				)
				result["status"] = "write_applied"
				result["reason"] = "Metadata-resolver scaffold applied component override state successfully"
			except Exception as err:  # pragma: no cover - defensive runtime guard
				result["status"] = "write_error"
				result["reason"] = "Component override-state update failed during metadata-resolver scaffold apply"
				result["error"] = str(err)
			finally:
				c._write_in_progress = False

		if result["status"] in {"dry_run_ok", "noop_already_selected", "write_applied", "write_error"}:
			WritePathFabric.mark_write_touch(c)

		result["completed_at"] = datetime.now(UTC).isoformat()
		self._last_metadata_resolver_attempt = result
		WritePathFabric.stamp_last_write_attempt(
			c,
			result=result,
			source="run_metadata_resolver_scaffold",
			correlation_id=corr,
			active_target=selected_meta_entity,
		)
		c.refresh_snapshot()
		return result

	async def async_run_metadata_trial_bridge_scaffold(
		self,
		*,
		window_id: str,
		reason: str,
		resolver_dry_run: bool,
		trial_dry_run: bool,
		force: bool,
		expected_target: str | None,
		expected_route: str | None,
		expected_meta_entity: str | None,
		correlation_id: str | None,
	) -> dict[str, Any]:
		c = self._coordinator
		requested_at = datetime.now(UTC).isoformat()
		corr = (correlation_id or "").strip() or f"meta-bridge-{uuid4().hex[:12]}"
		window = (window_id or "").strip() or f"meta-bridge-{uuid4().hex[:8]}"
		operator_reason = (reason or "").strip() or "Metadata trial bridge scaffold"

		def _capture_cutover_proof(stage: str) -> dict[str, Any]:
			snapshot = c.build_snapshot()
			metadata_prep = (
				snapshot.get("metadata_prep_validation", {})
				if isinstance(snapshot.get("metadata_prep_validation", {}), dict)
				else {}
			)
			route_trace = snapshot.get("route_trace", {}) if isinstance(snapshot.get("route_trace", {}), dict) else {}
			return {
				"stage": stage,
				"captured_at": datetime.now(UTC).isoformat(),
				"write_authority_mode": c._write_authority_mode,
				"metadata_authority_owner": str(metadata_prep.get("metadata_authority_owner", "") or ""),
				"metadata_cutover_active": bool(metadata_prep.get("metadata_cutover_active", False)),
				"metadata_ready": bool(metadata_prep.get("ready_for_metadata_handoff", False)),
				"cutover_block_reason": str(metadata_prep.get("cutover_block_reason", "") or ""),
				"authority_mode": str(metadata_prep.get("authority_mode", "") or ""),
				"route_decision": str(route_trace.get("decision", "") or ""),
				"active_target": str(route_trace.get("active_target", "") or ""),
			}

		authority_before = c._write_authority_mode
		result: dict[str, Any] = {
			"status": "pending",
			"reason": "",
			"requested_at": requested_at,
			"completed_at": requested_at,
			"correlation_id": corr,
			"window_id": window,
			"authority_before": authority_before,
			"authority_after": authority_before,
			"resolver_dry_run": bool(resolver_dry_run),
			"trial_dry_run": bool(trial_dry_run),
			"force": bool(force),
			"expected_target": (expected_target or "").strip(),
			"expected_route": (expected_route or "").strip(),
			"expected_meta_entity": (expected_meta_entity or "").strip(),
			"stages": {},
			"cutover_proof": {
				"pre_window": _capture_cutover_proof("pre_window"),
				"in_window": None,
				"post_window": None,
			},
		}

		try:
			if c._write_authority_mode != WRITE_AUTH_COMPONENT:
				await c.async_set_write_authority(
					mode=WRITE_AUTH_COMPONENT,
					reason=f"{operator_reason} (resolver-stage)",
				)
				result["stages"]["set_component_authority"] = "applied"
			else:
				result["stages"]["set_component_authority"] = "noop_already_component"

			pre_window = result.get("cutover_proof", {}).get("pre_window", {}) if isinstance(result.get("cutover_proof", {}), dict) else {}
			pre_target = str(pre_window.get("active_target", "") or "").strip()
			pre_route = str(pre_window.get("route_decision", "") or "").strip()
			expected_target_norm = str(result.get("expected_target", "") or "").strip()
			expected_route_norm = str(result.get("expected_route", "") or "").strip()

			target_window_stable = (
				expected_target_norm != ""
				and expected_target_norm == pre_target
				and (expected_route_norm == "" or expected_route_norm == pre_route)
				and pre_route == "route_linkplay_tcp"
			)

			if target_window_stable:
				result["stages"]["auto_select_scaffold"] = {
					"status": "skipped_expected_target_stable",
					"reason": "Expected target/route already stable; skipping recovery auto-select",
					"selected_target": pre_target,
					"options_synced": False,
				}
			else:
				auto_select_result = await c.async_run_auto_select_scaffold(
					dry_run=False,
					force=True,
					sync_options_if_missing=True,
					include_none=True,
					correlation_id=f"{corr}-auto-select",
				)
				result["stages"]["auto_select_scaffold"] = {
					"status": auto_select_result.get("status", "unknown"),
					"reason": auto_select_result.get("reason", ""),
					"selected_target": auto_select_result.get("selected_target", ""),
					"options_synced": bool(auto_select_result.get("options_synced", False)),
				}

				auto_status = str(auto_select_result.get("status", "") or "")
				if auto_status.startswith("blocked_") or auto_status == "write_error":
					result["cutover_proof"]["in_window"] = _capture_cutover_proof("blocked_target_recovery_stage")
					result["status"] = "blocked_target_recovery_stage"
					result["reason"] = "Automatic control-capable target recovery did not pass guards"
					return result

			resolver_result = await self.async_run_metadata_resolver_scaffold(
				dry_run=resolver_dry_run,
				force=True,
				correlation_id=f"{corr}-resolver",
			)
			result["stages"]["resolver_scaffold"] = {
				"status": resolver_result.get("status", "unknown"),
				"reason": resolver_result.get("reason", ""),
				"selected_meta_entity": resolver_result.get("selected_meta_entity", ""),
			}

			resolver_status = str(resolver_result.get("status", "") or "")
			if resolver_status.startswith("blocked_") or resolver_status == "write_error":
				result["cutover_proof"]["in_window"] = _capture_cutover_proof("blocked_resolver_stage")
				result["status"] = "blocked_resolver_stage"
				result["reason"] = "Resolver scaffold stage did not pass guards"
			else:
				resolver_window = _capture_cutover_proof("post_resolver_stage")
				result["cutover_proof"]["in_window"] = resolver_window
				selected_meta = (expected_meta_entity or "").strip()
				if selected_meta == "":
					selected_meta = str(resolver_result.get("selected_meta_entity", "") or "").strip()

				trial_mode = WRITE_AUTH_COMPONENT
				result["stages"]["trial_authority_mode"] = trial_mode

				if c._write_authority_mode != WRITE_AUTH_COMPONENT:
					await c.async_set_write_authority(
						mode=WRITE_AUTH_COMPONENT,
						reason=f"{operator_reason} (trial-stage)",
					)
					result["stages"]["set_component_authority"] = "applied"
				else:
					result["stages"]["set_component_authority"] = "noop_already_component"

				trial_result = await self.async_metadata_write_trial(
					mode=trial_mode,
					window_id=window,
					reason=f"{operator_reason} (bridge)",
					dry_run=trial_dry_run,
					expected_target=(expected_target or "").strip() or None,
					expected_route=(expected_route or "").strip() or None,
					expected_meta_entity=selected_meta or None,
					correlation_id=f"{corr}-trial",
				)
				result["stages"]["metadata_trial"] = {
					"status": trial_result.get("status", "unknown"),
					"reason": trial_result.get("reason", ""),
					"expected_meta_entity": trial_result.get("expected_meta_entity", ""),
					"observed_active_meta_entity": trial_result.get("observed_active_meta_entity", ""),
				}

				trial_status = str(trial_result.get("status", "") or "")
				if trial_status.startswith("blocked_") or trial_status == "write_error":
					result["cutover_proof"]["in_window"] = _capture_cutover_proof("blocked_trial_stage")
					result["status"] = "blocked_trial_stage"
					result["reason"] = "Metadata trial stage did not pass guards"
				else:
					result["cutover_proof"]["in_window"] = _capture_cutover_proof("post_trial_stage_component")
					result["status"] = "bridge_completed"
					result["reason"] = "Resolver-authority gating and metadata trial bridge completed"
		finally:
			if c._write_authority_mode != authority_before:
				c._write_authority_mode = authority_before
				result.setdefault("stages", {})["restore_authority"] = "restored"
			if isinstance(result.get("cutover_proof", {}), dict):
				result["cutover_proof"]["post_window"] = _capture_cutover_proof("post_window")
			result["authority_after"] = c._write_authority_mode
			result["completed_at"] = datetime.now(UTC).isoformat()
			self._last_metadata_bridge_attempt = result
			WritePathFabric.stamp_last_write_attempt(
				c,
				result=result,
				source="run_metadata_trial_bridge_scaffold",
				correlation_id=corr,
				active_target=str(result.get("expected_meta_entity", "") or ""),
			)
			c.refresh_snapshot()

		return result

	async def async_metadata_write_trial(
		self,
		*,
		mode: str,
		window_id: str,
		reason: str,
		dry_run: bool,
		expected_target: str | None,
		expected_route: str | None,
		expected_meta_entity: str | None = None,
		correlation_id: str | None = None,
	) -> dict[str, Any]:
		c = self._coordinator
		requested_at = datetime.now(UTC).isoformat()
		completed_at = requested_at
		corr = (correlation_id or "").strip() or f"metadata-trial-{uuid4().hex[:12]}"
		requested_mode = c._normalize_write_authority(mode)
		effective_mode = c._write_authority_mode
		window = (window_id or "").strip()
		operator_reason = (reason or "").strip()
		expected_target_norm = (expected_target or "").strip()
		expected_route_norm = (expected_route or "").strip()
		expected_meta_entity_norm = (expected_meta_entity or "").strip()

		snapshot = c.build_snapshot()
		route_trace = snapshot.get("route_trace", {}) if isinstance(snapshot.get("route_trace", {}), dict) else {}
		contract_validation = (
			snapshot.get("contract_validation", {}) if isinstance(snapshot.get("contract_validation", {}), dict) else {}
		)
		metadata_validation = (
			snapshot.get("metadata_prep_validation", {})
			if isinstance(snapshot.get("metadata_prep_validation", {}), dict)
			else {}
		)

		active_target = str(route_trace.get("active_target", "") or "").strip()
		route_decision = str(route_trace.get("decision", "") or "").strip()
		contract_valid = bool(contract_validation.get("valid", False))
		metadata_ready = bool(metadata_validation.get("ready_for_metadata_handoff", False))
		metadata_cutover_active = bool(metadata_validation.get("metadata_cutover_active", False))
		metadata_authority_owner = str(metadata_validation.get("metadata_authority_owner", "") or "")
		active_meta_entity = str(
			c.hass.states.get(LEGACY_ACTIVE_META_ENTITY).state
			if c.hass.states.get(LEGACY_ACTIVE_META_ENTITY) is not None
			else ""
		).strip()
		scaffolds = c._build_component_scaffolds()
		resolver_plan = (
			scaffolds.get("metadata_resolver_plan", {})
			if isinstance(scaffolds.get("metadata_resolver_plan", {}), dict)
			else {}
		)
		scaffold_meta_entity = str(resolver_plan.get("selected_meta_entity", "") or "").strip()
		override_state = self._component_override_state()
		override_active = bool(override_state.get("active", False))
		override_entity = str(override_state.get("entity", "") or "").strip()

		result: dict[str, Any] = {
			"requested_at": requested_at,
			"completed_at": completed_at,
			"window_id": window,
			"requested_mode": requested_mode,
			"effective_mode": effective_mode,
			"dry_run": bool(dry_run),
			"reason": operator_reason,
			"correlation_id": corr,
			"expected_target": expected_target_norm,
			"expected_route": expected_route_norm,
			"expected_meta_entity": expected_meta_entity_norm,
			"active_target": active_target,
			"route_decision": route_decision,
			"observed_active_meta_entity": active_meta_entity,
			"observed_scaffold_meta_entity": scaffold_meta_entity,
			"observed_override_active": override_active,
			"observed_override_entity": override_entity,
			"contract_valid": contract_valid,
			"metadata_ready": metadata_ready,
			"metadata_cutover_active": metadata_cutover_active,
			"metadata_authority_owner": metadata_authority_owner,
			"blocking_reasons": [],
		}

		authority_satisfied = c._write_authority_mode == WRITE_AUTH_COMPONENT or metadata_cutover_active

		if not window:
			result.update(
				{
					"status": "blocked_missing_window_id",
					"reason": "window_id is required for bounded metadata trial auditability",
				}
			)
		elif not operator_reason:
			result.update(
				{
					"status": "blocked_missing_reason",
					"reason": "reason is required for metadata trial auditability",
				}
			)
		elif self._metadata_trial_in_progress:
			result.update(
				{
					"status": "blocked_reentrancy",
					"reason": "A prior metadata trial attempt is still in progress",
				}
			)
		elif not authority_satisfied:
			result.update(
				{
					"status": "blocked_authority_not_satisfied",
					"reason": "Metadata trial requires component authority or active component metadata cutover",
				}
			)
		elif not contract_valid:
			result.update(
				{
					"status": "blocked_contract_invalid",
					"reason": "Required contract entities are missing; fail-closed",
				}
			)
		elif not metadata_ready:
			result.update(
				{
					"status": "blocked_metadata_not_ready",
					"reason": "Metadata prep validation is not PASS/ready; fail-closed",
				}
			)
		elif expected_route_norm and route_decision != expected_route_norm:
			result.update(
				{
					"status": "blocked_expected_route_mismatch",
					"reason": "Observed route decision does not match expected_route",
				}
			)
		elif expected_target_norm and active_target != expected_target_norm:
			result.update(
				{
					"status": "blocked_expected_target_mismatch",
					"reason": "Observed active target does not match expected_target",
				}
			)
		elif expected_meta_entity_norm and expected_meta_entity_norm not in {
			active_meta_entity,
			scaffold_meta_entity,
			(override_entity if override_active else ""),
		}:
			result.update(
				{
					"status": "blocked_expected_meta_mismatch",
					"reason": "Observed metadata resolver surfaces do not match expected_meta_entity",
				}
			)
		elif not dry_run and requested_mode == WRITE_AUTH_COMPONENT and not metadata_cutover_active:
			result.update(
				{
					"status": "blocked_component_mode_without_cutover",
					"reason": "Component-mode non-dry-run metadata trial requires active metadata cutover",
				}
			)
		else:
			self._metadata_trial_in_progress = True
			try:
				if dry_run:
					result.update(
						{
							"status": "dry_run_ok",
							"reason": "Metadata trial contract preflight passed (dry run)",
						}
					)
				else:
					result.update(
						{
							"status": "noop_applied",
							"reason": "Metadata trial contract executed with no write-side effects",
						}
					)
			finally:
				self._metadata_trial_in_progress = False

		result["effective_mode"] = c._write_authority_mode
		result["completed_at"] = datetime.now(UTC).isoformat()

		status = str(result.get("status", "") or "")
		blocking_reasons: list[str] = []
		if status.startswith("blocked_"):
			blocking_reasons.append(status)
		result["blocking_reasons"] = blocking_reasons

		missing_audit_fields = self.metadata_trial_audit_missing_fields(result)
		audit_payload_complete = len(missing_audit_fields) == 0
		result["audit_payload_complete"] = audit_payload_complete
		result["missing_audit_fields"] = missing_audit_fields
		result["audit_payload_state"] = "COMPLETE" if audit_payload_complete else "PARTIAL"

		if status.startswith("blocked_"):
			trial_gate_verdict = "FAIL"
		elif status in {"dry_run_ok", "noop_applied"}:
			trial_gate_verdict = "PASS"
		else:
			trial_gate_verdict = "WARN"
		result["trial_gate_verdict"] = trial_gate_verdict
		result["eligible_for_closeout"] = (
			trial_gate_verdict == "PASS"
			and audit_payload_complete
			and authority_satisfied
		)
		self._last_metadata_trial_attempt = result
		c.refresh_snapshot()
		return result
