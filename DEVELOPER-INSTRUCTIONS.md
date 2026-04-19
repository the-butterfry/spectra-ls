<!-- Description: Contributor/developer workflow for Spectra L/S implementation, preflight, instrumentation, and documentation/code parity. -->
<!-- Version: 2026.04.19.1 -->
<!-- Last updated: 2026-04-19 -->

# Spectra L/S Developer Instructions

This document is the contributor runbook for implementation work on `main`.

Authoritative policy still lives in `.github/copilot-instructions.md`; this file operationalizes that policy into an implementation-ready workflow.

## 1) Preflight (Required Before Implementation)

Run this checklist before coding any feature slice:

1. **Branch + scope check**
   - Confirm target branch (`main` for active runtime work, `menu-only` only for stabilized v2/control-py).
   - Confirm authoritative workspace path is `/mnt/homeassistant`.

2. **Roadmap parity check**
   - Read current:
     - `esphome/spectra_ls_system/CUSTOM-COMPONENT-ROADMAP.md`
     - `esphome/spectra_ls_system/v-next-NOTES.md`
     - `esphome/spectra_ls_system/PARALLEL-PROGRAM-PLAYBOOK.md`
   - Verify intended slice is mapped for both tracks:
     - runtime (`packages/` + `esphome/`), and
     - custom component (`custom_components/spectra_ls/`) implemented/shimmed/deferred.

3. **Baseline architecture context**
   - Review:
     - `esphome/spectra_ls_system/CODEBASE-RUNTIME-ARCHITECTURE.md`
     - `packages/ma_control_hub/CONTROL-HUB-ARCHITECTURE.md`
     - `esphome/spectra_ls_system/DEAD-PATHS-CLEANUP.md`

4. **Contract freeze for target slice**
   - Identify and list helper/entity/script contracts that must not drift.
   - If contract changes are intentional, define migration behavior up front.

5. **System diagnostic baseline**
   - Run the Dev Tools templates baseline in order:
     - Template 1 (health)
     - Template 2 (routing path)
     - Template 3 (command readiness)
     - Template 5 (one-screen smoke)
   - Record baseline status (PASS/WARN/FAIL) before code edits.

6. **Build/compile baseline (ESPHome/runtime slices)**
   - Compile current target once before edits using local build helper when applicable.
   - Treat compile failure as a blocker before implementation proceeds.

## 2) Implementation Slice Workflow (Required)

For each slice:

1. Update `CHANGELOG.md` first with planned slice summary.
2. Make small, reversible changes local to root cause.
3. Keep comments current; remove stale nearby comments when behavior changes.
4. Run targeted verification after each small increment.
5. Keep both tracks explicitly mapped (runtime + custom-component disposition).

## 3) Instrumentation and Verification Workflow

Use instrumentation as the first verification layer, not a final afterthought.

### Home Assistant Dev Tools Templates

Primary playbook: `esphome/spectra_ls_system/DEVTOOLS-TEMPLATES.local.md`

Recommended routine after each meaningful change:

- Template 1: core health and sentinel entities
- Template 2: target → host → meta → now-playing path
- Template 3: writable controls and readiness
- Template 4: before/after action effect verification
- Template 5: compact smoke summary

### ESPHome Runtime Validation

- Validate and compile modified entrypoint/package stack before commit.
- For deployment tasks, OTA success evidence is required to claim completion.

### Logging and diagnostics discipline

- Prefer existing diagnostics entities/templates over ad-hoc noisy logging.
- Add temporary instrumentation only when required for root-cause proof.
- Remove temporary instrumentation in the same slice once issue is resolved.

## 4) Documentation Parity Workflow

When behavior/contracts/architecture change, update in the same change set:

1. `CHANGELOG.md`
2. Relevant architecture/runtime docs (for the changed domain)
3. `README.md` when operator-facing behavior/workflow changed
4. `esphome/spectra_ls_system/CUSTOM-COMPONENT-ROADMAP.md`
5. `esphome/spectra_ls_system/v-next-NOTES.md`

If README does not need a material update, note parity rationale explicitly in the slice notes/changelog context.

## 5) Code Hygiene Expectations

- Favor root-cause fixes over symptom patches.
- Avoid broad refactors unless requested or required by correctness.
- Keep naming stable and intent-revealing.
- Add concise in-code intent notes for non-obvious logic and guardrails.
- Preserve existing helper/entity contracts unless migration is intentional and documented.

## 6) Commit / Push / Proof

Before push:

1. Confirm required verification is complete (compile/tests/templates as applicable).
2. Commit a clean logical slice with a clear message.
3. Push and provide proof:
   - current `HEAD` short SHA,
   - `origin/main` short SHA,
   - match status when claiming synced.

For deployment slices, also include explicit OTA result evidence (`OTA successful` or exact blocker).

## 7) Definition of Done (Implementation Slice)

A slice is done only when all are true:

- Code change implemented and verified.
- Runtime/custom-component track disposition recorded.
- Required docs parity updates completed.
- Changelog updated.
- Commit pushed with sync proof.
- (If deployment requested) OTA completed with explicit success evidence.
