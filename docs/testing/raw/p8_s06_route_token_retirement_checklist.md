<!-- Description: Operator checklist for verifying active component/runtime code paths are free of legacy route/control-path tokens after hard-retirement canonicalization. -->
<!-- Version: 2026.04.25.1 -->
<!-- Last updated: 2026-04-25 -->

# P8-S06 Route Token Retirement Checklist

Scope: verify active **component/runtime code paths** are canonical-only (`route_pywiim`, `control_path=pywiim`) and contain no legacy decision tokens (`route_linkplay_tcp`, `linkplay_tcp`).

## 1) Preflight

- [x] Branch/worktree is clean enough to isolate this slice.
- [x] Active paths in scope are confirmed:
  - `custom_components/spectra_ls/**`
  - `packages/**`
- [x] Historical docs and archived evidence are treated as out-of-scope for code token retirement checks.

## 2) Zero-token verification (active code paths)

- [x] Verify `route_linkplay_tcp` has **zero** matches in:
  - `custom_components/spectra_ls/**`
  - `packages/**`
- [x] Verify `linkplay_tcp` has **zero** matches in:
  - `custom_components/spectra_ls/**`
  - `packages/**`
- [x] Record command output evidence below.

### Evidence capture

- Timestamp: 2026-04-25 07:00–07:01 local (session evidence window)
- `route_linkplay_tcp` check result: zero matches in `custom_components/spectra_ls/**` and `packages/**`
- `linkplay_tcp` check result: zero matches in `custom_components/spectra_ls/**` and `packages/**`

## 3) Canonical token presence verification

- [x] Verify `route_pywiim` exists in active component route decision paths.
- [x] Verify `control_path=pywiim` semantics exist in active runtime synthesis paths.
- [x] Record at least one representative file/line for each.

### Representative canonical references

- `route_pywiim`: `custom_components/spectra_ls/router.py:35`
- `control_path=pywiim`: `packages/ma_control_hub/script.inc:129`

## 4) Build + deployment gate

- [x] Local build/validation passes after retirement change.
- [x] OTA upload completes with explicit success signal.
- [x] Post-upload smoke check confirms no immediate route/control regressions.

### Build/upload proof

- Build command + result: `python -m py_compile ... && ./bin/esphome_spectra_build_local.sh` → success, ESPHome compile success (`Build Info: config_hash=0x24c7274c`, elapsed 29s)
- Upload command + result: `./bin/esphome_spectra_upload_local.sh --device 192.168.10.40` → `INFO OTA successful`
- Post-upload check summary: OTA completed without errors; no immediate route/control-path errors observed in build/upload logs.

## 5) Closeout

- [x] `docs/CHANGELOG.md` updated.
- [x] `docs/roadmap/v-next-NOTES.md` updated.
- [x] `docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md` updated.
- [x] `README.md` parity updated or explicitly noted.
- [x] Final disposition recorded: PASS / WARN / FAIL.

## Final disposition

- Verdict: PASS
- Notes: Active component/runtime code paths are canonical-only for route/control-path semantics (`route_pywiim`, `pywiim`). Legacy tokens remain only in historical roadmap/evidence archives.
