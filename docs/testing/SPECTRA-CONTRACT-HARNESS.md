<!-- Description: Usage and extension guide for Spectra LS isolated contract regression harness. -->
<!-- Version: 2026.08.18.3 -->
<!-- Last updated: 2026-08-18 -->

# Spectra LS Contract Harness (Isolated `unittest`)

This document explains what the local contract harness is, why it exists, and how to use/extend it safely.

## What this is

The contract harness is a lightweight Python test lane under:

- `tests/spectra_ls_contracts/harness.py`
- `tests/spectra_ls_contracts/test_contracts.py`

It validates **component packet/contract invariants** for refactor safety without booting a full Home Assistant runtime.

## Why we use this

- Fast regression checks during cohesion/hardening slices.
- Catch packet-shape/verdict drift that compile checks cannot detect.
- Keep refactors safer while preserving integration contracts.

This lane complements (not replaces) runtime/system validation templates in `docs/testing/raw/`.

## Current test coverage

The suite currently checks contract behavior for:

- Metadata cutover-prep validation packet structure.
- Metadata bridge stale-wait recovery status normalization.
- Scheduler decision packet shape and candidate behavior.
- Scheduler validation FAIL posture when route trace is missing.
- Route-safety validation mismatch fail semantics.
- Action-catalog validation summary schema semantics.
- Crossfade validation WARN posture when F4-S02 dependency is not ready.
- Explicit target-set dry-run contract semantics.
- Passthrough source-only keepalive semantics (no blank OLED label when source continuity is active).

## How to run

From repo root (`/mnt/homeassistant`):

- Run all tests:
  - `/home/cory/.venvs/esphome-ha/bin/python -m unittest discover -s /mnt/homeassistant/tests -p 'test_*.py'`

- Run only this harness module:
  - `/home/cory/.venvs/esphome-ha/bin/python -m unittest tests.spectra_ls_contracts.test_contracts`

Expected success output includes:

- `Ran <N> tests`
- `OK`

## Harness design notes

- The harness stubs `homeassistant.const.Platform` to avoid importing full HA packages.
- `FakeCoordinator`, `FakeHass`, and `FakeState` provide deterministic test doubles.
- Spectra modules are loaded via package-aware dynamic import so relative imports continue to work.

## How to add new tests (recommended workflow)

1. Add/adjust fake state payloads in test methods (prefer minimal payloads).
2. Call one workflow builder/method per test (single responsibility).
3. Assert:
   - contract keys exist,
   - verdict semantics are correct,
   - blocker/reason tokens are stable,
   - compatibility fields remain present where expected.
4. Keep assertions focused on **external contract behavior**; avoid brittle internal implementation coupling.

## Guardrails for future contributors

- Do not convert this lane into full HA integration tests; keep it fast and isolated.
- Keep test data explicit; avoid hidden global mutable fixtures.
- If a contract intentionally changes, update:
  1) tests,
  2) changelog,
  3) operator/developer docs that depend on that contract.

## Relationship to broader validation

Use this harness for quick local refactor confidence.
Use the run-window/diagnostic templates in `docs/testing/raw/` for system-level behavior verification and parity gates.
