<!-- Description: Component-first canonical playback data-fabric architecture for robust multi-source metadata/progress ownership in Spectra LS. -->
<!-- Version: 2026.05.05.11 -->
<!-- Last updated: 2026-05-05 -->

# Spectra LS Component Data Fabric Architecture (Canonical Playback Contract)

## Latest implementation note (2026-05-05, CA-S08 closeout validation seal)

- CA-S08 closeout governance is sealed as validated at the board level (`docs/roadmap/v-next-NOTES.md`, `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`) while preserving explicit lane-level LC-06/07/08 retirement/defer execution gates in `docs/roadmap/LEGACY-CODEPATH-CLEANUP-TRACKER.md`.
- Final-seal evidence contract remains authoritative in `docs/program/CA-S08-DOMAIN-CLOSEOUT-ROLLBACK-SEAL-CHECKLIST.md` and `docs/testing/raw/ca_s08_domain_closeout_rollback_seal_validation.jinja`.
- Runtime track disposition remains compatibility-shimmed (rollback-safe baseline explicitly bounded); component track disposition remains implemented (component-first closeout contract remains canonical).
- P1/P2/P3 impact check: no source-of-truth ownership reassignment; closeout state consistency and ledger integrity hardening only.

## Latest implementation note (2026-05-05, Slice-CE)

- Resolver-authority bridge readiness now supports explicit component no-mix startup posture as a valid satisfied state when metadata prep is ready, cutover is active, and component now-playing authority is resolved.
- Handoff inventory metadata resolver lane now classifies as `implemented` from active component-authority readiness (owner/cutover/bridge-satisfaction + resolved component now-playing entity), not only from explicit resolver/trial write-attempt telemetry.
- Legacy resolver surfaces remain compatibility fallback only and are no longer required for component resolver-authority readiness classification in diagnostics.

## CA-S01B canonical contract tables (authority tokens + resolver invariants)

These tables are normative for CA-S01 freeze validation.

### Authority token contract table

| Surface | Allowed values | Required meaning | Fail/degraded handling |
| --- | --- | --- | --- |
| `health.authority_mode` | `ma_primary`, `ma_degraded_fallback` | Primary authority state for canonical playback contract | Any non-allowed value is invalid contract shape |
| `metadata_authority_owner` | `component_contract_surfaces`, `legacy_runtime_compat` | Active metadata write/ownership lane | Non-component owner under CA-S01 active mode must emit explicit blocker reason |
| `health.reasons[*]` | tokenized reason strings | Deterministic degraded attribution | Missing reason tokens on degraded mode is contract-incomplete |

Required degraded tokens (minimum set when degraded):

- `ma_degraded_fallback_active`
- `ma_payload_stale`
- `ma_payload_shape_invalid`
- `ma_api_unreachable`

### Resolver invariant contract table

| Invariant ID | Condition | Required result | Blocker token on violation |
| --- | --- | --- | --- |
| `resolver.inv.01` | metadata prep ready and cutover active with resolved component now-playing entity | Bridge satisfaction may pass under intentional no-mix startup posture | `resolver_candidate_missing` |
| `resolver.inv.02` | resolver stage required | resolver status must be one of `dry_run_ok`, `noop_already_selected`, `write_applied` | `resolver_stage_not_ok` |
| `resolver.inv.03` | resolver stage not required (component no-mix satisfied) | resolver status may be `skipped_component_authority_active` without failure | none (informational skip) |
| `resolver.inv.04` | trial stage required | trial status must be one of `dry_run_ok`, `noop_applied` | `trial_stage_not_ok` |
| `resolver.inv.05` | trial stage not required due active cutover/no-mix satisfaction | no trial failure should be emitted solely for non-attempted stage | none (stage intentionally skipped) |

CA-S01 acceptance rule: contract is freeze-ready only when authority token table and resolver invariants pass with deterministic tokenized reasons for any degraded state.

## CA-S02A resolver determinism scoring contract (matrix + acceptance packet)

This section is normative for CA-S02A execution and acceptance.

### Resolver scoring matrix (deterministic)

Per-candidate score:

$$
S = w_c C + w_f F + w_m M + w_s P
$$

Where:

- $C$: normalized confidence score $[0,1]$
- $F$: normalized freshness score $[0,1]$
- $M$: normalized match-strength score $[0,1]$
- $P$: normalized source-priority score $[0,1]$

Default CA-S02A weights:

| Metric | Symbol | Weight | Notes |
| --- | --- | --- | --- |
| Confidence | $C$ | 0.35 | Contract-shape and field validity confidence |
| Freshness | $F$ | 0.30 | Age/clock recency for candidate evidence |
| Match strength | $M$ | 0.20 | Track/entity correlation quality |
| Source priority | $P$ | 0.15 | Preferred authority/source order |

Weight invariants:

- weights must sum to $1.0$,
- no weight may be negative,
- any weight-set change requires explicit plan-delta logging.

### Deterministic tie-break order

When two candidates have equal $S$ within epsilon (`<= 0.001`), apply this strict order:

1. higher freshness ($F$),
2. higher confidence ($C$),
3. higher source priority ($P$),
4. lexicographically stable `source_ref` ordering.

### Resolver acceptance packet fields (required)

A CA-S02 acceptance packet for resolver determinism must include:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `schema_version` | string | yes | Acceptance packet schema tag |
| `slice_id` | string | yes | Expected `CA-S02A` |
| `parity_stamp` | string | yes | Deterministic run stamp |
| `weights` | object | yes | Active `{confidence,freshness,match_strength,source_priority}` |
| `tie_break_policy` | string | yes | Policy identifier/version |
| `candidate_count` | integer | yes | Number of evaluated candidates |
| `top_candidates` | array | yes | Ranked top set with per-metric breakdown |
| `winner` | object | yes | Selected candidate and total score |
| `winner_provenance` | object | yes | Source + authority context for winner |
| `determinism_replay_hash` | string | yes | Stable hash proving replay-consistent ordering |
| `blocking_reasons` | array | yes | Deterministic blocker list (empty allowed) |
| `runtime_track_disposition` | string | yes | Two-track disposition value |
| `component_track_disposition` | string | yes | Two-track disposition value |

### CA-S02A pass criteria

`CA-S02A` is pass-ready only when all are true:

1. identical candidate input payloads produce identical winner + rank order,
2. acceptance packet contains all required fields,
3. tie-break policy resolves epsilon ties without nondeterministic ordering,
4. blocking reasons are tokenized and stable across replay.

## CA-S02B resolver replay validation contract (checklist + sample packet publication)

This section is normative for CA-S02B execution and acceptance.

### Required CA-S03 artifact

- `docs/program/CA-S02B-RESOLVER-REPLAY-CHECKLIST.md` is the authoritative replay-validation checklist and deterministic sample acceptance packet source for CA-S02B.

### Required replay assertions

For identical `input_payload_hash` and `resolver_config_hash`:

1. winner target must remain stable,
2. ranked ordering must remain stable,
3. score totals must remain stable within epsilon policy,
4. replay hash must remain stable,
5. blocker tokens must remain stable.

### CA-S02B pass criteria

`CA-S02B` is pass-ready only when:

1. checklist-required replay matrix runs are completed,
2. deterministic sample packet schema is published and complete,
3. no unexplained winner/rank/hash drift exists under identical fingerprints,
4. two-track disposition and P1/P2/P3 impact statement are explicit.

## CA-S03 consumer projection cutover contract (templates/diagnostics/sensors)

This section is normative for CA-S03 execution and acceptance.

### Required artifact

- `docs/program/CA-S03-CONSUMER-PROJECTION-CUTOVER-CHECKLIST.md` is the authoritative consumer projection cutover checklist and sample evidence packet source for CA-S03.

### Required projection assertions

For active projection consumers:

1. effective source lane must be emitted per projected field,
2. component-first lane must be preferred when available,
3. runtime fallback use must be counted and reasoned,
4. cutover readiness must be emitted with explicit blocker reasons.

### CA-S03 pass criteria

`CA-S03` is pass-ready only when:

1. projection checklist-required fields and fallback counters are published,
2. consumer output includes deterministic `projection_cutover_ready` posture,
3. fallback usage (if present) is explicit and non-contradictory,
4. two-track disposition and P1/P2/P3 impact statement are explicit.

## CA-S04 runtime write-lane retirement contract (wave-1)

This section is normative for CA-S04 execution and acceptance.

### Required CA-S04 artifact

- `docs/program/CA-S04-RUNTIME-WRITE-LANE-RETIREMENT-CHECKLIST.md` is the authoritative wave-1 runtime write-lane retirement checklist and sample evidence packet source.

### Required wave-1 assertions

For wave-1 lanes (`LC6-L01`, `LC6-L03`, `LC6-L05`):

1. lane readiness must be emitted as `ready|hold|blocked` with explicit reasons,
2. authority and helper-write guard posture must be visible,
3. blocker taxonomy must be tokenized and deterministic,
4. retirement readiness must fail-closed when required signals are missing.

### CA-S04 pass criteria

`CA-S04` is pass-ready only when:

1. all wave-1 lane statuses are published with deterministic reasons,
2. helper writer guard outcomes are visible and non-contradictory,
3. blocker taxonomy is complete and stable,
4. two-track disposition and P1/P2/P3 impact statement are explicit.

## CA-S05 ESP fallback-listener soak contract (LC-07)

This section is normative for CA-S05 execution and acceptance.

### Required CA-S05 artifacts

- `docs/program/CA-S05-ESP-FALLBACK-LISTENER-SOAK-CHECKLIST.md` is the authoritative soak/retirement-gate checklist.
- `docs/testing/raw/ca_s05_esp_fallback_listener_soak_validation.jinja` is the one-screen deterministic validator for readiness/blocker evidence.

### Required LC-07 assertions

For fallback-listener lanes (`ESP-L04`, `ESP-L05`, `ESP-L06`):

1. pre/in/post soak windows must be captured,
2. fallback apply counters must be explicit and deterministic,
3. authority/route posture must remain safe and non-contradictory,
4. contract/parity cleanliness must fail-closed on missing required evidence,
5. retirement recommendation must be derived from blocker taxonomy, not free-form interpretation.

### CA-S05 pass criteria

`CA-S05` is pass-ready only when:

1. at least one complete pre/in/post evidence packet is captured,
2. fallback apply counters remain zero across the packet window,
3. authority/route posture remains safe for supported path operation,
4. blocker taxonomy is complete, deterministic, and empty for READY posture,
5. two-track disposition and P1/P2/P3 impact statement are explicit.

## CA-S06 runtime write/helper retirement contract (wave-2 tails)

This section is normative for CA-S06 execution and acceptance.

### Required CA-S06 artifacts

- `docs/program/CA-S06-RUNTIME-WRITE-HELPER-RETIREMENT-WAVE2-CHECKLIST.md` is the authoritative wave-2 tail-lane checklist.
- `docs/testing/raw/ca_s06_runtime_write_helper_retirement_wave2_validation.jinja` is the one-screen deterministic validator for lane disposition evidence.

### Required wave-2 assertions

For wave-2 tail lanes (`LC6-L01`, `LC6-L03`, `LC6-L06`, `LC6-L02`):

1. each lane must have explicit disposition,
2. retained lanes must be explicitly compatibility-shimmed or deferred-with-rationale,
3. replacement component contract presence must be visible,
4. blocker taxonomy must be deterministic,
5. missing required evidence must fail closed.

### CA-S06 pass criteria

`CA-S06` is pass-ready only when:

1. all target lane dispositions are published and non-contradictory,
2. retained compatibility tails include explicit rationale,
3. component replacement contract surfaces are present for active consumers,
4. blocker taxonomy is complete/stable and empty for READY posture,
5. two-track disposition and P1/P2/P3 impact statement are explicit.

## CA-S07 legacy diagnostics/template fallback cleanup contract (LC-08)

This section is normative for CA-S07 execution and acceptance.

### Required CA-S07 artifacts

- `docs/program/CA-S07-LEGACY-DIAGNOSTICS-TEMPLATE-FALLBACK-CLEANUP-CHECKLIST.md` is the authoritative LC-08 cleanup checklist.
- `docs/testing/raw/ca_s07_legacy_diagnostics_template_fallback_cleanup_validation.jinja` is the one-screen deterministic validator for fallback cleanup readiness.

### Required CA-S07 assertions

For legacy diagnostics/template fallback lanes:

1. component-first consumer surfaces must be verified,
2. legacy fallback references must be inventoried and classified,
3. runtime fallback hits must be explicit and justified when non-zero,
4. blocker taxonomy must be deterministic,
5. missing required evidence must fail closed.

### CA-S07 pass criteria

`CA-S07` is pass-ready only when:

1. required component diagnostics/template surfaces are resolved,
2. legacy fallback inventory is complete and non-contradictory,
3. fallback hits are zero or explicitly bounded with rationale,
4. blocker taxonomy is complete/stable and empty for READY posture,
5. two-track disposition and P1/P2/P3 impact statement are explicit.

## CA-S08 domain closeout + rollback-safe seal contract (LC-06/07/08 final seal)

This section is normative for CA-S08 execution and acceptance.

### Required CA-S08 artifacts

- `docs/program/CA-S08-DOMAIN-CLOSEOUT-ROLLBACK-SEAL-CHECKLIST.md` is the authoritative final closeout checklist.
- `docs/testing/raw/ca_s08_domain_closeout_rollback_seal_validation.jinja` is the one-screen deterministic validator for final-seal readiness.

### Required CA-S08 assertions

For final closeout lanes:

1. LC-06, LC-07, and LC-08 each have explicit final disposition,
2. non-retired lanes include explicit bounded rationale,
3. rollback-safe runtime compatibility posture remains explicit,
4. component-first ownership posture remains explicit and non-contradictory,
5. closure ledger consistency is explicit across changelog, architecture, roadmap boards, and tracker.

### CA-S08 pass criteria

`CA-S08` is pass-ready only when:

1. final dispositions for LC-06/07/08 are present and non-contradictory,
2. rollback-safe posture is explicitly asserted,
3. ledger consistency is clean,
4. blocker taxonomy is complete/stable and empty for READY posture,
5. two-track disposition and P1/P2/P3 impact statement are explicit.

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
  - classification guardrail: when target host resolution is successful and transport compatibility indicates supported Linkplay/TCP routing (including WiiM-discovered targets resolved onto compatible host transport), registry classification must not degrade to `control_path=unknown`/`control_capable=false` for that target.
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
- Metadata bridge cutover-proof contract must capture the in-window checkpoint under the effective authority mode for that window (component when metadata cutover is active); trial-stage authority transitions must not manufacture false in-window owner/cutover regressions.
- Metadata bridge bounded windows with operator-provided `expected_target` must preserve target/route stability when that expected target is already active and route-supported; preflight recovery logic must not reselect non-capable targets mid-window.
- Metadata trial audit payloads are closeout-critical contracts and must always include canonical status fields (`status`, `requested_at`, `completed_at`) even when expected-meta preflight checks pass, so audit completeness and endpoint gates are deterministic.
- Metadata prep freshness gating must tolerate bounded active-playback contract-complete windows (resolved state/title/position/duration) when progress-clock freshness is temporarily stale; this posture must not fail-close authority ownership if core playback contract surfaces remain resolved.

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
