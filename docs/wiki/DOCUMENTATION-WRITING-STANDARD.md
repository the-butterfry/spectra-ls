<!-- Description: Writing standard for Spectra documentation and wiki pages, focused on native-English clarity, task completion, and reference-first structure. -->
<!-- Version: 2026.04.22.2 -->
<!-- Last updated: 2026-04-22 -->

# Documentation Writing Standard (Native-English, Directive, Useful)

Use this standard for [`README`](https://github.com/the-butterfry/spectra-ls/blob/main/README.md), [`docs/`](https://github.com/the-butterfry/spectra-ls/tree/main/docs), and all [`docs/wiki/`](https://github.com/the-butterfry/spectra-ls/tree/main/docs/wiki) pages.

## External style baselines used

This standard is aligned with patterns from:

- Home Assistant documentation standards and style guidance:
  - `https://developers.home-assistant.io/docs/documenting/standards/`
  - `https://developers.home-assistant.io/docs/documenting/general-style-guide`
- Kubernetes docs style/content guidance:
  - `https://kubernetes.io/docs/contribute/style/style-guide/`
  - `https://kubernetes.io/docs/contribute/style/content-guide/`
- Django documentation model and writing guidance:
  - `https://docs.djangoproject.com/en/stable/internals/contributing/writing-documentation/`
- Microsoft style baseline:
  - `https://learn.microsoft.com/style-guide/welcome/`

## Why this exists

Some pages currently read like generated text: generic wording, weak action verbs, and low task value.

This standard shifts docs to:

- plain, direct English,
- concrete operator actions,
- clear expected outcomes,
- practical troubleshooting and decision flow.

## Core writing rules

1. **Say what to do, not what might be done**
   - Prefer: “Run X, then verify Y.”
   - Avoid: “X can be used to potentially help with Y.”

1. **Lead with outcome**
   - First 3-5 lines should answer: “What problem does this page solve?”

1. **Use explicit step sequences**
   - Numbered steps for procedures.
   - Include pass/fail checks after each critical stage.

1. **Name real artifacts and surfaces**
   - Include exact file paths, service names, entity names, and menu paths.

1. **Replace vague adjectives with verifiable conditions**
   - Avoid: “works correctly”, “healthy”, “properly configured”.
   - Use: “build completes”, “OTA successful”, “entity state changes within expected interval”.

1. **State boundaries and non-goals explicitly**
   - Include short “In scope / Out of scope” blocks for operational pages.

1. **Troubleshooting must be decisive**
   - Symptom → likely cause → exact action.
   - No hand-wavy “check logs” without where/how/what to look for.

1. **Keep tone human and confident**
   - Short sentences.
   - Active voice.
   - No “AI voice” filler.

1. **Use direct links with context-rich link text**
   - Prefer: “See [`docs/roadmap/v-next-NOTES.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/roadmap/v-next-NOTES.md) for active slice status.”
   - Avoid: “See here” or bare URLs in body text.

1. **Use second-person guidance where actions are required**

   - Prefer: “Select…”, “Run…”, “Verify…”.
   - Avoid abstract phrasing that hides the actor.

1. **Separate content by doc type**

   - Tutorial: beginner outcome-first walkthrough.
   - How-to: task completion recipe.
   - Reference: strict facts/contracts only.
   - Explanation: architecture/context and rationale.

## Required page pattern (wiki)

Each operator-facing page should follow this structure:

1. **What this page is for** (2-4 lines)
2. **Before you start** (prerequisites)
3. **Do this** (numbered steps)
4. **Expected result** (pass criteria)
5. **If it fails** (troubleshooting table)
6. **Escalation path** (issue/discussion links)
7. **Source-of-truth references** (canonical docs)

### Reference section minimum

Every operational page should link at least:

- one canonical runtime/component source file,
- one roadmap ledger (`v-next` or component roadmap),
- one process/governance artifact ([`CONTRIBUTING.md`](https://github.com/the-butterfry/spectra-ls/blob/main/CONTRIBUTING.md), PR template, or runbook).

## Anti-patterns to remove during maintenance

- Generic orientation paragraphs with no action.
- Duplicate wording across multiple pages.
- Long roadmap prose inside operator runbooks.
- Ambiguous terms (“soon”, “future”, “maybe”, “generally”).
- Mixed audience pages (operator + deep developer internals in one page).

## Example edits

### Weak example A

“This page provides guidance for setup and integration and may evolve over time.”

### Strong example A

“Use this page to install Spectra on your Home Assistant instance and verify audio + lighting control in under 30 minutes.”

---

### Weak example B

“If something is wrong, check your configuration and logs.”

### Strong example B

“If room/target menus are empty after restart: confirm placeholder values are resolved in [`docs/setup/SPECTRA-HA-CONFIG-PLACEHOLDERS.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/setup/SPECTRA-HA-CONFIG-PLACEHOLDERS.md), then revalidate HA config and refresh helper states.”

## Definition of done for documentation slices

A docs slice is complete only when:

- page language is direct and actionable,
- each procedure includes explicit expected outcomes,
- troubleshooting paths are concrete,
- wiki navigation points users to the right page in 1-2 clicks,
- roadmap/changelog parity entries are updated.

## Language defaults

- Use American English.
- Use sentence case headings.
- Prefer “for example” over “e.g.”.
- Avoid minimizing words (`just`, `simply`, `easy`, `obviously`).
- Avoid “we” where “you” or explicit subject is clearer.
