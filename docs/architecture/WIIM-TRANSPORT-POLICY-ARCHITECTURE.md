<!-- Description: WiiM transport policy architecture and mandatory startup decision flow for universal device handling. -->
<!-- Version: 2026.08.24.2 -->
<!-- Last updated: 2026-08-24 -->

# WiiM Transport Policy Architecture (Locked-In)

## Goal

Replace ad-hoc protocol heuristics with a universal, policy-driven decision flow for WiiM-capable devices that is:

- capability-evidence first,
- deterministic under startup churn,
- deterministic as the single startup path.

## Problem framing

Current setup behavior mixes:

- cached endpoint replay,
- partial capability probing,
- profile-name inference,
- startup retries.

This can create device-specific instability (for example protocol mismatch loops or repeated `initializing/unavailable` transitions) when cached assumptions and live transport posture diverge.

## Design principles

1. **Evidence over inference**
   - Prefer explicit capability fields and observed health over model-name assumptions.
2. **Two-phase resolution**
   - Pre-detect (cache-aware) decision, then post-detect (capability-aware) refinement.
3. **Fail-closed with bounded fallback**
   - Keep known-good paths unless evidence says they are wrong.
4. **Transport policy is internal API**
   - Setup code consumes a decision object; policy logic stays isolated.
5. **Single authoritative path**
   - Startup always uses transport policy resolution (no legacy branch toggle).

## Proposed module layout

- `custom_components/wiim/transport_policy.py`
  - policy enums/data classes
  - decision resolver for endpoint/protocol/port
  - policy diagnostics helpers
- `custom_components/wiim/__init__.py`
  - orchestration only: call resolver and apply decision
- `custom_components/wiim/const.py`
  - integration constants (no startup policy toggle)
- `custom_components/wiim/config_flow.py`
  - operator-facing options unrelated to startup policy path selection

## Decision tree (v1)

### Inputs

- host
- cached endpoint
- cached capabilities
- detected/live capabilities
- `http_port_reachable`

### Branches

1. If explicit HTTPS signals exist (`securemode=1`, explicit HTTPS security, HTTPS-only priority):
   - set endpoint `https://host:443`.
2. Else if capabilities prefer HTTP and port 80 reachable:
   - set endpoint `http://host:80`.
3. Else if cached endpoint exists:
   - keep cached endpoint.
4. Else:
   - keep autodetect posture (`endpoint=None`, no forced protocol/port).

### Side outcome

- `suppress_upnp_init` recommendation is policy-driven, but setup remains compatible when coordinator does not support that argument.

## Migration steps

1. **Slice A (completed)**
   - Add architecture doc + feature flag plumbing.
   - Add policy module with non-invasive v1 decision tree.
   - Wire setup path behind flag and promote to default-on while keeping option override.
2. **Slice B**
   - Add structured policy telemetry counters/reason codes.
   - Add failure-classification memory (timeout/refused/protocol mismatch).
3. **Slice C**
   - Adaptive strategy switching based on bounded error thresholds.
4. **Slice D (completed)**
   - Lock in policy as mandatory startup decision path and remove legacy toggle/branch wiring.

## Operational safety posture

- Startup decisioning is single-path through the policy resolver.
- Policy decisions remain fail-closed with bounded autodetect fallback.
- Constructor compatibility guard remains for optional coordinator arguments.

## Exit criteria for lock-in

- No setup regressions across mixed device profiles.
- Reduced startup flapping frequency on previously unstable devices.
- Stable endpoint persistence across restarts.
- No increase in setup-time `ConfigEntryNotReady` loops.
