<!-- Description: Complete end-to-end operator runbook for Spectra install, validation, troubleshooting, rollback, and escalation. -->
<!-- Version: 2026.08.01.1 -->
<!-- Last updated: 2026-08-01 -->

# Complete Operator Runbook

Use this when you want one page that tells you exactly what to do from install to recovery.

## What success looks like

- Spectra is deployed
- Audio and lighting controls both work
- Room/target menus are populated
- You can prove state with build/deploy evidence
- If something breaks, you have a deterministic recovery path

## Before you touch anything

- [ ] Home Assistant is reachable
- [ ] ESPHome integration/add-on is available
- [ ] You have a known-good backup/snapshot
- [ ] Local secrets/placeholders are resolved

Reference: [`docs/setup/SPECTRA-HA-CONFIG-PLACEHOLDERS.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/setup/SPECTRA-HA-CONFIG-PLACEHOLDERS.md)

## Deploy flow (do this in order)

1. Validate HA config
2. Build ESPHome
3. Deploy OTA/flash
4. Open HA control surfaces
5. Verify routing + controls

Keep these proof lines every time:

- build status
- OTA status (or explicit reason not deployed)
- local `HEAD` and `origin/main` short SHAs

## Functional validation checklist

- [ ] `control_path` and `control_capable` surfaces look coherent
- [ ] At least one audio action succeeds and state reflects change
- [ ] At least one lighting action succeeds and state reflects change
- [ ] Active target aligns with expected route host/target
- [ ] OLED/now-playing telemetry updates at expected cadence

## Daily operations loop

1. Check sidebar/settings readiness
2. Run safe dry-run controls after mapping changes
3. Confirm last-attempt status
4. Capture quick evidence before and after risky edits

Related page: [Spectra Sidebar Settings](Spectra-Sidebar-Settings)

## Troubleshooting quick matrix

| Symptom | Likely cause | First action | Escalation |
| --- | --- | --- | --- |
| Empty room/target options | unresolved placeholders or helper/entity drift | re-check placeholder and helper state | run [Operations Runbooks](Operations-Runbooks) |
| Commands fire but state doesn’t move | route metadata unresolved or wrong target | verify active target + route metadata | capture logs and file bug |
| OLED blank/stale while playback is active | metadata selection or display-allow policy gate | verify display-allowed + freshness surfaces | collect now-playing packet evidence |
| CI hardcode guard fails | install-specific literal or namespace policy mismatch | run local audit, inspect listed file/line | apply scoped contract-safe fix |

## Rollback runbook

Use rollback when behavior regresses and quick fixes are uncertain.

1. Restore known-good config snapshot
2. Re-deploy known-good firmware
3. Re-validate audio + lighting controls
4. Record what changed between known-good and failed state
5. Open follow-up issue with repro and rollback evidence

## Escalation packet (copy/paste)

- Environment: HA + ESPHome versions
- Branch/commit:
- Last known-good commit:
- Repro steps:
- Expected behavior:
- Actual behavior:
- Impact:
- Logs/evidence:
- Rollback attempted (yes/no + result):

## Where to go next

- Install path: [Install on Your Own Home Assistant](Install-on-Your-Own-HA)
- Setup/integration detail: [User Setup, Deploy, and HA Integration](User-Setup-Deploy-and-HA-Integration)
- Incident response: [Operations Runbooks](Operations-Runbooks)
- Bug intake: [Welcome, README, and Bug Workflow](Welcome-README-and-Bug-Workflow)
