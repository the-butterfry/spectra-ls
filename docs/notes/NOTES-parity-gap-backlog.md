<!-- Description: Structured backlog for runtime vs component parity gaps with pickup-ready implementation details. -->
<!-- Version: 2026.04.26.7 -->
<!-- Last updated: 2026-04-26 -->

# Parity Gap Backlog (Runtime ↔ Component)

Purpose:

- Capture every confirmed parity mismatch between legacy runtime (`packages/` + `esphome/`) and component (`custom_components/spectra_ls`) with enough detail to resume later without re-discovery.
- Keep entries discovery-first and rollback-safe.

## How to log a gap

When a mismatch is found, append a new entry using the schema below.

### Required schema (copy/paste)

```md
## GAP-YYYYMMDD-<slug>

- Status: open | in-progress | blocked | closed
- Severity: low | medium | high
- Found in slice: <slice id / date>
- Legacy source-of-truth:
  - File: `<absolute-or-repo-path>`
  - Symbol(s): `<automation/script/template/service names>`
  - Behavior summary: `<what legacy does>`
- Component current behavior:
  - File: `<absolute-or-repo-path>`
  - Symbol(s): `<method/service names>`
  - Observed mismatch: `<what is different>`
- Parity impact:
  - User-visible effect: `<effect>`
  - Risk: `<loop/race/regression/contract drift/etc>`
- Contract surfaces involved:
  - Entities/helpers/services: `<list>`
- Repro steps:
  1. `<step>`
  2. `<step>`
- Expected parity outcome:
  - `<explicit pass condition>`
- Proposed fix direction (no cowboy):
  - `<minimal root-cause fix approach>`
- Validation plan:
  - Static: `<py_compile/lint/template checks>`
  - Runtime evidence: `<exact template/service proof lines to capture>`
- Two-track disposition plan:
  - Runtime track: implemented | compatibility-shimmed | deferred (why)
  - Component track: implemented | compatibility-shimmed | deferred (why)
- Owner/next pickup cue:
  - `<what to do first when resuming>`
- Linked changelog/roadmap refs:
  - `<docs/CHANGELOG.md entry>`
  - `<roadmap references>`
```

## Open gaps

## GAP-20260426-ma-players-target-options-refresh

- Status: closed
- Severity: medium
- Found in slice: 2026-04-26 parity sweep (post no-control feedback closure)
- Legacy source-of-truth:
  - File: `/mnt/homeassistant/packages/ma_control_hub/automation.inc`
  - Symbol(s): `ma_update_target_options_start`
  - Behavior summary: on `sensor.ma_players` changes, legacy lifecycle refreshes target options (`script.ma_update_target_options`) before running auto-select (`script.ma_auto_select`).
- Component current behavior:
  - File: `/mnt/homeassistant/custom_components/spectra_ls/coordinator.py`
  - Symbol(s): `_compute_component_target_options_plan`, `async_run_component_players_change_refresh`, `_handle_state_change`, `async_run_component_auto_select_loop`
  - Observed mismatch (resolved): component listener path now refreshes target-options scaffold before auto-select on `sensor.ma_players` changes, and candidate synthesis additively includes capability-aware registry/profile-backed targets.
- Parity impact:
  - User-visible effect: helper option set can lag MA player inventory churn during component-authority migration windows.
  - Risk: stale options increase candidate mismatch/no-candidate loops.
- Contract surfaces involved:
  - Entities/helpers/services: `sensor.ma_players`, `input_select.ma_active_target`, target-options scaffold path, auto-select scaffold path, registry capability/profile signals.
- Repro steps:
  1. Enter component authority migration window.
  2. Change MA player inventory/state so available candidates differ.
  3. Verify whether helper options refresh occurs before component auto-select attempt.
- Expected parity outcome:
  - On MA-players changes, component performs bounded target-options refresh before auto-select.
- Proposed fix direction (no cowboy):
  - Add additive MA-player-change pre-step that invokes target-options scaffold before auto-select, and augment candidate synthesis with capability-aware registry/profile-backed candidates (no rewrite of existing planning path).
- Validation plan:
  - Static: `python3 -m py_compile /mnt/homeassistant/custom_components/spectra_ls/coordinator.py /mnt/homeassistant/custom_components/spectra_ls/const.py /mnt/homeassistant/custom_components/spectra_ls/__init__.py`.
  - Runtime evidence: in component-authority mode, capture MA-player-change sequence showing options-refresh attempt then auto-select attempt.
- Two-track disposition plan:
  - Runtime track: compatibility-shimmed (legacy automation remains rollback baseline).
  - Component track: implemented (MA-player-triggered options-refresh parity sequencing).
- Owner/next pickup cue:
  - Closed on 2026-04-26 after MA-player-change sequencing implementation and compile validation pass.
- Linked changelog/roadmap refs:
  - `docs/CHANGELOG.md` (2026-04-26 MA-players target-options refresh parity entry)
  - `docs/roadmap/v-next-NOTES.md` / `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`

## GAP-20260426-no-control-feedback-lifecycle

- Status: closed
- Severity: medium
- Found in slice: 2026-04-26 parity sweep (post watcher-gap closure)
- Legacy source-of-truth:
  - File: `/mnt/homeassistant/packages/ma_control_hub/automation.inc`
  - Symbol(s): `ma_feedback_no_control_capable_hosts`
  - Behavior summary: when `binary_sensor.ma_no_control_capable_hosts` stays `on` for 30s, runtime performs one-shot self-heal (`script.ma_update_target_options` + `script.ma_auto_select`), waits 10s, then creates persistent notification if still degraded; dismisses notification immediately when state goes `off`.
- Component current behavior:
  - File: `/mnt/homeassistant/custom_components/spectra_ls/coordinator.py`
  - Symbol(s): `_handle_state_change`, `_handle_no_control_feedback_hold_timer`, `_async_run_no_control_feedback_self_heal`, `_handle_no_control_feedback_post_heal_timer`, `_async_finalize_no_control_feedback_notification`, `_async_dismiss_no_control_feedback_notification`
  - Observed mismatch (resolved): component previously lacked equivalent no-control-capable-host feedback lifecycle; now implemented under guarded component authority.
- Parity impact:
  - User-visible effect: degraded host capability windows in component migration mode may miss expected warning/self-heal lifecycle behavior.
  - Risk: operator blind spot during persistent no-host windows and divergence from legacy recovery UX.
- Contract surfaces involved:
  - Entities/helpers/services: `binary_sensor.ma_no_control_capable_hosts`, `input_select.ma_active_target`, `sensor.ma_active_control_path`, `binary_sensor.ma_active_control_capable`, `sensor.ma_control_hosts`, persistent notification id `spectra_ls_no_control_capable_hosts`.
- Repro steps:
  1. Enter component authority migration window.
  2. Keep `binary_sensor.ma_no_control_capable_hosts` at `on` for >30s.
  3. Verify whether component performs self-heal + delayed persistent notification and dismisses on `off` transition.
- Expected parity outcome:
  - Component mirrors legacy lifecycle semantics (30s hold, one-shot heal, 10s recheck, create/dismiss notification), with explicit authority-safety gating to avoid duplicate compatibility-path behavior.
- Proposed fix direction (no cowboy):
  - Add bounded coordinator listeners/timers for no-control feedback lifecycle and reuse existing component scaffold methods (`async_build_target_options_scaffold`, `async_run_auto_select_scaffold`) for self-heal before notification.
- Validation plan:
  - Static: `python3 -m py_compile /mnt/homeassistant/custom_components/spectra_ls/coordinator.py /mnt/homeassistant/custom_components/spectra_ls/const.py /mnt/homeassistant/custom_components/spectra_ls/__init__.py`.
  - Runtime evidence: observe create/dismiss behavior of `spectra_ls_no_control_capable_hosts` against `binary_sensor.ma_no_control_capable_hosts` `on`/`off` transitions in component authority mode.
- Two-track disposition plan:
  - Runtime track: compatibility-shimmed (legacy automation retained as rollback baseline).
  - Component track: implemented (parity lifecycle mirrored under guarded component authority).
- Owner/next pickup cue:
  - Closed on 2026-04-26 after coordinator callback/timer parity implementation and `py_compile` pass.
- Linked changelog/roadmap refs:
  - `docs/CHANGELOG.md` (2026-04-26 no-control feedback parity entry)
  - `docs/roadmap/v-next-NOTES.md` / `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`

## GAP-20260426-auto-select-loop-watched-options-filter

- Status: closed
- Severity: medium
- Found in slice: 2026-04-26 parity evidence capture (lock/unlock/auto-select-loop)
- Legacy source-of-truth:
  - File: `/mnt/homeassistant/packages/ma_control_hub/automation.inc`
  - Symbol(s): `ma_auto_select_loop`
  - Behavior summary: event-trigger branch watches all helper options from `input_select.ma_active_target` and triggers auto-select when `trigger.event.data.entity_id` is in that full options list.
  - Evidence lines: `55-56` (`watched = options`, `ent in watched`).
- Component current behavior (resolved):
  - File: `/mnt/homeassistant/custom_components/spectra_ls/coordinator.py`
  - Symbol(s): `_handle_global_state_change`, `async_run_component_auto_select_loop`
  - Observed mismatch (historical): global state-change watcher narrowed watched options to entries starting with `media_player.` only.
  - Resolution: watcher now uses full non-empty helper-options membership (legacy-equivalent watched set semantics) and removes the unnecessary `media_player.` prefix filter.
- Parity impact:
  - User-visible effect: auto-select loop may not trigger for non-`media_player` helper option entries that legacy logic would still watch.
  - Risk: selection refresh drift / missed re-evaluation event in mixed option catalogs.
- Contract surfaces involved:
  - Entities/helpers/services: `input_select.ma_active_target` options, `sensor.ma_players`, `input_boolean.ma_override_active`, component global `state_changed` handling.
- Repro steps:
  1. Include a non-`media_player` option token in `input_select.ma_active_target` options (legacy-accepted shape).
  2. Emit a `state_changed` event for that option entity and compare legacy auto-select-loop trigger vs component watcher trigger.
- Expected parity outcome:
  - Component watcher should match legacy semantics for watched options resolution (or apply a documented/intentional divergence gate with explicit rationale).
- Proposed fix direction (no cowboy):
  - Replace hard `media_player.` prefix filter with legacy-equivalent watched-options membership check, then enforce safety via existing auto-select preflight guards (`players>0`, `override off`, authority gating).
- Validation plan:
  - Static: `python3 -m py_compile` on `custom_components/spectra_ls/coordinator.py`.
  - Runtime evidence: confirm state-change trigger parity by capturing whether `async_run_component_auto_select_loop` is invoked for watched non-`media_player` option entities.
- Two-track disposition plan:
  - Runtime track: implemented (legacy baseline unchanged).
  - Component track: implemented (watcher-filter parity gap closed).
- Owner/next pickup cue:
  - Gap closed on 2026-04-26; no further pickup action required unless regression evidence reopens this item.
- Linked changelog/roadmap refs:
  - `docs/CHANGELOG.md` (2026-04-26 parity build-out + backlog protocol entries)
  - `docs/roadmap/v-next-NOTES.md` / `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md` (latest run update)

## Non-gap reminders (evidence follow-ups)

- 2026-04-26: Lock/unlock/auto-select-loop parity behavior was implemented in component coordinator; collect runtime proof lines in next validation pass to close evidence loop.
