# Description: MA control hub numeric thresholds and control tuning helpers.
# Version: 2026.04.27.1
# Last updated: 2026-04-27
# HUB MUST-READ: Contract parser methodology.
# - For complex attributes (`rooms`, `candidates_json`, etc.), prefer native sequence/mapping values first.
# - Only parse string JSON when trimmed payload starts with `[` or `{` and is not unknown/unavailable/none/''.
# - Never assume attribute payloads are string-only.
# - Some readers may still be unpatched; if you touch or find one, patch it to this dual-mode contract in the same change.

ma_balance:
  name: MA Group Balance
  min: -1.0
  max: 1.0
  step: 0.01
  mode: slider
  unit_of_measurement: ""
ma_meta_confidence_min:
  name: MA Meta Confidence Min
  min: 0
  max: 10
  step: 1
  initial: 4
ma_meta_stale_s:
  name: MA Meta Stale (s)
  min: 5
  max: 300
  step: 1
  initial: 45
ma_meta_paused_hide_s:
  # How long (seconds) a paused entity's metadata is kept before being hidden on all display surfaces.
  # Default 600 (10 minutes). Increase to keep metadata visible longer after pause; decrease for faster clear.
  name: MA Meta Paused Hide (s)
  min: 30
  max: 3600
  step: 30
  initial: 600
ma_pos_stall_s:
  name: MA Position Stall (s)
  min: 5
  max: 300
  step: 1
  initial: 15
ma_end_tolerance_s:
  name: MA End Tolerance (s)
  min: 0
  max: 10
  step: 0.5
  initial: 2
ma_override_pause_s:
  name: MA Override Pause Timeout (s)
  min: 5
  max: 600
  step: 1
  initial: 60
ma_auto_idle_s:
  name: MA Auto Select Idle (s)
  min: 5
  max: 600
  step: 1
  initial: 45
ma_auto_playing_s:
  name: MA Auto Select Playing (s)
  min: 1
  max: 60
  step: 1
  initial: 5
