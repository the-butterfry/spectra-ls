<!-- Description: CA-S02B resolver replay validation checklist and deterministic sample acceptance packet for closure-grade replay evidence. -->
<!-- Version: 2026.05.05.1 -->
<!-- Last updated: 2026-05-05 -->

# CA-S02B Resolver Replay Validation Checklist + Deterministic Sample Packet

## Purpose

Operationalize CA-S02 replay determinism verification with a single repeatable artifact.

This checklist is normative for CA-S02B closure claims.

## Required replay checklist

Run these checks in order. A replay run is valid only when all required checks pass.

1. **Input fingerprint capture**
   - Record immutable input payload fingerprint (`input_payload_hash`).
   - Record resolver config fingerprint (`resolver_config_hash`).
   - Record scoring weights and tie-break policy version.

2. **Replay matrix execution**
   - Execute at least 3 replay runs against the same input fingerprint.
   - Use explicit replay IDs (`replay-01`, `replay-02`, `replay-03`).
   - Capture each run timestamp and environment stamp.

3. **Winner/rank invariance checks**
   - `winner.target` must be identical across all runs.
   - Ordered ranked-candidate list (top N) must be identical across all runs.
   - Per-candidate `score_total` must be identical up to precision policy (`<= 0.001`).

4. **Determinism hash checks**
   - `determinism_replay_hash` must be identical across all runs.
   - Any hash drift is fail-closed unless explicitly justified by input/config fingerprint drift.

5. **Tie-break determinism checks**
   - For epsilon ties, final order must follow policy:
     1) freshness,
     2) confidence,
     3) source priority,
     4) stable lexical `source_ref`.
   - Record at least one tie-case replay when available.

6. **Blocker taxonomy checks**
   - Blockers must be tokenized and stable across identical replay runs.
   - Empty blockers allowed when clean; missing blocker field is not allowed.

7. **Two-track disposition + impact check**
   - Runtime disposition and component disposition must be explicit.
   - P1/P2/P3 impact statement must be explicit.

## CA-S02B pass policy

- **PASS**: all required checks pass, no unexplained hash/order drift.
- **WARN**: non-critical evidence omission (for example missing optional tie-case sample) with explicit rationale.
- **FAIL**: any winner/rank/hash instability under identical input+config fingerprints, or missing required fields.

## Deterministic sample acceptance packet (canonical example)

Use this structure when publishing CA-S02B replay evidence.

```json
{
  "schema_version": "ca_s02b.replay.v1",
  "slice_id": "CA-S02B",
  "parity_stamp": "2026-05-05/CA-S02B-replay-validation",
  "input_payload_hash": "sha256:4e0f4e4d5f6a5abf8d2f6c2f8782d2af5d2db6f45c1c0b0a8f9d22d5e09f6b64",
  "resolver_config_hash": "sha256:95f0fdb96383d99aa4af0f4d6a5a0bf2bbdf34f6aa2398d7994dbf6a6a5f15e7",
  "weights": {
    "confidence": 0.35,
    "freshness": 0.30,
    "match_strength": 0.20,
    "source_priority": 0.15
  },
  "tie_break_policy": "ca_s02a.tie_break.v1",
  "replay_runs": [
    {
      "replay_id": "replay-01",
      "timestamp": "2026-05-05T02:11:04Z",
      "winner_target": "media_player.spectra_ls_2",
      "winner_score": 0.912,
      "ranked_targets_top3": [
        "media_player.spectra_ls_2",
        "media_player.kitchen_speakers",
        "media_player.tv_room"
      ],
      "determinism_replay_hash": "sha256:8a4f64f1d52b6d6f1c2f6485b0f6a1bc92e8df2fdbb8f76f2290f3a9b3bbd8c4",
      "blocking_reasons": []
    },
    {
      "replay_id": "replay-02",
      "timestamp": "2026-05-05T02:11:16Z",
      "winner_target": "media_player.spectra_ls_2",
      "winner_score": 0.912,
      "ranked_targets_top3": [
        "media_player.spectra_ls_2",
        "media_player.kitchen_speakers",
        "media_player.tv_room"
      ],
      "determinism_replay_hash": "sha256:8a4f64f1d52b6d6f1c2f6485b0f6a1bc92e8df2fdbb8f76f2290f3a9b3bbd8c4",
      "blocking_reasons": []
    },
    {
      "replay_id": "replay-03",
      "timestamp": "2026-05-05T02:11:29Z",
      "winner_target": "media_player.spectra_ls_2",
      "winner_score": 0.912,
      "ranked_targets_top3": [
        "media_player.spectra_ls_2",
        "media_player.kitchen_speakers",
        "media_player.tv_room"
      ],
      "determinism_replay_hash": "sha256:8a4f64f1d52b6d6f1c2f6485b0f6a1bc92e8df2fdbb8f76f2290f3a9b3bbd8c4",
      "blocking_reasons": []
    }
  ],
  "replay_assertions": {
    "winner_stable": true,
    "rank_order_stable": true,
    "score_stable_within_epsilon": true,
    "hash_stable": true,
    "blockers_stable": true
  },
  "runtime_track_disposition": "compatibility-shimmed",
  "component_track_disposition": "implemented",
  "p1_p2_p3_impact": "No source-of-truth ownership reassignment; replay-governance determinism hardening only.",
  "closure_decision": "PASS"
}
```

## No-go conditions

Do not declare CA-S02B complete when any condition below is true:

- identical input/config fingerprints produce different `winner_target`,
- ranked candidate order drifts across replay runs,
- replay hash drifts without corresponding input/config fingerprint change,
- required fields are omitted from the acceptance packet.
