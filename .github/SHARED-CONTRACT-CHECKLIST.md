<!-- Description: Mandatory go/no-go parity checklist for shared-contract changes across main and menu-only. -->
<!-- Version: 2026.04.19.1 -->
<!-- Last updated: 2026-04-16 -->

# Shared-Contract Checklist (Go / No-Go)

Use this checklist for any change that affects shared contracts between `main` and `menu-only`, including:

- RP2040 event protocol and IDs
- Control API behavior
- Helper/entity contracts and naming dependencies

If the change is **not** shared-contract scope, mark `N/A` in Section 1 and proceed with normal branch workflow.

---

## 1) Scope Classification

- [ ] I confirmed this change is shared-contract scope.
- [ ] Affected contract area(s) documented:
  - [ ] RP2040 protocol
  - [ ] Control API behavior
  - [ ] Helper/entity contracts
  - [ ] Other (document below)
- Notes:

## 2) Branch Parity Strategy (pick one)

- [ ] **Paired update path**: equivalent contract changes implemented in both branches.
- [ ] **Intentional divergence path**: divergence is required and migration plan recorded.

If divergence path selected:

- [ ] `docs/CHANGELOG.md` includes explicit divergence + migration note.
- [ ] Roll-forward plan and owner documented.

## 3) Implementation Evidence

- [ ] `main` commit SHA(s):
- [ ] `menu-only` commit SHA(s):
- [ ] Equivalent entrypoints/packages touched for both branches (or documented divergence):

## 4) Validation Gate (required)

- [ ] `main` entrypoint validated: `esphome/spectra_ls_system.yaml`
- [ ] `menu-only` entrypoint validated: `control-board-esp32-tcp.yaml`
- [ ] Required package paths exist and load in both branches.
- [ ] No contract-breaking helper/entity rename without migration note.

## 5) Deployment Safety

- [ ] Live filesystem paths were not moved/deleted; or reversible backup+restore was tested.
- [ ] Secret files remain untracked (`secrets.yaml`, `control-py/secrets.yaml`).

## 6) Final Decision

- [ ] **GO** — all required items complete and evidence recorded.
- [ ] **NO-GO** — unresolved parity risk remains.
- Decision summary:
- Reviewer/owner:
- Date:
