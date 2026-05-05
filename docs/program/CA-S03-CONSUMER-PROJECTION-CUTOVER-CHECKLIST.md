<!-- Description: CA-S03 component-first consumer projection cutover checklist with deterministic readiness scoring and sample evidence packet. -->
<!-- Version: 2026.05.05.1 -->
<!-- Last updated: 2026-05-05 -->

# CA-S03 Consumer Projection Cutover Checklist

## Purpose

Drive component-first consumer projection cutover with deterministic, auditable evidence.

This artifact is normative for CA-S03 closure claims.

## Scope

CA-S03 covers projection consumers (templates/diagnostics/sensor readers) and does **not** change write-path ownership.

## Required checks

1. **Projection source-lane check**
   - Confirm active consumer reads component-native surface first.
   - Confirm runtime surface is fallback-only.
   - Record effective source lane per field.

2. **Fallback-hit accounting**
   - Capture per-field fallback hits (`component_unavailable`, `payload_missing`, `runtime_fallback_used`).
   - Zero fallback hits is not required for this slice, but unexplained fallback drift is fail-closed.

3. **Consumer consistency check**
   - Confirm selected projection source lane aligns with policy summary shown in diagnostics output.
   - Confirm no contradictory next-action hints (for example claiming cutover-ready while fallback blockers are unresolved).

4. **Readiness gate check**
   - Compute deterministic projection-readiness gate from:
     - scheduler readiness,
     - selected target alignment,
     - component projection lane availability,
     - blocker/fallback posture.
   - Emit explicit `projection_cutover_ready=true|false` with reasons.

5. **Two-track disposition + impact check**
   - Runtime disposition and component disposition must be explicit.
   - P1/P2/P3 impact statement must be explicit.

## Pass policy

- **PASS**: component-first lane verified, fallback accounting present, readiness gate emitted with deterministic reasons.
- **WARN**: fallback activity exists but is bounded, explained, and non-contradictory.
- **FAIL**: missing projection lane evidence, contradictory readiness output, or unresolved blocker ambiguity.

## Canonical sample evidence packet

```json
{
  "schema_version": "ca_s03.projection.v1",
  "slice_id": "CA-S03",
  "parity_stamp": "2026-05-05/CA-S03-projection-cutover-baseline",
  "projection_fields": [
    {
      "field": "now_playing_entity",
      "preferred_source": "sensor.component_now_playing_entity",
      "effective_source": "sensor.component_now_playing_entity",
      "fallback_used": false
    },
    {
      "field": "now_playing_source",
      "preferred_source": "sensor.component_now_playing_source",
      "effective_source": "sensor.ma_active_source",
      "fallback_used": true,
      "fallback_reason": "component_sensor_unavailable"
    }
  ],
  "projection_fallback_counts": {
    "component_unavailable": 1,
    "payload_missing": 0,
    "runtime_fallback_used": 1
  },
  "projection_cutover_ready": false,
  "projection_blockers": [
    "component_now_playing_source_unavailable"
  ],
  "runtime_track_disposition": "compatibility-shimmed",
  "component_track_disposition": "implemented",
  "p1_p2_p3_impact": "No source-of-truth ownership reassignment; projection-consumer migration hardening only.",
  "closure_decision": "WARN"
}
```

## No-go conditions

Do not declare CA-S03 complete when any of these are true:

- consumer output does not report effective projection source lanes,
- fallback usage occurs without explicit reasons,
- cutover readiness is emitted without blocker-reason transparency,
- two-track disposition or P1/P2/P3 impact statement is missing.
