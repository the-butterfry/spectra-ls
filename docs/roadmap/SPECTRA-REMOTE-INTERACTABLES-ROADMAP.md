<!-- Description: Roadmap for Spectra remote BLE-first evolution with extensible interactables architecture. -->
<!-- Version: 2026.07.17.6 -->
<!-- Last updated: 2026-07-17 -->

# Spectra Remote + Interactables Roadmap

## Purpose

Define the implementation roadmap for evolving Spectra remote control from Wi-Fi-first to BLE-first hybrid operation while preserving Home Assistant policy ownership and enabling additional Spectra interactables (knobs, buttons, pads, sensors, remotes) to plug into the same control plane later.

This document is planning-only and intentionally separates roadmap design from implementation slices.

## Scope and Non-Goals

### In Scope

- BLE-first remote input path with deep-sleep-first battery posture.
- On-demand Wi-Fi maintenance mode (long-press trigger) for OTA/debug.
- HA-side ingest, mapping, dedupe, and observability for interactable events.
- Contract model that supports future interactables beyond the current remote.

### Out of Scope (for this roadmap phase)

- Immediate replacement of all current Wi-Fi controls.
- Hard removal of existing runtime fallback paths before parity proof.
- Device-specific hardcoded entity IDs in product logic.

## Current-State Baseline (confirmed)

- Home Assistant runtime includes `bluetooth`, `bluetooth_adapters`, `esphome`, `automation`, `script`, and `websocket_api`.
- BLE infrastructure is active (BLE proxy/presence entities present).
- Spectra control-plane service `spectra_ls.execute_control_center_input` is available and already models canonical input events:
  - `encoder_turn`, `encoder_press`, `encoder_long_press`, `button_1..button_4`.
- Current remote path already includes deep-sleep and reduced telemetry posture, with HA contract-state subscription active.

## Design Principles

1. **Policy in HA/component, transport at edge**  
   Interactables emit intent; HA/component decides target/action.

2. **Discovery-first contracts**  
   Prefer capability/route contracts over install-specific entity hardcoding.

3. **Fail-closed + explicit fallback**  
   Unknown/ambiguous mapping should not execute uncontrolled writes.

4. **Battery-first runtime defaults**  
   BLE for routine controls; Wi-Fi only for bounded maintenance windows.

5. **Interactable-extensible event schema**  
   One normalized event contract for remote + future interactables.

## Canonical Event Contract (proposed)

All interactable-origin input should normalize into this logical payload before action execution:

- `interactable_id` (stable source identity; e.g., `spectra_remote_primary`)
- `input_event` (canonical key; e.g., `encoder_turn`, `button_2`)
- `delta` (optional signed numeric for turn/analog events)
- `gesture` (optional; tap/double/long/hold/release)
- `target_hint` (optional route hint)
- `correlation_id` (optional trace token)
- `ts_ms` (event timestamp)
- `transport` (`ble` | `wifi_api`)

The execution sink remains `spectra_ls.execute_control_center_input` (direct or via mapper).

## Target Architecture

### A) BLE-first Control Lane (default)

- Interactable wakes briefly and emits compact BLE event frame.
- Nearby always-on ESPHome BLE proxies forward into HA Bluetooth stack.
- HA mapping automation/service bridge normalizes and dispatches control-center input.
- Interactable returns to deep sleep quickly.

### B) Wi-Fi Maintenance Lane (bounded)

- Long-press action enables Wi-Fi/API for a maintenance TTL window.
- Purpose: OTA, diagnostics, contract troubleshooting.
- Window auto-expires and device returns to BLE-first posture.

### C) Safety + Fallback

- If BLE ingest degrades, maintenance long-press provides operator recovery.
- Optional fallback execution mode may route through existing Wi-Fi path until BLE parity is proven.

## HA-Side Workstream

### 1) Ingest and Normalization

- Introduce BLE-event intake automation(s) that parse BLE payloads and normalize into canonical event fields.
- Add explicit schema validation and reject malformed events.

### 2) Mapping and Execution

- Route normalized events to `spectra_ls.execute_control_center_input`.
- Enforce input allowlist (`CONTROL_CENTER_INPUT_EVENTS`) and optional source allowlist (`interactable_id`).

### 3) Dedupe and Rate Control

- Apply short dedupe windows for bursty hardware events (especially turns).
- Keep deterministic ordering for sequential events.

### 4) Observability

- Add helper/diagnostic surfaces:

  - last BLE event timestamp/source
  - event drop/invalid counters
  - p50/p95 action latency from event-receive to action dispatch

### 5) Governance and Operator UX

- Dashboard card for interactable health and maintenance-mode state.
- Runbook for BLE degradation triage and manual fallback.

## Firmware Workstream (Remote First)

### Stage R1 — Hybrid Readiness

- Keep current Wi-Fi path intact.
- Add BLE event emission in parallel (non-authoritative dry-run capable).

### Stage R2 — BLE Authoritative Actions

- Promote BLE lane to authoritative for routine controls.
- Keep Wi-Fi maintenance long-press available.

### Stage R3 — Power Profile Tightening

- Shorten awake windows, minimize telemetry, confirm deep-sleep cadence.
- Validate no regression in perceived interaction latency.

## Interactable Expansion Model (beyond remote)

Future interactables should integrate by implementing the same canonical event contract.

### Planned interactable classes

- Rotary modules (single/double encoder)
- Button pads/macros
- Room scene triggers
- Gesture/touch controls
- Environmental/presence-informed control surfaces

### Onboarding checklist per interactable

1. Assign `interactable_id` and capability profile.
2. Map hardware gestures to canonical `input_event` keys.
3. Validate event schema + dedupe behavior.
4. Prove action parity via control-center execution.
5. Add observability counters and rollback toggle.

## Phased Milestones

### M0 — Spec and Instrumentation (planning + diagnostics)

- Finalize event schema.
- Add HA diagnostic entities/counters for BLE lane evaluation.
- Exit criteria: observability in place; no runtime behavior cutover yet.

### M1 — BLE Parallel Shadow

- BLE events processed in shadow mode (dry-run + audit).
- Compare BLE-intended actions vs current authoritative actions.
- Exit criteria: parity confidence and low mismatch rate.

### M2 — BLE Active for Core Inputs

- Activate BLE authoritative lane for encoder turn/press + next-track class inputs.
- Keep Wi-Fi maintenance and rollback switches.
- Exit criteria: operator-acceptable latency and reliability.

### M3 — Multi-Interactable Generalization

- Add second interactable type using same contract.
- Prove schema and mapping are reusable beyond remote.
- Exit criteria: no per-device one-off control logic required.

### M4 — Cleanup and Stabilization

- Retire obsolete polling/redundant transport branches where safe.
- Lock in docs/runbooks/dashboard parity.
- Exit criteria: stable BLE-first operations with explicit fallback posture.

## Milestone Status Snapshot (2026-07-17)

- `M0`: implemented (observability and bridge instrumentation in place)
- `M1`: implemented (shadow validation and parity harness in place)
- `M2`: implemented (cutover profiles + readiness/rollback safety + activation gating)
- `M3`: active (closeout certification + sustained packet cadence executing)
- `M4`: active (stabilization starter + closeout/retirement/finalization evidence lanes executing)

Latest run update (2026-07-17, M3 closeout packet + reusable-contract evidence gate):

- Added deterministic M3 closeout certification surfaces in the runtime interactables lane: reusable-contract status, unique interactable count, closeout blockers/verdict, and one-click packet capture path for operator proof.
- Runtime track disposition: implemented (M3 closure automation and evidence surfaces added in package lane).
- Component track disposition: compatibility-shimmed (execution continues through existing `spectra_ls.execute_control_center_input` sink; no component semantic mutation).
- M3 impact check: no source-of-truth ownership reassignment; reusable-contract closure proof and activation confidence hardening only.

Latest run update (2026-07-17, M3 acceleration + M4 stabilization starter):

- Added closeout freshness timestamping, automatic closeout packet cadence, explicit closeout-ready binary gate, and M4 starter stabilization cycle controls (notification hygiene + bounded counter reset + health packet output).
- Runtime track disposition: implemented (cadence + stabilization controls in package lane).
- Component track disposition: compatibility-shimmed (existing execution sink reused; no component semantic mutation).
- M3/M4 impact check: no source-of-truth ownership reassignment; rollout velocity and operational stability hardening only.

Latest run update (2026-07-17, M4 closeout gate + packet cadence):

- Added deterministic M4 closeout governance surfaces: closeout blockers/verdict, closeout-ready binary gate, one-click packet capture, and timed auto-capture cadence for sustained readiness evidence.
- Runtime track disposition: implemented (M4 closeout readiness contract and packet automation added in package lane).
- Component track disposition: compatibility-shimmed (execution sink remains `spectra_ls.execute_control_center_input`; no component semantic mutation).
- M4 impact check: no source-of-truth ownership reassignment; stabilization-closeout evidence determinism and operator proof hardening only.

Latest run update (2026-07-17, M4 retirement-readiness gate + packet cadence):

- Added deterministic M4 retirement-readiness governance surfaces: retirement blockers/verdict, retirement-ready binary gate, one-click retirement packet capture, and periodic retirement auto-capture cadence for sustained-ready evidence.
- Runtime track disposition: implemented (M4 retirement-readiness contract and packet automation added in package lane).
- Component track disposition: compatibility-shimmed (execution sink remains `spectra_ls.execute_control_center_input`; no component semantic mutation).
- M4 impact check: no source-of-truth ownership reassignment; stabilization-retirement evidence determinism and operator readiness proof hardening only.

Latest run update (2026-07-17, M4 finalization super-slice):

- Added sustained retirement-soak and finalization governance surfaces: retirement-ready soak age tracking, finalization blockers/verdict, finalization-ready binary gate, one-click finalization packet capture, and periodic finalization auto-capture cadence.
- Runtime track disposition: implemented (M4 finalization readiness contract and packet automation added in package lane).
- Component track disposition: compatibility-shimmed (execution sink remains `spectra_ls.execute_control_center_input`; no component semantic mutation).
- M4 impact check: no source-of-truth ownership reassignment; stabilization-to-retirement closeout determinism and operator finalization proof hardening only.

## Validation Matrix

Minimum validation gates before each phase promotion:

- **Correctness:** expected action executes for each mapped input.
- **Latency:** p50/p95 dispatch latency within agreed UX target.
- **Reliability:** event loss/duplication under stress below threshold.
- **Power:** battery-life delta improves versus Wi-Fi-first baseline.
- **Recovery:** long-press maintenance mode reliably restores OTA/debug access.

## Risks and Mitigations

- **BLE coverage holes** → require proxy overlap in active zones; add coverage diagnostics.
- **Duplicate turn events** → dedupe windows + directional cadence guards.
- **Event schema drift** → enforce schema validation and contract tests.
- **Operational confusion during hybrid period** → clear dashboard status and maintenance TTL indicator.
- **Fallback regressions** → explicit rollback toggles + documented operator runbook.

## Ownership and Deliverables

- **Runtime track (`packages/`, `esphome/`)**: firmware transport posture + maintenance triggers + telemetry minimization.
- **Component track (`custom_components/spectra_ls/`)**: canonical event ingest, mapping, policy execution, diagnostics.
- **Docs track (`docs/`)**: roadmap, validation runbook, operator maintenance workflow.

Each implementation slice should record two-track disposition:

- runtime track: `implemented` / `compatibility-shimmed` / `deferred with rationale`
- component track: `implemented` / `compatibility-shimmed` / `deferred with rationale`
