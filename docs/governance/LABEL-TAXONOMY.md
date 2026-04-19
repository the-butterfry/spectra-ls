<!-- Description: Recommended GitHub labels taxonomy for issue triage, prioritization, and release hygiene. -->
<!-- Version: 2026.04.19.1 -->
<!-- Last updated: 2026-04-19 -->

# Label Taxonomy (Recommended)

Use this taxonomy to keep triage and release notes consistent.

## Type labels

- `bug`
- `enhancement`
- `documentation`
- `governance`
- `refactor`

## Priority labels

- `priority:p0`
- `priority:p1`
- `priority:p2`
- `priority:p3`

## Area labels

- `area:esphome-runtime`
- `area:ma-control-hub`
- `area:rp2040`
- `area:docs`
- `area:tooling`

## Workflow labels

- `good-first-issue`
- `needs-triage`
- `needs-repro`
- `blocked`
- `ready-for-review`

## Changelog labels (optional future automation)

- `changelog:breaking-change`
- `changelog:deprecated`
- `changelog:security`
- `changelog:feature`
- `changelog:enhancement`
- `changelog:bugfix`
- `changelog:documentation`

## Usage rules

- Apply at least one `type` + one `area` label on every issue.
- Add `priority` label after initial triage.
- Use `changelog:*` labels for PRs intended for release-note grouping.
