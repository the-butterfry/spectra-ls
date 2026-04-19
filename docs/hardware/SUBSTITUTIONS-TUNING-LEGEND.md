<!-- Description: Tuning legend for Spectra LS substitutions with baseline profile presets and rollout guidance. -->
<!-- Version: 2026.04.17.4 -->
<!-- Last updated: 2026-04-17 -->

# Substitutions Tuning Legend (Stage Profiles)

This guide defines reusable tuning profiles for `esphome/spectra_ls_system/substitutions.yaml`.

Use this when you want to compare control responsiveness vs. stability across different networks/devices.

## Substitutions layout map (where to edit what)

`substitutions.yaml` is now organized by domain so tuning isn’t buried in mixed UI/audio/lighting blocks.

- **System Runtime Cadence**: global scheduler + idle cadence (`audio_poll_interval_ms`, `heartbeat_interval_ms`, screensaver/boot/ring/encoder).
- **UI Display + Typography**: fonts, splash, scroll, now-playing text sizing.
- **UI Menu Layout + Behavior**: menu spacing/tiles/debug/idle behavior.
- **Audio UX + Metadata Windows**: audio overlay windows, meta freshness, volume UI range.
- **Audio Control-Target Prompting + Loop Tuning**: prompt cadence/guardrails, control loop tick, log throttles.
- **Audio Source Cycle + Meta Labels**: source cycling codes/labels and physical meta select label map.
- **Lighting UX Tunables**: hue/sat/brightness step + send cadence and brightness-only slider mode.
- **Display Loop Profiling (Debug)**: optional display loop profiling logs.

## Scope

These profiles tune five layers:

1. **Pot defer/settle behavior** (volume + EQ)
2. **TCP pacing/coalescing behavior**
3. **Burst guard behavior**
4. **TCP worker queue/task/log behavior**
5. **Control-loop/UI sync/log cadence behavior**

> Note: Arylic TCP tunables are compile-time values (passed via build flags). After changing them in substitutions, do a full ESPHome compile + upload.

## Parameters (what each one does)

### Pot pipeline knobs

- `volume_pot_send_interval_ms`: minimum spacing between immediate volume sends.
- `volume_pot_settle_ms`: how long volume waits for movement to settle before deferred send.
- `volume_pot_jump_steps`: bypass defer logic when a move is large enough.
- `eq_pot_send_interval_ms`: minimum spacing for EQ sends.
- `eq_pot_settle_ms`: EQ settle window before deferred send.
- `eq_pot_jump_steps`: EQ jump threshold.

### TCP pacing/coalescing knobs

- `arylic_tcp_timeout_ms`: TCP connect/send timeout per command.
- `arylic_tcp_min_interval_ms`: minimum per-host gap between sends.
- `arylic_tcp_dup_suppress_ms`: duplicate enqueue suppression window.
- `arylic_tcp_backoff_ms`: failure backoff after timeout/error.

### Burst guard knobs

- `arylic_tcp_burst_guard_enabled`: `1` enable, `0` disable.
- `arylic_tcp_burst_window_ms`: sliding window size.
- `arylic_tcp_burst_max_sends`: max sends inside one window before guard wait.

### TCP worker/log knobs

- `arylic_tcp_queue_len`: transport queue depth.
- `arylic_tcp_worker_stack`: worker task stack size.
- `arylic_tcp_worker_prio`: worker task priority.
- `arylic_tcp_log_interval_ms`: minimum interval between TX log lines.

### Control-loop/UI sync/log knobs

- `audio_control_loop_interval_ms`: scheduler tick for control-target evaluation + deferred pot flush.
- `ma_target_refresh_interval_ms`: periodic helper refresh cadence for MA active target helper.
- `meta_override_settle_ms`: settle wait after meta target cycle before label refresh.
- `input_raw_log_interval_ms`: throttle for raw input/status log lines.
- `input_send_log_interval_ms`: throttle for send/defer input log lines.
- `audio_gate_log_interval_ms`: throttle for gate-block warning logs.

## Profile presets

Apply one full profile at a time.

### Profile 0 — Baseline (conservative)

```yaml
volume_pot_send_interval_ms: "50"
volume_pot_settle_ms: "120"
volume_pot_jump_steps: "3"
eq_pot_send_interval_ms: "200"
eq_pot_settle_ms: "120"
eq_pot_jump_steps: "3"

arylic_tcp_timeout_ms: "120"
arylic_tcp_min_interval_ms: "50"
arylic_tcp_dup_suppress_ms: "50"
arylic_tcp_backoff_ms: "200"
arylic_tcp_burst_guard_enabled: "1"
arylic_tcp_burst_window_ms: "180"
arylic_tcp_burst_max_sends: "3"
arylic_tcp_queue_len: "16"
arylic_tcp_worker_stack: "4096"
arylic_tcp_worker_prio: "1"
arylic_tcp_log_interval_ms: "500"
```

### Profile A — Safe (smoother, less lag)

```yaml
volume_pot_send_interval_ms: "35"
volume_pot_settle_ms: "80"
volume_pot_jump_steps: "2"
eq_pot_send_interval_ms: "140"
eq_pot_settle_ms: "90"
eq_pot_jump_steps: "2"

arylic_tcp_timeout_ms: "120"
arylic_tcp_min_interval_ms: "40"
arylic_tcp_dup_suppress_ms: "35"
arylic_tcp_backoff_ms: "200"
arylic_tcp_burst_guard_enabled: "1"
arylic_tcp_burst_window_ms: "150"
arylic_tcp_burst_max_sends: "4"
arylic_tcp_queue_len: "16"
arylic_tcp_worker_stack: "4096"
arylic_tcp_worker_prio: "1"
arylic_tcp_log_interval_ms: "500"
```

### Profile B+ — Performance Default (recommended)

```yaml
volume_pot_send_interval_ms: "25"
volume_pot_settle_ms: "50"
volume_pot_jump_steps: "1"
eq_pot_send_interval_ms: "90"
eq_pot_settle_ms: "60"
eq_pot_jump_steps: "1"

arylic_tcp_timeout_ms: "140"
arylic_tcp_min_interval_ms: "45"
arylic_tcp_dup_suppress_ms: "45"
arylic_tcp_backoff_ms: "220"
arylic_tcp_burst_guard_enabled: "1"
arylic_tcp_burst_window_ms: "120"
arylic_tcp_burst_max_sends: "5"
arylic_tcp_queue_len: "16"
arylic_tcp_worker_stack: "4096"
arylic_tcp_worker_prio: "1"
arylic_tcp_log_interval_ms: "500"

audio_control_loop_interval_ms: "150"
ma_target_refresh_interval_ms: "15000"
meta_override_settle_ms: "160"
input_raw_log_interval_ms: "700"
input_send_log_interval_ms: "450"
audio_gate_log_interval_ms: "1200"
```

### Profile B++ — DJ Candidate (TBD soak)

```yaml
volume_pot_send_interval_ms: "20"
volume_pot_settle_ms: "35"
volume_pot_jump_steps: "1"
eq_pot_send_interval_ms: "70"
eq_pot_settle_ms: "45"
eq_pot_jump_steps: "1"

arylic_tcp_timeout_ms: "90"
arylic_tcp_min_interval_ms: "40"
arylic_tcp_dup_suppress_ms: "35"
arylic_tcp_backoff_ms: "140"
arylic_tcp_burst_guard_enabled: "1"
arylic_tcp_burst_window_ms: "110"
arylic_tcp_burst_max_sends: "6"
arylic_tcp_queue_len: "20"
arylic_tcp_worker_stack: "4096"
arylic_tcp_worker_prio: "2"
arylic_tcp_log_interval_ms: "500"

audio_control_loop_interval_ms: "130"
ma_target_refresh_interval_ms: "12000"
meta_override_settle_ms: "140"
input_raw_log_interval_ms: "600"
input_send_log_interval_ms: "400"
audio_gate_log_interval_ms: "1000"
```

## Network-quality guidance (using your ping-style checks)

- If RTT is mostly single-digit ms with **occasional spikes** (e.g., max around 40–60ms), use **B+ default**.
- If RTT remains tight and stable under sustained control tests (minimal timeout warnings), test **B++**.
- If timeout warnings increase, roll back to B+ and raise `arylic_tcp_timeout_ms`/`arylic_tcp_backoff_ms` before touching pot cadence.

## Stage-by-stage rollout

1. Apply profile values in `substitutions.yaml`.
2. Compile/upload ESPHome.
3. Run fast knob sweeps for volume + EQ for 60–120s each.
4. Check logs for:
   - `Pot defer` / `Pot deferred send` density
   - `connect() timeout` frequency
   - burst guard wait logs (if enabled)
5. If timeouts increase, raise timeout/backoff before reducing responsiveness.

## Suggested decision rules

- If feel is laggy but stable: reduce `*_settle_ms` and `*_send_interval_ms` first.
- If TCP timeouts appear during aggressive movement: raise `arylic_tcp_timeout_ms` and `arylic_tcp_backoff_ms`.
- If command bursts overwhelm target: lower `arylic_tcp_burst_max_sends` or raise `arylic_tcp_burst_window_ms`.
- If controls feel over-throttled: lower `arylic_tcp_min_interval_ms` and `arylic_tcp_dup_suppress_ms` in small steps.

## Where to edit

- Runtime tuning values: `esphome/spectra_ls_system/substitutions.yaml`
- TCP implementation defaults and usage: `esphome/spectra_ls_system/components/arylic_tcp.h`
- Build-flag wiring: `esphome/spectra_ls_system.yaml`
