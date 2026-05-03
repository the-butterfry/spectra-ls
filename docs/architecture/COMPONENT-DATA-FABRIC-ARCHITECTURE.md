<!-- Description: Component-first canonical playback data-fabric architecture for robust multi-source metadata/progress ownership in Spectra LS. -->
<!-- Version: 2026.05.03.2 -->
<!-- Last updated: 2026-05-03 -->

# Spectra LS Component Data Fabric Architecture (Canonical Playback Contract)

## Why this exists

The current runtime path can produce correct behavior, but it is still distributed across multiple inline contracts and fallback branches. The component path has more flexibility and should own a structured, resilient, field-level canonical model that does **not collapse when one source goes missing**.

This architecture defines that model.

## Core design goals

1. **Field-level resilience**
   - Resolve `position`, `duration`, `state`, `title`, and route signals independently.
   - Never require one entity/source to provide all fields.

2. **Multi-source, evidence-driven resolution**
   - Ingest from multiple providers (MA payload surfaces, HA media entities, runtime helper contracts, optional transport feedback).
   - Resolve by confidence and freshness, not brittle single-ID matching.

3. **Deterministic healing**
   - Keep a last-known-good contract with bounded TTL.
   - Re-resolve continuously when evidence changes; degrade field-by-field, not globally.

4. **First-class provenance**
   - Every canonical field carries source attribution and confidence.
   - Diagnostics must explain *why* each value was selected.

5. **Migration-safe compatibility**
   - Preserve legacy helper/entity surfaces via compatibility projection until cutover gates pass.
   - Component becomes canonical owner, runtime remains rollback-safe baseline.

## Architecture governance contract (plugin-core + MA-first authority)

This section is normative and governs the rest of this document.

### Plugin-core boundaries (required)

- Treat Spectra as a plugin-based platform around one canonical core.
- **Source plugins** ingest evidence and normalize candidate records; they never set canonical fields directly.
- **Subscriber plugins** consume canonical/projection snapshots; they never run source-correlation logic.
- **Core** owns correlation, per-field resolution, policy gating, provenance, health/blockers, and compatibility projection.
- Source-specific quirks stay inside plugins, not in core inline branches.

### MA Authority Contract v1 (normative)

Music Assistant (MA) is the primary authority by default. Spectra adds orchestration/correlation/projection and does not re-implement MA internals.

#### Authority tiers

- Tier 1 (default): `ma_runtime_source` plugin.
- Tier 2 (conditional fallback): protocol plugins (`arylic_transport_source`, `wiim_transport_source`, `chromecast_source`) only when Tier 1 is degraded.
- Tier 3 (last resort): generic HA media scan plugin for continuity-only fill.

#### MA-first field ownership

- MA-authoritative when healthy:
  - `identity.track_key`, `identity.title`, `identity.artist`, `identity.album`
  - `transport.state`
  - `timing.position_s`, `timing.duration_s`
  - `identity.source_app`
- Spectra-policy-owned:
  - `policy.display_allowed`, `policy.suppression_reason`
  - `health.blocking_reasons`, `health.quality_score`
- Fabric route-context owned:
  - `routing.active_target`, `routing.control_host`, `routing.control_path`, `routing.control_capable`

#### MA health gates (all required for MA-primary mode)

- `ma_api_reachable=true`
- `ma_payload_shape_valid=true`
- `ma_payload_fresh_age_s <= ma_freshness_sla`
- `ma_identity_confidence >= ma_identity_floor`
- `ma_timing_confidence >= ma_timing_floor`

#### Fallback and recovery rules

- Enter fallback only if any MA health gate fails for `ma_degrade_grace_s`.
- Fallback is **per-field**, not whole-contract collapse.
- Emit `health.authority_mode=ma_degraded_fallback` with explicit reasons.
- Return to MA-primary only after all gates pass for `ma_recovery_stability_s`.

#### Do-not-reimplement boundaries

- Spectra core must not re-implement MA queue semantics, MA playback state machine internals, MA identity generation, or MA provider enrichment logic.
- Spectra core may perform normalization, cross-plugin correlation, policy gating, projection, and diagnostics attribution.

#### Required authority diagnostics

- `health.authority_mode` (`ma_primary` | `ma_degraded_fallback`)
- `health.authority_gate_results` (per-gate pass/fail + values)
- per-field provenance (`source`, `selected_from_plugin`, `confidence`, `age_s`, `fallback_level`)
- `health.reasons` including at minimum:
  - `ma_degraded_fallback_active`
  - `ma_payload_stale`
  - `ma_payload_shape_invalid`
  - `ma_api_unreachable`

## Non-goals (for this architecture slice)

- No immediate legacy helper/entity retirement.
- No broad runtime rewrite in one change.
- No install-specific hardcoded entity-ID assumptions.

## Canonical model: playback contract object

Component-owned canonical object (`playback_contract.v1`) with required sections:

- `identity`
  - `track_key`, `title`, `artist`, `album`, `source_app`, `source_input`
- `transport`
  - `state`, `playing_signal`, `paused_signal`, `fresh_play_signal`
- `timing`
  - `position_s`, `duration_s`, `position_updated_at`, `at_track_end_stuck`
- `routing`
  - `active_target`, `control_host`, `control_path`, `control_capable`
- `policy`
  - `media_class`, `display_allowed`, `suppression_reason`
- `health`
  - `contract_ready`, `blocking_reasons`, `quality_score`
- `provenance`
  - per-field: `source`, `confidence`, `age_s`, `fallback_level`

## Data fabric pipeline

### 1) Ingestion adapters

Adapters normalize raw evidence into typed candidate records:

- `adapter_ma_players`
  - `sensor.ma_players.result` + MA-derived player fields
- `adapter_ma_active_contract`
  - `sensor.ma_active_*` family
- `adapter_now_playing_contract`
  - `sensor.now_playing_*` family
- `adapter_media_entity_scan`
  - `states.media_player` with MA hints + title/artist correlation
- `adapter_runtime_shadow` (optional)
  - coordinator/diagnostics snapshots when needed for reasoning support

All adapters emit a common shape:

- `candidate_type` (`timing`, `identity`, `transport`, `route`)
- `field`
- `value`
- `source_ref`
- `evidence_time`
- `confidence_base`
- `match_context`

### 2) Correlation layer

Correlate candidates by a durable `track_key` strategy:

- preferred: MA URI / player item key
- fallback: normalized title+artist tuple
- fallback: active target + playback window recency

### 3) Field resolver

Resolve each canonical field independently with weighted scoring:

$$
\text{score} = w_c \cdot \text{confidence} + w_f \cdot \text{freshness} + w_m \cdot \text{match_strength} + w_s \cdot \text{source_priority}
$$

Rules:

- reject stale playing-at-end candidates for active progress clocks,
- permit cross-entity fill (for example duration from MA peer, position from renderer),
- fail-soft to last-known-good within TTL,
- fail-closed to null/0 only when no valid evidence survives.

### 4) Contract health + blockers

Mandatory blocker taxonomy:

- `missing_identity_contract`
- `missing_transport_contract`
- `playing_with_missing_duration_contract`
- `route_unresolved_for_control_expected`
- `policy_render_mismatch`

### 5) Compatibility projection

Project canonical fields to compatibility surfaces while cutover is gated:

- legacy-aligned sensors/helpers remain available,
- component exposes canonical-native surfaces for future consumers,
- parity diagnostics compare canonical vs projected values.

## Component ownership surfaces (target end state)

### Canonical entities

- `sensor.spectra_ls_playback_contract_status`
- `sensor.spectra_ls_playback_contract` (JSON state/attribute payload, bounded)
- `sensor.spectra_ls_playback_progress_position`
- `sensor.spectra_ls_playback_progress_duration`
- `sensor.spectra_ls_playback_title`
- `sensor.spectra_ls_playback_source`

### Diagnostics entities

- `sensor.spectra_ls_playback_contract_quality`
- `sensor.spectra_ls_playback_contract_blockers`
- `sensor.spectra_ls_playback_contract_provenance`

### Services

- `spectra_ls.rebuild_playback_contract`
- `spectra_ls.dump_playback_contract`
- `spectra_ls.validate_playback_contract`
- `spectra_ls.replay_contract_resolution` (diagnostics-only dry run)

## Anti-collapse behavior policy

1. If one source drops fields, keep unaffected fields from other sources.
2. If all live timing sources drop temporarily, hold last-known-good progress briefly (bounded TTL).
3. If correlation confidence drops below threshold, mark low-confidence with explicit blocker; do not pretend healthy.
4. Never erase valid duration/position solely because the active renderer lacks one of them.

## Migration plan (component-first)

### CDF-S01: Canonical model + adapter scaffolding

- Implement typed candidate record model and adapter registry.
- No write-authority expansion.

### CDF-S02: Field-level resolver + provenance

- Implement per-field scoring and confidence/provenance output.
- Add blocker taxonomy and health scoring.

### CDF-S03: Compatibility projection bridge

- Project canonical model to legacy-compatible surfaces.
- Add deterministic parity report between canonical and legacy projections.

### CDF-S04: Contract cutover gate

- Require sustained PASS windows (`playing_with_missing_duration_contract=false` under active playback).
- Keep rollback to legacy runtime authority explicit.
- Host-control authority cutover uses explicit gate packet semantics (`host_control_cutover_gate`) with fail-closed blockers; component-authority scheduler writes are blocked unless gate readiness is true.
- Gate readiness and activation are distinct: `ready_for_cutover` proves parity/path readiness, while `ready_for_authoritative_activation` additionally requires active component authority mode.
- Host-cutover packet contract is service-addressable through `spectra_ls.get_host_cutover_gate` for deterministic automation and closeout evidence capture.

## Risks and mitigations

1. **Correlation false match risk (High)**
   - Mitigation: weighted correlation with confidence floor + explicit low-confidence blocker.
2. **State payload bloat risk (Medium)**
   - Mitigation: bounded JSON payloads and recorder-safe attribute exclusions.
3. **Dual-authority drift risk (High)**
   - Mitigation: single-writer policy unchanged; component canonical owner only after gate acceptance.

## Two-track disposition for this architecture slice

- Runtime track (`packages/` + `esphome/`): compatibility-shimmed (no ownership expansion in this spec slice).
- Component track (`custom_components/spectra_ls/`): implemented as architecture/system-design target, execution queued in CDF slices.

## P1/P2/P3 impact check

- **P1:** no change to read-only parity ownership.
- **P2:** registry/router foundations remain active and are reused as routing evidence inputs.
- **P3:** single-writer authority boundary unchanged; no immediate write-path ownership flip.
