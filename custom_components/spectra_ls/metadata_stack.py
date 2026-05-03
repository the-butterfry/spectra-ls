# Description: Extracted metadata stack workflows for Spectra LS (metadata prep/bridge/cutover validation and metadata trial services).
# Version: 2026.05.03.3
# Last updated: 2026-05-03
# PARITY DIRECTIVE (until full cutover): behavior/contract edits here require same-slice two-track parity review
# and version-metadata review in runtime (`packages/` + `esphome/`) and component (`custom_components/spectra_ls/`) tracks.

from __future__ import annotations

from datetime import UTC, datetime
import json
from time import monotonic
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
	LEGACY_META_DETECTED_ENTITY,
	LEGACY_META_OVERRIDE_ACTIVE,
	LEGACY_META_OVERRIDE_ENTITY,
	LEGACY_META_PAUSED_HIDE_S,
	LEGACY_META_RESOLVER,
	LEGACY_META_STALE_S,
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
	WRITE_AUTH_LEGACY,
)


class MetadataStackWorkflow:
	"""Owns metadata-stack logic extracted from the coordinator."""

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

	def set_last_metadata_bridge_attempt(self, payload: dict[str, Any]) -> None:
		self._last_metadata_bridge_attempt = payload

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
		resolver_selected = str(resolver_plan.get("selected_meta_entity", "") or "").strip()
		resolver_attempt = self._last_metadata_resolver_attempt if isinstance(self._last_metadata_resolver_attempt, dict) else {}
		bridge_attempt = self._last_metadata_bridge_attempt if isinstance(self._last_metadata_bridge_attempt, dict) else {}
		trial_attempt = self._last_metadata_trial_attempt if isinstance(self._last_metadata_trial_attempt, dict) else {}

		resolver_status = str(resolver_attempt.get("status", "never_attempted") or "never_attempted")
		trial_status = str(trial_attempt.get("status", "never_attempted") or "never_attempted")
		bridge_status = str(bridge_attempt.get("status", "never_attempted") or "never_attempted")
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
		trial_authority_legacy = c._write_authority_mode == WRITE_AUTH_LEGACY or bridge_status == "bridge_completed"
		trial_authority_satisfied = trial_authority_legacy or metadata_cutover_active
		resolver_candidate_present = c._is_resolved_state(resolver_selected)
		resolver_stage_ok = resolver_status in {"dry_run_ok", "noop_already_selected", "write_applied"}
		trial_stage_required = not metadata_cutover_active
		trial_stage_ok = trial_status in {"dry_run_ok", "noop_applied"} or not trial_stage_required

		checks = {
			"metadata_prep_ready": metadata_prep_ready,
			"resolver_candidate_present": resolver_candidate_present,
			"trial_authority_legacy": trial_authority_legacy,
			"trial_authority_satisfied": trial_authority_satisfied,
			"resolver_stage_ok": resolver_stage_ok,
			"trial_stage_ok": trial_stage_ok,
			"trial_stage_required": trial_stage_required,
			"metadata_cutover_active": metadata_cutover_active,
			"ma_boot_ready": ma_boot_ready,
		}

		verdict = "PASS"
		if not ma_boot_ready:
			verdict = "WARN"
		elif not metadata_prep_ready or not resolver_candidate_present:
			verdict = "FAIL"
		elif not trial_authority_satisfied:
			verdict = "WARN"
		elif not resolver_stage_ok or not trial_stage_ok:
			verdict = "WARN"

		blocking_reasons: list[str] = []
		if not ma_boot_ready:
			blocking_reasons.append("waiting_for_ma_boot")
		if not metadata_prep_ready:
			blocking_reasons.append("metadata_prep_not_ready")
		if not resolver_candidate_present:
			blocking_reasons.append("resolver_candidate_missing")
		if ma_boot_ready and not trial_authority_satisfied:
			blocking_reasons.append("trial_authority_not_legacy")
		if not resolver_stage_ok and resolver_status != "never_attempted":
			blocking_reasons.append("resolver_stage_not_ok")
		if trial_stage_required and not trial_stage_ok and trial_status != "never_attempted":
			blocking_reasons.append("trial_stage_not_ok")

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

		cutover_proof = bridge_attempt.get("cutover_proof", {}) if isinstance(bridge_attempt.get("cutover_proof", {}), dict) else {}
		pre_window = cutover_proof.get("pre_window") if isinstance(cutover_proof.get("pre_window"), dict) else None
		in_window = cutover_proof.get("in_window") if isinstance(cutover_proof.get("in_window"), dict) else None
		post_window = cutover_proof.get("post_window") if isinstance(cutover_proof.get("post_window"), dict) else None

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

		blocking_reasons: list[str] = []
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
		for key, passed in checks.items():
			if not passed:
				blocking_reasons.append(reason_map[key])

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

		metadata_authority_owner = (
			METADATA_AUTH_OWNER_COMPONENT if metadata_cutover_active else METADATA_AUTH_OWNER_LEGACY
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

	def _build_now_playing_signal(self, entity_id: str) -> dict[str, Any]:
		c = self._coordinator
		if not c._is_resolved_state(entity_id):
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
				"suppression_reason": META_SUPPRESSION_ENTITY_MISSING,
				"meta_stale_s": float(META_POLICY_DEFAULTS["meta_stale_s"]),
				"paused_hide_s": float(META_POLICY_DEFAULTS["paused_hide_s"]),
			}

		state = c.hass.states.get(entity_id)
		if state is None:
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
				"suppression_reason": META_SUPPRESSION_ENTITY_MISSING,
				"meta_stale_s": float(META_POLICY_DEFAULTS["meta_stale_s"]),
				"paused_hide_s": float(META_POLICY_DEFAULTS["paused_hide_s"]),
			}

		state_norm = c._normalize_state(state.state)
		play_state_attr = c._normalize_state(str(state.attributes.get("play_state", "") or ""))
		is_playing_attr = state.attributes.get("is_playing")
		is_paused_attr = state.attributes.get("is_paused")
		pos_age_from_position = c._timestamp_age_seconds(state.attributes.get("media_position_updated_at"))
		pos_age_source = "media_position_updated_at"
		pos_age_s = pos_age_from_position
		if pos_age_s is None:
			pos_age_s = c._timestamp_age_seconds(state.last_changed)
			pos_age_source = "last_changed" if pos_age_s is not None else "missing"

		meta_stale_s_state = c.hass.states.get(LEGACY_META_STALE_S)
		meta_stale_s = float(meta_stale_s_state.state) if (
			meta_stale_s_state is not None
			and meta_stale_s_state.state not in ("", "unknown", "unavailable")
		) else float(META_POLICY_DEFAULTS["meta_stale_s"])
		paused_hide_s_state = c.hass.states.get(LEGACY_META_PAUSED_HIDE_S)
		paused_hide_s = float(paused_hide_s_state.state) if (
			paused_hide_s_state is not None
			and paused_hide_s_state.state not in ("", "unknown", "unavailable")
		) else float(META_POLICY_DEFAULTS["paused_hide_s"])

		recent_play_progress = pos_age_s is not None and pos_age_s <= meta_stale_s
		recent_paused_progress = pos_age_s is not None and pos_age_s <= paused_hide_s
		has_progress_clock = pos_age_s is not None

		media_position = state.attributes.get("media_position")
		media_duration = state.attributes.get("media_duration")
		position_s = float(media_position) if isinstance(media_position, (int, float)) else None
		duration_s = float(media_duration) if isinstance(media_duration, (int, float)) else None

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

		playing_with_fresh_signal = (
			playing_signal
			and not playing_at_track_end_stuck
			and (not has_progress_clock or recent_play_progress)
		)
		playing_without_fresh_signal = (
			playing_signal
			and (
				playing_at_track_end_stuck
				or (has_progress_clock and not recent_play_progress)
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

	def build_metadata_prep_validation(
		self,
		*,
		route_trace: dict[str, Any],
		contract_validation: dict[str, Any],
	) -> dict[str, Any]:
		c = self._coordinator
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
		now_playing_entity = now_playing_entity_raw.state if now_playing_entity_raw is not None else "missing"
		now_playing_state = now_playing_state_raw.state if now_playing_state_raw is not None else "missing"
		now_playing_title = now_playing_title_raw.state if now_playing_title_raw is not None else "missing"
		now_playing_position = now_playing_position_raw.state if now_playing_position_raw is not None else "missing"
		now_playing_duration = now_playing_duration_raw.state if now_playing_duration_raw is not None else "missing"
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

		active_meta_entity_resolved = c._is_resolved_state(active_meta_entity)
		now_playing_entity_resolved = c._is_resolved_state(now_playing_entity)
		now_playing_state_resolved = c._is_resolved_state(now_playing_state)
		now_playing_title_resolved = c._is_resolved_state(now_playing_title)
		now_playing_position_resolved = c._is_resolved_state(now_playing_position)
		now_playing_duration_resolved = c._is_resolved_state(now_playing_duration)
		ma_active_duration_resolved = c._is_resolved_state(ma_active_duration)
		now_playing_media_class_resolved = now_playing_media_class in {"music", "non_music", "none"}
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
		now_playing_preview_age_s = c._timestamp_age_seconds(
			now_playing_preview_key_raw.last_changed if now_playing_preview_key_raw is not None else None
		)
		music_guard_active = False

		expected_display_allowed: bool | None
		if not now_playing_media_class_resolved:
			expected_display_allowed = None
		elif now_playing_media_class == "music":
			expected_display_allowed = True
		else:
			expected_display_allowed = False

		media_contract_consistent = (
			now_playing_display_allowed_resolved
			and expected_display_allowed is not None
			and now_playing_display_allowed_value == expected_display_allowed
		)

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

		candidate_payload_ready = self._metadata_candidate_payload_ready()
		now_playing_signal = self._build_now_playing_signal(now_playing_entity)
		active_playback_signal = c._normalize_state(now_playing_state) == "playing" or bool(
			now_playing_signal.get("fresh_play_signal", False)
		)
		playing_with_missing_duration_contract = (
			active_playback_signal
			and isinstance(now_playing_position_v, float)
			and now_playing_position_v > 0
			and isinstance(now_playing_duration_v, float)
			and now_playing_duration_v <= 0
		)
		playing_without_fresh_signal = bool(now_playing_signal.get("playing_without_fresh_signal", False))
		paused_without_fresh_signal = bool(now_playing_signal.get("paused_without_fresh_signal", False))
		long_idle_stale_hidden = bool(now_playing_signal.get("long_idle_stale_hidden", False))
		playing_at_track_end_stuck = bool(now_playing_signal.get("playing_at_track_end_stuck", False))
		now_playing_fresh_play_signal = bool(now_playing_signal.get("fresh_play_signal", False))
		now_playing_title_signal_ready = now_playing_title_resolved or (
			now_playing_fresh_play_signal and active_meta_entity_resolved
		)
		scaffolds = c._build_component_scaffolds()
		resolver_plan = (
			scaffolds.get("metadata_resolver_plan", {})
			if isinstance(scaffolds.get("metadata_resolver_plan", {}), dict)
			else {}
		)
		resolver_selected = str(resolver_plan.get("selected_meta_entity", "") or "").strip()
		metadata_authority = self._resolve_metadata_authority_state(
			metadata_prep_ready=(
				contract_valid
				and active_meta_entity_resolved
				and now_playing_entity_resolved
				and now_playing_state_resolved
				and now_playing_title_signal_ready
				and candidate_payload_ready
				and route_trace_present
				and now_playing_fresh_play_signal
				and not playing_with_missing_duration_contract
			),
			resolver_selected=resolver_selected,
		)
		metadata_authority_owner = str(metadata_authority.get("metadata_authority_owner", METADATA_AUTH_OWNER_LEGACY))
		metadata_cutover_active = bool(metadata_authority.get("metadata_cutover_active", False))
		cutover_block_reason = str(metadata_authority.get("cutover_block_reason", METADATA_CUTOVER_BLOCK_NOT_CUT_OVER) or "")
		no_authority_expansion = c._write_authority_mode in {WRITE_AUTH_LEGACY, WRITE_AUTH_COMPONENT}

		authority_gate_results = {
			"ma_api_reachable": bool(contract_valid and route_trace_present),
			"ma_payload_shape_valid": bool(candidate_payload_ready),
			"ma_payload_fresh": bool(now_playing_fresh_play_signal),
			"ma_identity_confidence": bool(active_meta_entity_resolved and now_playing_entity_resolved),
			"ma_timing_confidence": bool(
				not playing_with_missing_duration_contract
				and not playing_without_fresh_signal
				and not playing_at_track_end_stuck
			),
		}
		authority_mode = (
			FABRIC_AUTH_MODE_PRIMARY
			if all(bool(value) for value in authority_gate_results.values())
			else FABRIC_AUTH_MODE_DEGRADED_FALLBACK
		)
		authority_reasons: list[str] = []
		if authority_mode == FABRIC_AUTH_MODE_DEGRADED_FALLBACK:
			authority_reasons.append(FABRIC_AUTH_REASON_DEGRADED_ACTIVE)
			if not authority_gate_results["ma_api_reachable"]:
				authority_reasons.append(FABRIC_AUTH_REASON_API_UNREACHABLE)
			if not authority_gate_results["ma_payload_shape_valid"]:
				authority_reasons.append(FABRIC_AUTH_REASON_PAYLOAD_SHAPE_INVALID)
			if not authority_gate_results["ma_payload_fresh"]:
				authority_reasons.append(FABRIC_AUTH_REASON_PAYLOAD_STALE)

		gate_checks: dict[str, bool] = {
			"contract_valid": contract_valid,
			"active_meta_entity_resolved": active_meta_entity_resolved,
			"now_playing_entity_resolved": now_playing_entity_resolved,
			"now_playing_state_resolved": now_playing_state_resolved,
			"now_playing_title_signal_ready": now_playing_title_signal_ready,
			"candidate_payload_ready": candidate_payload_ready,
			"route_trace_present": route_trace_present,
			"no_authority_expansion": no_authority_expansion,
			"now_playing_fresh_play_signal": now_playing_fresh_play_signal,
			"progress_duration_contract_ready": not playing_with_missing_duration_contract,
		}
		gate_score = sum(1 for ok in gate_checks.values() if ok)
		gate_max = len(gate_checks)
		blocking_reasons: list[str] = []
		if not contract_valid:
			blocking_reasons.append("contract_invalid")
		if len(missing_required) > 0:
			blocking_reasons.append("missing_required_metadata_entities")
		if not active_meta_entity_resolved:
			blocking_reasons.append("active_meta_entity_unresolved")
		if not now_playing_entity_resolved:
			blocking_reasons.append("now_playing_entity_unresolved")
		if not now_playing_state_resolved:
			blocking_reasons.append("now_playing_state_unresolved")
		if not now_playing_position_resolved:
			blocking_reasons.append("now_playing_position_unresolved")
		if not now_playing_duration_resolved:
			blocking_reasons.append("now_playing_duration_unresolved")
		if not ma_active_duration_resolved:
			blocking_reasons.append("ma_active_duration_unresolved")
		if not now_playing_title_signal_ready:
			blocking_reasons.append("now_playing_title_unresolved")
		if not now_playing_media_class_resolved:
			blocking_reasons.append("now_playing_media_class_unresolved")
		if not now_playing_display_allowed_resolved:
			blocking_reasons.append("now_playing_display_allowed_unresolved")
		if now_playing_media_class_resolved and not media_contract_consistent:
			blocking_reasons.append("now_playing_display_contract_mismatch")
		if not candidate_payload_ready:
			blocking_reasons.append("candidate_payload_not_ready")
		if not route_trace_present:
			blocking_reasons.append("route_trace_missing")
		if not no_authority_expansion:
			blocking_reasons.append("authority_mode_not_legacy")
		if playing_with_missing_duration_contract:
			blocking_reasons.append("playing_with_missing_duration_contract")
		if playing_without_fresh_signal and not playing_at_track_end_stuck and now_playing_title_resolved:
			blocking_reasons.append("playing_without_recent_progress")
		if playing_at_track_end_stuck and now_playing_title_resolved:
			blocking_reasons.append("playing_stuck_at_track_end")
		elif paused_without_fresh_signal and now_playing_title_resolved:
			blocking_reasons.append("paused_without_recent_progress")
		elif long_idle_stale_hidden and now_playing_title_resolved:
			blocking_reasons.append("long_idle_stale_hidden")
		elif not now_playing_fresh_play_signal and now_playing_title_resolved:
			blocking_reasons.append("no_fresh_play_signal")
		for token in authority_reasons:
			if token not in blocking_reasons:
				blocking_reasons.append(token)

		verdict = "PASS"
		if len(missing_required) > 0 or not contract_valid:
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
		elif not media_contract_consistent:
			verdict = "WARN"
		elif not no_authority_expansion:
			verdict = "WARN"
		elif playing_with_missing_duration_contract:
			verdict = "WARN"
		elif playing_at_track_end_stuck and now_playing_title_resolved:
			verdict = "WARN"
		elif playing_without_fresh_signal and now_playing_title_resolved:
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
			"required_entities": required_entities,
			"missing_required": missing_required,
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
				"now_playing_media_class_resolved": now_playing_media_class_resolved,
				"now_playing_preview_key_resolved": now_playing_preview_key_resolved,
				"now_playing_display_allowed_resolved": now_playing_display_allowed_resolved,
				"now_playing_display_contract_consistent": media_contract_consistent,
				"now_playing_expected_display_allowed": expected_display_allowed,
				"now_playing_music_guard_active": music_guard_active,
				"candidate_payload_ready": candidate_payload_ready,
				"route_trace_present": route_trace_present,
				"no_authority_expansion": no_authority_expansion,
				"now_playing_fresh_play_signal": now_playing_fresh_play_signal,
				"now_playing_recent_play_progress": now_playing_signal.get("recent_play_progress"),
				"now_playing_recent_paused_progress": now_playing_signal.get("recent_paused_progress"),
				"now_playing_playing_at_track_end_stuck": playing_at_track_end_stuck,
				"now_playing_playing_without_fresh_signal": playing_without_fresh_signal,
				"now_playing_paused_without_fresh_signal": paused_without_fresh_signal,
				"now_playing_long_idle_stale_hidden": long_idle_stale_hidden,
				"now_playing_suppression_reason": now_playing_signal.get("suppression_reason", ""),
				"active_playback_signal": active_playback_signal,
				"playing_with_missing_duration_contract": playing_with_missing_duration_contract,
				"metadata_component_mode_active": bool(metadata_authority.get("component_mode_active", False)),
				"metadata_resolver_candidate_ready": bool(metadata_authority.get("resolver_candidate_ready", False)),
				"metadata_component_cutover_ready": bool(metadata_authority.get("component_cutover_ready", False)),
			},
			"values": {
				"active_meta_entity": active_meta_entity,
				"now_playing_entity": now_playing_entity,
				"now_playing_state": now_playing_state,
				"now_playing_title": now_playing_title,
				"now_playing_position": now_playing_position_v,
				"now_playing_duration": now_playing_duration_v,
				"ma_active_duration": ma_active_duration_v,
				"now_playing_media_class": now_playing_media_class,
				"now_playing_preview_key": now_playing_preview_key,
				"now_playing_display_allowed": now_playing_display_allowed_value,
				"now_playing_preview_age_s": round(now_playing_preview_age_s, 1)
				if isinstance(now_playing_preview_age_s, float)
				else None,
				"music_guard_active": music_guard_active,
				"expected_display_allowed": expected_display_allowed,
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

		override_active_state = c.hass.states.get(override_active_entity)
		override_entity_state = c.hass.states.get(override_entity_helper)
		override_active_exists = override_active_state is not None
		override_entity_exists = override_entity_state is not None

		current_override_active = c._normalize_state(override_active_state.state if override_active_state is not None else "") == "on"
		current_override_entity = str(override_entity_state.state if override_entity_state is not None else "").strip()

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
		elif not override_active_exists or not override_entity_exists:
			result["status"] = "blocked_missing_override_helpers"
			result["reason"] = "Metadata override helpers are missing"
		elif c._write_authority_mode != WRITE_AUTH_COMPONENT:
			result["status"] = "blocked_authority"
			result["reason"] = "Write authority is legacy; metadata-resolver scaffold apply is intentionally blocked"
		elif c._write_in_progress and not force:
			result["status"] = "blocked_reentrancy"
			result["reason"] = "A prior write attempt is still in progress"
		elif not force and not dry_run and c._last_write_monotonic > 0:
			elapsed = monotonic() - c._last_write_monotonic
			if elapsed < c._write_debounce_s:
				result["status"] = "blocked_debounce"
				result["reason"] = "Debounce guard active"
				result["elapsed_s"] = round(elapsed, 3)
				result["debounce_s"] = c._write_debounce_s

		if result["status"] == "pending" and current_override_active and current_override_entity == selected_meta_entity:
			result["status"] = "noop_already_selected"
			result["reason"] = "Metadata override is already active for the selected metadata entity"

		if result["status"] == "pending" and dry_run:
			result["status"] = "dry_run_ok"
			result["reason"] = "Metadata-resolver scaffold guards passed (dry run)"

		if result["status"] == "pending":
			c._write_in_progress = True
			try:
				await c.hass.services.async_call(
					"input_text",
					"set_value",
					{
						"entity_id": override_entity_helper,
						"value": selected_meta_entity,
					},
					blocking=True,
				)
				await c.hass.services.async_call(
					"input_boolean",
					"turn_on",
					{
						"entity_id": override_active_entity,
					},
					blocking=True,
				)
				result["status"] = "write_applied"
				result["reason"] = "Metadata-resolver scaffold applied override helper state successfully"
			except Exception as err:  # pragma: no cover - defensive runtime guard
				result["status"] = "write_error"
				result["reason"] = "Service call failed during metadata-resolver scaffold apply"
				result["error"] = str(err)
			finally:
				c._write_in_progress = False

		if result["status"] in {"dry_run_ok", "noop_already_selected", "write_applied", "write_error"}:
			c._last_write_monotonic = monotonic()

		result["completed_at"] = datetime.now(UTC).isoformat()
		self._last_metadata_resolver_attempt = result
		c._last_write_attempt = {
			"status": result.get("status", "unknown"),
			"timestamp": result.get("completed_at"),
			"authority_mode": c._write_authority_mode,
			"reason": result.get("reason", ""),
			"correlation_id": corr,
			"source": "run_metadata_resolver_scaffold",
			"active_target": selected_meta_entity,
		}
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
				result["cutover_proof"]["in_window"] = _capture_cutover_proof("post_resolver_stage")
				selected_meta = (expected_meta_entity or "").strip()
				if selected_meta == "":
					selected_meta = str(resolver_result.get("selected_meta_entity", "") or "").strip()

				if c._write_authority_mode != WRITE_AUTH_LEGACY:
					await c.async_set_write_authority(
						mode=WRITE_AUTH_LEGACY,
						reason=f"{operator_reason} (trial-stage)",
					)
					result["stages"]["set_legacy_authority"] = "applied"
				else:
					result["stages"]["set_legacy_authority"] = "noop_already_legacy"

				trial_result = await self.async_metadata_write_trial(
					mode=WRITE_AUTH_LEGACY,
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
					result["cutover_proof"]["in_window"] = _capture_cutover_proof("post_trial_stage")
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
			c._last_write_attempt = {
				"status": result.get("status", "unknown"),
				"timestamp": result.get("completed_at"),
				"authority_mode": c._write_authority_mode,
				"reason": result.get("reason", ""),
				"correlation_id": corr,
				"source": "run_metadata_trial_bridge_scaffold",
				"active_target": str(result.get("expected_meta_entity", "") or ""),
			}
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
		override_active_state = c.hass.states.get(LEGACY_META_OVERRIDE_ACTIVE)
		override_active = c._normalize_state(override_active_state.state if override_active_state is not None else "") == "on"
		override_entity_state = c.hass.states.get(LEGACY_META_OVERRIDE_ENTITY)
		override_entity = str(override_entity_state.state if override_entity_state is not None else "").strip()

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

		authority_satisfied = c._write_authority_mode == WRITE_AUTH_LEGACY or metadata_cutover_active

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
					"reason": "Metadata trial requires legacy authority or active component metadata cutover",
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
		elif expected_meta_entity_norm:
			meta_matches = expected_meta_entity_norm in {
				active_meta_entity,
				scaffold_meta_entity,
				(override_entity if override_active else ""),
			}
			if not meta_matches:
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
